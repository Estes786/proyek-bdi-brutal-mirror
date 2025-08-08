"""
Lightweight Belief System untuk Termux
Optimized untuk resource constraints Android device
"""

import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class BeliefSystemLite:
    """Lightweight Belief System dengan minimal resource usage"""

    def __init__(self, db_manager, config):
        self.db = db_manager
        self.config = config
        self.beliefs_cache = {}
        self.last_update = None

        # Initialize database schema
        self.init_schema()

        # Setup data sources
        self.data_sources = self.setup_data_sources()

    def init_schema(self):
        """Initialize database schema untuk beliefs"""
        schema = """
        CREATE TABLE IF NOT EXISTS beliefs (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            relevance_score REAL DEFAULT 0.0,
            processed BOOLEAN DEFAULT FALSE
        )
        """
        self.db.execute_schema(schema)

        # Create indexes untuk performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_beliefs_timestamp ON beliefs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_beliefs_source ON beliefs(source)",
            "CREATE INDEX IF NOT EXISTS idx_beliefs_processed ON beliefs(processed)"
        ]
        for index in indexes:
            self.db.execute_schema(index)

    def setup_data_sources(self):
        """Setup data sources berdasarkan konfigurasi"""
        sources = []
        
        # Kita akan buat ini lebih dinamis nanti dari config
        sources.append(LocalSensorSource())
        sources.append(APIEndpointSource())
        sources.append(FileSystemSource())

        return sources

    def update_beliefs(self) -> Dict[str, Any]:
        """Update beliefs dari semua data sources"""
        start_time = time.time()
        results = {
            "beliefs_processed": 0,
            "new_beliefs": 0,
            "errors": 0,
            "sources_processed": 0
        }

        try:
            for source in self.data_sources:
                try:
                    data = source.collect_data(timeout=10)

                    if data:
                        processed = self.process_source_data(source.name, data)
                        results["beliefs_processed"] += processed["processed"]
                        results["new_beliefs"] += processed["new"]

                    results["sources_processed"] += 1

                except Exception as e:
                    results["errors"] += 1
                    print(f"Error processing source {source.name}: {e}")

            self.last_update = datetime.now()
            results["duration"] = time.time() - start_time
            results["count"] = self.get_beliefs_count()

            return results

        except Exception as e:
            results["error"] = str(e)
            return results

    def process_source_data(self, source_name: str, data: List[Dict]) -> Dict[str, int]:
        processed_count = 0
        new_count = 0
        for item in data:
            try:
                import hashlib
                content_str = json.dumps(item, sort_keys=True)
                belief_id = hashlib.md5(f"{source_name}_{content_str}".encode()).hexdigest()

                # Check if belief already exists
                existing = self.db.fetch_one("SELECT id FROM beliefs WHERE id = ?", (belief_id,))

                if not existing:
                    self.insert_belief({
                        "id": belief_id,
                        "content": content_str,
                        "source": source_name,
                        "confidence": 0.8, # Placeholder
                        "timestamp": datetime.now().isoformat()
                    })
                    new_count += 1
                processed_count += 1
            except Exception as e:
                print(f"Error processing belief item: {e}")
        return {"processed": processed_count, "new": new_count}

    def insert_belief(self, belief: Dict):
        query = "INSERT INTO beliefs (id, content, source, confidence, timestamp) VALUES (?, ?, ?, ?, ?)"
        params = (belief["id"], belief["content"], belief["source"], belief["confidence"], belief["timestamp"])
        self.db.execute(query, params)

    def get_beliefs_count(self) -> int:
        return self.db.fetch_scalar("SELECT COUNT(*) FROM beliefs")

class LocalSensorSource:
    def __init__(self):
        self.name = "local_sensors"
    def collect_data(self, timeout: int = 10) -> List[Dict]:
        import subprocess
        data = []
        try:
            battery_result = subprocess.run(
                ["termux-battery-status"], capture_output=True, text=True, timeout=timeout
            )
            if battery_result.returncode == 0:
                data.append({"type": "battery", "data": json.loads(battery_result.stdout)})
        except Exception as e:
            print(f"Error collecting battery data: {e}")
        return data

class APIEndpointSource:
    def __init__(self):
        self.name = "api_endpoints"
    def collect_data(self, timeout: int = 10) -> List[Dict]:
        data = []
        try:
            response = requests.get("https://api.github.com/zen", timeout=timeout)
            if response.status_code == 200:
                data.append({"type": "api", "endpoint": "github_zen", "data": response.text})
        except Exception as e:
            print(f"Error collecting API data: {e}")
        return data

class FileSystemSource:
    def __init__(self):
        self.name = "file_system"
    def collect_data(self, timeout: int = 10) -> List[Dict]:
        import shutil
        data = []
        try:
            disk_usage = shutil.disk_usage('/')
            data.append({
                "type": "disk_usage",
                "data": {"total": disk_usage.total, "used": disk_usage.used, "free": disk_usage.free}
            })
        except Exception as e:
            print(f"Error collecting file system data: {e}")
        return data
