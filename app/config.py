import os
from pathlib import Path
from pydantic import BaseModel

def get_project_root() -> Path:
    """
    Get the absolute path to the project's root directory.
    """
    return Path(__file__).resolve().parent.parent

PROJECT_ROOT = get_project_root()
DEFAULT_SKILLS_DIR = Path.cwd() / "skills"

class Config(BaseModel):

    default_model: str = "deepseek-chat"
    default_provider: str = "deepseek"
    log_level: str = "INFO"
    logfile_level: str = "DEBUG"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        Load framework configuration from environment variables.
        """
        return cls(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            logfile_level=os.getenv("LOGFILE_LEVEL", "DEBUG")
        )