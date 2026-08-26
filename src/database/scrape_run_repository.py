from datetime import datetime
from uuid import UUID

from src.database.connection import get_connection
from src.database.run_metrics_repository import (
    RunMetricsRepository,
)


class ScrapeRunRepository:

    def create_run(
        self,
        source_id: UUID | None = None,
    ) -> UUID:

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scrape_runs (
                        source_id,
                        status
                    )
                    VALUES (
                        %s,
                        'running'
                    )
                    RETURNING run_id;
                    """,
                    (source_id,),
                )

                run_id = cursor.fetchone()[0]

            # Commit immediately so the run_id is saved globally in PostgreSQL
            connection.commit()

        finally:
            connection.close()

        # Initialize metrics using a separate connection after the parent transaction is committed
        metrics_repository = RunMetricsRepository()
        metrics_repository.initialize(run_id)

        return run_id

    def update_run(
        self,
        run_id: UUID,
        *,
        status: str,
        pages_attempted: int,
        pages_succeeded: int,
        records_extracted: int,
        records_failed: int = 0,
        error_message: str | None = None,
    ) -> None:

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE scrape_runs
                    SET
                        finished_at = NOW(),
                        status = %s,
                        pages_attempted = %s,
                        pages_succeeded = %s,
                        records_extracted = %s,
                        records_failed = %s,
                        error_message = %s
                    WHERE run_id = %s;
                    """,
                    (
                        status,
                        pages_attempted,
                        pages_succeeded,
                        records_extracted,
                        records_failed,
                        error_message,
                        run_id,
                    ),
                )

            connection.commit()

        finally:
            connection.close()

    def create_page(
        self,
        run_id: UUID,
        page_number: int,
        page_url: str,
    ) -> UUID:

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scrape_pages (
                        run_id,
                        page_number,
                        page_url,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        'running'
                    )
                    RETURNING page_id;
                    """,
                    (
                        run_id,
                        page_number,
                        page_url,
                    ),
                )

                page_id = cursor.fetchone()[0]

            connection.commit()

            return page_id

        finally:
            connection.close()

    def update_page(
        self,
        page_id: UUID,
        *,
        status: str,
        records_extracted: int = 0,
        error_message: str | None = None,
    ) -> None:

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE scrape_pages
                    SET
                        finished_at = NOW(),
                        status = %s,
                        records_extracted = %s,
                        error_message = %s
                    WHERE page_id = %s;
                    """,
                    (
                        status,
                        records_extracted,
                        error_message,
                        page_id,
                    ),
                )

            connection.commit()

        finally:
            connection.close()