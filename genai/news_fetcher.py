# -*- coding: utf-8 -*-
"""Fetches crypto news from free public RSS feeds (no API key required)."""

import feedparser

FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
}


def fetch_latest_news(max_per_feed=10):
    """Fetch recent articles from all configured RSS feeds.

    Returns a list of dicts: {title, summary, link, published, source}
    """
    articles = []
    for source, url in FEEDS.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:max_per_feed]:
            articles.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", entry.get("description", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": source,
            })
    return articles


if __name__ == "__main__":
    news = fetch_latest_news(max_per_feed=3)
    print(f"Fetched {len(news)} articles")
    for a in news[:5]:
        print(f"- [{a['source']}] {a['title']}")
