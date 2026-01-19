"""Experience Memory - Stores and retrieves past execution experiences."""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class Experience(BaseModel):
    """Represents a single execution experience (success or failure)."""
    experience_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    goal: str
    initial_state: str
    final_state: str
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    success: bool
    duration: float  # seconds
    obstacles: List[Dict[str, Any]] = Field(default_factory=list)
    obstacle_solutions: List[Dict[str, Any]] = Field(default_factory=list)
    llm_used: bool = False
    llm_calls: int = 0
    strategy_id: Optional[str] = None
    graph_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExperienceMemory:
    """Manages storage and retrieval of experiences using SQLite."""

    def __init__(self, db_path: str = "data/experience.db"):
        """Initialize Experience Memory.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    experience_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    initial_state TEXT,
                    final_state TEXT,
                    actions_taken TEXT,
                    success INTEGER,
                    duration REAL,
                    obstacles TEXT,
                    obstacle_solutions TEXT,
                    llm_used INTEGER,
                    llm_calls INTEGER,
                    strategy_id TEXT,
                    graph_id TEXT,
                    metadata TEXT
                )
            """)

    def save_experience(self, experience: Experience):
        """Save a new experience to the database."""
        data = experience.model_dump()
        
        # Serialize complex types
        data['timestamp'] = data['timestamp'].isoformat()
        data['actions_taken'] = json.dumps(data['actions_taken'])
        data['obstacles'] = json.dumps(data['obstacles'])
        data['obstacle_solutions'] = json.dumps(data['obstacle_solutions'])
        data['metadata'] = json.dumps(data['metadata'])
        data['success'] = 1 if data['success'] else 0
        data['llm_used'] = 1 if data['llm_used'] else 0

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO experiences (
                    experience_id, timestamp, goal, initial_state, final_state,
                    actions_taken, success, duration, obstacles, obstacle_solutions,
                    llm_used, llm_calls, strategy_id, graph_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['experience_id'], data['timestamp'], data['goal'],
                data['initial_state'], data['final_state'], data['actions_taken'],
                data['success'], data['duration'], data['obstacles'],
                data['obstacle_solutions'], data['llm_used'], data['llm_calls'],
                data['strategy_id'], data['graph_id'], data['metadata']
            ))
        logger.info(f"Saved experience: {experience.experience_id} (Success: {experience.success})")

    def find_similar_experiences(self, goal: str, limit: int = 5) -> List[Experience]:
        """Find past experiences with similar goals."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Simple keyword matching for now. In V2, we'd use vector search.
            cursor = conn.execute(
                "SELECT * FROM experiences WHERE goal LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{goal}%", limit)
            )
            return [self._row_to_experience(row) for row in cursor.fetchall()]

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        """Retrieve a specific experience by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM experiences WHERE experience_id = ?", (experience_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_experience(row)
        return None

    def _row_to_experience(self, row: sqlite3.Row) -> Experience:
        """Convert a SQLite row to an Experience object."""
        data = dict(row)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['actions_taken'] = json.loads(data['actions_taken'])
        data['obstacles'] = json.loads(data['obstacles'])
        data['obstacle_solutions'] = json.loads(data['obstacle_solutions'])
        data['metadata'] = json.loads(data['metadata'])
        data['success'] = bool(data['success'])
        data['llm_used'] = bool(data['llm_used'])
        return Experience(**data)
