def calculate_data_quality(
    lead: dict,
    email_validation: dict,
) -> dict:

    score = 0
    issues = []

    # -------------------------
    # Identity
    # -------------------------

    if lead.get("first_name"):
        score += 10
    else:
        issues.append(
            "missing_first_name"
        )

    if lead.get("last_name"):
        score += 10
    else:
        issues.append(
            "missing_last_name"
        )

    # -------------------------
    # Contact
    # -------------------------

    if email_validation.get(
        "syntax_valid"
    ):
        score += 15
    else:
        issues.append(
            "invalid_email_syntax"
        )

    if email_validation.get(
        "mx_valid"
    ):
        score += 15
    else:
        issues.append(
            "email_domain_not_verified"
        )

    # -------------------------
    # Company
    # -------------------------

    if lead.get("company_name"):
        score += 15
    else:
        issues.append(
            "missing_company"
        )

    if lead.get("domain"):
        score += 10
    else:
        issues.append(
            "missing_domain"
        )

    if lead.get("industry"):
        score += 5

    if lead.get("country"):
        score += 5

    if lead.get("job_title"):
        score += 10
    else:
        issues.append(
            "missing_job_title"
        )

    # -------------------------
    # Email quality
    # -------------------------

    if email_validation.get(
        "is_disposable"
    ):
        score -= 30

        issues.append(
            "disposable_email"
        )

    if email_validation.get(
        "is_free_provider"
    ):
        score -= 10

        issues.append(
            "free_email_provider"
        )

    score = max(
        0,
        min(score, 100),
    )

    if score >= 85:
        quality = "excellent"

    elif score >= 70:
        quality = "good"

    elif score >= 50:
        quality = "fair"

    else:
        quality = "poor"

    return {
        "score": score,
        "quality": quality,
        "issues": issues,
    }