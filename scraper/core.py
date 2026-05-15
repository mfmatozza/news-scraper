import urllib.parse
from datetime import date
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-scraper/1.0)"}


def fetch_rss(topic: str, n: int) -> list[dict]:
    encoded = urllib.parse.quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries[:n]:
        results.append({
            "title": getattr(entry, "title", ""),
            "url": getattr(entry, "link", ""),
            "published": getattr(entry, "published", ""),
            "description": getattr(entry, "summary", ""),
        })
    return results


def fetch_article_body(url: str) -> str:
    response = requests.get(url, headers=_HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    return " ".join(p for p in paragraphs if p)


def summarize(text: str, n_sentences: int = 3) -> str:
    if not text.strip():
        return ""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    sentences = summarizer(parser.document, n_sentences)
    return " ".join(str(s) for s in sentences)


def fetch_and_summarize(topic: str, n: int = 5, sentences: int = 3) -> list[dict]:
    articles = fetch_rss(topic, n)
    if len(articles) < n:
        print(f"  [info] Found {len(articles)} article(s) (requested {n})")
    results = []
    for article in articles:
        try:
            body = fetch_article_body(article["url"])
        except Exception as e:
            print(f"  [warning] Skipping fetch for '{article['title']}': {e}")
            body = ""
        text = body if body.strip() else article["description"]
        summary = summarize(text, sentences)
        results.append({**article, "summary": summary})
    return results


def save_output(data, filename: str):
    """Stub for save_output"""
    pass
