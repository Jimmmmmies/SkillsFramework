from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class Role(str, Enum):
    """
    Enum representing different roles in a conversation.
    """
    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"
    TOOL: str = "tool"

ROLE_VALUES = tuple(role.value for role in Role)

class ToolChoice(str, Enum):
    """
    Enum representing tool choice options.
    """
    NONE: str = "none"
    AUTO: str = "auto"
    REQUIRED: str = "required"

TOOLCHOICE_VALUES = tuple(choice.value for choice in ToolChoice)

class Function(BaseModel):
    name: str
    arguments: str

class ToolCall(BaseModel):
    """
    The following is an example of a tool call in OpenAI format.
    "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Beijing\", \"unit\": \"c\"}"
            }
          }
        ]
    """
    id: str
    type: str = "function"
    function: Function

class AgentState(str, Enum):
    """
    Enum representing different states of an agent.
    """
    IDLE: str = "idle"
    RUNNING: str = "running"
    FINISHED: str = "finished"
    ERROR: str = "error"

class Messages(BaseModel):
    role: Role = Field(...)
    content: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    tool_calls: Optional[List[ToolCall]] = Field(default=None)
    tool_call_id: Optional[str] = Field(default=None)

    def __add__(self, other) -> List["Messages"]:
        """
        Support Messages + list or Messages + Messages operation.
        """
        if isinstance(other, list):
            return [self] + other
        elif isinstance(other, Messages):
            return [self, other]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __radd__(self, other) -> List["Messages"]:
        """
        Support list + Messages operation.
        """
        if isinstance(other, list):
            return other + [self]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(other).__name__}' and '{type(self).__name__}'"
            )

    def to_dict(self) -> dict:
        """Convert the message to a dictionary."""
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.name is not None:
            message["name"] = self.name
        if self.tool_calls is not None:
            message["tool_calls"] = [
                tool_call.model_dump() for tool_call in self.tool_calls
            ]
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        return message

    @classmethod
    def user_message(cls, content: str) -> "Messages":
        """Create a user message."""
        return cls(role=Role.USER, content=content)

    @classmethod
    def system_message(cls, content: str) -> "Messages":
        """Create a system message."""
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def assistant_message(cls, content: Optional[str] = None) -> "Messages":
        """Create an assistant message."""
        return cls(role=Role.ASSISTANT, content=content)

    @classmethod
    def tool_message(cls, content: str, name: str, tool_call_id: str) -> "Messages":
        """Create a tool message."""
        return cls(
            role=Role.TOOL, content=content, name=name, tool_call_id=tool_call_id
        )

    @classmethod
    def from_tool_calls(
        cls, tool_calls: List[ToolCall], content: Optional[str] = "", **kwargs
    ):
        """
        Create tool call messages from raw tool call data.
        """
        formatted_tool_calls = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": tool_call.function.model_dump(),
            }
            for tool_call in tool_calls
        ]
        return cls(
            role=Role.ASSISTANT,
            content=content,
            tool_calls=formatted_tool_calls,
            **kwargs,
        )

class Memory(BaseModel):
    """
    Memory schema for storing conversation history.
    """
    messages: List[Messages] = Field(default_factory=list)
    max_length: int = Field(default=100)

    def add_message(self, message: Messages) -> None:
        """
        Add a message to the memory.
        """
        self.messages.append(message)
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length :]

    def add_messages(self, new_messages: List[Messages]) -> None:
        """
        Add multiple messages to the memory.
        """
        self.messages.extend(new_messages)
        if len(self.messages) > self.max_length:
            self.messages = self.messages[-self.max_length :]

    def clear(self) -> None:
        """
        Clear the memory.
        """
        self.messages.clear()

    def get_n_messages(self, n: int) -> List[Messages]:
        """
        Get the last n messages from memory.
        """
        return self.messages[-n:]

    def to_dict_list(self) -> List[dict]:
        """
        Convert all messages in memory to a list of dictionaries.
        """
        return [message.to_dict() for message in self.messages]

class SkillMetadata(BaseModel):
    """
    Represents the metadata of a skill, extracted from the SKILL.md file.
    """
    name: str
    description: str
    path: Path

    def to_prompt_line(self) -> str:
        """
        Converts the skill metadata into a single line for prompting.
        """
        return f"{self.name}: {self.description}"

class SkillContent(BaseModel):
    """
    The full content of a skill, including metadata and body.
    """
    metadata: SkillMetadata
    body: str