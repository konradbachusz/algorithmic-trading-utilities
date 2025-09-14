from crewai_tools import ScrapeWebsiteTool
import time
import os
import json
from urllib.parse import urlparse


def scrape_page(url, max_retries=5):
    """
    Scrapes the content of a specified webpage with retry logic.

    This function utilizes the ScrapeWebsiteTool to extract text from the
    webpage at the given URL. It will retry up to 5 times if it encounters
    a client challenge message, using exponential backoff between attempts.

    Args:
        url (str): The URL of the webpage to scrape.
        max_retries (int): Maximum number of retry attempts. Defaults to 5.

    Returns:
        str: The text content extracted from the webpage.

    Raises:
        RuntimeError: If all retry attempts fail to get valid content.
    """
    js_disabled_text = "JavaScript is disabled in your browser"

    for attempt in range(max_retries):
        try:
            tool = ScrapeWebsiteTool(website_url=url)
            scraped_page_text = tool.run()
            
            if js_disabled_text not in scraped_page_text:
                print(scraped_page_text)
                return scraped_page_text
            
            delay = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
            print(f"Attempt {attempt + 1} failed due to client challenge. Retrying in {delay} seconds...")
            time.sleep(delay)
            
        except Exception as e:
            delay = 2 ** attempt
            print(f"Error on attempt {attempt + 1}: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
        
    raise RuntimeError(f"Failed to scrape page after {max_retries} attempts")

#TODO remove comments below after testing
# scraped_text = scrape_page("https://thehackernews.com/2025/09/new-hybridpetya-ransomware-bypasses.html")
# os.makedirs("articles", exist_ok=True)
# with open(os.path.join("articles", "scraped_page6.txt"), "w", encoding="utf-8") as f:
#     f.write(scraped_text)

def scrape_multiple_pages(urls, output_filename="scraped_articles.json"):
    """
    Scrapes multiple web pages and saves their content to a JSON file.

    Each entry in the JSON file will contain the URL, the scraped content,
    and the source (domain name).

    Args:
        urls (list): A list of URLs to scrape.
        output_filename (str): The name of the JSON file to save the results to.
                               Defaults to "scraped_articles.json".
    """
    scraped_data = []
    for url in urls:
        try:
            print(f"Scraping {url}...")
            content = scrape_page(url)
            parsed_url = urlparse(url)
            source = parsed_url.netloc

            scraped_data.append({"url": url, "content": content, "source": source})
            print(f"Successfully scraped {url}")
        except RuntimeError as e:
            print(f"Failed to scrape {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while scraping {url}: {e}")

    # Save the scraped data to a JSON file inside the 'articles' directory
    if scraped_data:
        os.makedirs("articles", exist_ok=True)
        output_path = os.path.join("articles", output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, indent=4)
        print(f"\nScraped data for {len(scraped_data)} URLs saved to {output_path}")
    else:
        print("\nNo data was scraped.")

#TODO remove
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
scrape_multiple_pages(urls)