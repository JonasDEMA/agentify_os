"""Strategy Manager - Manages high-level strategies (playbooks) for achieving goals."""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class Strategy(BaseModel):
    """Represents a learned or predefined strategy to achieve a specific goal."""
    strategy_id: str
    name: str
    description: str
    goal: str
    preconditions: List[str] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    average_duration: float = 0.0
    learned_from: str = "llm"  # 'llm', 'manual', 'experience'
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    graph_id: Optional[str] = None

class StrategyManager:
    """Manages CRUD operations and persistence for strategies using SQLite."""

    def __init__(self, db_path: str = "data/strategies.db"):
        """Initialize Strategy Manager.

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
                CREATE TABLE IF NOT EXISTS strategies (
                    strategy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    goal TEXT NOT NULL,
                    preconditions TEXT,
                    steps TEXT,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    average_duration REAL DEFAULT 0.0,
                    learned_from TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    graph_id TEXT
                )
            """)

    def save_strategy(self, strategy: Strategy):
        """Save or update a strategy in the database."""
        strategy.updated_at = datetime.now()
        data = strategy.model_dump()
        
        # Serialize lists/dicts to JSON strings for SQLite
        data['preconditions'] = json.dumps(data['preconditions'])
        data['steps'] = json.dumps(data['steps'])
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO strategies (
                    strategy_id, name, description, goal, preconditions, steps,
                    success_count, failure_count, average_duration, learned_from,
                    created_at, updated_at, graph_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['strategy_id'], data['name'], data['description'], data['goal'],
                data['preconditions'], data['steps'], data['success_count'],
                data['failure_count'], data['average_duration'], data['learned_from'],
                data['created_at'], data['updated_at'], data['graph_id']
            ))
        logger.info(f"Saved strategy: {strategy.name} ({strategy.strategy_id})")

    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Retrieve a strategy by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM strategies WHERE strategy_id = ?", (strategy_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_strategy(row)
        return None

    def list_strategies(self, goal: Optional[str] = None) -> List[Strategy]:
        """List all strategies, optionally filtered by goal."""
        query = "SELECT * FROM strategies"
        params = ()
        if goal:
            query += " WHERE goal LIKE ?"
            params = (f"%{goal}%",)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_strategy(row) for row in cursor.fetchall()]

    def delete_strategy(self, strategy_id: str):
        """Delete a strategy by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM strategies WHERE strategy_id = ?", (strategy_id,))
        logger.info(f"Deleted strategy: {strategy_id}")

    def _row_to_strategy(self, row: sqlite3.Row) -> Strategy:
        """Convert a SQLite row to a Strategy object."""
        data = dict(row)
        data['preconditions'] = json.loads(data['preconditions'])
        data['steps'] = json.loads(data['steps'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return Strategy(**data)
