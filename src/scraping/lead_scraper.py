from src.database.lead_repository import LeadRepository
from src.database.scrape_run_repository import ScrapeRunRepository
from src.processing.lead_processor import LeadProcessor
from src.processing.lead_validator import validate_lead
from src.scraping.http_client import HTTPClient
from src.scraping.lead_parser import find_next_page, parse_leads
from src.scraping.page_worker import PageJob
from src.scraping.concurrent_runner import ConcurrentPageRunner


class LeadScraper:

    def __init__(
        self,
        start_url: str,
        http_client: HTTPClient | None = None,
        run_repository: ScrapeRunRepository | None = None,
        lead_repository: LeadRepository | None = None,
        processor: LeadProcessor | None = None,
        max_workers: int = 3,
    ):
        self.start_url = start_url
        self.http_client = http_client if http_client is not None else HTTPClient()
        self.run_repository = run_repository if run_repository is not None else ScrapeRunRepository()
        self.lead_repository = lead_repository if lead_repository is not None else LeadRepository()
        self.processor = processor if processor is not None else LeadProcessor()
        
        # Connect existing http_client.get to the runner
        self.concurrent_runner = ConcurrentPageRunner(
            http_get=self.http_client.get,
            max_workers=max_workers,
        )

    def scrape_all(self) -> list[dict]:
        run_id = self.run_repository.create_run()
        print(f"[SCRAPER] Started run: {run_id}")

        all_leads = []
        pages_attempted = 0
        pages_succeeded = 0

        try:
            # 1. Page Link Discovery Phase (or pre-generate known page URLs)
            # Fetch target page URLs to build jobs array
            discovered_urls = []
            curr_url = self.start_url
            
            while curr_url:
                discovered_urls.append(curr_url)
                # Fetch minimal header/page to discover next page if dynamic
                html = self.http_client.get(curr_url)
                curr_url = find_next_page(html, curr_url)

            # 2. Build jobs for Concurrent Acquisition
            jobs = [
                PageJob(page_number=idx + 1, page_url=url)
                for idx, url in enumerate(discovered_urls)
            ]

            # 3. Concurrent Page Acquisition Phase
            print(f"[SCRAPER] Fetching {len(jobs)} pages concurrently...")
            results = self.concurrent_runner.run(jobs)

            # 4. Sequential Processing, Validation & Persistence Phase
            for result in results:
                pages_attempted += 1
                page_number = result.page_number
                
                print(f"[SCRAPER] Processing results for page {page_number}")
                page_id = self.run_repository.create_page(
                    run_id, page_number, result.page_url
                )

                if result.error:
                    print(f"[SCRAPER] Page {page_number} failed: {result.error}")
                    self.run_repository.update_page(
                        page_id,
                        status="failed",
                        error_message=str(result.error),
                    )
                    continue

                try:
                    leads = parse_leads(result.html)
                    page_processed_leads = []

                    for raw_lead in leads:
                        processed = self.processor.process(raw_lead)
                        normalized_lead = processed["lead"]

                        is_valid, errors = validate_lead(normalized_lead)
                        if not is_valid:
                            print(f"[LEAD] Validation failed: {errors}")
                            continue

                        email_val = processed["email_validation"]
                        qual = processed["quality"]

                        print(
                            f"[QUALITY] {normalized_lead.get('email')} | "
                            f"{email_val['status']} | "
                            f"score={qual['score']} | "
                            f"{qual['quality']}"
                        )

                        lead_id = self.lead_repository.upsert_lead(
                            processed,
                            source_id=None,
                            run_id=run_id,
                        )

                        print(f"[LEAD] Stored: {lead_id}")
                        page_processed_leads.append(normalized_lead)

                    all_leads.extend(page_processed_leads)
                    pages_succeeded += 1

                    self.run_repository.update_page(
                        page_id,
                        status="completed",
                        records_extracted=len(leads),
                    )

                    print(
                        f"[SCRAPER] Page {page_number} -> "
                        f"{len(page_processed_leads)} valid records processed"
                    )

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
                records_extracted=len(all_leads),
            )

            print(f"[SCRAPER] Run completed: {run_id}")
            return all_leads

        except Exception as exc:
            self.run_repository.update_run(
                run_id,
                status="failed",
                pages_attempted=pages_attempted,
                pages_succeeded=pages_succeeded,
                records_extracted=len(all_leads),
                error_message=str(exc),
            )
            print(f"[SCRAPER] Run failed: {run_id}")
            raise