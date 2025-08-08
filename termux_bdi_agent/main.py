#!/usr/bin/env python3
"""
DWAN BDI Agent - VERSI UPGRADE DENGAN PEMANCAR KUANTUM
"""

import os
import sys
import time
import json
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sqlite_manager import SQLiteManager
from utils.coordinator import PlatformCoordinator # <- MODUL BARU DIIMPOR
from core.belief_lite import BeliefSystemLite
from core.desire_lite import DesireSystemLite
from core.intention_lite import IntentionSystemLite

class TermuxBDIAgent:
    """BDI Agent dengan kemampuan komunikasi lintas platform"""

    def __init__(self):
        self.config = self.load_config()
        self.running = True
        self.cycle_count = 0
        self.cycle_interval = 60 # Kita perpanjang siklus jadi 1 menit

        self.setup_logging()
        self.logger = logging.getLogger("TermuxBDI")
        
        # Inisialisasi semua komponen
        self.db = SQLiteManager('data/termux_bdi.db')
        self.coordinator = PlatformCoordinator(self.config) # <- PEMANCAR DIINISIALISASI
        self.belief_system = BeliefSystemLite(self.db, self.config)
        self.desire_system = DesireSystemLite(self.db, self.config)
        self.intention_system = IntentionSystemLite(self.db, self.config)
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.last_github_trigger = datetime.now() - timedelta(minutes=10)

    def load_config(self):
        """Memuat konfigurasi dari config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("!!! FATAL: File 'config.json' tidak ditemukan!")
            sys.exit(1) # Keluar jika config tidak ada
        except json.JSONDecodeError:
            self.logger.error("!!! FATAL: File 'config.json' tidak valid!")
            sys.exit(1)

    def setup_logging(self):
        # ... (kode logging tetap sama)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'termux_bdi.log'),
                logging.StreamHandler()
            ]
        )

    def signal_handler(self, signum, frame):
        self.logger.info("Menerima sinyal berhenti, mematikan agen...")
        self.coordinator.update_vercel_status('termux_agent', 'offline')
        self.running = False
    
    def start(self):
        self.logger.info("🚀🚀🚀 AGEN BDI DENGAN PEMANCAR KUANTUM SIAP BERAKSI! 🚀🚀🚀")
        while self.running:
            # ... (kode loop tetap sama)
            self.run_bdi_cycle()
            time.sleep(self.cycle_interval)
        
        self.logger.info("Agen BDI telah berhenti.")
        self.db.close()

    def run_bdi_cycle(self):
        self.cycle_count += 1
        self.logger.info(f"--- SIKLUS BDI KE-{self.cycle_count} DIMULAI ---")
        
        # 1. BELIEF
        belief_context = self.belief_system.update_beliefs()
        
        # 2. DESIRE
        desire_context = self.desire_system.optimize_desires(belief_context)
        
        # 3. INTENTION
        intention_result = self.intention_system.execute_intentions(desire_context)
        
        # 4. LAPORAN & PICU!
        self.coordinator.update_vercel_status(
            'termux_agent', 
            'active', 
            {'total_cycles': self.cycle_count}
        )
        
        # Pemicuan GitHub setiap 5 menit
        if datetime.now() - self.last_github_trigger > timedelta(minutes=5):
            if self.coordinator.trigger_github_workflow():
                self.last_github_trigger = datetime.now()
                self.coordinator.update_vercel_status('quantum_processor', 'triggered')
        
        self.logger.info(f"--- SIKLUS BDI SELESAI ---")

if __name__ == "__main__":
    # SANGAT PENTING: Set GITHUB_TOKEN sebagai environment variable
    # Jalankan agen dengan: GITHUB_TOKEN="ghp_xxxx" python main.py
    if 'GITHUB_TOKEN' not in os.environ:
        print("\n!!! TOKEN GITHUB BELUM DI-SET !!!")
        print("Jalankan dengan cara: GITHUB_TOKEN=\"token_milikmu\" python main.py\n")
    else:
        agent = TermuxBDIAgent()
        agent.start()
