import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pprint import pprint

from src.processing.email_validator import (
    validate_email,
)


TEST_EMAILS = [
    "john.smith@techvision.com",
    "SARAH.JOHNSON@CLOUDWORKS.COM",
    "invalid-email",
    "someone@gmail.com",
    "test@mailinator.com",
]


for email in TEST_EMAILS:

    print()
    print("=" * 60)
    print(email)
    print("=" * 60)

    result = validate_email(email)

    pprint(result)