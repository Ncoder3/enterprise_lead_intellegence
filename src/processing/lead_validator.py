import re


EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def validate_email(
    email: str | None,
) -> bool:

    if not email:
        return False

    return bool(
        EMAIL_PATTERN.match(email)
    )


def validate_employee_count(
    employee_count,
) -> bool:

    if employee_count is None:
        return True

    return (
        isinstance(
            employee_count,
            int,
        )
        and employee_count >= 0
    )


def validate_lead(
    lead: dict,
) -> tuple[bool, list[str]]:

    errors = []

    if not validate_email(
        lead.get("email")
    ):
        errors.append(
            "Invalid email address"
        )

    if not validate_employee_count(
        lead.get("employee_count")
    ):
        errors.append(
            "Invalid employee count"
        )

    return (
        len(errors) == 0,
        errors,
    )