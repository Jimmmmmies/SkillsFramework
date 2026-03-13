import unittest
from contextlib import AsyncExitStack

from app.context import ToolContext
from app.tools.base import BaseTool, ToolResult
from app.tools.mcp import MCPServer, MCPTransport, MultiMCPServer
from app.tools.registry import ToolRegistry


class ContextEchoTool(BaseTool):
    async def execute(self, context=None, **kwargs):
        wd = str(context.working_dir) if context is not None else ""
        return ToolResult(output=wd)


class FakeMCPServer(MCPServer):
    async def list_tools_metadata(self):
        return [
            {
                "name": "forecast",
                "description": "Forecast tool",
                "parameters": {"type": "object", "properties": {}},
            }
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, object]):
        return ToolResult(output=f"{tool_name}:{arguments}")


class ReuseCounterServer(MCPServer):
    opens: int = 0

    async def _open_session(self):
        self.opens += 1

        class FakeSession:
            async def initialize(self):
                return None

            async def list_tools(self):
                class Result:
                    tools = [
                        type(
                            "ToolMeta",
                            (),
                            {
                                "name": "count",
                                "description": "Count tool",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        )()
                    ]

                return Result()

            async def call_tool(self, tool_name, arguments=None):
                class Result:
                    isError = False
                    content = [type("Text", (), {"text": f"{tool_name}:{arguments}"})()]

                return Result()

        return FakeSession(), AsyncExitStack()


class MCPMountTests(unittest.IsolatedAsyncioTestCase):
    def test_server_requires_transport_specific_fields(self):
        with self.assertRaises(ValueError):
            MCPServer(name="bad-stdio", transport=MCPTransport.STDIO)
        with self.assertRaises(ValueError):
            MCPServer(name="bad-sse", transport=MCPTransport.SSE)
        with self.assertRaises(ValueError):
            MCPServer(name="bad-http", transport=MCPTransport.STREAMABLE_HTTP)

    async def test_mount_mcp_server_registers_tools(self):
        server = FakeMCPServer(
            name="weather",
            transport=MCPTransport.STDIO,
            command="python",
            args=["Servers/Getweather.py"],
        )

        registry = ToolRegistry()
        await registry.mount_mcp_servers(server)

        self.assertIn("weather__forecast", registry.tool_map)
        result = await registry.execute_tool("weather__forecast", {"city": "beijing"})
        self.assertEqual(result.error, None)
        self.assertIn("forecast", result.output)

    async def test_execute_tool_injects_context_for_base_tool(self):
        tool = ContextEchoTool(
            name="ctx",
            description="ctx",
            parameters={"type": "object", "properties": {}},
        )
        registry = ToolRegistry(tool, tool_context=ToolContext())

        result = await registry.execute_tool("ctx", {})
        self.assertEqual(result.error, None)
        self.assertTrue(result.output)

    async def test_mcp_server_session_is_reused(self):
        server = ReuseCounterServer(
            name="reuse",
            transport=MCPTransport.STREAMABLE_HTTP,
            url="https://example.com/mcp",
        )
        registry = ToolRegistry()
        await registry.mount_mcp_servers(server)

        r1 = await registry.execute_tool("reuse__count", {"x": 1})
        r2 = await registry.execute_tool("reuse__count", {"x": 2})

        self.assertEqual(r1.error, None)
        self.assertEqual(r2.error, None)
        self.assertEqual(server.opens, 1)

        await registry.close_mcp_sessions()

    async def test_multi_mcp_server_from_dict_mounts_all(self):
        config = {
            "weather": {
                "transport": "stdio",
                "command": "python",
                "args": ["Servers/Getweather.py"],
            },
            "search": {
                "name": "search",
                "transport": "stdio",
                "command": "python",
                "args": ["Servers/Search.py"],
            },
        }
        multi = MultiMCPServer(config)

        names = [srv.name for srv in multi.to_servers()]
        self.assertEqual(names, ["weather", "search"])
        self.assertEqual(multi.to_servers()[0].transport, MCPTransport.STDIO)

    async def test_multi_mcp_server_from_json_string(self):
        config_json = '{"leetcode":{"transport":"stdio","command":"npx","args":["-y","@jinzcdev/leetcode-mcp-server","--site","cn"]}}'
        multi = MultiMCPServer(config_json)
        servers = multi.to_servers()

        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].name, "leetcode")
        self.assertEqual(servers[0].transport, MCPTransport.STDIO)


if __name__ == "__main__":
    unittest.main()
