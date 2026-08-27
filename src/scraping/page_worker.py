from dataclasses import dataclass


@dataclass
class PageJob:
    page_number: int
    page_url: str


@dataclass
class PageResult:
    page_number: int
    page_url: str
    records: list[dict]
