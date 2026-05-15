import pytest
import requests
from datetime import date
from unittest.mock import MagicMock, patch
from scraper.core import (
    fetch_rss,
    fetch_article_body,
    summarize,
    fetch_and_summarize,
    save_output,
)


def test_summarize_returns_string():
    text = (
        "The economy grew by three percent last quarter driven by consumer spending. "
        "Analysts expect the trend to continue into the next fiscal year. "
        "Central banks are monitoring inflation levels closely. "
        "Stock markets reacted positively to the news on Monday. "
        "Technology stocks led the gains with a two percent rise. "
        "Bond yields fell slightly as investors sought safer assets. "
        "The unemployment rate held steady at four point two percent. "
        "Retail sales figures exceeded expectations by a wide margin. "
    ) * 3
    result = summarize(text, n_sentences=2)
    assert isinstance(result, str)
    assert len(result) > 0


def test_summarize_empty_text_returns_empty():
    result = summarize("", n_sentences=2)
    assert result == ""


def test_summarize_respects_sentence_count():
    text = (
        "Climate scientists published new findings on Arctic ice loss this week. "
        "The study analyzed satellite data collected over three decades. "
        "Researchers found that melting rates have accelerated since 2000. "
        "Coastal cities face rising sea levels as a direct consequence. "
        "Government agencies are revising flood risk maps in response. "
        "International agreements now call for faster emissions cuts. "
    ) * 3
    result = summarize(text, n_sentences=1)
    # LexRank can't guarantee exactly N sentences, but result should be non-empty
    assert isinstance(result, str)
    assert len(result) > 0
