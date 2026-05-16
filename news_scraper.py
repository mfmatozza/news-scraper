import sys
import os

# When running as a PyInstaller bundle, point NLTK to the bundled data directory
if getattr(sys, 'frozen', False):
    import nltk
    nltk.data.path.insert(0, os.path.join(sys._MEIPASS, 'nltk_data'))

import argparse
from datetime import date
from scraper.core import fetch_and_summarize, save_output


def _print_results(results: list[dict], topic: str) -> None:
    today = date.today().isoformat()
    print(f'\n=== News Summary: "{topic}" ({today}) ===\n')
    for i, article in enumerate(results, 1):
        print(f"[{i}] {article['title']}")
        print(f"    Published: {article['published']}")
        print(f"    URL: {article['url']}")
        print(f"    Summary:")
        print(f"      {article['summary']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape and summarize news articles by topic."
    )
    parser.add_argument("--topic", required=True, help="Topic to search for")
    parser.add_argument("--articles", type=int, default=5, help="Number of articles (default: 5)")
    parser.add_argument("--sentences", type=int, default=3, help="Sentences per summary (default: 3)")
    parser.add_argument("--save", action="store_true", help="Save output to a .txt file")
    parser.add_argument("--output-dir", default=".", help="Directory for saved file (default: .)")
    args = parser.parse_args()

    print(f'\nFetching news for: "{args.topic}"...\n')
    results = fetch_and_summarize(args.topic, args.articles, args.sentences)
    _print_results(results, args.topic)
    if args.save:
        path = save_output(results, args.topic, args.output_dir)
        print(f"Output saved to: {path}")


if __name__ == "__main__":
    main()
