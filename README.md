# News Scraper

Scrape and summarize news articles on any topic — no Python required.

## Download

Grab the latest binary from the [Releases page](https://github.com/mfmatozza/news-scraper/releases/latest):

| Platform | File |
|---|---|
| Windows | `news-scraper-windows.exe` |
| macOS (Apple Silicon) | `news-scraper-macos` |

**macOS first run:** macOS blocks unsigned binaries from the internet. Run once:
```bash
xattr -d com.apple.quarantine news-scraper-macos
chmod +x news-scraper-macos
```

## Usage

```bash
# Windows
.\news-scraper-windows.exe --topic "artificial intelligence" --articles 5

# macOS
./news-scraper-macos --topic "artificial intelligence" --articles 5
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--topic` | required | Topic to search for |
| `--articles` | 5 | Number of articles to fetch |
| `--sentences` | 3 | Sentences per summary |
| `--save` | off | Save output to a `.txt` file |
| `--output-dir` | `.` | Directory for the saved file |

## Build from Source

Requires Python 3.10+.

```bash
git clone https://github.com/mfmatozza/news-scraper.git
cd news-scraper
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt_tab')"
python news_scraper.py --topic "tech" --articles 5
```

## Run Tests

```bash
pytest tests/ -v
```
