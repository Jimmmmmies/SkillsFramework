import os
from typing import (
    Optional, 
    Literal, 
    List,
    Union, 
    AsyncIterator
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception
)
from dotenv import load_dotenv
from app.exceptions import LLMException
from app.schema import Messages, ToolChoice, ROLE_VALUES, TOOLCHOICE_VALUES
from app.logger import logger
from openai import (
    AsyncOpenAI,
    OpenAIError,
    AuthenticationError,
    RateLimitError,
    APIError,
    APIConnectionError,
    APIStatusError
)
from openai.types.chat import ChatCompletionMessage
SUPPORTED_PROVIDERS = Literal[
    "deepseek",
    "ollama",
    "vllm"
    ]
load_dotenv()

def _should_retry(e: Exception) -> bool:
    """
    Determine whether to retry based on the exception type.
    """
    if isinstance(e, RateLimitError):
        return True
    if isinstance(e, APIConnectionError):
        return True
    if isinstance(e, APIStatusError) and e.status_code >= 500:
        return True
    return False

class LLM:
    
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: Optional[SUPPORTED_PROVIDERS] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs
        ):
        """
        Initialize the LLM client with given parameters or environment variables.
        """
        self.model = model or os.getenv("LLM_MODEL")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))
        self.kwargs = kwargs
        
        self.provider = provider or self._auto_detect_provider(api_key, base_url)
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        if not (self.api_key and self.base_url): 
            self.api_key, self.base_url = self._resolve_credentials()
        
        self._client = self._create_client()
    
    def _create_client(self) -> AsyncOpenAI:
        """
        Create and return an OpenAI client instance.
        """
        return AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
        
    def _auto_detect_provider(self, api_key: Optional[str], base_url: Optional[str]) -> str:
        """
        Auto-detect the LLM provide.
        """
        if os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek"
        if os.getenv("OLLAMA_API_KEY"):
            return "ollama"
        if os.getenv("VLLM_API_KEY"):
            return "vllm"

        env_api_key = api_key or os.getenv("LLM_API_KEY")
        if env_api_key:
            env_api_key_lower = env_api_key.lower()
            if env_api_key_lower == "vllm":
                return "vllm"
            elif env_api_key_lower == "ollama":
                return "ollama"
            elif env_api_key_lower.startswith("sk-"):
                pass
            
        env_base_url = base_url or os.getenv("LLM_BASE_URL")
        if env_base_url:
            env_base_url_lower = env_base_url.lower()
            if "api.deepseek.com" in env_base_url_lower:
                return "deepseek"
            elif "localhost" in env_base_url_lower or "127.0.0.1" in env_base_url_lower:
                if ":11434" in env_base_url_lower:
                    return "ollama"
                elif ":8000" in env_base_url_lower:
                    return "vllm"
            elif any(port in env_base_url_lower for port in [":8080", ":7860", ":5000"]):
                return "local"
            
        return "auto"
    
    def _resolve_credentials(self) -> tuple[str, str]:
        """
        Resolve the API key and base URL based on the provider.
        """
        if self.provider == "deepseek":
            resolved_api_key = os.getenv("DEEPSEEK_API_KEY")
            resolved_base_url = os.getenv("DEEPSEEK_BASE_URL") or "https://api.deepseek.com/v1"
        elif self.provider == "ollama":
            resolved_api_key = os.getenv("OLLAMA_API_KEY") or "ollama"
            resolved_base_url = os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434/v1"
        elif self.provider == "vllm":
            resolved_api_key = os.getenv("VLLM_API_KEY") or "vllm"
            resolved_base_url = os.getenv("VLLM_BASE_URL") or "http://localhost:8000/v1"
        elif self.provider == "local":
            resolved_api_key = "local"
            resolved_base_url = "http://localhost:8080/v1"
        else:
            raise LLMException("Cannot resolve api key and URL. Please specify them correctly and explicitly.")
            
        return resolved_api_key, resolved_base_url

    @staticmethod
    def format_messages(messages: List[Union[dict, Messages]]) -> List[dict]:
        """
        Format messages for llm by converting them to OpenAI message format.
        """
        formatted_messages = []
        for message in messages:
            if isinstance(message, Messages):
                message = message.to_dict()
            if isinstance(message, dict):
                if "role" not in message:
                    raise ValueError("Message dict must contain 'role' key.")
                if "content" in message or "tool_calls" in message:
                    formatted_messages.append(message)
            else:
                raise TypeError(f"Unsupported message type: {type(message)}")
        for message in formatted_messages:
            if message["role"] not in ROLE_VALUES:
                raise ValueError(f"Invalid role value: {message['role']}.")
                
        return formatted_messages

    @retry(
        wait=wait_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception(_should_retry)
    )
    async def _make_openai_request(self, stream, **params):
        """
        Create the base request payload for OpenAI API.
        """
        response = await self._client.chat.completions.create(
            **params, stream=stream
        )
        return response
        
    async def invoke(
        self,
        messages: List[Union[dict, Messages]],
        system_messages: Optional[List[Union[dict, Messages]]] = None,
        stream: bool = True,
        temperature: Optional[float] = None,
        isthinking: bool = False # Indicate whether it's a thinking process.
        ) -> str | AsyncIterator[str]:
        """
        Send messages to the LLM and return text reply.
        """
        try:
            if system_messages:
                system_messages = self.format_messages(system_messages)
                messages = system_messages + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)

            params = {
                "model": self.model,
                "messages": messages,
            }
            if not isthinking:
                params["temperature"] = temperature if temperature is not None else self.temperature
                params["max_tokens"] = self.max_tokens
            else:
                params["max_completion_tokens"] = self.max_tokens

            if not stream:
                response = await self._make_openai_request(stream, **params)
                if not response.choices or not response.choices[0].message:
                    raise ValueError("No valid response from LLM.")
                return response.choices[0].message.content

            async def _stream() -> AsyncIterator[str]:
                collected_messages = []
                response = await self._make_openai_request(stream, **params)
                async for chunk in response:
                    chunk_message = chunk.choices[0].delta.content or ""
                    collected_messages.append(chunk_message)
                    if chunk_message:
                        yield chunk_message
                full_response = "".join(collected_messages).strip()
                if not full_response:
                    raise ValueError("No valid response from LLM.")
            return _stream()

        except ValueError as ve:
            logger.exception(f"Validation error occurred: {ve}")
            raise
        except OpenAIError as oe:
            logger.exception("OpenAI API error occurred.")
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Please check your API key.")
            if isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry intervals.")
            if isinstance(oe, APIError):
                logger.error("API error occurred.")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error {e} occurred.")
            raise
    
    async def invoke_tool(
        self,
        messages: List[Union[dict, Messages]],
        system_messages: Optional[List[Union[dict, Messages]]] = None,
        timeout: int = 300,
        tools: Optional[List[str]] = None,
        tool_choice: ToolChoice = ToolChoice.AUTO,
        temperature: Optional[float] = None,
        isthinking: bool = False,
        **kwargs
        ) -> ChatCompletionMessage | None:
        """
        Send messages to the LLM with tool usage and return the tool call response.
        """
        try:
            if tool_choice not in TOOLCHOICE_VALUES:
                raise ValueError(f"Invalid tool_choice value: {tool_choice}.")

            if system_messages:
                system_messages = self.format_messages(system_messages)
                messages = system_messages + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)
                
            if tools:
                for tool in tools:
                    if not isinstance(tool, dict) or "type" not in tool:
                        raise ValueError("Each tool must be in OpenAI schema format.")
            
            params = {
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": tool_choice,
                "timeout": timeout,
                **kwargs
            }
            
            if not isthinking:
                params["temperature"] = temperature if temperature is not None else self.temperature
                params["max_tokens"] = self.max_tokens
            else:
                params["max_completion_tokens"] = self.max_tokens
            
            response = await self._make_openai_request(stream=False, **params)
            
            if not response.choices or not response.choices[0].message:
                raise ValueError("No valid response from LLM.")
            
            return response.choices[0].message
                
        except ValueError as ve:
            logger.exception(f"Validation error occurred: {ve}")
            raise
        except OpenAIError as oe:
            logger.exception(f"OpenAI API error occurred: {oe}")
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Please check your API key.")
            if isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry intervals.")
            if isinstance(oe, APIError):
                logger.error("API error occurred.")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error {e} occurred.")
            raise