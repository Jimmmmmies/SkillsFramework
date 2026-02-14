from abc import ABC, abstractmethod
from app.agents.base import BaseAgent

class ReActAgent(BaseAgent, ABC):
    """
    Abstract base class for ReAct agents.
    """
    @abstractmethod
    async def think(self) -> bool:
        """
        Perform the agent's thinking process.
        Decide on the next action or conclusion.
        """
        
    @abstractmethod
    async def act(self) -> str:
        """
        Execute the agent's chosen action.
        Return the result of the action.
        """
    
    async def step(self) -> str:
        """
        Perform a single step of the ReAct agent's process.
        Combines thinking and acting.
        """
        can_proceed = await self.think()
        if not can_proceed:
            return "Thinking process completed. No further action."
        
        result = await self.act()
        return result