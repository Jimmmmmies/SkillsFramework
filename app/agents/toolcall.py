import json
from typing import List, Any
from pydantic import Field

from app.agents.react import ReActAgent
from app.prompts.toolcall import SYSTEM_PROMPT, NEXT_STEP_PROMPT
from app.schema import ToolChoice, ToolCall, Messages, AgentState
from app.tools.registry import ToolRegistry
from app.tools.builtin import terminate
from app.logger import logger

class ToolCallAgent(ReActAgent):
    """
    Agent that utilizes tools via ReAct framework.
    """
    name: str = "toolcall_agent"
    description: str = "An agent that can execute tools via ReAct."
    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT
    
    available_tools: ToolRegistry = ToolRegistry(
        terminate
    )
    special_tool_names: List[str] = Field(
        default_factory=lambda: [terminate.name],
        description="Special tools, for example to change agent state."
        )
    tool_choice: ToolChoice = ToolChoice.AUTO
    tool_calls: List[ToolCall] = Field(default_factory=list)
    
    max_steps: int = 30
    
    async def think(self) -> bool:
        """
        Perform the agent's thinking process.
        """
        if self.next_step_prompt:
            user_message = Messages.user_message(self.next_step_prompt)
            self.memory.add_message(user_message)
            
        try:
            response = await self.llm.invoke_tool(
                messages=self.memory.messages,
                system_messages=(
                    [Messages.system_message(self.system_prompt)]
                    if self.system_prompt
                    else None
                ),
                tools=self.available_tools.to_openai_schema(),
                tool_choice=self.tool_choice,
            )
            
        except ValueError:
            raise
        except Exception:
            raise
        
        self.tool_calls = tool_calls = (
                response.tool_calls if response and response.tool_calls else []
            )
        content = response.content if response and response.content else ""
        
        # Thoughts
        logger.info(f"💡{self.name}'s thoughts: {content}")
        logger.info(
            f"🔧{self.name} has selected {len(tool_calls) if tool_calls else 0} tools"
            )
        
        try:
            if response is None:
                raise RuntimeError("LLM response is None.")
            if self.tool_choice == ToolChoice.NONE:
                if tool_calls:
                    logger.warning(
                        f"⚠️{self.name} attempted to use tools when they are disabled."
                    )
                if content:
                    self.memory.add_message(Messages.assistant_message(content))
                return False
            
            assistant_message = (
                Messages.from_tool_calls(content=content, tool_calls=tool_calls)
                if tool_calls
                else Messages.assistant_message(content)
            )
            self.memory.add_message(assistant_message)
            
            if self.tool_choice == ToolChoice.REQUIRED and not tool_calls:
                return True
            if self.tool_choice == ToolChoice.AUTO and not tool_calls:
                return bool(content)
            
            return bool(tool_calls)
        
        except Exception as e:
            logger.error(f"Thinking process hit a snag: {str(e)}")
            self.memory.add_message(
                Messages.assistant_message(
                    f"Error encountered while processing: {str(e)}"
                )
            )
            return False

    async def act(self) -> str:
        """
        Execute the agent's chosen action.
        """
        if not self.tool_calls:
            if self.tool_choice == ToolChoice.REQUIRED:
                raise ValueError("Tool calls are required but none were provided.")
        
            return self.memory.messages[-1].content or "No action taken."
    
        results = []
        for tool_call in self.tool_calls:
            result = await self.execute_tool(tool_call)
            # Observation
            logger.info(
                f"🔧Tool '{tool_call.function.name}' succeeded with result: {result}"
            )
            
            tool_message = Messages.tool_message(
                content=result,
                name=tool_call.function.name,
                tool_call_id=tool_call.id
            )
            
            self.memory.add_message(tool_message)
            results.append(result)
        
        return "\n\n".join(results)
        
    async def execute_tool(self, tool_call: ToolCall) -> str:
        """
        Execute a single tool call with robust error handling
        and parameter parsing.
        """
        if not tool_call or not tool_call.function or not tool_call.function.name:
            return "Invalid tool call format."
        
        name = tool_call.function.name
        if name not in self.available_tools.tool_map:
            return f"Tool '{name}' is not available."
        
        try:
            args = json.loads(tool_call.function.arguments or "{}", strict=False)
            logger.info(f"Activating tool: {name}")
            result = await self.available_tools.execute_tool(name, args)
            
            await self.handle_special_tools(name, result)
            
            observation = (
                f"Observed output of tool '{name}': {result.output}"
                if result.output
                else f"Tool '{name}' executed with no output."
            )
            
            return observation
            
        except json.JSONDecodeError:
            logger.error(
                f"The arguments for tool '{name}' don't make sense - invalid JSON, arguments:{tool_call.function.arguments}"
            )
            return f"Error: Invalid JSON arguments for tool '{name}'."
        
        except Exception as e:
            logger.exception(
                f"Special tool '{name}' has completed the task!"
            )
            return f"Error: {str(e)} while executing tool '{name}'."
        
    async def handle_special_tools(self, name: str, result: Any, **kwargs):
        """
        Handle special tools execution and state updates.
        """
        if name.lower() not in (
            special_tool_name.lower() for special_tool_name in self.special_tool_names
            ):
            return 
        
        if self._should_finish_execution(tool_name=name, result=result, **kwargs):
            logger.info(f"Special tool '{name}' has completed the task!")
            self.state = AgentState.FINISHED
        
    @staticmethod
    def _should_finish_execution(**kwargs) -> bool:
        """
        Determine if the agent should finish execution.
        Can be overwritten for subclasses to provide custom logic.
        By default, always returns True because usaully only terminate tool is special tool
        and it always ends the execution.
        """
        return True
