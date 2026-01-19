"""LLM Wrapper and Providers - Abstraction layer for different LLM backends."""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from scheduler.core.task_graph import TaskGraph, ToDo
from scheduler.config.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_prompt: Optional[str] = None, 
        **kwargs
    ) -> T:
        """Generate structured data from prompt using a Pydantic model.

        Args:
            prompt: User prompt
            response_model: Pydantic model for the response
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific arguments

        Returns:
            Instance of response_model
        """
        pass

    @abstractmethod
    async def embed(self, text: str, **kwargs) -> List[float]:
        """Generate embeddings for text.

        Args:
            text: Input text
            **kwargs: Additional provider-specific arguments

        Returns:
            List of floats representing the embedding
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of input texts
            **kwargs: Additional provider-specific arguments

        Returns:
            List of lists of floats representing the embeddings
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name to use
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generate error: {e}")
            raise

    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_prompt: Optional[str] = None, 
        **kwargs
    ) -> T:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Using JSON mode or tools/function calling for structured output
            # For simplicity and broad compatibility, we'll use JSON mode if supported
            # and instruct the model to return JSON.
            
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=messages,
                response_format={"type": "json_object"},
                temperature=kwargs.get("temperature", 0.0), # Lower temperature for structured output
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
                
            data = json.loads(content)
            return response_model.model_validate(data)
        except Exception as e:
            logger.error(f"OpenAI generate_structured error: {e}")
            raise

    async def embed(self, text: str, **kwargs) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model=kwargs.get("model", "text-embedding-3-small"),
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embed error: {e}")
            raise

    async def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                model=kwargs.get("model", "text-embedding-3-small"),
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embed_batch error: {e}")
            raise


class LLMWrapper:
    """Wrapper class to provide high-level LLM functionality to the scheduler."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        """Initialize LLM wrapper.

        Args:
            provider: LLM provider instance. If None, uses OpenAI with settings.
        """
        if provider:
            self.provider = provider
        else:
            # Default to OpenAI if configured
            if settings.openai_api_key:
                self.provider = OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model
                )
            else:
                logger.warning("No LLM provider configured. LLM features will be unavailable.")
                self.provider = None

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Proxy to provider generate."""
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        return await self.provider.generate(prompt, system_prompt, **kwargs)

    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_prompt: Optional[str] = None, 
        **kwargs
    ) -> T:
        """Proxy to provider generate_structured."""
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        return await self.provider.generate_structured(prompt, response_model, system_prompt, **kwargs)

    async def embed(self, text: str, **kwargs) -> List[float]:
        """Proxy to provider embed."""
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        return await self.provider.embed(text, **kwargs)

    async def embed_batch(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Proxy to provider embed_batch."""
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        return await self.provider.embed_batch(texts, **kwargs)

    async def intent_to_task_graph(self, intent: str, description: str) -> TaskGraph:
        """Convert a high-level intent and description into a structured TaskGraph.

        Args:
            intent: Intent name
            description: Detailed description of the request

        Returns:
            TaskGraph instance
        """
        system_prompt = """You are a Task Planner for a Cognitive Process Automation system.
        Your goal is to decompose a high-level user intent into a series of discrete tasks (ToDo items).
        Available actions: open_app, click, type, wait_for, playwright, uia, send_mail.
        Return the result as a JSON object matching the TaskGraph schema.
        Example: {"tasks": {"task1": {"action": "open_app", "selector": "notepad.exe", "depends_on": []}}}
        """
        prompt = f"Intent: {intent}\nDescription: {description}"
        
        return await self.generate_structured(prompt, TaskGraph, system_prompt=system_prompt)

    async def select_agent_for_task(self, task: ToDo, agents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best agent for a given task from a list of available agents.

        Args:
            task: The task to be executed
            agents: List of available agents with their capabilities and status

        Returns:
            Selected agent dictionary or None
        """
        # For now, this is a simple rule-based selection or LLM-based if needed.
        # Let's implement a simple version first.
        if not agents:
            return None
            
        # Return the first active agent for now
        # TODO: Use LLM to match capabilities if provided in agent info
        for agent in agents:
            if agent.get("is_active"):
                return agent
        return None
