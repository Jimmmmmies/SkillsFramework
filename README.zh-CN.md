# SkillsFramework

[English](README.md) | 简体中文

SkillsFramework 是一个轻量级 Agent 框架，支持 **工具调用** 与 **技能（SKILL.md）注入**。通过继承基础 Agent 并组合内置工具/技能，实现多步执行与扩展能力。

## 特性

- **Agent 继承体系**：`BaseAgent` → `ReActAgent` → `ToolCallAgent` → `SkillsAgent`
- **工具系统**：将函数封装为 Tool，自动生成 OpenAI 工具调用 schema
- **MCP 集成**：支持将远程 MCP Server（`stdio` / `sse` / `streamable_http`）挂载为本地可调用工具
- **技能加载器**：从 `skills/<skill>/SKILL.md` 读取技能并注入提示词
- **LLM 客户端**：OpenAI 兼容异步客户端，自动识别 provider，带重试机制
- **结构化记忆**：统一消息/角色 schema
- **日志体系**：基于 loguru 输出按运行时间命名的日志文件

## 目录结构（核心文件）

```
app/
  agents/
    base.py        # BaseAgent：生命周期/记忆/状态
    react.py        # ReActAgent：思考/执行抽象
    toolcall.py     # ToolCallAgent：工具调用
    skills.py       # SkillsAgent：工具调用 + 技能注入
  tools/
    base.py         # tool 装饰器/ToolResult/schema 生成
    mcp.py          # MCP 传输/服务封装与远程工具挂载
    registry.py     # ToolRegistry 执行与 schema
    skillloader.py  # SkillLoader 读取 SKILL.md
    builtin/        # 内置工具（bash/load_skill/ask_human/file_edit...）
  prompts/
    toolcall.py     # ToolCallAgent 提示词
    skills.py       # SkillsAgent 提示词
  llm.py            # OpenAI 兼容异步客户端
  schema.py         # 消息/工具 schema
  config.py         # 默认配置与环境变量
skills/
  web-search/       # 示例技能包
tests/
  skillsagent.py    # 简单交互式 demo
```

## 快速开始

1. 安装依赖

```bash
uv sync
```

2. 配置环境变量（示例）

```bash
export LLM_API_KEY=...
export LLM_BASE_URL=...
export LLM_MODEL=deepseek-chat
```

3. 运行示例交互

```bash
uv run -m tests.skillsagent
```

## 技能（Skill）

每个技能放在 `skills/` 下独立目录，必须包含 `SKILL.md`（带 YAML frontmatter）。

**最小结构**：

```
skills/
  my-skill/
    SKILL.md
    scripts/        # 可选
    references/     # 可选
    assets/         # 可选
```

`SkillLoader` 会扫描技能目录并将技能元信息注入系统提示词，使 Agent 在需要时调用 `load_skill`。

## 工具系统

工具通过**基于装饰器的注解方式**进行注册。装饰器会解析函数签名与文档字符串，自动生成 OpenAI 工具 schema，因此开发者只需要声明函数及其参数。

**示例：使用注解注册工具（无需实现具体逻辑）**

```python
from app.tools.base import tool

@tool
async def search_docs(query: str, top_k: int = 5) -> dict:
    """
    搜索内部文档并返回匹配结果。

    Args:
        query: 搜索关键词。
        top_k: 返回结果的最大数量。

    Returns:
        包含匹配条目的字典。
    """
    ...
```

随后将该工具加入 `ToolRegistry`（或加入 Agent 的可用工具列表），Agent 才能调用该工具。

## 技能系统逻辑

技能是位于 `skills/<skill>/SKILL.md` 下、包含 YAML frontmatter 的**指令包**。运行时流程如下：

1. `SkillLoader` 扫描技能目录并解析 `SKILL.md` 的 frontmatter（name、description、path）。
2. Agent 的系统提示词会被**增强**：注入可用技能列表与简短使用说明。
3. 当用户请求与某个技能匹配时，Agent 会调用 `load_skill` 工具。
4. `load_skill` 会读取完整 `SKILL.md` 内容并返回给 Agent。
5. Agent 按照技能说明执行（可能包含运行 `skills/<skill>/scripts/` 下的脚本）。

## MCP 支持

SkillsFramework 支持通过 `MultiMCPServer` + `ToolRegistry` 一次性挂载多个远程 MCP Server，并统一暴露为本地可调用工具。

- **支持传输方式**：`stdio`、`sse`、`streamable_http`
- **配置输入**：支持 `dict` / `list` / JSON 字符串（由 `MultiMCPServer` 自动归一化）
- **挂载接口**：`await registry.mount_mcp_servers(multi)`
- **工具命名规则**：`<server_name>__<remote_tool_name>`（例如 `weather__forecast`）
- **会话生命周期**：在结束时调用 `await registry.close_mcp_sessions()`，以便优雅关闭 MCP 会话

**最小示例**：

```python
from app.tools import MultiMCPServer
from app.tools.registry import ToolRegistry

registry = ToolRegistry()

multi = MultiMCPServer(
    {
        "leetcode": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@jinzcdev/leetcode-mcp-server", "--site", "cn"],
        },
        "opgg-mcp": {
            "transport": "streamable_http",
            "url": "https://mcp-api.op.gg/mcp",
        },
    }
)

await registry.mount_mcp_servers(multi)
await registry.close_mcp_sessions()
```

**传输参数要求**：

- `stdio` 必须提供 `command`
- `sse` 与 `streamable_http` 必须提供 `url`

## 许可证

MIT 许可。详见 [LICENSE](LICENSE)。
