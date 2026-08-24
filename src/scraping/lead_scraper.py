from src.database.scrape_run_repository import (
    ScrapeRunRepository,
)
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
        run_repository: ScrapeRunRepository | None = None,
    ):
        self.start_url = start_url

        self.http_client = (
            http_client
            if http_client is not None
            else HTTPClient()
        )

        self.run_repository = (
            run_repository
            if run_repository is not None
            else ScrapeRunRepository()
        )

    def scrape_all(self) -> list[dict]:

        run_id = self.run_repository.create_run()

        print(
            f"[SCRAPER] Started run: {run_id}"
        )

        current_url = self.start_url

        all_leads = []

        page_number = 1

        pages_attempted = 0
        pages_succeeded = 0

        try:

            while current_url:

                pages_attempted += 1

                print(
                    f"[SCRAPER] Processing page "
                    f"{page_number}"
                )

                page_id = (
                    self.run_repository.create_page(
                        run_id,
                        page_number,
                        current_url,
                    )
                )

                try:

                    html = self.http_client.get(
                        current_url
                    )

                    leads = parse_leads(html)

                    next_url = find_next_page(
                        html,
                        current_url,
                    )

                    all_leads.extend(leads)

                    pages_succeeded += 1

                    self.run_repository.update_page(
                        page_id,
                        status="completed",
                        records_extracted=len(
                            leads
                        ),
                    )

                    print(
                        f"[SCRAPER] Page "
                        f"{page_number} → "
                        f"{len(leads)} records"
                    )

                    current_url = next_url

                    page_number += 1

                except Exception as exc:

                    self.run_repository.update_page(
                        page_id,
                        status="failed",
                        error_message=str(exc),
                    )

                    raise

            self.run_repository.update_run(
                run_id,
                status="completed",
                pages_attempted=pages_attempted,
                pages_succeeded=pages_succeeded,
                records_extracted=len(
                    all_leads
                ),
            )

            print(
                f"[SCRAPER] Run completed: "
                f"{run_id}"
            )

            return all_leads

        except Exception as exc:

            self.run_repository.update_run(
                run_id,
                status="failed",
                pages_attempted=pages_attempted,
                pages_succeeded=pages_succeeded,
                records_extracted=len(
                    all_leads
                ),
                error_message=str(exc),
            )

            print(
                f"[SCRAPER] Run failed: "
                f"{run_id}"
            )

            raise