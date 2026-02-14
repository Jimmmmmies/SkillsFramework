from app.tools.base import tool
from app.exceptions import ToolException

@tool
async def ask_human(question: str) -> str:
    """
    Ask a question to the human user and return their response.
    
    Use this for:
    - When the agent needs clarification from the user.
    - When the agent needs additional information from the user.
    - When the agent wants to confirm an action before proceeding.
    
    Args:
        question (str): The question to ask the user.
    Returns:
        str: The user's response.
    """
    if not question or not question.strip():
        raise ToolException("The question must be a non-empty string")
    
    response = input(f"""Bot: {question}\n\nYou: """).strip()
    return response