"""Tests for LLM Wrapper and Providers."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel
from scheduler.llm.llm_wrapper import LLMWrapper, OpenAIProvider

class SampleModel(BaseModel):
    """Sample model for structured output tests."""
    name: str
    value: int

@pytest.mark.asyncio
async def test_openai_provider_generate():
    """Test text generation with OpenAI provider."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello world"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch("scheduler.llm.llm_wrapper.AsyncOpenAI", return_value=mock_client):
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate("test prompt")
        assert result == "Hello world"
        mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_openai_provider_generate_structured():
    """Test structured generation with OpenAI provider."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"name": "test", "value": 123}'
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    with patch("scheduler.llm.llm_wrapper.AsyncOpenAI", return_value=mock_client):
        provider = OpenAIProvider(api_key="test-key")
        result = await provider.generate_structured("test prompt", SampleModel)
        assert isinstance(result, SampleModel)
        assert result.name == "test"
        assert result.value == 123

@pytest.mark.asyncio
async def test_llm_wrapper_proxy():
    """Test that LLMWrapper correctly proxies calls to the provider."""
    mock_provider = MagicMock(spec=OpenAIProvider)
    mock_provider.generate = AsyncMock(return_value="proxy result")
    
    wrapper = LLMWrapper(provider=mock_provider)
    result = await wrapper.generate("test")
    assert result == "proxy result"
    mock_provider.generate.assert_called_once_with("test", None)

@pytest.mark.asyncio
async def test_llm_wrapper_unconfigured():
    """Test that LLMWrapper raises error when no provider is configured."""
    with patch("scheduler.llm.llm_wrapper.settings") as mock_settings:
        mock_settings.openai_api_key = ""
        wrapper = LLMWrapper(provider=None)
        with pytest.raises(RuntimeError, match="LLM provider not configured"):
            await wrapper.generate("test")
