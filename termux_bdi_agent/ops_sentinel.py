#!/usr/bin/env python3
#
# OpsSentinelAgent - Mata Elang Pemantau Website (Versi Final)
#
import requests
import subprocess
from datetime import datetime

# --- KONFIGURASI MISI ---
# Ganti dengan URL website yang ingin Anda awasi
TARGET_URL = "https://proyek-bdi-brutal1.vercel.app" 
LOG_FILE = "ops_sentinel.log"

def log(message):
    """Mencatat semua aktivitas ke file log dan ke layar."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def send_notification(title, content):
    """Mengirim notifikasi brutal ke HP Raja."""
    log(f"MENGIRIM NOTIFIKASI: {title} - {content}")
    try:
        subprocess.run([
            "termux-notification",
            "--title", title,
            "--content", content,
            "--priority", "high",
            "--sound" # Tambahkan suara agar lebih mengguncang!
        ], check=True, timeout=10)
    except Exception as e:
        log(f"GAGAL MENGIRIM NOTIFIKASI: {e}")

def check_website_status():
    """Mata Elang mulai mengintai!"""
    log(f"Mengintai target: {TARGET_URL}...")
    try:
        # Lakukan pengintaian dengan timeout 15 detik
        response = requests.get(TARGET_URL, timeout=15)

        # Analisis hasil pengintaian
        if 200 <= response.status_code < 300:
            log(f"LAPORAN: Target AMAN! (Status: {response.status_code})")
        else:
            log(f"PERINGATAN! Target dalam MASALAH! (Status: {response.status_code})")
            send_notification(
                "ðŸ”¥ WEBSITE DALAM MASALAH! ðŸ”¥",
                f"Target {TARGET_URL} merespons dengan status {response.status_code}!"
            )

    except requests.exceptions.Timeout:
        log(f"BAHAYA! Target SANGAT LAMBAT atau TIMEOUT!")
        send_notification(
            "ðŸš🐢 WEBSITE LAMBAT! ðŸš🐢",
            f"Pengintaian ke {TARGET_URL} timeout. Periksa performa!"
        )
    except requests.exceptions.RequestException as e:
        log(f"BAHAYA! Target TIDAK BISA DIHUBUNGI! (Error: {e})")
        send_notification(
            "ðŸš¨ WEBSITE DOWN! ðŸš¨",
            f"Target {TARGET_URL} tidak bisa diakses. Periksa segera!"
        )

if __name__ == "__main__":
    log("--- Misi Pengintaian OpsSentinel DIMULAI ---")
    check_website_status()
    log("--- Misi Pengintaian OpsSentinel SELESAI ---")
