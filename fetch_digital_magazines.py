import feedparser
import json
from datetime import datetime, timezone
from pathlib import Path

# ================= CONFIG =================
MAG_FEEDS = {
    "SAFETY": [
        "https://www.safetyandhealthmagazine.com/rss",
        "https://ohsonline.com/rss-feeds.aspx"
    ],
    "ELECTRICAL": [
        "https://electricalindia.in/feed/"
    ],
    "INDUSTRY": [
        "https://www.mining-technology.com/feed/"
    ],
    "MECHANICAL": [
        "https://www.manufacturingtodayindia.com/feed/",
        "https://www.engineering.com/rss/"
    ],
    "INSTRUMENTATION": [
        "https://www.instrumentation.co.in/feed/",
        "https://www.automationmag.com/feed/"
    ],
    "CIVIL": [
        "https://www.theconstructor.org/feed/",
        "https://www.constructionweekonline.in/feed/"
    ],
    "POWER": [
        "https://www.powerline.net.in/feed/"
    ],
    "RENEWABLE": [
        "https://www.renewableenergyworld.com/feed/"
    ]
}

OUTPUT_DIR = Path("json/magazines")
MAX_ITEMS = 10000
# =========================================

now = datetime.now(timezone.utc)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 🔹 PROCESS EACH CATEGORY SEPARATELY
for category, feeds in MAG_FEEDS.items():

    output_file = OUTPUT_DIR / f"{category}.json"

    # 🔹 LOAD EXISTING DATA (APPEND MODE PER CATEGORY)
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            existing_items = json.load(f).get("items", [])
    else:
        existing_items = []

    # 🔹 DEDUPE USING URL
    items = {item["url"]: item for item in existing_items}

    for url in feeds:
        feed = feedparser.parse(
            url,
            request_headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        if not feed.entries:
            print(f"⚠ DEAD / EMPTY FEED: {category} → {url}")
            continue

        for e in feed.entries:
            if not hasattr(e, "link"):
                continue

            link = e.link.strip()

            published = (
                datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
                if hasattr(e, "published_parsed") and e.published_parsed
                else now
            )

            items[link] = {
                "title": e.title.strip(),
                "category": category,
                "date": published.isoformat(),
                "url": link,
                "source": feed.feed.get("title", "Unknown"),
                "type": "magazine"
            }

    # 🔹 SORT + LIMIT
    final_items = sorted(
        items.values(),
        key=lambda x: x["date"],
        reverse=True
    )[:MAX_ITEMS]

    # 🔹 WRITE CATEGORY JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "category": category,
                "items": final_items,
                "last_updated_utc": now.isoformat()
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"✅ {category}: {len(final_items)} items written")
