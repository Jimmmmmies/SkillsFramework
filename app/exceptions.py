class SkillAgentException(Exception):
    """
    Base exception for Skill Agent errors.
    """
    pass

class LLMException(SkillAgentException):
    """
    Exception for LLM-related errors.
    """
    pass

class ToolException(SkillAgentException):
    """
    Exception for Tool-related errors.
    """
    def __init__(self, message):
        self.message = message