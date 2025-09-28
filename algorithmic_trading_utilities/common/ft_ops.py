import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Any
import time

from crewai_tools import ScrapeWebsiteTool
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
def scrape_ft_articles() -> List[Dict[str, Any]]:
    """
    Scrapes articles from the Financial Times news feed pages.

    This function iterates through a list of FT news feed URLs, sending HTTP requests
    to each page and parsing the HTML content to extract article details such as
    title, link, content, and tags. It handles potential 'Application Error' responses
    by implementing an exponential backoff retry mechanism. The scraped articles are
    returned as a list of dictionaries, each containing the article's metadata.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing an article
        with keys 'link', 'content', 'title', 'source', and 'tag'.
    """
    urls = [
        "https://www.ft.com/news-feed",
        "https://www.ft.com/news-feed?page=2",
        "https://www.ft.com/news-feed?page=3",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # Empty placeholder for articles
    articles = []

    # Iterate through FT latest news pages
    for url in urls:
        print("\nScraping page", url)
        try:

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            print("soup", soup) #TODO remove

            for article in soup.find_all("div", class_="o-teaser"):

                link_tag = article.find("a", class_="js-teaser-heading-link")
                content_tag = article.find("div", class_="o-teaser__body")
                title_tag = article.find("div", class_="o-teaser__heading")
                tag_tags = article.find_all("a", class_="o-teaser__tag")

                link = "https://www.ft.com" + link_tag["href"] if link_tag else ""
                content = content_tag.get_text(strip=True) if content_tag else ""
                title = (
                    title_tag.get_text(strip=True).replace("Premiumcontent", "")
                    if title_tag
                    else ""
                )  # Remove "Premiumcontent" from title
                tags = [tag.get_text(strip=True) for tag in tag_tags]

                if link != "":

                    print("Scraping title:", title)

                    # Get all text from the article link
                    content = scrape_page(link)

                    # If the content string returned by scrape_page(link) contains "Application Error" add an exponential backoff to wait a few seconds and try again. Try at least 5 times.
                    retries = 0
                    while "Application Error" in content and retries < 5:
                        retries += 1
                        wait_time = 2**retries
                        print(
                            f"Application Error encountered. Retrying in {wait_time} seconds..."
                        )
                        time.sleep(wait_time)
                        content = scrape_page(link)

                    if "Application Error" in content:
                        print("Application Error encountered. Skipping article.")
                        continue
                    else:
                        print("Article scraped")
                        articles.append(
                            {
                                "link": link,
                                "content": content,
                                "title": title,
                                "source": "Financial Times",
                                "tag": tags,
                            }
                        )

        except Exception as e:
            print(f"An error occurred: {e}")

    print("FT Articles Scraped:", len(articles))

    return articles


def save_articles_to_json(articles: List[Dict[str, Any]]) -> None:
    """
    Save a list of articles to a JSON file.

    This function takes a list of articles, each represented as a dictionary,
    and saves them to a JSON file named with the current date in the format
    'scraped_data/ft_scraped_data_YYYY-MM-DD.json'. The JSON file is formatted
    with UTF-8 encoding and includes indentation for readability.

    Args:
        articles (List[Dict[str, Any]]): A list of dictionaries, where each
        dictionary contains article data to be saved.

    Returns:
        None
    """
    today = datetime.today().strftime("%Y-%m-%d")
    file_path = f"articles/ft_scraped_data_{today}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"articles": articles}, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    articles = scrape_ft_articles()
    save_articles_to_json(articles)