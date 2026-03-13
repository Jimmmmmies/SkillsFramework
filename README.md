# SkillsFramework

English | [简体中文](README.zh-CN.md)

SkillsFramework is a lightweight agent framework that supports tool calling and skill (SKILL.md) injection. Agents inherit from a base class and can be extended with tools and skills to execute multi-step workflows.

## Features

- **Agent hierarchy**: `BaseAgent` → `ReActAgent` → `ToolCallAgent` → `SkillsAgent`
- **Tool system**: wrap Python functions as tools with auto-generated schemas
- **MCP integration**: mount remote MCP servers (`stdio` / `sse` / `streamable_http`) as local callable tools
- **Skill loader**: load skills from `skills/<skill>/SKILL.md` and inject metadata into prompts
- **LLM client**: OpenAI-compatible async client with provider auto-detection and retry
- **Structured memory**: message history with role-aware schema
- **Logging**: loguru-based, per-run log files

## Project Structure (key files)

```
app/
  agents/
    base.py        # BaseAgent: lifecycle, memory, state
    react.py        # ReActAgent: think/act abstraction
    toolcall.py     # ToolCallAgent: OpenAI tool calling
    skills.py       # SkillsAgent: tool calling + skill injection
  tools/
    base.py         # tool decorator, ToolResult, schema generation
    mcp.py          # MCP transport/server wrappers and remote tool mounting
    registry.py     # ToolRegistry execution & schema
    skillloader.py  # SkillLoader for SKILL.md
    builtin/        # built-in tools (bash, load_skill, ask_human, file_edit...)
  prompts/
    toolcall.py     # prompts for ToolCallAgent
    skills.py       # prompts for SkillsAgent
  llm.py            # OpenAI-compatible async client
  schema.py         # message/tool schema
  config.py         # defaults and env config
skills/
  web-search/       # example skill package
tests/
  skillsagent.py    # example interactive loop
```

## Quick Start

1. Install dependencies

```bash
uv sync
```

2. Configure environment variables (example)

```bash
export LLM_API_KEY=...
export LLM_BASE_URL=...
export LLM_MODEL=deepseek-chat
```

3. Run the demo chat loop

```bash
uv run -m tests.skillsagent
```

## Skills

Each skill lives in its own folder under `skills/` and must contain a `SKILL.md` with YAML frontmatter.

**Minimal structure**:

```
skills/
  my-skill/
    SKILL.md
    scripts/        # optional
    references/     # optional
    assets/         # optional
```

The `SkillLoader` scans the skills directory and injects available skill metadata into the system prompt, so the agent can decide when to call `load_skill`.

## Tool System

Tools are registered via a **decorator-based annotation**. The decorator inspects the function signature and docstring to generate the OpenAI tool schema automatically, so developers only need to declare the function and its arguments.

**Example: register a tool with annotations (no implementation required)**

```python
from app.tools.base import tool

@tool
async def search_docs(query: str, top_k: int = 5) -> dict:
    """
    Search internal documentation and return matched entries.

    Args:
        query: Search keywords.
        top_k: Maximum number of results to return.

    Returns:
        A dictionary containing matched entries.
    """
    ...
```

Then add your tool into a `ToolRegistry` (or include it in an agent's available tools) so the agent can call it.

## Skill System Logic

Skills are **instruction packs** living under `skills/<skill>/SKILL.md` with YAML frontmatter. At runtime:

1. `SkillLoader` scans skill folders and parses `SKILL.md` frontmatter (name, description, path).
2. The agent's system prompt is **augmented** with the available skills list and a short usage guide.
3. When the user request matches a skill, the agent calls the `load_skill` tool.
4. `load_skill` reads the full `SKILL.md` content and returns it to the agent.
5. The agent follows the skill instructions (may include running scripts under `skills/<skill>/scripts/`).

## MCP Support

SkillsFramework supports mounting multiple remote MCP servers as local callable tools via `MultiMCPServer` + `ToolRegistry`.

- **Supported transports**: `stdio`, `sse`, `streamable_http`
- **Config input**: `dict` / `list` / JSON string (normalized by `MultiMCPServer`)
- **Mount API**: `await registry.mount_mcp_servers(multi)`
- **Tool naming**: `<server_name>__<remote_tool_name>` (for example, `weather__forecast`)
- **Lifecycle**: call `await registry.close_mcp_sessions()` on shutdown to close MCP sessions cleanly

**Minimal example**:

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

**Transport requirements**:

- `stdio` requires `command`
- `sse` and `streamable_http` require `url`

## License

MIT License. See [LICENSE](LICENSE).
