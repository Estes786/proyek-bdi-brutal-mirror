#!/usr/bin/env python3
import json
import random
import sys
from datetime import datetime

def log(message):
    """Mencatat aktivitas agen."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [BusinessInsightAgent] {message}")

def simulate_data_fetching():
    """Simulasi pengambilan data bisnis dari berbagai sumber."""
    log("Mengambil data bisnis (simulasi)...")
    # Dalam dunia nyata, ini akan mengambil data dari Vercel API, Supabase, dll.
    simulated_data = [
        {'product_id': 'A', 'sentiment': 'positive', 'sales_trend': 'up'},
        {'product_id': 'B', 'sentiment': 'negative', 'sales_trend': 'down'},
        {'product_id': 'C', 'sentiment': 'neutral', 'sales_trend': 'stable'},
        {'product_id': 'D', 'sentiment': 'positive', 'sales_trend': 'up'},
    ]
    # Acak salah satu data untuk menjadi anomali
    if random.random() > 0.6: # 40% kemungkinan ada anomali
        log("ANOMALI DITEMUKAN DALAM SIMULASI!")
        simulated_data.append({'product_id': 'B', 'sentiment': 'negative', 'sales_trend': 'down'})
        simulated_data.append({'product_id': 'B', 'sentiment': 'negative', 'sales_trend': 'down'})
    return simulated_data

def analyze_data(data):
    """Menganalisis data untuk menemukan wawasan (insights)."""
    log("Menganalisis data untuk mencari peluang dan ancaman...")
    insights = []
    
    # Hitung frekuensi sentimen untuk setiap produk
    sentiment_counts = {}
    for item in data:
        pid = item['product_id']
        sentiment = item['sentiment']
        if pid not in sentiment_counts:
            sentiment_counts[pid] = {'positive': 0, 'negative': 0, 'neutral': 0}
        sentiment_counts[pid][sentiment] += 1
        
    # Logika analisis brutal
    for product_id, counts in sentiment_counts.items():
        total_reviews = sum(counts.values())
        
        # ANCAMAN: Jika ulasan negatif lebih dari 30%
        if counts['negative'] / total_reviews > 0.3:
            insight = {
                "type": "ANCAMAN",
                "product_id": product_id,
                "message": f"Sentimen negatif untuk produk {product_id} melonjak!",
                "recommendation": f"Segera periksa ulasan produk {product_id}."
            }
            insights.append(insight)

        # PELUANG: Jika ulasan positif lebih dari 70%
        if counts['positive'] / total_reviews > 0.7:
            insight = {
                "type": "PELUANG",
                "product_id": product_id,
                "message": f"Produk {product_id} sangat disukai pelanggan!",
                "recommendation": f"Pertimbangkan untuk membuat promosi 'Best Seller' untuk produk {product_id}."
            }
            insights.append(insight)
            
    return insights

def generate_report(insights):
    """Menghasilkan laporan dari wawasan yang ditemukan."""
    log("Menghasilkan laporan...")
    if not insights:
        log("Tidak ada wawasan bisnis signifikan yang ditemukan. Semua terpantau aman.")
        return

    print("\n" + "="*50)
    print("ðŸ“ˆ LAPORAN WAWASAN BISNIS OTONOMUS ðŸ“ˆ")
    print("="*50)
    for insight in insights:
        icon = "âš¡" if insight['type'] == 'ANCAMAN' else "ðŸ’°"
        print(f"{icon} Tipe: {insight['type']}")
        print(f"   - Pesan: {insight['message']}")
        print(f"   - Rekomendasi Aksi: {insight['recommendation']}")
        print("-" * 20)
    print("="*50)

if __name__ == "__main__":
    log("Misi dimulai: Menganalisis kesehatan bisnis kerajaan...")
    business_data = simulate_data_fetching()
    valuable_insights = analyze_data(business_data)
    generate_report(valuable_insights)
    log("Misi selesai.")

```4.  Simpan dan keluar.
