"""
Script ini dijalankan oleh GitHub Actions (bukan oleh PythonAnywhere).
Tugasnya: ambil berita XAUUSD dari RSS feed + kalender ekonomi dari
ForexFactory, lalu simpan sebagai file JSON (news.json, calendar.json)
di dalam repository GitHub ini.

Kenapa lewat GitHub dulu? Karena GitHub Actions punya akses internet
penuh (tidak ada batasan whitelist seperti PythonAnywhere free tier).
Nanti bot di PythonAnywhere tinggal baca file JSON ini dari
raw.githubusercontent.com, yang sudah otomatis diizinkan di
PythonAnywhere free tier.
"""

import json
import feedparser
import requests
from datetime import datetime, timezone

RSS_FEEDS = {
    "Kitco News": "https://www.kitco.com/rss/KitcoNews.xml",
    "Investing.com - Commodities": "https://www.investing.com/rss/commodities.rss",
    "FXStreet - News": "https://www.fxstreet.com/rss/news",
    "Reuters - Business": "https://feeds.reuters.com/reuters/businessNews",
}

KEYWORDS = [
    "gold", "xau", "bullion", "fed", "fomc", "interest rate",
    "inflation", "cpi", "nonfarm", "nfp", "dollar", "dxy",
    "treasury yield", "safe haven", "powell", "warsh", "rate cut", "rate hike"
]

FF_CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
CALENDAR_CURRENCY_FILTER = ["USD"]

MAX_NEWS_ITEMS = 15


def is_relevant(text):
    return any(kw in text.lower() for kw in KEYWORDS)


def fetch_news():
    found = []
    for source_name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"Gagal ambil feed {source_name}: {e}")
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            if is_relevant(f"{title} {summary}"):
                found.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                })

    return found[:MAX_NEWS_ITEMS]


def fetch_calendar():
    try:
        resp = requests.get(FF_CALENDAR_URL, timeout=15)
        resp.raise_for_status()
        events = resp.json()
    except Exception as e:
        print(f"Gagal ambil kalender: {e}")
        return []

    usd_events = [e for e in events if e.get("country", "") in CALENDAR_CURRENCY_FILTER]
    return usd_events


def main():
    news = fetch_news()
    calendar = fetch_calendar()

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "news": news,
    }
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    output_cal = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "events": calendar,
    }
    with open("calendar.json", "w", encoding="utf-8") as f:
        json.dump(output_cal, f, ensure_ascii=False, indent=2)

    print(f"Selesai: {len(news)} berita, {len(calendar)} event kalender.")


if __name__ == "__main__":
    main()
