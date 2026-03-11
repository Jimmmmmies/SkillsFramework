import inspect
import asyncio
from typing import TYPE_CHECKING, Any, List, Optional
from app.tools.base import BaseTool, ToolResult
from app.exceptions import ToolException
from app.logger import logger
from app.context import ToolContext

if TYPE_CHECKING:
    from app.tools.mcp import MCPServer


class ToolRegistry:
    """
    Registry for managing available tools.
    """

    def __init__(self, *tools: BaseTool, tool_context: Optional[ToolContext] = None):
        self.tools = list(tools)
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.tool_context = tool_context
        self._mcp_servers: list["MCPServer"] = []

    async def mount_mcp_servers(self, *servers: "MCPServer") -> "ToolRegistry":
        from app.tools.mcp import MCPServer

        for server in servers:
            if not isinstance(server, MCPServer):
                raise TypeError(f"Expected MCPServer, got {type(server).__name__}")

            mounted_tools = await server.build_tools()
            self.add_tools(*mounted_tools)
            if server not in self._mcp_servers:
                self._mcp_servers.append(server)

        return self

    async def close_mcp_sessions(self) -> "ToolRegistry":
        for server in self._mcp_servers:
            try:
                await asyncio.shield(server.close_session())
            except Exception as e:
                logger.warning(f"⚠️Failed to close MCP server '{server.name}': {e}")
        return self

    def __iter__(self):
        """
        Iterate over registered tools.
        """
        return iter(self.tools)

    def to_openai_schema(self) -> List[dict[str, Any]]:
        """
        Convert all registered tools to OpenAI schema format.
        """
        return [tool.to_openai_schema() for tool in self.tools]

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Retrieve a tool by its name.
        """
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        """
        Add a new tool to the registry.
        """
        if tool.name in self.tool_map:
            logger.warning(
                f"⚠️Tool with name '{tool.name}' already exists in the registry."
            )
            return self

        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        return self

    def add_tools(self, *tools: BaseTool):
        """
        Add multiple tools to the registry.
        """
        for tool in tools:
            self.add_tool(tool)
        return self

    def remove_tool(self, name: str):
        """
        Remove a tool from the registry by its name.
        """
        tool = self.tool_map.pop(name, None)

        if tool:
            logger.info(f"🗑️Removed tool '{name}' from the registry.")
            self.tools.remove(tool)
        return self

    def remove_tools(self, *names: str):
        """
        Remove multiple tools from the registry by their names.
        """
        for name in names:
            self.remove_tool(name)
        return self

    def clear(self):
        """
        Clear all tools from the registry.
        """
        self.tools.clear()
        self.tool_map.clear()
        return self

    async def execute_tool(self, name: str, tool_input: dict[str, Any]) -> ToolResult:
        """
        Execute a tool by its name with the given input.
        """
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(error=f"Tool '{name}' is not valid.")
        try:
            final_input = tool_input.copy() if tool_input else {}
            target = getattr(tool, "func", None)
            if target is None:
                target = tool.execute

            signature = inspect.signature(target)

            if "context" in signature.parameters:
                if "context" not in final_input:
                    final_input["context"] = self.tool_context

            result = await tool(**final_input)
            return result

        except ToolException as e:
            return ToolResult(error=e.message)
