import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.scraping.basic_scraper import scrape_page


def main():
    url = "https://example.com"

    result = scrape_page(url)

    print("Scraping successful!")
    print(result)


if __name__ == "__main__":
    main()