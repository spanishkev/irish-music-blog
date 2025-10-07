import os
import feedparser
from datetime import datetime
from transformers import pipeline

# === 1. Define your RSS feeds ===
# Irish + International music & entertainment news
RSS_FEEDS = [
    "https://www.rte.ie/entertainment/rss/",
    "https://www.hotpress.com/rss/news",
    "https://pitchfork.com/rss/news/",
    "https://www.nme.com/news/music/feed",
]

# === 2. Set up Hugging Face summarization model ===
API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", use_auth_token=API_TOKEN)

# === 3. Fetch and summarize news ===
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:3]:  # limit to first 3 per source
        title = entry.title
        link = entry.link
        summary_text = entry.get("summary", "") or entry.get("description", "")

        # Summarize using Hugging Face model
        try:
            summary = summarizer(summary_text, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        except Exception:
            summary = summary_text[:300] + "..."

        # === 4. Save as markdown draft ===
        date_str = datetime.now().strftime("%Y-%m-%d")
        slug = title.lower().replace(" ", "-").replace("/", "-")[:50]
        filename = f"posts/{date_str}-{slug}.md"

        os.makedirs("posts", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"""---
title: "{title}"
date: {date_str}
source: "{link}"
draft: true
---

{summary}

[Read full story]({link})
""")
