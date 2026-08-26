import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pprint import pprint

from src.config.logging_config import configure_logging
from src.scraping.lead_scraper import LeadScraper
from src.processing.lead_processor import LeadProcessor
from src.database.scrape_run_repository import ScrapeRunRepository
from src.database.lead_repository import LeadRepository
from src.database.run_metrics_repository import RunMetricsRepository


def main():
    configure_logging()

    start_url = "http://127.0.0.1:8000/leads?page=1"

    # Initialize components and repositories
    scraper = LeadScraper(start_url=start_url)
    processor = LeadProcessor()
    lead_repository = LeadRepository()
    scrape_run_repository = ScrapeRunRepository()
    metrics = RunMetricsRepository()

    # 1. Create scrape run (this automatically initializes run_metrics via ScrapeRunRepository)
    run_id = scrape_run_repository.create_run(source_id=None)
    
    pages_attempted = 0
    pages_succeeded = 0
    records_extracted_total = 0
    records_failed_total = 0

    try:
        leads = scraper.scrape_all()
        
        records_discovered_count = len(leads)
        metrics.increment(run_id, "records_discovered", records_discovered_count)
        records_extracted_total = records_discovered_count
        pages_attempted = 1
        pages_succeeded = 1

        print()
        print("=" * 70)
        print(f"PROCESSING LEADS FOR RUN ID: {run_id}")
        print("=" * 70)
        print(f"Total leads discovered: {records_discovered_count}")

        # Process each lead through pipeline & increment metrics
        for index, raw_lead in enumerate(leads, start=1):
            try:
                # 1. Process (Normalization, Validation, Quality, Identity)
                processed = processor.process(raw_lead)
                metrics.increment(run_id, "records_normalized")

                # 2. Validation check
                is_valid = processed.get("is_valid", False)
                if is_valid:
                    metrics.increment(run_id, "records_valid")
                else:
                    metrics.increment(run_id, "records_invalid")
                    continue  # Skip invalid records from persistence/quality steps

                # 3. Quality breakdown metrics
                quality_data = processed.get("quality", {})
                quality_level = quality_data.get("quality", "low")

                if quality_level == "excellent":
                    metrics.increment(run_id, "high_quality_leads")
                elif quality_level == "good":
                    metrics.increment(run_id, "medium_quality_leads")
                else:
                    metrics.increment(run_id, "low_quality_leads")

                # 4. Entity Resolution decision hook (defaulting to unique unless handled)
                decision = "unique"  # Change to "merge" or "review" if using your entity resolution module

                if decision == "merge":
                    metrics.increment(run_id, "duplicates_detected")
                    metrics.increment(run_id, "records_merged")
                elif decision == "review":
                    metrics.increment(run_id, "duplicates_detected")
                    metrics.increment(run_id, "records_reviewed")

                # 5. Database Upsert & Operation Metric Tracking
                operation = lead_repository.upsert_lead(
                    processed=processed,
                    source_id=None,
                    run_id=run_id
                )

                if operation == "inserted":
                    metrics.increment(run_id, "records_inserted")
                elif operation == "updated":
                    metrics.increment(run_id, "records_updated")

            except Exception as lead_err:
                records_failed_total += 1
                print(f"Error processing lead #{index}: {lead_err}")

        # Update final run state status to completed
        scrape_run_repository.update_run(
            run_id=run_id,
            status="completed",
            pages_attempted=pages_attempted,
            pages_succeeded=pages_succeeded,
            records_extracted=records_extracted_total,
            records_failed=records_failed_total
        )

        print()
        print("=" * 70)
        print("FINAL RESULTS & METRICS POPULATED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        scrape_run_repository.update_run(
            run_id=run_id,
            status="failed",
            pages_attempted=pages_attempted,
            pages_succeeded=pages_succeeded,
            records_extracted=records_extracted_total,
            records_failed=records_failed_total,
            error_message=str(e)
        )
        raise

    finally:
        metrics.finish(run_id)


if __name__ == "__main__":
    main()