"""
TVCharts Günlük İzleyici - Adım 3: Yorum Agenti
================================================
Token maliyeti: ~200-400 token/gün  (Claude Haiku)
Görevi: Karşılaştırma özetini alır, kısa yorum üretir.
"""

import anthropic
import os
from datetime import date

DATA_DIR = "data"
TODAY    = date.today().isoformat()

# ── API istemcisi ──────────────────────────────────────────
# API key'i ortam değişkeninden okur.
# Çalıştırmadan önce terminale şunu yaz:
#   Windows: set ANTHROPIC_API_KEY=sk-ant-...
#   Mac/Linux: export ANTHROPIC_API_KEY=sk-ant-...
client = anthropic.Anthropic()


# ── Özeti dosyadan oku ─────────────────────────────────────
def load_summary(day: str) -> str | None:
    path = f"{DATA_DIR}/summary_{day}.txt"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Claude'a gönder, yorum al ──────────────────────────────
def get_commentary(summary: str) -> str:
    """
    Özeti Claude Haiku'ya gönderir.
    Sadece farkları gönderiyoruz — tüm listeyi değil.
    Bu sayede token kullanımı minimumda kalır.
    """
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=(
            "Sen kısa ve eğlenceli bir TV dizi takipçisisin. "
            "Günlük TVCharts sıralama değişimlerini 3-4 cümleyle yorumlarsın. "
            "Türkçe yanıt ver. Gereksiz giriş cümlesi kullanma, direkt yoruma gir."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Bugünkü TVCharts değişimleri:\n\n{summary}\n\n"
                    "Bu değişimleri 3-4 cümleyle yorumla. "
                    "En dikkat çekici hareketi öne çıkar."
                )
            }
        ]
    )

    return message.content[0].text


# ── Raporu kaydet ──────────────────────────────────────────
def save_report(summary: str, commentary: str) -> str:
    report = f"""
╔══════════════════════════════════════════════╗
  TVCharts Günlük Rapor — {TODAY}
╚══════════════════════════════════════════════╝

{summary}

──────────────────────────────────────────────
  🤖 Claude Yorumu
──────────────────────────────────────────────
{commentary}
""".strip()

    path = f"{DATA_DIR}/report_{TODAY}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

    return report, path


# ── Ana akış ──────────────────────────────────────────────
def main():
    print(f"\n{'='*45}")
    print(f"  Yorum Agenti çalışıyor — {TODAY}")
    print(f"{'='*45}\n")

    # Özeti yükle
    summary = load_summary(TODAY)
    if summary is None:
        print("[!] Özet bulunamadı. Önce tvcharts_compare.py'yi çalıştır.")
        return

    print("[✓] Özet yüklendi")
    print("[…] Claude Haiku'ya gönderiliyor...\n")

    # Yorum al
    commentary = get_commentary(summary)
    print("── Claude Yorumu ────────────────────────")
    print(commentary)

    # Raporu kaydet
    report, path = save_report(summary, commentary)
    print(f"\n[✓] Rapor kaydedildi → {path}")

    return commentary


if __name__ == "__main__":
    main()
