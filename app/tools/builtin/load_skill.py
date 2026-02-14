from typing import Optional
from app.tools.base import tool
from app.schema import SkillContent
from app.context import ToolContext

@tool
async def load_skill(skill_name: str, context: ToolContext) -> Optional[SkillContent]:
    """
    Load the complete content of a skill by its name.

    This tool reads the SKILL.md file for the specified skill and returns
    its complete instructions. Use this when the user's request matches
    a skill's description which it can satisfy the user from the available
    skills list.

    The skill's instructions will guide you on how to complete the task,
    which may include running scripts via the `bash` tool.

    Args:
        skill_name: The name of the skill to load.
        context: The shared runtime container when executing tools.
                 It provides common dependencies (e.g. SkillLoader) so tools
                 stay focused on logic without managing global resources.
    Returns:
        The full content of the skill, or None if the skill is not found.
    """
    skill_loader = context.skill_loader
    skill_content = skill_loader.load_skill(skill_name)

    if not skill_content:
        if skill_loader.skills:
            available_skills = ", ".join(skill_loader.skills.keys())
            return f"Skill '{skill_name}' not found. Available skills are: {available_skills}."
        else:
            return f"Skill '{skill_name}' not found, and no skills are currently available."

    skill_path = skill_content.metadata.path
    scripts_dir = skill_path / "scripts"

    path_info = f"""
## Skill Path Information:
- Skill Directory: {skill_path}
- Scripts Directory: {scripts_dir if scripts_dir.exists() else "No scripts directory"}

** Important**: When script directory exists, running scripts through absolute paths like:
```bash
uv run -m {scripts_dir}.script_name [args]
``` 
"""

    return f"""# Skill: {skill_name}

## Instructions:

{skill_content.body}
{path_info}
"""
