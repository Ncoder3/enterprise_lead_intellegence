from src.processing.data_quality import (
    calculate_data_quality,
)

from src.processing.email_validator import (
    validate_email,
)

from src.processing.lead_identity import (
    build_identity_key,
    build_normalized_full_name,
)

from src.processing.lead_normalizer import (
    normalize_lead,
)


class LeadProcessor:

    def process(
        self,
        raw_lead: dict,
    ) -> dict:

        # -------------------------
        # 1. Normalize
        # -------------------------

        lead = normalize_lead(
            raw_lead
        )

        # -------------------------
        # 2. Validate email
        # -------------------------

        email_validation = (
            validate_email(
                lead.get("email")
            )
        )

        # -------------------------
        # 3. Identity
        # -------------------------

        normalized_full_name = (
            build_normalized_full_name(
                lead
            )
        )

        identity_key = (
            build_identity_key(
                lead
            )
        )

        # -------------------------
        # 4. Quality
        # -------------------------

        quality = (
            calculate_data_quality(
                lead,
                email_validation,
            )
        )

        return {
            "lead": lead,

            "email_validation":
                email_validation,

            "normalized_full_name":
                normalized_full_name,

            "identity_key":
                identity_key,

            "quality":
                quality,
        }