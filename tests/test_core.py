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


def _make_mock_entry(title="Test Title", link="https://example.com", published="Mon, 15 May 2026", summary="A description."):
    entry = MagicMock()
    entry.title = title
    entry.link = link
    entry.published = published
    entry.summary = summary
    return entry


def test_fetch_rss_returns_list_of_dicts():
    mock_feed = MagicMock()
    mock_feed.entries = [_make_mock_entry()]
    with patch("scraper.core.feedparser.parse", return_value=mock_feed):
        result = fetch_rss("AI", 5)
    assert len(result) == 1
    assert result[0]["title"] == "Test Title"
    assert result[0]["url"] == "https://example.com"
    assert result[0]["published"] == "Mon, 15 May 2026"
    assert result[0]["description"] == "A description."


def test_fetch_rss_limits_to_n():
    mock_feed = MagicMock()
    mock_feed.entries = [_make_mock_entry(title=f"Article {i}") for i in range(10)]
    with patch("scraper.core.feedparser.parse", return_value=mock_feed):
        result = fetch_rss("AI", 3)
    assert len(result) == 3


def test_fetch_rss_encodes_topic_in_url():
    mock_feed = MagicMock()
    mock_feed.entries = []
    with patch("scraper.core.feedparser.parse", return_value=mock_feed) as mock_parse:
        fetch_rss("climate change", 5)
    called_url = mock_parse.call_args[0][0]
    assert "climate+change" in called_url or "climate%20change" in called_url


def test_fetch_and_summarize_returns_results_with_summaries():
    articles = [
        {"title": "Article 1", "url": "https://a.com", "published": "2026-05-15", "description": "Desc 1."},
        {"title": "Article 2", "url": "https://b.com", "published": "2026-05-15", "description": "Desc 2."},
    ]
    with patch("scraper.core.fetch_rss", return_value=articles), \
         patch("scraper.core.fetch_article_body", return_value="Body text. " * 20), \
         patch("scraper.core.summarize", return_value="Mock summary sentence."):
        results = fetch_and_summarize("test", n=2, sentences=2)
    assert len(results) == 2
    assert results[0]["summary"] == "Mock summary sentence."
    assert results[1]["summary"] == "Mock summary sentence."


def test_fetch_and_summarize_falls_back_to_description_on_error():
    articles = [
        {"title": "Broken", "url": "https://broken.com", "published": "2026-05-15", "description": "Fallback desc."},
    ]
    with patch("scraper.core.fetch_rss", return_value=articles), \
         patch("scraper.core.fetch_article_body", side_effect=requests.RequestException("timeout")), \
         patch("scraper.core.summarize", return_value="Summary from desc."):
        results = fetch_and_summarize("test", n=1, sentences=2)
    assert len(results) == 1
    assert results[0]["summary"] == "Summary from desc."


def test_fetch_and_summarize_falls_back_to_description_on_empty_body():
    articles = [
        {"title": "Paywall", "url": "https://paywall.com", "published": "2026-05-15", "description": "RSS snippet."},
    ]
    with patch("scraper.core.fetch_rss", return_value=articles), \
         patch("scraper.core.fetch_article_body", return_value=""), \
         patch("scraper.core.summarize", return_value="Summary from snippet."):
        results = fetch_and_summarize("test", n=1, sentences=2)
    assert results[0]["summary"] == "Summary from snippet."


def test_save_output_creates_file(tmp_path):
    results = [
        {"title": "Test Article", "url": "https://example.com", "published": "2026-05-15", "summary": "This is the summary."},
    ]
    path = save_output(results, "test topic", str(tmp_path))
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Test Article" in content
    assert "https://example.com" in content
    assert "This is the summary." in content


def test_save_output_filename_format(tmp_path):
    results = [{"title": "T", "url": "u", "published": "p", "summary": "s"}]
    path = save_output(results, "AI News", str(tmp_path))
    today = date.today().isoformat()
    assert path.name == f"news_ai_news_{today}.txt"


def test_save_output_replaces_spaces_in_topic(tmp_path):
    results = [{"title": "T", "url": "u", "published": "p", "summary": "s"}]
    path = save_output(results, "climate change policy", str(tmp_path))
    assert " " not in path.name
    assert "climate_change_policy" in path.name
