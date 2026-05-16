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
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
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
