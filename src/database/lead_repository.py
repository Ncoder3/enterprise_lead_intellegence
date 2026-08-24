from uuid import UUID
from src.database.connection import get_connection


class LeadRepository:

    def upsert_lead(
        self,
        processed: dict,
        source_id: UUID | None,
        run_id: UUID,
    ) -> UUID:
        lead = processed["lead"]
        email_validation = processed["email_validation"]
        quality = processed["quality"]
        normalized_full_name = processed["normalized_full_name"]
        identity_key = processed["identity_key"]

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
                        employee_count,
                        normalized_full_name,
                        identity_key,
                        email_validation_status,
                        email_validation_reason,
                        email_mx_valid,
                        email_is_free_provider,
                        email_is_disposable,
                        email_validated_at,
                        lead_quality_score,
                        lead_quality,
                        quality_reasons,
                        data_quality_score,
                        duplicate_status
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, NOW(), %s,
                        %s, %s, %s, %s
                    )
                    ON CONFLICT ((LOWER(email)))
                    DO UPDATE SET
                        source_id = EXCLUDED.source_id,
                        run_id = EXCLUDED.run_id,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        job_title = EXCLUDED.job_title,
                        company_name = EXCLUDED.company_name,
                        domain = EXCLUDED.domain,
                        industry = EXCLUDED.industry,
                        country = EXCLUDED.country,
                        employee_count = EXCLUDED.employee_count,
                        normalized_full_name = EXCLUDED.normalized_full_name,
                        identity_key = EXCLUDED.identity_key,
                        email_validation_status = EXCLUDED.email_validation_status,
                        email_validation_reason = EXCLUDED.email_validation_reason,
                        email_mx_valid = EXCLUDED.email_mx_valid,
                        email_is_free_provider = EXCLUDED.email_is_free_provider,
                        email_is_disposable = EXCLUDED.email_is_disposable,
                        email_validated_at = NOW(),
                        lead_quality_score = EXCLUDED.lead_quality_score,
                        lead_quality = EXCLUDED.lead_quality,
                        quality_reasons = EXCLUDED.quality_reasons,
                        data_quality_score = EXCLUDED.data_quality_score,
                        duplicate_status = EXCLUDED.duplicate_status,
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
                        normalized_full_name,
                        identity_key,
                        email_validation.get("status"),
                        email_validation.get("reason"),
                        email_validation.get("mx_valid"),
                        email_validation.get("is_free_provider"),
                        email_validation.get("is_disposable"),
                        quality.get("score"),
                        quality.get("quality"),
                        quality.get("issues"),
                        quality.get("score"),
                        "unique",
                    ),
                )

                lead_id = cursor.fetchone()[0]

            connection.commit()
            return lead_id

        finally:
            connection.close()