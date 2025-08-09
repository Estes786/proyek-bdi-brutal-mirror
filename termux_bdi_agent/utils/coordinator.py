import requests
import json
import os
from datetime import datetime

class PlatformCoordinator:
    def __init__(self, config):
        self.config = config.get('integration', {})
        self.vercel_url = self.config.get('vercel_url')
        # ... (sisa __init__ tetap sama)

    def update_vercel_status(self, component, status, metrics={}):
        if not self.vercel_url:
            print("URL Vercel tidak diatur.")
            return False
        
        try:
            url = f"{self.vercel_url}/api/status"
            payload = { "component": component, "status": status, "metrics": metrics }
            # Tambahkan timeout yang lebih masuk akal
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Status '{component}' berhasil dikirim ke Vercel.")
                return True
            else:
                # Jangan panik, cukup catat sebagai warning
                print(f"WARNING: Gagal update status ke Vercel (Status: {response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            # Jangan panik, ini mungkin hanya masalah jaringan sementara
            print(f"WARNING: Tidak bisa terhubung ke Vercel API: {e}")
            return False

    def trigger_github_workflow(self):
        if not self.github_repo or not self.github_token:
            print("Repo GitHub atau Token tidak diatur. Pemicuan dibatalkan.")
            return False

        url = f"https://api.github.com/repos/{self.github_repo}/dispatches"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.github_token}"
        }
        data = {
            "event_type": "quantum-processing-trigger",
            "client_payload": {
                "source": "TermuxAgent",
                "timestamp": datetime.now().isoformat()
            }
        }
        try:
            print("Mencoba memicu Workflow di GitHub...")
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 204:
                print("Sinyal ke Otak Kuantum GitHub BERHASIL dikirim!")
                return True
            else:
                print(f"Pemicuan GitHub GAGAL: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error koneksi ke GitHub: {e}")
            return False
