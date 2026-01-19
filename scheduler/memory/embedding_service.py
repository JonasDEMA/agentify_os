"""Embedding Service - Generates vector representations of text."""
from typing import List, Optional
from scheduler.llm.llm_wrapper import LLMWrapper

class EmbeddingService:
    """Service for generating embeddings using an LLM provider."""

    def __init__(self, llm_wrapper: LLMWrapper):
        """Initialize embedding service.
        
        Args:
            llm_wrapper: LLM wrapper instance for calling embedding models
        """
        self.llm = llm_wrapper

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        return await self.llm.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        return await self.llm.embed_batch(texts)
