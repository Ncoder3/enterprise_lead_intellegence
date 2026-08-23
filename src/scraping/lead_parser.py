from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_leads(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")

    lead_cards = soup.select(".lead-card")

    leads = []

    for card in lead_cards:

        name_element = card.select_one(".person-name")
        job_title_element = card.select_one(".job-title")
        email_element = card.select_one(".email")
        company_name_element = card.select_one(".company-name")
        domain_element = card.select_one(".domain")
        industry_element = card.select_one(".industry")
        country_element = card.select_one(".country")
        employee_count_element = card.select_one(".employee-count")

        if not name_element:
            continue

        full_name = name_element.get_text(" ", strip=True)

        name_parts = full_name.split(maxsplit=1)

        first_name = name_parts[0]

        last_name = (
            name_parts[1]
            if len(name_parts) > 1
            else None
        )

        employee_count = None

        if employee_count_element:
            try:
                employee_count = int(
                    employee_count_element.get_text(strip=True)
                )
            except ValueError:
                employee_count = None

        lead = {
            "first_name": first_name,
            "last_name": last_name,
            "job_title": (
                job_title_element.get_text(strip=True)
                if job_title_element
                else None
            ),
            "email": (
                email_element.get_text(strip=True)
                if email_element
                else None
            ),
            "company_name": (
                company_name_element.get_text(strip=True)
                if company_name_element
                else None
            ),
            "domain": (
                domain_element.get_text(strip=True)
                if domain_element
                else None
            ),
            "industry": (
                industry_element.get_text(strip=True)
                if industry_element
                else None
            ),
            "country": (
                country_element.get_text(strip=True)
                if country_element
                else None
            ),
            "employee_count": employee_count,
        }

        leads.append(lead)

    return leads


def find_next_page(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    next_link = soup.select_one(".next-page")

    if not next_link:
        return None

    href = next_link.get("href")

    if not href:
        return None

    return urljoin(current_url, href)