from src.scraping.http_client import HTTPClient
from src.scraping.lead_parser import (
    find_next_page,
    parse_leads,
)


class LeadScraper:

    def __init__(
        self,
        start_url: str,
        http_client: HTTPClient | None = None,
    ):
        self.start_url = start_url

        self.http_client = (
            http_client
            if http_client is not None
            else HTTPClient()
        )

    def scrape_page(
        self,
        url: str,
    ) -> tuple[list[dict], str | None]:

        print(f"[SCRAPER] Fetching: {url}")

        html = self.http_client.get(url)

        leads = parse_leads(html)

        next_url = find_next_page(
            html,
            url,
        )

        return leads, next_url

    def scrape_all(self) -> list[dict]:

        current_url = self.start_url

        all_leads = []

        page_number = 1

        while current_url:

            print(
                f"[SCRAPER] Processing page "
                f"{page_number}"
            )

            leads, next_url = self.scrape_page(
                current_url
            )

            print(
                f"[SCRAPER] Extracted "
                f"{len(leads)} records"
            )

            all_leads.extend(leads)

            current_url = next_url

            page_number += 1

        print(
            f"[SCRAPER] Finished. "
            f"Total records: {len(all_leads)}"
        )

        return all_leads