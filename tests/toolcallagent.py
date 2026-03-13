import asyncio

from app.llm import LLM
from app.agents.toolcall import ToolCallAgent
from app.tools import MultiMCPServer
from app.tools.builtin import (
    file_edit,
    getweather,
    ask_human,
    bash,
)

client = MultiMCPServer(
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

async def ainput(prompt: str = "") -> str:

    return await asyncio.to_thread(input, prompt)

async def chat_loop() -> None:
    agent = ToolCallAgent(llm=LLM(model="deepseek-chat"))
    try:
        await agent.available_tools.mount_mcp_servers(client)
        agent.available_tools.add_tools(
            file_edit,
            getweather,
            ask_human,
            bash,
        )
        print("Please enter your messages. Type 'quit' or 'exit' to end the chat.")
        while True:
            user_msg = (await ainput("You: ")).strip()
            if user_msg.lower() in {"quit", "exit"}:
                break
            if not user_msg:
                continue

            result = await agent.run(user_msg)
            print("\n--- Agent reply ---")
            print(result)
            print("\n")
    finally:
        await agent.available_tools.close_mcp_sessions()

if __name__ == "__main__":
    asyncio.run(chat_loop())