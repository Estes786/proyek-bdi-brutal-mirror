#!/usr/bin/env python3
"""
DWAN BDI Agent - Termux Version (Lightweight)
Koordinator utama yang menjalankan di Android device
"""

import os
import sys
import time
import json
import signal
import logging
from datetime import datetime
from pathlib import Path

# Baris ajaib agar Python bisa menemukan file-file kita
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.sqlite_manager import SQLiteManager
from core.belief_lite import BeliefSystemLite
from core.desire_lite import DesireSystemLite
from core.intention_lite import IntentionSystemLite

class TermuxBDIAgent:
    """Lightweight BDI Agent untuk Android Termux"""

    def __init__(self):
        self.config = {} # Untuk sekarang, kita buat simpel
        self.running = True
        self.cycle_count = 0
        self.cycle_interval = 30 # Agen akan berjalan setiap 30 detik

        # Inisialisasi semua komponen
        self.db = SQLiteManager('data/termux_bdi.db')
        self.belief_system = BeliefSystemLite(self.db, self.config)
        self.desire_system = DesireSystemLite(self.db, self.config)
        self.intention_system = IntentionSystemLite(self.db, self.config)

        self.setup_logging()
        self.logger = logging.getLogger("TermuxBDI")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_logging(self):
        """Setup pencatatan aktivitas agen"""
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
        """Fungsi untuk berhenti dengan aman"""
        self.logger.info("Menerima sinyal berhenti, mematikan agen...")
        self.running = False

    def run_bdi_cycle(self):
        """Menjalankan satu siklus BDI lengkap"""
        self.cycle_count += 1
        self.logger.info(f"--- SIKLUS BDI KE-{self.cycle_count} DIMULAI ---")
        
        # 1. BELIEF: Agen "Melihat" dan mengumpulkan informasi
        belief_context = self.belief_system.update_beliefs()
        self.logger.info(f"Beliefs updated: {belief_context.get('new_beliefs', 0)} new beliefs found.")
        
        # 2. DESIRE: Agen "Berpikir" dan menentukan keinginan
        desire_context = self.desire_system.optimize_desires(belief_context)
        top_desire_name = desire_context.get("top_desires", [{}])[0].get("name", "None")
        self.logger.info(f"Desire optimized: Keinginan utama adalah '{top_desire_name}'.")
        
        # 3. INTENTION: Agen "Bertindak" berdasarkan keinginan
        intention_result = self.intention_system.execute_intentions(desire_context)
        self.logger.info(f"Intentions executed: {intention_result.get('actions', 0)} aksi dilakukan.")
        self.logger.info(f"--- SIKLUS BDI SELESAI ---")

    def start(self):
        """Memulai agen untuk berjalan selamanya"""
        self.logger.info("🚀🚀🚀 AGEN BDI BRUTAL SIAP BERAKSI! 🚀🚀🚀")
        while self.running:
            try:
                cycle_start = time.time()
                self.run_bdi_cycle()
                cycle_duration = time.time() - cycle_start
                
                sleep_time = max(0, self.cycle_interval - cycle_duration)
                self.logger.info(f"Istirahat selama {sleep_time:.2f} detik...")
                time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"!!! SIKLUS GAGAL TOTAL: {e}", exc_info=True)
                time.sleep(60) # Tunggu sebentar jika ada error besar
        
        self.logger.info("Agen BDI telah berhenti.")
        self.db.close()

if __name__ == "__main__":
    agent = TermuxBDIAgent()
    agent.start()
