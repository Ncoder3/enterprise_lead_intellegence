import re

import dns.resolver


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


FREE_EMAIL_PROVIDERS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "icloud.com",
    "aol.com",
    "proton.me",
    "protonmail.com",
    "mail.com",
    "gmx.com",
}


DISPOSABLE_EMAIL_PROVIDERS = {
    "mailinator.com",
    "10minutemail.com",
    "guerrillamail.com",
    "tempmail.com",
    "throwawaymail.com",
}


def check_email_syntax(
    email: str | None,
) -> bool:

    if not email:
        return False

    return bool(
        EMAIL_PATTERN.fullmatch(email)
    )


def extract_domain(
    email: str,
) -> str:

    return email.rsplit(
        "@",
        1,
    )[1].lower()


def check_mx_records(
    domain: str,
) -> tuple[bool, str]:

    try:

        answers = dns.resolver.resolve(
            domain,
            "MX",
        )

        if answers:

            return (
                True,
                "mx_record_found",
            )

        return (
            False,
            "no_mx_record",
        )

    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):

        return (
            False,
            "mx_lookup_failed",
        )


def is_free_provider(
    domain: str,
) -> bool:

    return domain.lower() in (
        FREE_EMAIL_PROVIDERS
    )


def is_disposable_provider(
    domain: str,
) -> bool:

    return domain.lower() in (
        DISPOSABLE_EMAIL_PROVIDERS
    )


def validate_email(
    email: str | None,
) -> dict:

    result = {
        "email": email,
        "syntax_valid": False,
        "domain": None,
        "mx_valid": False,
        "is_free_provider": False,
        "is_disposable": False,
        "status": "invalid",
        "reason": None,
    }

    if not check_email_syntax(email):

        result["status"] = (
            "invalid_syntax"
        )

        result["reason"] = (
            "Email syntax is invalid"
        )

        return result

    domain = extract_domain(email)

    result["syntax_valid"] = True
    result["domain"] = domain

    if is_disposable_provider(domain):

        result["is_disposable"] = True

        result["status"] = (
            "disposable"
        )

        result["reason"] = (
            "Disposable email provider"
        )

        return result

    result["is_free_provider"] = (
        is_free_provider(domain)
    )

    mx_valid, mx_reason = check_mx_records(
        domain
    )

    result["mx_valid"] = mx_valid

    if not mx_valid:

        result["status"] = (
            "domain_no_mx"
        )

        result["reason"] = mx_reason

        return result

    if result["is_free_provider"]:

        result["status"] = (
            "free_provider"
        )

        result["reason"] = (
            "Free email provider with "
            "valid MX records"
        )

        return result

    result["status"] = (
        "domain_valid"
    )

    result["reason"] = (
        "Syntax and MX validation passed"
    )

    return result