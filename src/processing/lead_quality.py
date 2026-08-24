def calculate_lead_quality(
    lead: dict,
    email_validation: dict,
) -> dict:

    score = 0
    reasons = []

    # Email
    if email_validation.get(
        "syntax_valid"
    ):
        score += 20
    else:
        reasons.append(
            "Invalid email syntax"
        )

    if email_validation.get(
        "mx_valid"
    ):
        score += 25
    else:
        reasons.append(
            "No valid MX confirmation"
        )

    if not email_validation.get(
        "is_disposable"
    ):
        score += 10
    else:
        reasons.append(
            "Disposable email"
        )

    if not email_validation.get(
        "is_free_provider"
    ):
        score += 10
    else:
        reasons.append(
            "Free email provider"
        )

    # Person information
    if lead.get("first_name"):
        score += 5
    else:
        reasons.append(
            "Missing first name"
        )

    if lead.get("last_name"):
        score += 5
    else:
        reasons.append(
            "Missing last name"
        )

    if lead.get("job_title"):
        score += 10
    else:
        reasons.append(
            "Missing job title"
        )

    # Company information
    if lead.get("company_name"):
        score += 5
    else:
        reasons.append(
            "Missing company name"
        )

    if lead.get("domain"):
        score += 5
    else:
        reasons.append(
            "Missing company domain"
        )

    if lead.get("industry"):
        score += 3

    if lead.get("country"):
        score += 2

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
        "reasons": reasons,
    }