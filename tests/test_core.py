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
