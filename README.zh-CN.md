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

## MCP 支持

SkillsFramework 支持通过 `MCPServer` + `ToolRegistry` 将远程 MCP Server 挂载为本地可调用工具。

- **支持传输方式**：`stdio`、`sse`、`streamable_http`
- **挂载接口**：`await registry.mount_mcp_servers(...)`
- **工具命名规则**：`<server_name>__<remote_tool_name>`（例如 `weather__forecast`）
- **会话生命周期**：在结束时调用 `await registry.close_mcp_sessions()`，以便优雅关闭 MCP 会话

**最小示例**：

```python
from app.tools import MCPServer
from app.tools.registry import ToolRegistry

registry = ToolRegistry()

server = MCPServer(
    name="weather",
    transport="stdio",
    command="python",
    args=["Servers/Getweather.py"],
)

await registry.mount_mcp_servers(server)
result = await registry.execute_tool("weather__forecast", {"city": "beijing"})
await registry.close_mcp_sessions()
```

**传输参数要求**：

- `stdio` 必须提供 `command`
- `sse` 与 `streamable_http` 必须提供 `url`

## 许可证

MIT 许可。详见 [LICENSE](LICENSE)。
