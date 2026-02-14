from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from contextlib import asynccontextmanager

from app.llm import LLM
from app.config import Config
from app.schema import Messages, Memory, AgentState, Role
from app.logger import logger

class BaseAgent(BaseModel, ABC):
    """
    Abstract base class for all agents.
    """
    name: str = Field(..., description="The name of the agent.")
    description: Optional[str] = Field(
        None, description="A brief description of the agent."
        )
    system_prompt: Optional[str] = Field(
        None, description="The system prompt for the agent."
        )
    next_step_prompt: Optional[str] = Field(
        None, description="Prompt to guide the agent's next step."
        )

    llm: LLM = Field(
        default_factory=LLM, description="The LLM client instance."
        )
    memory: Memory = Field(
        default_factory=Memory, description="The current history for the agent."
        )
    state: AgentState = Field(
        default=AgentState.IDLE, description="The current state of the agent."
        )
    config: Config = Field(
        default_factory=Config, description="Default configuration for the agent."
        )
    
    max_steps: int = Field(default=10, description="Maximum steps per run.")
    current_step: int = Field(default=0, description="Current step in the run.")
    duplicate_threshold: int = 2
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
        )
    
    @property
    def history(self) -> List[Messages]:
        """
        Get the agent's memory messages.
        """
        return self.memory.messages
    
    @history.setter
    def history(self, messages: List[Messages]):
        """
        Set the agent's memory messages.
        """
        self.memory.messages = messages
    
    def update_memory(
        self,
        role: Role,
        content: str,
        **kwargs 
        ) -> None:
        """
        Update the agent's memory with a new message.
        """
        message_mapping = {
            "user": Messages.user_message,
            "system": Messages.system_message,
            "assistant": Messages.assistant_message,
            "tool": Messages.tool_message
        }
        if role.value not in message_mapping:
            raise ValueError(f"Invalid role: {role}")
        
        kwargs = {**(kwargs if role.value == "tool" else {})}
        self.memory.add_message(
            message_mapping[role.value](content, **kwargs)
            )
    
    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """
        Context manager for safe state transitions.
        And it automatically recovers the previous state after execution.
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"Invalid state: {new_state}")
        
        old_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR
            raise e
        finally:
            self.state = old_state
            
    async def run(self, input_text: Optional[str] = None) -> str:
        """
        Run the agent's main workflow.
        """
        if self.state != AgentState.IDLE:
            raise RuntimeError(f"Agent is busy. Current state: {self.state}")

        # Reset step counter at the start of each run
        self.current_step = 0
        
        if input_text:
            self.update_memory(Role.USER, input_text)
            
        results: List[str] = []
        async with self.state_context(AgentState.RUNNING):
            while (
                self.current_step < self.max_steps and self.state != AgentState.FINISHED
                ):
                self.current_step += 1
                logger.info(f"Executing step {self.current_step}/{self.max_steps}")
                step_result = await self.step()
                
                if self.is_stuck():
                    self.handle_stuck()
                results.append(f"Step {self.current_step}: {step_result}")
                
            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"Terminated after reaching max steps: {self.max_steps}")
            
            return "\n".join(results) if results else "No steps were executed."

    @abstractmethod
    async def step(self) -> str:
        """
        Perform a single step in agent's workflow.
        Must be implemented by subclasses.
        """
        
    def is_stuck(self) -> bool:
        """
        Determine if the agent is stuck based on its memory.
        """
        if len(self.memory.messages) < 2:
            return False
            
        last_message = self.memory.messages[-1]
        if not last_message.content:
            return False
        
        duplicate_messages = sum(
            1 for message in reversed(self.memory.messages[:-1])
            if message.role == Role.ASSISTANT and message.content == last_message.content
        )
        
        return duplicate_messages >= self.duplicate_threshold
        
    def handle_stuck(self) -> None:
        """
        Solve the stuck situation by adding a system prompt.
        """
        stuck_prompt = "\
        Observed duplicate responses. Consider new strategies and avoid repeating ineffective paths already attempted."
        if stuck_prompt not in self.next_step_prompt:
            self.next_step_prompt = f"{stuck_prompt}\n{self.next_step_prompt}"
            logger.warning(f"⚠️Agent detected stuck state. Added prompt: {stuck_prompt}")
