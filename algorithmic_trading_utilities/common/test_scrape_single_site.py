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

#TODO remove
links=['https://www.bbc.co.uk/news/articles/cdjzrl9kkkmo', 'https://www.bbc.co.uk/news/articles/c0q75q4l87no#comments', 'https://www.bbc.co.uk/news/articles/cm2djl9jem7o', 'https://www.bbc.co.uk/news/articles/c77dkl4ev36o', 'https://www.bbc.co.uk/news/articles/c23p028p200o#comments', 'https://www.bbc.co.uk/news/articles/cy8d4v69jw6o#comments', 'https://www.bbc.co.uk/news/articles/cn93e12rypgo', 'https://www.bbc.co.uk/news/articles/c74010vm7pdo', 'https://www.bbc.co.uk/news/articles/crkjreprp3po', 'https://www.bbc.co.uk/news/articles/c62l0j5037eo', 'https://www.bbc.co.uk/news/articles/c62zwz0k5dgo', 'https://www.bbc.co.uk/news/articles/c77dzm681ygo', 'https://www.bbc.co.uk/news/articles/cpq5w324pd3o', 'https://www.bbc.co.uk/news/articles/cvg8vjm4ee1o', 'https://www.bbc.co.uk/news/articles/cy8d4v69jw6o', 'https://www.bbc.co.uk/news/articles/cx275251xzro', 'https://www.bbc.co.uk/news/articles/cm2zv4md2wko', 'https://www.bbc.co.uk/news/articles/cjedze7e95lo', 'https://www.bbc.co.uk/news/articles/c0l6g13rlwko', 'https://www.bbc.co.uk/news/articles/c0q7395np59o', 'https://www.bbc.co.uk/news/articles/c23p028p200o', 'https://www.bbc.co.uk/news/articles/cgl15ykerlro', 'https://www.bbc.co.uk/news/articles/c4gvm1kjxxvo', 'https://www.bbc.co.uk/news/articles/cr4qwwk0g0yo', 'https://www.bbc.co.uk/news/articles/cn5q61kywx1o', 'https://www.bbc.co.uk/news/articles/cx275251xzro#comments', 'https://www.bbc.co.uk/news/articles/c0q75q4l87no', 'https://www.bbc.co.uk/news/articles/cpw1klke7z1o', 'https://www.bbc.co.uk/news/articles/c39r7p47wzgo', 'https://www.bbc.co.uk/news/articles/c179z10vy28o', 'https://www.bbc.co.uk/news/articles/c8d70d912e6o', 'https://www.bbc.co.uk/news/articles/cly1geen679o', 'https://www.bbc.co.uk/news/articles/c99g7ekex5mo', 'https://www.bbc.co.uk/news/articles/c62zggj69e0o', 'https://www.bbc.co.uk/news/articles/c5y5qllgpgzo', 'https://www.bbc.co.uk/news/articles/clyng762q4eo', 'https://www.bbc.co.uk/news/articles/c4gw25w9841o', 'https://www.bbc.co.uk/news/articles/cm2zvj2ex70o', 'https://www.bbc.co.uk/news/articles/c62nven55gro', 'https://www.bbc.co.uk/news/articles/c4gvpgy1w20o', 'https://www.bbc.co.uk/news/articles/cp08467m0zzo', 'https://www.bbc.co.uk/news/articles/c8d7y1gj319o']

#TODO bring back
scraped_articles = []
for url in links:
    print(f"Scraping {url}...")
    try:
        content = scrape_with_beautifulsoup(url)
        #content = scrape_page(url)
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
output_filename = "scraped_articles_soup2.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(scraped_articles, f, indent=4)
print(f"\nScraped data for {len(scraped_articles)} URLs saved to {output_filename}")

#TODO good news: FT, yahoo finance, BBC, Guardian?



#https://www.theguardian.com/business/stock-markets