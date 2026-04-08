"""
TVCharts Günlük İzleyici - Adım 2: Karşılaştırıcı
==================================================
Token maliyeti: 0  (saf Python, Claude yok)
Görevi: Dünkü ve bugünkü JSON'ı karşılaştır,
        değişimleri özetle → Claude'a sadece bunu gönder.
"""

import json
import os
from datetime import date, timedelta


DATA_DIR = "data"
TODAY    = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()


# ── Yardımcı: JSON yükle ───────────────────────────────────
def load(day: str) -> dict | None:
    path = f"{DATA_DIR}/{day}.json"
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Karşılaştır ────────────────────────────────────────────
def compare(yesterday: dict, today: dict) -> dict:
    """
    İki günlük veriyi karşılaştırır.
    Döner:
      new_entries   → bugün ilk kez listede olanlar
      dropped       → dünkü listeden çıkanlar
      big_movers    → 3+ basamak değişenler
      top5_change   → ilk 5'te değişim var mı?
    """
    y_map = {s["id"]: s for s in yesterday["shows"]}
    t_map = {s["id"]: s for s in today["shows"]}

    y_ids = set(y_map.keys())
    t_ids = set(t_map.keys())

    # Yeni girenler
    new_entries = [t_map[i] for i in (t_ids - y_ids)]

    # Çıkanlar
    dropped = [y_map[i] for i in (y_ids - t_ids)]

    # Büyük hareket edenler (3+ basamak)
    big_movers = []
    for sid, show in t_map.items():
        if sid not in y_map:
            continue
        old_rank = y_map[sid]["rank"]
        new_rank = show["rank"]
        diff = old_rank - new_rank   # pozitif = yükseldi
        if abs(diff) >= 3:
            big_movers.append({
                **show,
                "old_rank": old_rank,
                "diff": diff,
            })
    big_movers.sort(key=lambda x: abs(x["diff"]), reverse=True)

    # İlk 5 değişimi
    y_top5 = [s["title"] for s in sorted(yesterday["shows"], key=lambda x: x["rank"])[:5]]
    t_top5 = [s["title"] for s in sorted(today["shows"],     key=lambda x: x["rank"])[:5]]
    top5_changed = y_top5 != t_top5

    return {
        "date_yesterday": yesterday["date"],
        "date_today":     today["date"],
        "new_entries":    new_entries,
        "dropped":        dropped,
        "big_movers":     big_movers,
        "top5_yesterday": y_top5,
        "top5_today":     t_top5,
        "top5_changed":   top5_changed,
        "total_shows_today": len(today["shows"]),
    }


# ── Özet metin üret (Claude'a gönderilecek) ───────────────
def build_summary(diff: dict) -> str:
    """
    Karşılaştırma verisini kısa bir metin özetine dönüştürür.
    Bu metin Claude'a gönderilecek — mümkün olduğunca kısa tutulur.
    """
    lines = []
    lines.append(f"Tarih: {diff['date_yesterday']} → {diff['date_today']}")
    lines.append("")

    # Top 5
    lines.append("🏆 Top 5 Dün:")
    for i, t in enumerate(diff["top5_yesterday"], 1):
        lines.append(f"  {i}. {t}")
    lines.append("🏆 Top 5 Bugün:")
    for i, t in enumerate(diff["top5_today"], 1):
        lines.append(f"  {i}. {t}")
    lines.append("")

    # Yeni girenler
    if diff["new_entries"]:
        lines.append("🆕 Listeye Yeni Girenler:")
        for s in diff["new_entries"]:
            lines.append(f"  • {s['title']} (#{s['rank']}, ★{s['imdb']})")
    else:
        lines.append("🆕 Yeni giren yok.")
    lines.append("")

    # Çıkanlar
    if diff["dropped"]:
        lines.append("❌ Listeden Çıkanlar:")
        for s in diff["dropped"]:
            lines.append(f"  • {s['title']} (dün #{s['rank']}dı)")
    else:
        lines.append("❌ Listeden çıkan yok.")
    lines.append("")

    # Büyük hareketler
    if diff["big_movers"]:
        lines.append("📈 Büyük Hareketler (3+ basamak):")
        for s in diff["big_movers"]:
            arrow = "▲" if s["diff"] > 0 else "▼"
            lines.append(
                f"  {arrow} {s['title']}: "
                f"#{s['old_rank']} → #{s['rank']} ({s['diff']:+d})"
            )
    else:
        lines.append("📈 Büyük hareket eden dizi yok.")

    return "\n".join(lines)


# ── Ekrana güzel bas ───────────────────────────────────────
def print_report(diff: dict, summary: str) -> None:
    print(f"\n{'='*45}")
    print(f"  Karşılaştırma: {diff['date_yesterday']} → {diff['date_today']}")
    print(f"{'='*45}")
    print(summary)
    print(f"\n{'='*45}")
    print(f"  Claude'a gönderilecek token tahmini: ~{len(summary.split())*1.3:.0f}")
    print(f"{'='*45}\n")


# ── Ana akış ──────────────────────────────────────────────
def main():
    yesterday_data = load(YESTERDAY)
    today_data     = load(TODAY)

    if today_data is None:
        print(f"[!] Bugünün verisi bulunamadı: {TODAY}.json")
        print("    Önce tvcharts_scraper.py'yi çalıştır.")
        return None

    if yesterday_data is None:
        print(f"[!] Dünün verisi yok, ama bugünlük devam ediyoruz...")
        # Dün verisi yoksa, dünü bugüne eşitleyelim ki sistem ilerlesin
        yesterday_data = today_data

    diff    = compare(yesterday_data, today_data)
    summary = build_summary(diff)
    print_report(diff, summary)

    # Özeti dosyaya da kaydet (Adım 4'te Claude okuyacak)
    summary_path = f"{DATA_DIR}/summary_{TODAY}.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"[✓] Özet kaydedildi → {summary_path}")

    return summary


if __name__ == "__main__":
    main()
