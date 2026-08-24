from uuid import UUID

from src.database.connection import get_connection


class LeadRepository:

    def upsert_lead(
        self,
        lead: dict,
        source_id: UUID | None,
        run_id: UUID,
    ) -> UUID:

        connection = get_connection()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO leads (
                        source_id,
                        run_id,
                        first_name,
                        last_name,
                        job_title,
                        email,
                        company_name,
                        domain,
                        industry,
                        country,
                        employee_count
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s
                    )

                    ON CONFLICT (
                        (LOWER(email))
                    )

                    DO UPDATE SET

                        source_id = EXCLUDED.source_id,

                        run_id = EXCLUDED.run_id,

                        first_name =
                            EXCLUDED.first_name,

                        last_name =
                            EXCLUDED.last_name,

                        job_title =
                            EXCLUDED.job_title,

                        company_name =
                            EXCLUDED.company_name,

                        domain =
                            EXCLUDED.domain,

                        industry =
                            EXCLUDED.industry,

                        country =
                            EXCLUDED.country,

                        employee_count =
                            EXCLUDED.employee_count,

                        last_seen_at = NOW(),

                        updated_at = NOW()

                    RETURNING lead_id;
                    """,
                    (
                        source_id,
                        run_id,
                        lead.get("first_name"),
                        lead.get("last_name"),
                        lead.get("job_title"),
                        lead.get("email"),
                        lead.get("company_name"),
                        lead.get("domain"),
                        lead.get("industry"),
                        lead.get("country"),
                        lead.get("employee_count"),
                    ),
                )

                lead_id = cursor.fetchone()[0]

            connection.commit()

            return lead_id

        finally:

            connection.close()