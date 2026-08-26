import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uuid import UUID
from src.database.connection import get_connection


class RunMetricsRepository:

    def initialize(
        self,
        run_id: UUID,
    ) -> None:

        connection = get_connection()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO run_metrics (
                        run_id
                    )
                    VALUES (%s)
                    ON CONFLICT (run_id)
                    DO NOTHING;
                    """,
                    (run_id,),
                )

            connection.commit()

        finally:

            connection.close()

    def increment(
        self,
        run_id: UUID,
        field: str,
        amount: int = 1,
    ) -> None:

        allowed_fields = {
            "records_discovered",
            "records_parsed",
            "records_normalized",
            "records_valid",
            "records_invalid",
            "records_inserted",
            "records_updated",
            "duplicates_detected",
            "records_merged",
            "records_reviewed",
            "high_quality_leads",
            "medium_quality_leads",
            "low_quality_leads",
        }

        if field not in allowed_fields:
            raise ValueError(
                f"Invalid metric field: {field}"
            )

        connection = get_connection()

        try:

            with connection.cursor() as cursor:

                query = f"""
                    UPDATE run_metrics
                    SET {field} =
                        {field} + %s
                    WHERE run_id = %s;
                """

                cursor.execute(
                    query,
                    (
                        amount,
                        run_id,
                    ),
                )

            connection.commit()

        finally:

            connection.close()

    def finish(
        self,
        run_id: UUID,
    ) -> None:

        connection = get_connection()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE run_metrics
                    SET finished_at = NOW()
                    WHERE run_id = %s;
                    """,
                    (run_id,),
                )

            connection.commit()

        finally:

            connection.close()