import re
import json
import inspect
from abc import ABC, abstractmethod
from typing import Optional, Any, Union, Callable, get_type_hints
from pydantic import BaseModel, Field, PrivateAttr, create_model
from app.logger import logger

class ToolResult(BaseModel):
    """
    Model representing the result of a tool execution.
    """
    output: Any = Field(default=None, description="The output produced by the tool.")
    error: Optional[str] = Field(default=None, description="Error message if the tool execution failed.")
    
    model_config = {
        "arbitrary_types_allowed": True
    }    
    
    def __add__(self, other: "ToolResult") -> "ToolResult":
        """
        Combine two ToolResult instances(for string concatenation).
        """
        def combine_fields(
          field: Optional[str], other_field: Optional[str], concatenate: bool = True 
        ):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine these two messages.")
            return field or other_field
        
        return ToolResult(
            output=combine_fields(self.output, other.output),
            error=combine_fields(self.error, other.error)
        )
    
    def __str__(self) -> str:
        return f"Error: {self.error}" if self.error else f"Output: {self.output}"
    
    def replace(self, **kwargs) -> "ToolResult":
        """
        Create a new ToolResult with updated fields.
        """
        allowed_keys = {"output", "error"}
        unknown = set(kwargs) - allowed_keys
        if unknown:
            raise ValueError(f"Invalid fields for ToolResult: {unknown}")
        return ToolResult(
            output=kwargs.get("output", self.output),
            error=kwargs.get("error", self.error),
        )

class BaseTool(BaseModel, ABC):
    """
    Abstract base class for all tools in the application.
    """
    name: str = Field(..., description="The name of the tool.")
    description: str = Field(..., description="A brief description of the tool.")
    parameters: Optional[dict] = Field(None, description="Optional parameters for the tool.")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }
    
    async def __call__(self, **kwargs) -> Any:
        """
        Invoke the tool with the given parameters.
        """
        return await self.execute(**kwargs)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Abstract method to execute the tool's functionality.
        Must be implemented by subclasses.
        """
        
    def to_openai_schema(self) -> dict:
        """
        Convert the tool to OpenAI schema format.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
        
    def success_response(self, success_message: Union[dict[str, Any], str]) -> ToolResult:
        """
        Generate a successful tool result response.
        """
        if isinstance(success_message, str):
            text = success_message
        else:
            text = json.dumps(success_message, indent=2, ensure_ascii=False)
        logger.debug(f"Created successful response for tool {self.name}")
        return ToolResult(output=text)
        
    def failure_response(self, error_message: str) -> ToolResult:
        """
        Generate a failed tool result response with an error message.
        """
        logger.debug(f"Created failure response for tool {self.name} with error: {error_message}")
        return ToolResult(error=error_message)
    
class FunctionTool(BaseTool):
    """
    A tool that wraps a simple function.
    """
    _func: Callable = PrivateAttr()
    
    def __init__(self, func: Callable, **kwargs):
        
        super().__init__(**kwargs)
        self._func = func
        
    @property
    def func(self) -> Callable:
        """
        Get the original function wrapped by this tool.
        """
        return self._func
        
    async def execute(self, **kwargs) -> Any:
        """
        Execute the wrapped function with the provided arguments.
        """
        try:
            if inspect.iscoroutinefunction(self._func):
                response =  await self._func(**kwargs)
            else:
                response = self._func(**kwargs)
                
            if isinstance(response, ToolResult):
                return response
            return self.success_response(response)
            
        except Exception as e:
            return self.failure_response(str(e))

def _get_tool_description(func: Callable) -> str:
    """
    Generate the tool description from the docstring.
    The docstring should be in the format(a searching tool example):
        
        Searches for an order in the database by its ID.
        
        Use this tool when the user asks about the status or details of a specific purchase.
        If the user doesn't provide an order ID, ask them for it first.

        Args:
            order_id: The unique string identifier for the order (e.g., "ORD-123").
            status: Optional filter. Can be 'pending', 'shipped', or 'delivered'.

        Returns:
            A dictionary containing order details including items, date, and shipping status.

    """
    doc = inspect.getdoc(func) or ""
    if not doc:
        return None
    
    collected_description = []
    lines = doc.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("Args:") or line.startswith("Returns:"):
            break
        if line:
            collected_description.append(line)

    return "\n".join(collected_description)

def _get_param_descriptions(docstring: str) -> dict[str, str]:
    """
    Parse parameters' descriptions from a docstring.
    """
    descriptions: dict[str, str] = {}
    args_match = re.search(
        r"Args:\s*\n(.*?)(?:\n\s*\n|Returns:|$)", docstring, re.DOTALL
    )
    if not args_match:
        return descriptions

    args_section = args_match.group(1)
    param_pattern = (
        r"^\s*(\w+)(?:\s*\([^)]+\))?\s*:\s*(.+?)(?=^\s*\w+\s*(?:\([^)]+\))?\s*:|$)"
    )
    for match in re.finditer(param_pattern, args_section, re.MULTILINE | re.DOTALL):
        name = match.group(1).strip()
        desc = re.sub(r"\s+", " ", match.group(2).strip())
        descriptions[name] = desc

    return descriptions

def _get_tool_parameters(func: Callable) -> dict:
    """
    Get the tool parameters from the function signature and docstring.
    """
    docstring = inspect.getdoc(func) or ""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    param_descriptions = _get_param_descriptions(docstring)

    fields = {}
    for name, param in sig.parameters.items():
        if name in {"self", "cls", "context"}:
            continue

        annotations = type_hints.get(name, str)
        default = param.default
        if default == inspect.Parameter.empty:
            default_value = ...
        else:
            default_value = default
        description = param_descriptions.get(name, None)

        fields[name] = (annotations, Field(default=default_value, description=description))
    
    DynamicModel = create_model(f"{func.__name__}Args", **fields)    
    schema = DynamicModel.model_json_schema()
    
    def clean_schema(node):
        """
        Clean all the titles in the schema recursively.
        """
        if isinstance(node, dict):
            node.pop("title", None)
            for key, value in node.items():
                clean_schema(value)
        elif isinstance(node, list):
            for item in node:
                clean_schema(item)
    clean_schema(schema)

    return schema
            
def tool(name: Optional[Union[str, Callable]] = None, description: Optional[str] = None):
    """
    Decorator to convert a function into a FunctionTool.
    Can be used as @tool or @tool(name="foo", description="bar").
    """
    def create_tool_instance(
        func: Callable, tool_name: Optional[str] = None, tool_description: Optional[str] = None
        ) -> FunctionTool:
        """
        Create a FunctionTool instance from the given function.
        """
        final_name = tool_name or func.__name__
        final_description = tool_description or _get_tool_description(func) or f"Tool named {final_name}"
        parameters = _get_tool_parameters(func)
        
        return FunctionTool(
            name=final_name,
            description=final_description,
            parameters=parameters,
            func=func
        )
    
    if callable(name):
        return create_tool_instance(name)
    else:
        def wrapper(func: Callable) -> FunctionTool:
            return create_tool_instance(func, tool_name=name, tool_description=description)
        return wrapper
