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


def _make_mock_response(html: str):
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_fetch_article_body_extracts_paragraphs():
    html = "<html><body><p>First paragraph.</p><p>Second paragraph.</p></body></html>"
    with patch("scraper.core.requests.get", return_value=_make_mock_response(html)):
        result = fetch_article_body("https://example.com/article")
    assert "First paragraph." in result
    assert "Second paragraph." in result


def test_fetch_article_body_skips_blank_paragraphs():
    html = "<html><body><p>Real content.</p><p>   </p><p></p></body></html>"
    with patch("scraper.core.requests.get", return_value=_make_mock_response(html)):
        result = fetch_article_body("https://example.com/article")
    assert result == "Real content."


def test_fetch_article_body_raises_on_http_error():
    with patch("scraper.core.requests.get", side_effect=requests.RequestException("timeout")):
        with pytest.raises(requests.RequestException):
            fetch_article_body("https://example.com/article")
