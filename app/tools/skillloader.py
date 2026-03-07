import re
import yaml
from pathlib import Path
from typing import List, Optional

from app.schema import SkillMetadata, SkillContent
from app.config import DEFAULT_SKILLS_DIR

class SkillLoader:
    """
    Loads and manages skills from SKILL.md files.
    
    A skill is a FOLDER containing:
    - SKILL.md (required): YAML frontmatter + markdown instructions
    - scripts/ (optional): Helper scripts the model can run
    - references/ (optional): Additional documentation
    - assets/ (optional): Templates, files for output

    """
    def __init__(self, skill_paths: List[Path] = None):
        """
        Using "List[Path]" to allow project level
        and user level skill directories
        """
        self.skill_paths = skill_paths or [DEFAULT_SKILLS_DIR]
        self.skills = self.scan_skills()
        
    def scan_skills(self) -> dict[str, SkillMetadata]:
        """
        Scans the skill directory for SKILL.md files and loads their metadata.
        """
        skills = {}
        seen_skill_names = set()
        
        for skill_path in self.skill_paths:
            
            if not skill_path.exists():
                continue
            
            for skill_dir in skill_path.iterdir():
                if not skill_dir.is_dir():
                    continue
                
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue
                
                metadata = self.parse_markdown(skill_md)
                if metadata and metadata.name not in seen_skill_names:
                    skills[metadata.name] = metadata
                    seen_skill_names.add(metadata.name)
                    
        return skills
        
    def parse_markdown(self, file_path: Path) -> Optional[SkillMetadata]:
        """
        Parsing the SKILL.md file to extract frontmatter and content.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None
        
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n',
            content,
            re.DOTALL
        )
        if not frontmatter_match:
            return None
        
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            name = frontmatter.get("name", "")
            description = frontmatter.get("description", "")
            
            if not name:
                return None

            return SkillMetadata(
                name=name, 
                description=description, 
                path=file_path.parent
                )

        except yaml.YAMLError:
            return None
        
    def inject_system_prompt(self, system_prompt: str) -> str:
        """
        Injects the skill metadata into the system prompt.
        """
        if not self.skills:
            return system_prompt
        
        skill_lines = [skill.to_prompt_line() for skill in self.skills.values()]
        skills_section = "\n".join(skill_lines)
        skills_section += "\n"
        skills_section += "### How to Use Skills\n\n"
        skills_section += "1. **Discover**: Review the skills list above\n"
        skills_section += "2. **Load**: When a user request matches a skill's description, "
        skills_section += "use `load_skill` tool to get detailed instructions\n"
        skills_section += "3. **Execute**: Follow the skill's instructions, which may include "
        skills_section += "running scripts via `bash` tool\n\n"
        skills_section += "**Important**: Only load a skill when it's relevant to the user's request. "
        skills_section += "Script code never enters the context - only their output does.\n"
        
        return f"{system_prompt}\n\nAvailable Skills:\n{skills_section}"
    
    def load_skill(self, skill_name: str) -> Optional[SkillContent]:
        """
        Load the complete content of a skill by its name.
        
        This reads the SKILL.md file for the specified skill and returns
        its complete instructions.
        """
        metadata = self.skills.get(skill_name)
        
        if not metadata:
            self.skills = self.scan_skills()
            metadata = self.skills.get(skill_name)
            
        if not metadata:
            return None
        
        skill_md = metadata.path / "SKILL.md"
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception:
            return None
        
        body_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n(.*)$',
            content,
            re.DOTALL
        )
        body = body_match.group(2).strip() if body_match else ""
        
        return SkillContent(
            metadata=metadata,
            body=body
        )