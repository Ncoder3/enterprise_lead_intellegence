import hashlib


def normalize_identity_text(
    value: str | None,
) -> str:

    if not value:
        return ""

    return (
        value
        .strip()
        .lower()
        .replace(" ", "")
    )


def build_normalized_full_name(
    lead: dict,
) -> str:

    first_name = normalize_identity_text(
        lead.get("first_name")
    )

    last_name = normalize_identity_text(
        lead.get("last_name")
    )

    return f"{first_name}{last_name}"


def build_identity_key(
    lead: dict,
) -> str:

    email = normalize_identity_text(
        lead.get("email")
    )

    domain = normalize_identity_text(
        lead.get("domain")
    )

    full_name = build_normalized_full_name(
        lead
    )

    if email:
        raw_key = f"email:{email}"

    elif full_name and domain:
        raw_key = (
            f"name_domain:"
            f"{full_name}:{domain}"
        )

    elif full_name:
        raw_key = f"name:{full_name}"

    else:
        raw_key = (
            f"unknown:"
            f"{lead.get('company_name', '')}"
        )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()