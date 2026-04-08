"""
TVCharts Günlük İzleyici - Adım 4: Bildirim Agenti
==================================================
Görevi: Hazırlanan raporu okur ve Telegram üzerinden gönderir.
"""

import requests
import os
from datetime import date

# Telegram bilgilerinizi buraya girin 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

DATA_DIR = "data"
TODAY = date.today().isoformat()

def load_report(day: str) -> str | None:
    path = f"{DATA_DIR}/report_{day}.txt"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()

def send_to_telegram(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("[✓] Rapor Telegram'a başarıyla gönderildi! Telefonunuzu kontrol edin.")
    else:
        print(f"[!] Gönderim hatası: {response.status_code}")
        print(response.text)

def main():
    print(f"\n{'='*45}")
    print(f"  Bildirim Agenti çalışıyor — {TODAY}")
    print(f"{'='*45}\n")

    # Adım 3'ün ürettiği nihai raporu yükle
    report = load_report(TODAY)
    if report is None:
        print(f"[!] Rapor bulunamadı ({TODAY}). Önce tvcharts_agent.py'yi çalıştırın.")
        return

    print("[…] Telegram'a gönderiliyor...\n")
    send_to_telegram(report)

if __name__ == "__main__":
    main()