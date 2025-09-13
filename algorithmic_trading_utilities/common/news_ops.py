from crewai_tools import ScrapeWebsiteTool
import time
import os


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

scraped_text = scrape_page("https://thehackernews.com/2025/09/new-hybridpetya-ransomware-bypasses.html")
os.makedirs("articles", exist_ok=True)
with open(os.path.join("articles", "scraped_page6.txt"), "w", encoding="utf-8") as f:
    f.write(scraped_text)