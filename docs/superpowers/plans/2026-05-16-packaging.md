# News Scraper Packaging & Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the news scraper CLI as standalone binaries for Windows and macOS, released automatically to GitHub Releases on every git tag push.

**Architecture:** PyInstaller bundles `news_scraper.py` and all dependencies (including NLTK punkt_tab data) into a single-file executable. A GitHub Actions workflow builds on `windows-latest` and `macos-latest` in parallel, then uploads both binaries to a GitHub Release. No changes to core logic — packaging only.

**Tech Stack:** PyInstaller, GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`, `softprops/action-gh-release@v2`), `pyproject.toml` (setuptools)

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `.gitignore` | Create | Exclude build artifacts and output files |
| `README.md` | Create | Download link, usage, build-from-source guide |
| `pyproject.toml` | Create | Package metadata + console_scripts entry point |
| `news_scraper.py` | Modify (top 5 lines) | Add NLTK data path setup when running as frozen binary |
| `news_scraper.spec` | Create | PyInstaller build config: single-file, bundled NLTK data, hidden imports |
| `.github/workflows/release.yml` | Create | CI: build + publish binaries on `v*` tag push |

---

## Task 1: .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Create `.gitignore`**

```
# Build artifacts
dist/
build/
*.spec.bak

# Python cache
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# News scraper output files
news_*.txt

# IDE
.vscode/
.idea/
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```

---

## Task 2: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

Replace `YOUR_USERNAME` with your actual GitHub username in the two places it appears.

```markdown
# News Scraper

Scrape and summarize news articles on any topic — no Python required.

## Download

