
"""Simple RSS fetch placeholder."""
import feedparser

FEEDS = [
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://toyokeizai.net/list/feed/rss",
    "https://www.nikkei.com/rss/nikkei/index.rdf",
]

def fetch_latest():
    all_articles = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_articles.append({"title": entry.title, "link": entry.link})
    return all_articles
