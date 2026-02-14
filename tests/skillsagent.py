import asyncio

from app.llm import LLM
from app.agents import SkillsAgent
    
async def ainput(prompt: str = "") -> str:

    return await asyncio.to_thread(input, prompt)

async def chat_loop() -> None:

    agent = SkillsAgent(
        llm=LLM(model="deepseek-chat"),
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

if __name__ == "__main__":
    asyncio.run(chat_loop())