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


def fetch_rss(url: str):
    """Stub for fetch_rss"""
    pass


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


def fetch_and_summarize(url: str):
    """Stub for fetch_and_summarize"""
    pass


def save_output(data, filename: str):
    """Stub for save_output"""
    pass
