from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from app.tools.skillloader import SkillLoader

@dataclass
class ToolContext:
    skill_loader: Optional[SkillLoader] = None
    working_dir: Path = field(default_factory=Path.cwd)