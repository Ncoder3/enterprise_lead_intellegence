import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
sys.path.append(str(Path(__file__).resolve().parents[1]))


from pprint import pprint
from src.scraping.lead_scraper import scrape_lead_page


def main():

    url = "http://127.0.0.1:8000/leads?page=1"

    leads = scrape_lead_page(url)

    print("=" * 70)
    print(f"Records extracted: {len(leads)}")
    print("=" * 70)

    for index, lead in enumerate(leads, start=1):

        print(f"\nLead #{index}")

        pprint(lead)


if __name__ == "__main__":
    main()