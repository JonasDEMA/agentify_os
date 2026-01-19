"""Context Memory Service - Manages short-term (Redis) and long-term (SQLite) agent memory."""
import json
import numpy as np
import aiosqlite
from datetime import datetime, UTC
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

from scheduler.llm.llm_wrapper import LLMWrapper
from scheduler.memory.embedding_service import EmbeddingService
from scheduler.queue.job_queue import JobQueue

class MemoryEntry(BaseModel):
    """Memory entry model for long-term storage."""
    id: Optional[str] = None
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class ContextMemory:
    """Service for managing agent context memory."""

    def __init__(
        self, 
        job_queue: JobQueue, 
        embedding_service: EmbeddingService,
        db_path: str = "./data/memory.db"
    ):
        """Initialize context memory.
        
        Args:
            job_queue: Job queue instance (provides access to Redis for short-term memory)
            embedding_service: Service for generating embeddings
            db_path: Path to SQLite database for long-term memory
        """
        self.job_queue = job_queue
        self.embedding_service = embedding_service
        self.db_path = db_path
        self._initialized = False

    async def _init_db(self) -> None:
        """Initialize SQLite database for long-term memory."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        self._initialized = True

    async def set_short_term(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Store value in short-term memory (Redis)."""
        if not self.job_queue.redis:
            raise RuntimeError("Redis not connected")
        
        data = json.dumps(value)
        await self.job_queue.redis.set(f"memory:short:{key}", data, ex=ttl)

    async def get_short_term(self, key: str) -> Optional[Any]:
        """Retrieve value from short-term memory."""
        if not self.job_queue.redis:
            raise RuntimeError("Redis not connected")
        
        data = await self.job_queue.redis.get(f"memory:short:{key}")
        if data:
            return json.loads(data)
        return None

    async def delete_short_term(self, key: str) -> None:
        """Delete value from short-term memory."""
        if not self.job_queue.redis:
            raise RuntimeError("Redis not connected")
        await self.job_queue.redis.delete(f"memory:short:{key}")

    async def store_long_term(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store text in long-term memory with embedding.
        
        Args:
            text: Text to remember
            metadata: Optional metadata
            
        Returns:
            ID of the stored entry
        """
        await self._init_db()
        embedding = await self.embedding_service.embed(text)
        mem_id = "mem_" + datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO long_term_memory (id, text, embedding, metadata) VALUES (?, ?, ?, ?)",
                (mem_id, text, json.dumps(embedding), json.dumps(metadata or {}))
            )
            await db.commit()
        
        return mem_id

    async def search_long_term(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Search long-term memory using semantic similarity.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching MemoryEntry objects
        """
        await self._init_db()
        query_embedding = await self.embedding_service.embed(query)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM long_term_memory") as cursor:
                rows = await cursor.fetchall()
        
        results = []
        for row in rows:
            embedding = json.loads(row["embedding"])
            similarity = self._cosine_similarity(query_embedding, embedding)
            results.append((similarity, row))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [
            MemoryEntry(
                id=res[1]["id"],
                text=res[1]["text"],
                embedding=json.loads(res[1]["embedding"]),
                metadata=json.loads(res[1]["metadata"]),
                created_at=datetime.fromisoformat(res[1]["created_at"]) if isinstance(res[1]["created_at"], str) else res[1]["created_at"]
            )
            for res in results[:limit]
        ]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(v1)
        b = np.array(v2)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
