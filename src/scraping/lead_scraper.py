from src.database.lead_repository import LeadRepository
from src.database.scrape_run_repository import (
    ScrapeRunRepository,
)
from src.processing.lead_normalizer import normalize_lead
from src.processing.lead_validator import validate_lead
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
        lead_repository: LeadRepository | None = None,
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

        self.lead_repository = (
            lead_repository
            if lead_repository is not None
            else LeadRepository()
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

                    page_processed_leads = []

                    for raw_lead in leads:

                        normalized_lead = normalize_lead(
                            raw_lead
                        )

                        is_valid, errors = validate_lead(
                            normalized_lead
                        )

                        if not is_valid:

                            print(
                                f"[LEAD] Validation failed: "
                                f"{errors}"
                            )

                            continue

                        lead_id = (
                            self.lead_repository.upsert_lead(
                                normalized_lead,
                                source_id=None,
                                run_id=run_id,
                            )
                        )

                        print(
                            f"[LEAD] Stored: {lead_id}"
                        )

                        page_processed_leads.append(normalized_lead)

                    all_leads.extend(page_processed_leads)

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
                        f"{len(page_processed_leads)} valid records processed"
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