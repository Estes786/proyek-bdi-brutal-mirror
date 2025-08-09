#!/usr/bin/env python3
import os
import re
import sys

# --- KAMUS KATA-KATA TERLARANG ---
# Pola-pola rahasia yang harus dijaga
PATTERNS = {
    "GitHub Token": "ghp_[0-9a-zA-Z]{36}",
    "Vercel Token": "[a-zA-Z0-9]{24}",
    "AWS Access Key": "AKIA[0-9A-Z]{16}",
    "Google API Key": "AIza[0-9A-Za-z\\-_]{35}",
    "Generic API Key": "[Aa][Pp][Ii]_?[Kk][Ee][Yy].*['|\"]([0-9a-zA-Z\\-_]+)['|\"]",
    "Password": "[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*['|\"](.*?)['|\"]"
}

# File atau folder yang tidak perlu diperiksa
EXCLUSIONS = ['.git', 'node_modules', '.vercel', 'artifacts', 'check_secrets.py', 'termux_bdi.db', '__pycache__']

def log(message):
    print(f"[CodeGuardianAgent] {message}")

def scan_file(file_path):
    """Memindai satu file untuk mencari rahasia."""
    found_secrets = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for secret_name, pattern in PATTERNS.items():
                    if re.search(pattern, line):
                        secret_info = {
                            "file": file_path,
                            "line": line_num,
                            "type": secret_name,
                            "snippet": line.strip()
                        }
                        found_secrets.append(secret_info)
    except Exception as e:
        log(f"WARNING: Tidak bisa membaca file {file_path}: {e}")
    return found_secrets

def run_scan():
    """Memulai misi pemindaian di seluruh kerajaan kode."""
    log("Misi dimulai: Memindai seluruh kode dari potensi kebocoran rahasia...")
    all_found_secrets = []
    
    for root, dirs, files in os.walk('.', topdown=True):
        # Hapus folder yang tidak perlu diperiksa
        dirs[:] = [d for d in dirs if d not in EXCLUSIONS]
        
        for file in files:
            if file in EXCLUSIONS:
                continue
            
            file_path = os.path.join(root, file)
            secrets_in_file = scan_file(file_path)
            if secrets_in_file:
                all_found_secrets.extend(secrets_in_file)

    if all_found_secrets:
        log("\n" + "="*40)
        log("ðŸš¨ BAHAYA! POTENSI KEBOCORAN RAHASIA DITEMUKAN! ðŸš¨")
        log("="*40)
        for secret in all_found_secrets:
            log(f"- File: {secret['file']} (Baris: {secret['line']})")
            log(f"  Jenis Rahasia: {secret['type']}")
            log(f"  Potongan Kode: {secret['snippet']}")
            log("-" * 20)
        log("KEAMANAN KERAJAAN TERANCAM! Proses digagalkan!")
        return False
    else:
        log("ðŸ›¡ï¸  LAPORAN: Semua kode BERSIH! Tidak ada rahasia yang bocor.")
        log("Keamanan kerajaan terjaga.")
        return True

if __name__ == "__main__":
    if not run_scan():
        sys.exit(1) # Keluar dengan kode error untuk menggagalkan workflow
