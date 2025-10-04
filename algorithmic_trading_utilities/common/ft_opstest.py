#TODO remove or tidy up once done

from bs4 import BeautifulSoup
from selenium import webdriver
import json
from datetime import datetime
from urllib.parse import urlparse
from crewai_tools import ScrapeWebsiteTool

driver = webdriver.Firefox()

urls=[
    "https://thehackernews.com/2025/09/new-hybridpetya-ransomware-bypasses.html",
    "https://www.ft.com/content/a2b6f8f6-26d0-4493-a961-2aeb0d527157",
    "https://www.ft.com/content/fe1fd1ff-8a7b-4958-b123-cf9fc93c6e36",
    "https://www.ft.com/content/585e7376-8006-4ada-8a12-d31d39b0cf39",
    "https://www.ft.com/content/f52feb05-d963-441c-b19a-fc4f64926e1b",
    "https://www.ft.com/content/be40c638-77ce-4986-9274-fa157d3a0ffb",
    "https://www.reuters.com/business/nasdaq-notches-record-high-close-traders-look-fed-meeting-2025-09-12/",
    "https://www.reuters.com/business/nasdaq-notches-record-high-close-traders-look-fed-meeting-2025-09-12/",
    "https://www.reuters.com/world/china/us-chinese-officials-launch-talks-spain-trade-irritants-tiktok-deadline-2025-09-14/",
    "https://www.bloomberg.com/news/articles/2025-09-14/switzerland-s-central-bank-learns-to-live-with-a-strong-franc",
    "https://www.bloomberg.com/news/articles/2025-09-14/polish-stock-rally-seen-rolling-on-despite-drones-bank-tax-hike",
    "https://www.bloomberg.com/news/articles/2025-09-14/cross-border-bank-consolidation-benefits-cyprus-patsalides-says?embedded-checkout=true"
]
#TODO bring back
# scraped_articles = []

# for url in urls:
#     print(f"Scraping: {url}")
#     try:
#         driver.get(url)
#         html = driver.page_source
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Extract content
#         content = soup.get_text(separator=' ', strip=True)
        
#         # Get source from URL
#         source = urlparse(url).netloc
        
#         # Get current timestamp
#         timestamp = datetime.now().isoformat()
        
#         scraped_articles.append({
#             "url": url,
#             "content": content,
#             "source": source,
#             "timestamp": timestamp
#         })
#         print(f"Successfully scraped: {url}")
#     except Exception as e:
#         print(f"Failed to scrape {url}: {e}")

#TODO bring back
# # Quit the driver after the loop
# driver.quit()

# # Save to a JSON file
# output_filename = "articles/scraped_selenium_articles.json"
# with open(output_filename, "w", encoding="utf-8") as f:
#     json.dump(scraped_articles, f, indent=4, ensure_ascii=False)

# print(f"\nSaved {len(scraped_articles)} articles to {output_filename}")

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

page=scrape_page("https://www.ft.com/content/9822b5ee-4d3e-4e73-bbf4-be382d2fada7")

print(page)