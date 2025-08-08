"""
Lightweight Intention System untuk Termux (VERSI UPGRADE)
Execute actions berdasarkan optimized desires
"""

import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class IntentionSystemLite:
    """Lightweight Intention System untuk action execution"""

    def __init__(self, db_manager, config):
        self.db = db_manager
        self.config = config
        self.available_actions = {
            "send_notification": self.send_notification,
            "simulate_action": self.simulate_action
        }
        self.init_schema()

    def init_schema(self):
        """Initialize database schema untuk log aksi"""
        log_schema = """
        CREATE TABLE IF NOT EXISTS action_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL NOT NULL,
            result_summary TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_schema(log_schema)

    def send_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mengirim notifikasi Android menggunakan Termux:API"""
        try:
            title = params.get("title", "BDI Agent Action")
            content = params.get("content", "Sebuah aksi telah dieksekusi.")
            print(f"  -> AKSI: Mencoba mengirim notifikasi: '{title}'...")
            
            # Perintah sakral untuk notifikasi
            subprocess.run(
                ["termux-notification", "--title", title, "--content", content],
                capture_output=True, text=True, timeout=10, check=True
            )
            
            print("  -> HASIL: Notifikasi berhasil dikirim!")
            return {"status": "success", "message": "Notification sent."}
        except FileNotFoundError:
            print("  -> ERROR: Perintah 'termux-notification' tidak ditemukan. Pastikan pkg termux-api sudah terinstall.")
            return {"status": "failed", "error": "command not found"}
        except Exception as e:
            print(f"  -> ERROR: Gagal mengirim notifikasi: {e}")
            return {"status": "failed", "error": str(e)}

    def simulate_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aksi simulasi untuk testing"""
        action_name = params.get('name', 'Unknown Action')
        print(f"  -> AKSI: Menjalankan simulasi untuk '{action_name}'...")
        time.sleep(0.5) # Pura-pura bekerja
        print(f"  -> HASIL: Simulasi '{action_name}' berhasil.")
        return {"status": "simulated_success"}

    def execute_intentions(self, desire_context: Dict[str, Any]) -> Dict[str, Any]:
        """Mengeksekusi niat berdasarkan keinginan utama"""
        top_desires = desire_context.get("top_desires", [])
        if not top_desires:
            return {"actions": 0, "duration": 0}

        top_desire = top_desires[0]
        action_type, params = self.select_action_for_desire(top_desire)
        
        result_summary = {"action_type": "none", "status": "no_action_selected", "duration": 0}

        if action_type and action_type in self.available_actions:
            action_func = self.available_actions[action_type]
            exec_start = time.time()
            result = action_func(params)
            exec_duration = time.time() - exec_start
            
            result_summary = {
                "action_type": action_type,
                "status": result.get("status"),
                "duration": exec_duration,
                "result_data": result
            }
            self.log_execution_results([result_summary])
        
        return {
            "actions": 1 if result_summary["status"] != "no_action_selected" else 0,
            "results": [result_summary]
        }

    def select_action_for_desire(self, desire: Dict) -> (Optional[str], Dict):
        """Memilih aksi dan menyiapkan parameternya"""
        desire_id = desire.get("id", "")
        
        # KITA PAKSA SEMUA KEINGINAN UNTUK MENGIRIM NOTIFIKASI UNTUK SEKARANG
        # INI UNTUK MEMASTIKAN NOTIFIKASI PASTI JALAN
        
        action_type = "send_notification"
        params = {
            "title": f"🔥 {desire.get('name', 'Tugas BDI')}",
            "content": f"Keinginan utama saat ini! Prioritas: {desire.get('priority', 0):.2f}"
        }
        return action_type, params

    def log_execution_results(self, results: List[Dict]):
        """Mencatat hasil eksekusi ke database"""
        for result in results:
            query = "INSERT INTO action_executions (action_type, status, duration, result_summary) VALUES (?, ?, ?, ?)"
            params = (result["action_type"], result["status"], result["duration"], json.dumps(result))
            self.db.execute(query, params)
