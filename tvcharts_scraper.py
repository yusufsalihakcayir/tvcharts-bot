"""
TVCharts Günlük İzleyici - Adım 1: Veri Çekici
=============================================
Token maliyeti: 0  (saf Python, Claude yok)
Çalışma süresi: ~1-2 saniye
"""

import requests
import json
import re
from datetime import date

# ── Sabitler ──────────────────────────────────────────────
BASE_URL   = "https://tvcharts.co"
DATA_DIR   = "data"          # JSON'lar buraya kaydedilir
TODAY      = date.today().isoformat()   # "2026-04-08"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


# ── 1. Build ID'yi dinamik olarak al ──────────────────────
def get_build_id() -> str:
    """
    Next.js build ID her deploy'da değişir.
    Ana sayfanın HTML'inden regex ile çekiyoruz.
    """
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    # Next.js her zaman şu pattern'i gömer: "buildId":"xxxx"
    match = re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text)
    if not match:
        raise RuntimeError("Build ID bulunamadı — site yapısı değişmiş olabilir.")

    build_id = match.group(1)
    print(f"[✓] Build ID: {build_id}")
    return build_id


# ── 2. Popular listesini çek ───────────────────────────────
def fetch_popular(build_id: str) -> list[dict]:
    """
    Ana sayfanın popular dizilerini JSON olarak döndürür.
    Örnek dönen alan:
      id, rank, title, imDbRating, rankUpDown, year
    """
    url = f"{BASE_URL}/_next/data/{build_id}/index.json"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    shows = data["pageProps"]["popular"]
    print(f"[✓] {len(shows)} dizi çekildi")
    return shows


# ── 3. Sadece işe yarayan alanları tut ────────────────────
def clean(shows: list[dict]) -> list[dict]:
    """
    Resim URL'i ve crew gibi gereksiz alanları atar,
    sayısal alanları düzeltir.
    """
    cleaned = []
    for s in shows:
        cleaned.append({
            "rank":       int(s["rank"]),
            "id":         s["id"],
            "title":      s["title"],
            "year":       s["year"],
            "imdb":       float(s["imDbRating"]) if s["imDbRating"] else None,
            "votes":      int(s["imDbRatingCount"]) if s["imDbRatingCount"] else 0,
            "rank_change": s["rankUpDown"],   # "+3", "-1", "0" gibi
        })
    return cleaned


# ── 4. Dosyaya kaydet ──────────────────────────────────────
def save(shows: list[dict], filename: str) -> None:
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    path = f"{DATA_DIR}/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"date": TODAY, "shows": shows}, f, ensure_ascii=False, indent=2)
    print(f"[✓] Kaydedildi → {path}")


# ── Ana akış ──────────────────────────────────────────────
def main():
    print(f"\n{'='*40}")
    print(f"TVCharts çekiliyor — {TODAY}")
    print(f"{'='*40}\n")

    build_id = get_build_id()
    raw      = fetch_popular(build_id)
    shows    = clean(raw)
    save(shows, f"{TODAY}.json")

    # Ekrana özet bas
    print("\n── Top 10 ──────────────────────────")
    for s in shows[:10]:
        change = s["rank_change"]
        arrow  = "▲" if change.startswith("+") else ("▼" if change.startswith("-") else "●")
        print(f"  {s['rank']:>2}. {s['title']:<35} ★{s['imdb']}  {arrow}{change}")

    print(f"\n[✓] Tamamlandı. {len(shows)} dizi işlendi.\n")
    return shows


if __name__ == "__main__":
    main()
