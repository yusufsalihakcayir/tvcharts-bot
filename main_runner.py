"""
TVCharts Günlük İzleyici - Ana Yönetici (Orkestratör)
======================================================
Görevi: Tüm adımları sırasıyla ve güvenli bir şekilde çalıştırır.
"""

import subprocess
import sys

# Çalıştırılacak dosyaların sırası kritik!
ADIMLAR = [
    "tvcharts_scraper.py",   # 1. Veriyi çek
    "tvcharts_compare.py",   # 2. Dün ile karşılaştır
    "tvcharts_agent.py",     # 3. Claude'a yorumlat
    "tvcharts_notifier.py"   # 4. Telegram'a gönder
]

def main():
    print("🚀 TVCharts Otonom Sistemi Başlatılıyor...\n")
    print("="*50)
    
    for script in ADIMLAR:
        print(f"▶ [{script}] sıraya alındı ve çalıştırılıyor...")
        
        # sys.executable, sistemdeki aktif Python yolunu otomatik bulur (örn: python.exe)
        result = subprocess.run([sys.executable, script])
        
        # Eğer returncode 0 değilse, o betikte bir hata oluşmuş demektir.
        if result.returncode != 0:
            print(f"\n❌ HATA: {script} çalışırken bir sorun oluştu!")
            print("Sistem güvenliğiniz için sonraki adımlar durduruldu.")
            break
        else:
            print(f"✅ {script} başarıyla tamamlandı.\n")
            print("-" * 50)
            
    else:
        # For döngüsü break ile kesilmeden bitmişse çalışır
        print("\n🎉 Tüm işlemler eksiksiz tamamlandı! Telegram'ı kontrol edin.")

if __name__ == "__main__":
    main()