import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from pprint import pprint

from src.config.logging_config import (
    configure_logging,
)
from src.scraping.lead_scraper import LeadScraper


def main():

    configure_logging()

    start_url = (
        "http://127.0.0.1:8000/leads?page=1"
    )

    scraper = LeadScraper(
        start_url=start_url
    )

    leads = scraper.scrape_all()

    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(
        f"Total leads extracted: {len(leads)}"
    )

    for index, lead in enumerate(
        leads,
        start=1,
    ):

        print()
        print(f"Lead #{index}")

        pprint(lead)


if __name__ == "__main__":
    main()