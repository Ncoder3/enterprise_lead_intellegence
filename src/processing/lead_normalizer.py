import re


def clean_text(value: str | None) -> str | None:

    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def normalize_email(
    email: str | None,
) -> str | None:

    email = clean_text(email)

    if email is None:
        return None

    return email.lower()


def normalize_domain(
    domain: str | None,
) -> str | None:

    domain = clean_text(domain)

    if domain is None:
        return None

    domain = domain.lower()

    domain = domain.removeprefix(
        "https://"
    )

    domain = domain.removeprefix(
        "http://"
    )

    domain = domain.removeprefix(
        "www."
    )

    domain = domain.rstrip("/")

    return domain


def normalize_name(
    name: str | None,
) -> str | None:

    name = clean_text(name)

    if name is None:
        return None

    return name.title()


def normalize_lead(
    lead: dict,
) -> dict:

    normalized = {
        "first_name": normalize_name(
            lead.get("first_name")
        ),

        "last_name": normalize_name(
            lead.get("last_name")
        ),

        "job_title": clean_text(
            lead.get("job_title")
        ),

        "email": normalize_email(
            lead.get("email")
        ),

        "company_name": clean_text(
            lead.get("company_name")
        ),

        "domain": normalize_domain(
            lead.get("domain")
        ),

        "industry": clean_text(
            lead.get("industry")
        ),

        "country": clean_text(
            lead.get("country")
        ),

        "employee_count": lead.get(
            "employee_count"
        ),
    }

    return normalized