from dataclasses import dataclass
from typing import Callable


@dataclass
class PageJob:
    page_number: int
    page_url: str


@dataclass
class PageResult:
    page_number: int
    page_url: str
    html: str | None = None
    error: Exception | None = None


def fetch_page(
    job: PageJob,
    http_get: Callable[[str], str],
) -> PageResult:

    try:
        html = http_get(job.page_url)

        return PageResult(
            page_number=job.page_number,
            page_url=job.page_url,
            html=html,
        )

    except Exception as exc:

        return PageResult(
            page_number=job.page_number,
            page_url=job.page_url,
            error=exc,
        )