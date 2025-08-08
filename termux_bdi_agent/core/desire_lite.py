"""
Lightweight Desire System untuk Termux
Optimized untuk resource constraints dengan simple optimization algorithms
"""

import json
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Optional

class DesireSystemLite:
    """Lightweight Desire System dengan minimal computational overhead"""

    def __init__(self, db_manager, config):
        self.db = db_manager
        self.config = config
        self.desires_cache = {}
        self.last_optimization = None

        # Initialize database schema
        self.init_schema()

        # Initialize default desires
        self.init_default_desires()

    def init_schema(self):
        """Initialize database schema untuk desires"""
        schema = """
        CREATE TABLE IF NOT EXISTS desires (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            target_value REAL NOT NULL,
            current_value REAL DEFAULT 0.0,
            priority REAL DEFAULT 0.5,
            weight REAL DEFAULT 1.0,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_schema(schema)

        # Optimization results table
        results_schema = """
        CREATE TABLE IF NOT EXISTS desire_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desires_snapshot TEXT NOT NULL,
            optimization_result TEXT NOT NULL,
            method TEXT DEFAULT 'lightweight',
            duration REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_schema(results_schema)

    def init_default_desires(self):
        """Initialize default desires jika belum ada"""
        if self.get_desires_count() == 0:
            default_desires = [
                {
                    "id": "revenue_generation",
                    "name": "Revenue Generation",
                    "type": "financial",
                    "target_value": 50000.0,
                    "current_value": 0.0,
                    "priority": 0.9,
                    "weight": 1.0
                },
                {
                    "id": "system_efficiency",
                    "name": "System Efficiency",
                    "type": "performance",
                    "target_value": 95.0,
                    "current_value": 80.0,
                    "priority": 0.8,
                    "weight": 0.8
                },
                {
                    "id": "user_satisfaction",
                    "name": "User Satisfaction",
                    "type": "quality",
                    "target_value": 90.0,
                    "current_value": 75.0,
                    "priority": 0.7,
                    "weight": 0.6
                },
                {
                    "id": "cost_optimization",
                    "name": "Cost Optimization",
                    "type": "financial",
                    "target_value": 0.0,
                    "current_value": 100.0,
                    "priority": 0.6,
                    "weight": 0.5
                }
            ]

            for desire in default_desires:
                self.insert_desire(desire)

    def optimize_desires(self, belief_context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize desires menggunakan lightweight algorithms"""
        start_time = time.time()

        try:
            # Get current desires
            current_desires = self.get_all_desires()

            # Update desires berdasarkan belief context
            updated_desires = self.update_desires_from_beliefs(current_desires, belief_context)

            # Run lightweight optimization
            optimization_result = self.run_lightweight_optimization(updated_desires)

            # Save optimization results
            self.save_optimization_result(updated_desires, optimization_result, time.time() - start_time)

            self.last_optimization = datetime.now()

            result = {
                "desires_processed": len(updated_desires),
                "optimization_method": self.config.get("optimization_method", "lightweight"),
                "duration": time.time() - start_time,
                "top_desires": optimization_result.get("prioritized_desires", [])[:5],
                "count": len(updated_desires)
            }

            return result

        except Exception as e:
            return {"error": str(e), "count": 0}

    def update_desires_from_beliefs(self, desires: List[Dict], belief_context: Dict[str, Any]) -> List[Dict]:
        """Update desire values berdasarkan belief context"""
        beliefs_count = belief_context.get("beliefs_processed", 0)
        new_beliefs = belief_context.get("new_beliefs", 0)

        updated_desires = []

        for desire in desires:
            updated_desire = desire.copy()

            if desire["type"] == "performance":
                if beliefs_count > 0:
                    improvement = min(5.0, beliefs_count * 0.1)
                    updated_desire["current_value"] = min(100.0, desire["current_value"] + improvement)

            elif desire["type"] == "financial":
                if new_beliefs > 0:
                    revenue_increase = new_beliefs * 10.0
                    updated_desire["current_value"] = desire["current_value"] + revenue_increase

            elif desire["type"] == "quality":
                if belief_context.get("errors", 0) == 0:
                    updated_desire["current_value"] = min(100.0, desire["current_value"] + 1.0)
                else:
                    updated_desire["current_value"] = max(0.0, desire["current_value"] - 2.0)

            gap = abs(updated_desire["target_value"] - updated_desire["current_value"])
            max_gap = max(1.0, updated_desire["target_value"])
            urgency = gap / max_gap
            updated_desire["priority"] = min(1.0, desire["priority"] + urgency * 0.1)

            updated_desire["updated_at"] = datetime.now().isoformat()
            self.update_desire(updated_desire)
            updated_desires.append(updated_desire)

        return updated_desires

    def run_lightweight_optimization(self, desires: List[Dict]) -> Dict[str, Any]:
        scored_desires = []
        for desire in desires:
            gap = abs(desire["target_value"] - desire["current_value"])
            max_value = max(1.0, max(abs(desire["target_value"]), abs(desire["current_value"])))
            gap_score = gap / max_value
            total_score = (desire["priority"] * 0.4 + gap_score * 0.4 + desire["weight"] * 0.2)
            scored_desires.append({"desire": desire, "score": total_score})

        scored_desires.sort(key=lambda x: x["score"], reverse=True)

        return {
            "prioritized_desires": [item["desire"] for item in scored_desires],
            "method": "lightweight_weighted_scoring"
        }

    def insert_desire(self, desire: Dict):
        query = "INSERT INTO desires (id, name, type, target_value, current_value, priority, weight) VALUES (?, ?, ?, ?, ?, ?, ?)"
        params = (desire["id"], desire["name"], desire["type"], desire["target_value"], desire["current_value"], desire["priority"], desire["weight"])
        self.db.execute(query, params)

    def update_desire(self, desire: Dict):
        query = "UPDATE desires SET current_value = ?, priority = ?, weight = ?, updated_at = ? WHERE id = ?"
        params = (desire["current_value"], desire["priority"], desire["weight"], desire["updated_at"], desire["id"])
        self.db.execute(query, params)

    def get_all_desires(self) -> List[Dict]:
        results = self.db.fetch_all("SELECT * FROM desires WHERE status = 'active' ORDER BY priority DESC")
        return [dict(zip([col[0] for col in self.db.cursor.description], row)) for row in results]

    def get_desires_count(self) -> int:
        return self.db.fetch_scalar("SELECT COUNT(*) FROM desires WHERE status = 'active'")

    def save_optimization_result(self, desires: List[Dict], result: Dict[str, Any], duration: float):
        query = "INSERT INTO desire_optimizations (desires_snapshot, optimization_result, method, duration) VALUES (?, ?, ?, ?)"
        params = (json.dumps(desires), json.dumps(result), result.get("method", "lightweight"), duration)
        self.db.execute(query, params)
