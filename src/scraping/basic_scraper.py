from bs4 import BeautifulSoup

from src.scraping.http_client import fetch_page


def scrape_page(url: str) -> dict:
    html = fetch_page(url)

    soup = BeautifulSoup(html, "lxml")

    return {
        "url": url,
        "title": soup.title.get_text(strip=True)
        if soup.title
        else None,
        "html_length": len(html),
    }