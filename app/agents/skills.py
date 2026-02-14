from app.agents.toolcall import ToolCallAgent
from app.context import ToolContext
from app.tools.skillloader import SkillLoader
from app.tools.registry import ToolRegistry
from app.prompts.skills import SYSTEM_PROMPT, NEXT_STEP_PROMPT
from app.tools.builtin import (
    bash,
    terminate,
    ask_human,
    load_skill,
    file_edit,
)
class SkillsAgent(ToolCallAgent):
    """
    Agents that can utilize skills.
    """
    name: str = "skills_agent"
    description: str = "An agent that can utilize skills."

    skill_loader: SkillLoader = SkillLoader()
    context: ToolContext = ToolContext(skill_loader=skill_loader)

    system_prompt: str = skill_loader.inject_system_prompt(SYSTEM_PROMPT)
    next_step_prompt: str = NEXT_STEP_PROMPT

    available_tools: ToolRegistry = ToolRegistry(
        load_skill, 
        terminate, 
        bash,
        ask_human,
        file_edit,
        tool_context=context,
    )
    
    max_steps: int = 50
