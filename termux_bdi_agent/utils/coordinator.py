import requests
import json
import os
from datetime import datetime

class PlatformCoordinator:
    """Mengelola komunikasi antara Termux, Vercel, dan GitHub."""
    def __init__(self, config):
        self.config = config.get('integration', {})
        self.vercel_url = self.config.get('vercel_url')
        self.github_repo = self.config.get('github_repository')
        self.github_token = os.getenv('GITHUB_TOKEN') # Nanti kita bisa set ini
        print("Koordinator Lintas Platform Siap!")

    def update_vercel_status(self, component, status, metrics={}):
        if not self.vercel_url:
            print("URL Vercel tidak diatur. Melewatkan update status.")
            return False
        
        try:
            url = f"{self.vercel_url}/api/status"
            payload = {
                "component": component,
                "status": status,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                print(f"Update status '{component}' ke Vercel BERHASIL.")
                return True
            else:
                print(f"Update status ke Vercel GAGAL: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error koneksi ke Vercel: {e}")
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