Grab the latest binary from the [Releases page](https://github.com/YOUR_USERNAME/news-scraper/releases/latest):

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
git clone https://github.com/YOUR_USERNAME/news-scraper.git
cd news-scraper
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt_tab')"
python news_scraper.py --topic "tech" --articles 5
```

## Run Tests

```bash
pytest tests/ -v
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with download and usage instructions"
```

---

## Task 3: pyproject.toml

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "news-scraper"
version = "1.0.0"
description = "CLI tool to scrape and summarize news articles by topic"
requires-python = ">=3.10"
readme = "README.md"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "feedparser>=6.0.11",
    "sumy>=0.11.0",
    "lxml>=4.9.0",
]

[project.scripts]
news-scraper = "news_scraper:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["scraper*"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml for package metadata"
```

---

## Task 4: Patch news_scraper.py + PyInstaller spec + local build test

**Files:**
- Modify: `news_scraper.py` (add 5 lines at the very top, before any other imports)
- Create: `news_scraper.spec`

- [ ] **Step 1: Patch the top of `news_scraper.py`**

Add these lines as the very first lines of the file, before `import argparse`:

```python
import sys
import os

# When running as a PyInstaller bundle, point NLTK to the bundled data directory
if getattr(sys, 'frozen', False):
    import nltk
    nltk.data.path.insert(0, os.path.join(sys._MEIPASS, 'nltk_data'))

```

The full top of `news_scraper.py` should now look like:

```python
import sys
import os

# When running as a PyInstaller bundle, point NLTK to the bundled data directory
if getattr(sys, 'frozen', False):
    import nltk
    nltk.data.path.insert(0, os.path.join(sys._MEIPASS, 'nltk_data'))

import argparse
from datetime import date
from scraper.core import fetch_and_summarize, save_output
```

- [ ] **Step 2: Run existing tests to confirm no regressions**

```
pytest tests/ -v
```

Expected: 16 passed

- [ ] **Step 3: Install PyInstaller**

```
pip install pyinstaller
```

- [ ] **Step 4: Create `news_scraper.spec`**

```python
import sys
import os
import nltk

# Locate the punkt_tab tokenizer data bundled with sumy
_punkt_tab = None
for _p in nltk.data.path:
    _candidate = os.path.join(_p, 'tokenizers', 'punkt_tab')
    if os.path.exists(_candidate):
        _punkt_tab = _candidate
        break

if _punkt_tab is None:
    raise RuntimeError(
        "punkt_tab not found. Run: python -c \"import nltk; nltk.download('punkt_tab')\""
    )

a = Analysis(
    ['news_scraper.py'],
    pathex=[],
    binaries=[],
    datas=[
        (_punkt_tab, 'nltk_data/tokenizers/punkt_tab'),
    ],
    hiddenimports=[
        'feedparser',
        'bs4',
        'bs4.builder',
        'bs4.builder._lxml',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'lxml.html',
        'sumy',
        'sumy.models',
        'sumy.models.tf',
        'sumy.nlp',
        'sumy.nlp.stemmers',
        'sumy.nlp.tokenizers',
        'sumy.parsers',
        'sumy.parsers.plaintext',
        'sumy.summarizers',
        'sumy.summarizers.lex_rank',
        'requests',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'certifi',
        'charset_normalizer',
        'idna',
        'nltk',
        'nltk.tokenize',
        'nltk.tokenize.punkt',
        'nltk.data',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='news-scraper',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
```

- [ ] **Step 5: Build the binary locally**

```
pyinstaller news_scraper.spec
```

Expected: Creates `dist/news-scraper.exe` (Windows) or `dist/news-scraper` (macOS). Build takes 1-3 minutes.

- [ ] **Step 6: Smoke test the binary**

Windows:
```
.\dist\news-scraper.exe --topic "AI" --articles 2 --sentences 2
```

macOS:
```
./dist/news-scraper --topic "AI" --articles 2 --sentences 2
```

Expected: Two article summaries printed to terminal. No import errors or NLTK data errors.

If you see `LookupError: Resource punkt_tab not found`, the NLTK data wasn't bundled correctly — check that `_punkt_tab` path in the spec printed a valid directory.

- [ ] **Step 7: Commit**

```bash
git add news_scraper.py news_scraper.spec
git commit -m "feat: add PyInstaller spec and frozen-binary NLTK path setup"
```

---

## Task 5: GitHub Actions release workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create `.github/workflows/release.yml`**

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            artifact: news-scraper-windows.exe
          - os: macos-latest
            artifact: news-scraper-macos

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt pyinstaller

      - name: Download NLTK punkt_tab data
        run: python -c "import nltk; nltk.download('punkt_tab')"

      - name: Build binary
        run: pyinstaller news_scraper.spec

      - name: Rename binary
        shell: bash
        run: |
          if [ "$RUNNER_OS" == "Windows" ]; then
            mv "dist/news-scraper.exe" "dist/${{ matrix.artifact }}"
          else
            mv "dist/news-scraper" "dist/${{ matrix.artifact }}"
          fi

      - name: Upload to GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: dist/${{ matrix.artifact }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add GitHub Actions release workflow for Windows and macOS binaries"
```

---

## Task 6: Push to GitHub and cut the first release

- [ ] **Step 1: Create a new GitHub repository**

Go to https://github.com/new and create a repository named `news-scraper`. Leave it empty (no README, no .gitignore — we have our own).

- [ ] **Step 2: Add the remote and push**

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/news-scraper.git
git branch -M main
git push -u origin main
```

Expected: all commits appear on GitHub.

- [ ] **Step 3: Push a release tag**

```bash
git tag v1.0.0
git push origin v1.0.0
```

Expected: GitHub Actions starts two jobs (Windows + macOS) visible at `https://github.com/YOUR_USERNAME/news-scraper/actions`.

- [ ] **Step 4: Verify the release**

Wait ~5 minutes for both jobs to complete. Then check:

```
https://github.com/YOUR_USERNAME/news-scraper/releases/tag/v1.0.0
```

Expected: Release page shows two downloadable files:
- `news-scraper-windows.exe`
- `news-scraper-macos`

- [ ] **Step 5: Update README with the real repo URL**

Open `README.md` and replace both occurrences of `YOUR_USERNAME` with your actual GitHub username. Then:

```bash
git add README.md
git commit -m "docs: update README with real GitHub repo URL"
git push origin main
```
