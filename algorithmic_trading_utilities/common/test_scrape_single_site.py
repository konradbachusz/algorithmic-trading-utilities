from crewai_tools import ScrapeWebsiteTool
import json
from urllib.parse import urlparse

import time
import os
import json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def scrape_page(url):
    """
    Scrapes the content of a specified webpage.

    This function utilizes the ScrapeWebsiteTool to extract text from the
    webpage at the given URL. It initializes the tool with the URL and
    executes the scraping process, returning the extracted text.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: The text content extracted from the webpage.
    """

    # To enable scrapping any website it finds during it's execution
    tool = ScrapeWebsiteTool()

    # Initialize the tool with the website URL,
    # so the agent can only scrap the content of the specified website
    tool = ScrapeWebsiteTool(website_url=url)

    # Extract the text from the site
    scraped_page_text = tool.run()
    return scraped_page_text

def scrape_with_beautifulsoup(url):
    """
    Scrapes a website using requests and BeautifulSoup.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The text content of the website, or None if an error occurs.
    """
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the text from the site
        text = soup.get_text()
        return text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None


links=["https://www.ft.com/content/0f2637ae-f49c-45c5-845f-3b7aa10bea0f",
                  "https://www.ft.com/content/c7f511e7-7512-436a-8ba8-12e11e21e110",
                  "https://www.ft.com/content/5b179bb6-684a-48d1-abac-a25aacb12a49",
                 "https://uk.finance.yahoo.com/news/finance-week-ahead-us-jobs-data-nike-tesco-greggs-and-jd-wetherspoon-142412365.html",
                  "https://uk.finance.yahoo.com/news/fca-faces-battle-over-1m-100043927.html",
                "https://www.bbc.co.uk/news/articles/c8d70d912e6o",
                "https://www.bbc.co.uk/news/articles/cgl15ykerlro",
                "https://www.bbc.co.uk/news/articles/cr4qwwk0g0yo",
                "https://www.bbc.co.uk/news/articles/cly1geen679o",
                "https://www.bbc.co.uk/news/articles/c179z10vy28o",
                "https://www.bbc.co.uk/news/articles/c8d70d912e6o",
                "https://www.bbc.co.uk/news/articles/crkjreprp3po",
                "https://www.bbc.co.uk/news/videos/cg5ege645reo",
                "https://www.bbc.co.uk/news/articles/cgl15ykerlro",
                "https://www.bbc.co.uk/news/articles/c62zggj69e0o",
                "https://www.theguardian.com/business/2025/sep/26/trump-latest-tariff-threat-raises-fresh-concerns-for-uk-pharma",
                "https://www.theguardian.com/business/live/2025/sep/26/trump-investors-tariffs-pharmaceuticals-trucks-kitchen-cabinets-markets-uk-borrowing-costs-business-live-news",
                "https://www.theguardian.com/business/2025/sep/26/bank-of-england-should-not-be-overly-cautious-on-interest-rate-cuts-says-policymaker",
                "https://www.theguardian.com/business/live/2025/sep/26/trump-investors-tariffs-pharmaceuticals-trucks-kitchen-cabinets-markets-uk-borrowing-costs-business-live-news",
                "https://www.theguardian.com/commentisfree/2025/sep/25/us-stock-market-trump-wall-street-financial-crisis-federal-reserve",
                "https://www.theguardian.com/business/live/2025/sep/24/markets-economy-gold-eli-lilly-drug-prices-business-live-news",
                "https://www.theguardian.com/business/live/2025/sep/23/gold-price-on-track-best-year-since-1979-record-high-global-economy-uk-growth-business-live-news",
                  "https://www.theguardian.com/business/live/2025/sep/24/markets-economy-gold-eli-lilly-drug-prices-business-live-news",
                "https://uk.finance.yahoo.com/news/chinese-industrial-profits-jump-august-041948233.html"]

#TODO bring back
scraped_articles = []
for url in links:
    print(f"Scraping {url}...")
    try:
        # content = scrape_with_beautifulsoup(url)
        content = scrape_page(url)
        #TODO if the content contains "Enable JavaScript" or "enable JS" or "Yahoo is part of the Yahoo family of brands" wait a random time and ztry again with beautiful soup or selenium
        source = urlparse(url).netloc
        scraped_articles.append({
            "url": url,
            "content": content,
            "source": source
        })
        print(f"Successfully scraped {url}")
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

print(scraped_articles)
output_filename = "scraped_articles_crew.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(scraped_articles, f, indent=4)
print(f"\nScraped data for {len(scraped_articles)} URLs saved to {output_filename}")

#TODO good news: FT, yahoo finance, BBC, Guardian?



#https://www.theguardian.com/business/stock-markets