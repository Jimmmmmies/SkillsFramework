import json
import asyncio
from importlib import import_module
from contextlib import AsyncExitStack
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from app.tools.base import BaseTool, ToolResult


class MCPTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


class MCPServer(BaseModel):
    name: str
    transport: MCPTransport
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    url: str | None = None
    headers: dict[str, str] | None = None
    tool_name_prefix: str | None = None
    _worker_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)
    _worker_queue: asyncio.Queue[dict[str, Any]] | None = PrivateAttr(default=None)
    _worker_task: asyncio.Task[Any] | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _validate_transport_fields(self) -> "MCPServer":
        if self.transport == MCPTransport.STDIO and not self.command:
            raise ValueError("stdio transport requires command")
        if (
            self.transport
            in {
                MCPTransport.SSE,
                MCPTransport.STREAMABLE_HTTP,
            }
            and not self.url
        ):
            raise ValueError("sse/streamable_http transport requires url")
        return self

    async def _ensure_worker(self) -> None:
        task = self._worker_task
        queue = self._worker_queue
        if task is not None and queue is not None and not task.done():
            return

        async with self._worker_lock:
            task = self._worker_task
            queue = self._worker_queue
            if task is not None and queue is not None and not task.done():
                return

            queue = asyncio.Queue()
            started: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            task = asyncio.create_task(
                self._worker_loop(queue, started), name=f"mcp-{self.name}-worker"
            )
            self._worker_queue = queue
            self._worker_task = task
            try:
                await started
            except Exception:
                self._worker_queue = None
                self._worker_task = None
                raise

    async def close_session(self) -> None:
        async with self._worker_lock:
            queue = self._worker_queue
            task = self._worker_task
            if queue is None or task is None:
                return

            ack: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            await queue.put({"op": "close", "future": ack})
            await ack

            await task
            self._worker_queue = None
            self._worker_task = None

    async def _invoke_on_worker(self, op: str, **kwargs) -> Any:
        await self._ensure_worker()
        queue = self._worker_queue
        if queue is None:
            raise RuntimeError("MCP worker queue is not initialized")

        future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
        payload: dict[str, Any] = {"op": op, "future": future}
        payload.update(kwargs)
        await queue.put(payload)
        return await future

    async def _worker_loop(
        self,
        queue: asyncio.Queue[dict[str, Any]],
        started: asyncio.Future[None],
    ) -> None:
        session = None
        stack: AsyncExitStack | None = None
        try:
            session, stack = await self._open_session()
            if not started.done():
                started.set_result(None)

            while True:
                item = await queue.get()
                op = item.get("op")
                future = item.get("future")

                if op == "close":
                    if isinstance(future, asyncio.Future) and not future.done():
                        future.set_result(None)
                    return

                try:
                    if op == "list_tools":
                        result = await session.list_tools()
                    elif op == "call_tool":
                        result = await session.call_tool(
                            item["tool_name"],
                            arguments=item.get("arguments", {}),
                        )
                    else:
                        raise RuntimeError(f"Unsupported worker operation: {op}")

                    if isinstance(future, asyncio.Future) and not future.done():
                        future.set_result(result)
                except Exception as exc:
                    if isinstance(future, asyncio.Future) and not future.done():
                        future.set_exception(exc)
        except Exception as exc:
            if not started.done():
                started.set_exception(exc)
            raise
        finally:
            if stack is not None:
                await stack.aclose()

    async def _open_session(self) -> tuple[Any, AsyncExitStack]:
        stack = AsyncExitStack()

        if self.transport == MCPTransport.STDIO:
            mcp_mod = import_module("mcp")
            stdio_mod = import_module("mcp.client.stdio")
            client_session = getattr(mcp_mod, "ClientSession")
            stdio_server_parameters = getattr(mcp_mod, "StdioServerParameters")
            stdio_client = getattr(stdio_mod, "stdio_client")

            server_params = stdio_server_parameters(
                command=self.command,
                args=self.args,
                env=self.env,
            )
            streams = await stack.enter_async_context(stdio_client(server_params))
            session = await stack.enter_async_context(client_session(*streams))
            await session.initialize()
            return session, stack

        if self.transport == MCPTransport.STREAMABLE_HTTP:
            mcp_mod = import_module("mcp")
            http_mod = import_module("mcp.client.streamable_http")
            client_session = getattr(mcp_mod, "ClientSession")
            streamable_http_client = getattr(http_mod, "streamable_http_client", None)
            if streamable_http_client is None:
                streamable_http_client = getattr(http_mod, "streamablehttp_client")

            streams = await stack.enter_async_context(streamable_http_client(self.url))
            if isinstance(streams, tuple):
                read_stream = streams[0]
                write_stream = streams[1]
            else:
                read_stream, write_stream = streams

            session = await stack.enter_async_context(
                client_session(read_stream, write_stream)
            )
            await session.initialize()
            return session, stack

        mcp_mod = import_module("mcp")
        sse_mod = import_module("mcp.client.sse")
        client_session = getattr(mcp_mod, "ClientSession")
        sse_client = getattr(sse_mod, "sse_client")

        streams = await stack.enter_async_context(
            sse_client(self.url, headers=self.headers or None)
        )
        session = await stack.enter_async_context(client_session(*streams))
        await session.initialize()
        return session, stack

    async def list_tools_metadata(self) -> list[dict[str, Any]]:
        result = await self._invoke_on_worker("list_tools")

        tools = getattr(result, "tools", [])
        out: list[dict[str, Any]] = []
        for tool in tools:
            name = getattr(tool, "name", None)
            if not name:
                continue
            description = getattr(tool, "description", "") or ""
            parameters = (
                getattr(tool, "inputSchema", None)
                or getattr(tool, "input_schema", None)
                or {"type": "object", "properties": {}}
            )
            if not isinstance(parameters, dict):
                parameters = {"type": "object", "properties": {}}
            out.append(
                {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                }
            )
        return out

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        try:
            result = await self._invoke_on_worker(
                "call_tool",
                tool_name=tool_name,
                arguments=arguments,
            )

            if getattr(result, "isError", False):
                return ToolResult(error=self._stringify_tool_result(result))
            return ToolResult(output=self._stringify_tool_result(result))
        except Exception as e:
            return ToolResult(error=str(e))

    async def build_tools(self) -> list[BaseTool]:
        metadata = await self.list_tools_metadata()
        tools: list[BaseTool] = []
        prefix = (
            self.tool_name_prefix if self.tool_name_prefix is not None else self.name
        )

        for item in metadata:
            local_name = f"{prefix}__{item['name']}" if prefix else item["name"]
            tools.append(
                MCPRemoteTool(
                    name=local_name,
                    description=item["description"],
                    parameters=item["parameters"],
                    server=self,
                    remote_name=item["name"],
                )
            )
        return tools

    @staticmethod
    def _stringify_tool_result(result: Any) -> str:
        content = getattr(result, "content", None)
        if isinstance(content, list):
            items = []
            for entry in content:
                text = getattr(entry, "text", None)
                if text is not None:
                    items.append(str(text))
                    continue
                if isinstance(entry, dict):
                    items.append(json.dumps(entry, ensure_ascii=False))
                    continue
                items.append(str(entry))
            merged = "\n".join(part for part in items if part)
            if merged:
                return merged
        if content is not None:
            return str(content)

        structured = getattr(result, "structuredContent", None)
        if structured is not None:
            return json.dumps(structured, ensure_ascii=False, indent=2)

        data = getattr(result, "model_dump", None)
        if callable(data):
            dumped = data()
            return json.dumps(dumped, ensure_ascii=False, indent=2)

        return str(result)


class MCPRemoteTool(BaseTool):
    server: MCPServer
    remote_name: str

    async def execute(self, **kwargs) -> Any:
        return await self.server.call_tool(self.remote_name, kwargs)
