import feedparser
import json
from datetime import datetime, timezone
from pathlib import Path

MAG_FEEDS = {
    "SAFETY": [
        "https://www.dgms.gov.in/rss.xml"
    ],
    "ELECTRICAL": [
        "https://electricalindia.in/feed/"
    ],
    "INDUSTRY": [
        "https://www.mining-technology.com/feed/"
    ]
}

OUTPUT = Path("json/digital_magazines.json")
items = []
now = datetime.now(timezone.utc)

for category, feeds in MAG_FEEDS.items():
    for url in feeds:
        feed = feedparser.parse(url)
        for e in feed.entries:
            items.append({
                "title": e.title,
                "category": category,
                "date": (
                    datetime(*e.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                    if hasattr(e, "published_parsed") else now.isoformat()
                ),
                "url": e.link,        # read online
                "source": feed.feed.get("title", "Unknown"),
                "type": "magazine"
            })

items = sorted(items, key=lambda x: x["date"], reverse=True)[:200]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump({
        "items": items,
        "last_updated_utc": now.isoformat()
    }, f, indent=2)

print(f"✅ Digital magazines updated: {len(items)}")
