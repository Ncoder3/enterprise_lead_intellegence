import sys
from pathlib import Path

# Adds project root (enterprise-lead-intelligence) to Python search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pprint import pprint

from src.processing.lead_identity import (
    build_identity_key,
    build_normalized_full_name,
)


leads = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@techvision.com",
        "domain": "techvision.com",
    },
    {
        "first_name": "JOHN",
        "last_name": "SMITH",
        "email": "JOHN.SMITH@TECHVISION.COM",
        "domain": "TECHVISION.COM",
    },
]


for lead in leads:

    print("=" * 60)

    pprint(
        {
            "name":
                build_normalized_full_name(
                    lead
                ),

            "identity_key":
                build_identity_key(
                    lead
                ),
        }
    )