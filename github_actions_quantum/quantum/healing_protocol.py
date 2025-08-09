#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime

def log(message):
    """Mencatat aktivitas agen penyembuh."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [SelfHealingAgent] {message}")

def check_system_health():
    """Memeriksa kesehatan komponen-komponen vital kerajaan."""
    log("Memulai patroli kesehatan sistem...")
    # Target vital yang harus diperiksa
    targets = {
        "Vercel Frontend": os.getenv("VERCEL_URL", "https://proyek-bdi-brutal1.vercel.app"),
        "Vercel Status API": f"{os.getenv('VERCEL_URL', 'https://proyek-bdi-brutal1.vercel.app')}/api/status"
    }
    
    failed_services = []
    for name, url in targets.items():
        try:
            response = requests.get(url, timeout=15)
            if response.status_code >= 400: # 4xx atau 5xx adalah masalah
                log(f"ðŸš¨ MASALAH DITEMUKAN! Layanan '{name}' merespons dengan status {response.status_code}.")
                failed_services.append({"name": name, "url": url, "status": response.status_code})
            else:
                log(f"âœ… Layanan '{name}' terpantau SEHAT.")
        except requests.exceptions.RequestException as e:
            log(f"ðŸš¨ KEGAGALAN KRITIS! Layanan '{name}' tidak bisa dihubungi. Error: {e}")
            failed_services.append({"name": name, "url": url, "status": "DOWN"})
    
    return failed_services

def attempt_healing(failures):
    """Mencoba protokol penyembuhan otonomus."""
    if not failures:
        log("Semua sistem sehat. Tidak ada tindakan penyembuhan yang diperlukan.")
        return

    log("MEMULAI PROTOKOL PENYEMBUHAN OTOMONOMUS!")
    for failure in failures:
        log(f"Mencoba menyembuhkan '{failure['name']}'...")
        
        # Protokol Penyembuhan Level 1: Memicu Redeploy di Vercel
        # Ini membutuhkan VERCEL_TOKEN, VERCEL_ORG_ID, dan VERCEL_PROJECT_ID di secrets
        if "Vercel" in failure['name']:
            log("-> Tindakan: Mencoba memicu redeployment Vercel...")
            
            # Di dunia nyata, kita akan memanggil Vercel API di sini.
            # Untuk simulasi, kita akan mencetak perintahnya.
            log("   (Simulasi) API Vercel untuk redeploy akan dipanggil di sini.")
            log("   -> HASIL: Permintaan redeploy berhasil dikirim (simulasi).")
            print("\n" + "="*50)
            print("ðŸ› ï¸  LAPORAN PENYEMBUHAN DIRI ðŸ› ï¸ ")
            print("="*50)
            print(f"Penyakit Terdeteksi: Layanan '{failure['name']}' Gagal")
            print(f"Obat yang Diberikan: Pemicuan Redeployment Otomatis ke Vercel")
            print("Status: Proses penyembuhan sedang berjalan.")
            print("="*50)

if __name__ == "__main__":
    log("Misi dimulai: Patroli kesehatan dan penyembuhan diri...")
    failed_systems = check_system_health()
    attempt_healing(failed_systems)
    log("Misi selesai.")
