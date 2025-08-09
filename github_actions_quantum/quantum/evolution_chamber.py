#!/usr/bin/env python3
import json
import random
import sys
import time
from datetime import datetime

def log(message):
    """Mencatat aktivitas agen evolusi."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [EvolutionAgent] {message}")

def define_experiment():
    """Menentukan eksperimen yang akan dijalankan."""
    log("Mendefinisikan eksperimen baru...")
    # Dalam dunia nyata, ini bisa diambil dari database 'ide eksperimen'
    experiment = {
        "id": f"exp_{int(time.time())}",
        "target_component": "Wirecutter-Revolution Homepage",
        "metric_to_optimize": "conversion_rate",
        "variations": [
            {"id": "A", "changes": {"button_color": "blue", "title": "Produk Terbaik 2025"}},
            {"id": "B", "changes": {"button_color": "green", "title": "Jangan Lewatkan! Diskon Terbatas!"}}
        ]
    }
    log(f"Eksperimen didefinisikan: Menguji warna tombol dan judul di Homepage.")
    return experiment

def run_simulation(experiment):
    """Menjalankan simulasi A/B Testing."""
    log("Memulai simulasi A/B Testing...")
    results = {}
    for variation in experiment['variations']:
        var_id = variation['id']
        # Simulasi hasil berdasarkan perubahan
        # Judul yang menarik (urgensi) biasanya punya konversi lebih tinggi
        if "Diskon" in variation['changes']['title']:
            simulated_conversion = random.uniform(5.5, 8.5)
        else:
            simulated_conversion = random.uniform(3.0, 5.0)
        
        results[var_id] = {
            "conversion_rate": round(simulated_conversion, 2),
            "visitors": 1000 # Anggap setiap variasi dilihat 1000 orang
        }
        log(f"  - Hasil Simulasi Variasi {var_id}: Conversion Rate = {results[var_id]['conversion_rate']}%")
    
    # Simulasi membutuhkan waktu
    time.sleep(2)
    return results

def analyze_and_decide(experiment, results):
    """Menganalisis hasil dan memutuskan pemenang."""
    log("Menganalisis hasil eksperimen...")
    
    if not results:
        log("Tidak ada hasil untuk dianalisis. Eksperimen dibatalkan.")
        return None

    # Temukan variasi dengan conversion rate tertinggi
    winner_id = max(results, key=lambda v: results[v]['conversion_rate'])
    winner_stats = results[winner_id]
    
    log(f"PEMENANG DITEMUKAN: Variasi '{winner_id}' dengan Conversion Rate {winner_stats['conversion_rate']}%!")

    decision = {
        "winner_variation_id": winner_id,
        "winning_changes": next(v['changes'] for v in experiment['variations'] if v['id'] == winner_id),
        "action_recommendation": f"Secara permanen terapkan perubahan dari Variasi {winner_id}."
    }
    return decision

def generate_report(decision):
    """Menghasilkan laporan evolusi."""
    if not decision:
        return

    print("\n" + "="*50)
    print("ðŸ¦„ LAPORAN EVOLUSI OTONOMUS ðŸ¦„")
    print("="*50)
    print(f"ðŸ † Pemenang Eksperimen: Variasi '{decision['winner_variation_id']}'")
    print("   - Perubahan yang Menang:")
    for key, value in decision['winning_changes'].items():
        print(f"     - {key.replace('_', ' ').title()}: {value}")
    print(f"\nðŸš€ Rekomendasi Aksi: {decision['action_recommendation']}")
    print("="*50)
    log("Laporan evolusi selesai dibuat.")


if __name__ == "__main__":
    log("Misi dimulai: Mencari cara untuk berevolusi menjadi lebih baik...")
    current_experiment = define_experiment()
    simulation_results = run_simulation(current_experiment)
    final_decision = analyze_and_decide(current_experiment, simulation_results)
    generate_report(final_decision)
    log("Misi evolusi selesai.")
