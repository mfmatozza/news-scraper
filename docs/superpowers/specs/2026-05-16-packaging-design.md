# News Scraper — Packaging & Distribution Design Spec

**Date:** 2026-05-16  
**Status:** Approved

---

## Overview

Package the existing news scraper CLI as standalone binaries for Windows and macOS — no Python installation required. GitHub Actions builds and publishes the binaries automatically when a git tag is pushed.

---

## Files Added

| File | Purpose |
|---|---|
| `pyproject.toml` | Package metadata (name, version, author, dependencies) |
| `news_scraper.spec` | PyInstaller build spec (single-file, bundles all deps + NLTK data) |
| `.gitignore` | Ignores `dist/`, `build/`, `__pycache__/`, `*.txt` output files |
| `README.md` | Download instructions, usage, build-from-source guide |
| `.github/workflows/release.yml` | CI workflow: build on tag push, publish to GitHub Releases |

No changes to existing source code (`news_scraper.py`, `scraper/`, `tests/`).

---

## Release Workflow

**Trigger:** `git tag v1.0.0 && git push origin v1.0.0`

**Parallel jobs:**
- `windows-latest` → `news-scraper-windows.exe`
- `macos-latest` → `news-scraper-macos`

**Each job:**
1. Checkout repo
2. Set up Python 3.12
3. `pip install -r requirements.txt pyinstaller`
4. Download NLTK punkt_tab data (required by sumy)
5. `pyinstaller news_scraper.spec`
6. Upload binary as GitHub Release asset

**Result:** A GitHub Release page with two downloadable files attached.

---

## PyInstaller Spec

- Mode: `--onefile` (single executable, no folder structure)
- Entry point: `news_scraper.py`
- Hidden imports: `feedparser`, `bs4`, `sumy`, `lxml`, `nltk`, `requests`
- Data files: NLTK `punkt_tab` tokenizer data bundled into the binary
- Output names: `news-scraper-windows` (Windows runner renames to `.exe`), `news-scraper-macos`

---

## README Sections

1. **What it does** — 2-sentence description
2. **Download** — link to GitHub Releases page, instructions per OS
3. **Usage** — `./news-scraper --topic "AI" --articles 5 --sentences 3`
4. **Build from source** — `pip install -r requirements.txt` + `python news_scraper.py`

---

## .gitignore Additions

```
dist/
build/
__pycache__/
*.pyc
.pytest_cache/
news_*.txt
```

---

## End-User Experience

**Windows:**
1. Download `news-scraper-windows.exe` from GitHub Releases
2. Open terminal, `cd` to download folder
3. Run: `.\news-scraper-windows.exe --topic "tech" --articles 5`

**macOS:**
1. Download `news-scraper-macos`
2. `chmod +x news-scraper-macos`
3. Run: `./news-scraper-macos --topic "tech" --articles 5`
