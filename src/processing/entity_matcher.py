from rapidfuzz import fuzz


def normalize_text(
    value: str | None,
) -> str:

    if not value:
        return ""

    return (
        value
        .lower()
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace(".", "")
    )


def name_similarity(
    name_a: str | None,
    name_b: str | None,
) -> float:

    a = normalize_text(name_a)
    b = normalize_text(name_b)

    if not a or not b:
        return 0.0

    return float(
        fuzz.ratio(a, b)
    )


def exact_match(
    value_a: str | None,
    value_b: str | None,
) -> bool:

    if not value_a or not value_b:
        return False

    return (
        normalize_text(value_a)
        == normalize_text(value_b)
    )


def calculate_match_score(
    incoming: dict,
    existing: dict,
) -> dict:

    score = 0
    reasons = []

    # -------------------------------------------------
    # Exact email
    # -------------------------------------------------

    if exact_match(
        incoming.get("email"),
        existing.get("email"),
    ):

        score += 100

        reasons.append(
            "exact_email_match"
        )

        return {
            "score": score,
            "confidence": "high",
            "reasons": reasons,
        }

    # -------------------------------------------------
    # Name
    # -------------------------------------------------

    incoming_name = (
        f"{incoming.get('first_name', '')}"
        f"{incoming.get('last_name', '')}"
    )

    existing_name = (
        f"{existing.get('first_name', '')}"
        f"{existing.get('last_name', '')}"
    )

    similarity = name_similarity(
        incoming_name,
        existing_name,
    )

    if similarity >= 95:

        score += 30

        reasons.append(
            "very_strong_name_match"
        )

    elif similarity >= 85:

        score += 20

        reasons.append(
            "strong_name_match"
        )

    elif similarity >= 70:

        score += 10

        reasons.append(
            "possible_name_match"
        )

    # -------------------------------------------------
    # Company domain
    # -------------------------------------------------

    if exact_match(
        incoming.get("domain"),
        existing.get("domain"),
    ):

        score += 30

        reasons.append(
            "same_company_domain"
        )

    # -------------------------------------------------
    # Company name
    # -------------------------------------------------

    company_similarity = name_similarity(
        incoming.get("company_name"),
        existing.get("company_name"),
    )

    if company_similarity >= 95:

        score += 20

        reasons.append(
            "very_strong_company_match"
        )

    elif company_similarity >= 85:

        score += 15

        reasons.append(
            "strong_company_match"
        )

    elif company_similarity >= 70:

        score += 8

        reasons.append(
            "possible_company_match"
        )

    # -------------------------------------------------
    # Job title
    # -------------------------------------------------

    if exact_match(
        incoming.get("job_title"),
        existing.get("job_title"),
    ):

        score += 5

        reasons.append(
            "same_job_title"
        )

    # -------------------------------------------------
    # Confidence
    # -------------------------------------------------

    if score >= 90:

        confidence = "high"

    elif score >= 70:

        confidence = "probable"

    elif score >= 50:

        confidence = "review"

    else:

        confidence = "low"

    return {
        "score": score,
        "confidence": confidence,
        "reasons": reasons,
    }