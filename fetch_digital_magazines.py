import feedparser
import json
from datetime import datetime, timezone
from pathlib import Path

# ================= CONFIG =================
MAG_FEEDS = {
    "SAFETY": [
        "https://www.dgms.gov.in/rss.xml"
    ],
    "ELECTRICAL": [
        "https://electricalindia.in/feed/"
    ],
    "INDUSTRY": [
        "https://www.mining-technology.com/feed/"
    ],
    "MECHANICAL": [
        "https://www.engineeringnews.co.za/rss/mechanical-engineering",
        "https://www.manufacturingtodayindia.com/feed/"
    ],
    "INSTRUMENTATION": [
        "https://www.instrumentation.co.in/feed/",
        "https://www.automationmag.com/feed/"
    ]
}

OUTPUT = Path("json/digital_magazines.json")
MAX_ITEMS = 10000
# =========================================

now = datetime.now(timezone.utc)

# 🔹 LOAD EXISTING DATA (APPEND MODE)
if OUTPUT.exists():
    with open(OUTPUT, "r", encoding="utf-8") as f:
        existing_items = json.load(f).get("items", [])
else:
    existing_items = []

# 🔹 DICTIONARY FOR DEDUPE (URL AS KEY)
items = {item["url"]: item for item in existing_items}

# 🔹 FETCH NEW DATA
for category, feeds in MAG_FEEDS.items():
    for url in feeds:
        feed = feedparser.parse(url)

        for e in feed.entries:
            link = e.link.strip()

            published = (
                datetime(*e.published_parsed[:6], tzinfo=timezone.utc)
                if hasattr(e, "published_parsed") and e.published_parsed
                else now
            )

            # 🔹 APPEND / UPDATE
            items[link] = {
                "title": e.title.strip(),
                "category": category,
                "date": published.isoformat(),
                "url": link,
                "source": feed.feed.get("title", "Unknown"),
                "type": "magazine"
            }

# 🔹 SORT + LIMIT TO 10,000
final_items = sorted(
    items.values(),
    key=lambda x: x["date"],
    reverse=True
)[:MAX_ITEMS]

# 🔹 WRITE JSON (SAFE OVERWRITE OF FILE, NOT DATA)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(
        {
            "items": final_items,
            "last_updated_utc": now.isoformat()
        },
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"✅ Digital magazines updated: {len(final_items)} items")
