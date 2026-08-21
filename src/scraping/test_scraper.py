from src.scraping.basic_scraper import scrape_page


def main():
    url = "https://example.com"

    result = scrape_page(url)

    print("Scraping successful!")
    print(result)


if __name__ == "__main__":
    main()