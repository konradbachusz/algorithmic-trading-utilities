from crewai_tools import ScrapeWebsiteTool
import time
import os
import json
from urllib.parse import urlparse
import requests
from datetime import date
from bs4 import BeautifulSoup

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

def get_latest_bbc_articles(url):
    """
    Scrapes the BBC Business news page to get a list of the latest articles.

    Args:
        url (str): The URL of the BBC Business news page.

    Returns:
        list: A list of dictionaries, each containing the 'url' and 'tag'
              for an article.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    
    articles = []
    processed_urls = set()

    # Find all article promo blocks, which act as containers for each article summary
    for promo in soup.find_all("div", class_=lambda x: x and "Promo" in x and "Wrapper" not in x):
        link_tag = promo.find("a", href=True)
        # Find the specific span for the category tag
        tag_span = promo.find("span", class_="ssrcss-61mhsj-MetadataText")

        if link_tag and link_tag['href'].startswith('/news/'):
            full_url = f"https://www.bbc.co.uk{link_tag['href']}"
            # Avoid duplicate articles by checking the URL
            if full_url not in processed_urls:
                tag_text = tag_span.get_text(strip=True) if tag_span else "N/A"
                
                # Find the post time
                # Find all spans with the specified class and get their text
                time_spans = promo.find_all("span", class_="visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0")
                post_time_text = [span.get_text(strip=True) for span in time_spans]

                articles.append({"url": full_url, "tag": tag_text, "post_time": post_time_text})
                processed_urls.add(full_url)
            
    return articles


def filter_bbc_posts(articles):
    """
    Filters a list of BBC articles based on specific tags and the presence of a post time.

    Args:
        articles (list): A list of article dictionaries from get_latest_bbc_articles.

    Returns:
        list: A filtered list of article dictionaries.
    """
    allowed_tags = {"Business", "Technology", "Politics"}
    # An empty list evaluates to False, so this keeps articles where post_time is not empty.
    filtered_articles = [
        article for article in articles
        if article.get("tag") in allowed_tags and
           any("ago" in s for s in article.get("post_time", []))
    ]
    return filtered_articles
#TODO good news: FT, yahoo finance, BBC, Guardian?




#todo REMOVE
url="https://www.bbc.co.uk/news/business"

links=get_latest_bbc_articles(url)
# links = filter_bbc_posts(links) #TODO fix
links = filter_bbc_posts(links)
print(f"Found {len(links)} relevant articles to scrape.")
# with open("bbc_business.html", "w", encoding="utf-8") as f:
#     f.write(str(soup))

#TODO bring back
scraped_articles = []
for article_data in links:
    url = article_data.get("url")
    tag = article_data.get("tag")
    post_time = article_data.get("post_time")
    print(f"Scraping {url} (Tag: {tag})...")
    try:
        content = scrape_with_beautifulsoup(url)
        #content = scrape_page(url)
        #TODO if the content contains "Enable JavaScript" or "enable JS" or "Yahoo is part of the Yahoo family of brands" wait a random time and ztry again with beautiful soup or selenium
        source = urlparse(url).netloc
        scraped_articles.append({
            "url": url,
            "tag": tag,
            "post_time": post_time,
            "content": content,
            "source": source
        })
        print(f"Successfully scraped {url}")
    except Exception as e:
        print(f"Failed to scrape {article_data}: {e}")

print(scraped_articles)
today_str = date.today().strftime("%Y%m%d")
output_filename = f"articles/scraped_articles_soup_{today_str}.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(scraped_articles, f, indent=4)
print(f"\nScraped data for {len(scraped_articles)} URLs saved to {output_filename}")

#TODO use only Business or Technology tags