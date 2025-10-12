from crewai_tools import ScrapeWebsiteTool
import time
import os
import json
from urllib.parse import urlparse
import requests
from datetime import date, datetime
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


def is_within_one_day(post_time_list: list) -> bool:
    """Checks if the post time is within one day."""
    if not post_time_list:
        return False
    
    # Find the relevant time string, e.g., "16 hours ago"
    time_string = next((s for s in post_time_list if "ago" in s), None)
    if not time_string:
        return False

    time_string = time_string.lower()
    
    # Always include if it's minutes or hours
    if "minute" in time_string or "hour" in time_string:
        return True
    # For days, only include if it's exactly "1 day ago" or "a day ago"
    if "day" in time_string and ("1 day" in time_string or "a day" in time_string):
        return True
    return False


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
        if article.get("tag") in allowed_tags and is_within_one_day(article.get("post_time"))
    ]
    return filtered_articles
#TODO good news: FT, yahoo finance, BBC, Guardian?


def get_bbc_links():
    """
    Scrapes multiple BBC news pages, combines and filters the articles.
    
    Returns:
        list: A filtered list of unique article dictionaries.
    """
    urls = [
        "https://www.bbc.co.uk/news/business/economy",
        "https://www.bbc.co.uk/news/topics/cw9l5jelpl1t",
        "https://www.bbc.co.uk/news/business"
    ]
    
    all_articles = []
    processed_urls = set()

    for url in urls:
        print(f"Scraping article links from: {url}")
        try:
            articles_from_page = get_latest_bbc_articles(url)
            for article in articles_from_page:
                if article.get('url') not in processed_urls:
                    article['source_page'] = url  # Add the URL of the page where the link was found
                    all_articles.append(article)
                    processed_urls.add(article.get('url'))
        except Exception as e:
            print(f"Could not scrape {url}: {e}")

    links = filter_bbc_posts(all_articles)
    print(f"Found {len(links)} relevant articles to scrape.")
    return links

def scrape_bbc_articles():

    links = get_bbc_links()
    scraped_articles = []
    for article_data in links:
        url = article_data.get("url")
        tag = article_data.get("tag")
        post_time = article_data.get("post_time")
        source = article_data.get("source_page")  # Get the source page URL
        print(f"Scraping {url} (Tag: {tag})...")
        try:
            content = scrape_with_beautifulsoup(url)
            #content = scrape_page(url)
            #TODO if the content contains "Enable JavaScript" or "enable JS" or "Yahoo is part of the Yahoo family of brands" wait a random time and ztry again with beautiful soup or selenium
            scraped_articles.append({
                "url": url,
                "tag": tag,
                "post_time": post_time,
                "content": content,
                "source": source  # Use the source page URL here
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

#TODO import from somewhere else
#scrape_bbc_articles()


def calculate_time_ago(pub_date_str):
    """
    Calculate relative time from a publication date string.
    
    Args:
        pub_date_str (str): ISO format timestamp string like "2025-10-11T19:27:39Z"
        
    Returns:
        str: Relative time format like "4h ago", "2d ago", etc.
    """
    if not pub_date_str:
        return ""
    
    try:
        # Parse the publication date
        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        
        # Get current time (assuming UTC for consistency with Yahoo Finance)
        current_time = datetime.now(pub_date.tzinfo)
        
        # Calculate the difference
        time_diff = current_time - pub_date
        
        # Convert to appropriate units
        total_seconds = int(time_diff.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s ago" if total_seconds > 1 else "1s ago"
        elif total_seconds < 3600:  # Less than 1 hour
            minutes = total_seconds // 60
            return f"{minutes}m ago" if minutes > 1 else "1m ago"
        elif total_seconds < 86400:  # Less than 1 day
            hours = total_seconds // 3600
            return f"{hours}h ago" if hours > 1 else "1h ago"
        elif total_seconds < 604800:  # Less than 1 week
            days = total_seconds // 86400
            return f"{days}d ago" if days > 1 else "1d ago"
        else:  # More than a week
            weeks = total_seconds // 604800
            return f"{weeks}w ago" if weeks > 1 else "1w ago"
            
    except (ValueError, AttributeError):
        return ""


def get_yahoo_news_links():
    """
    Scrapes Yahoo Finance homepage to get latest news links and their associated stock symbols.
    
    Returns:
        dict: Dictionary containing news articles with their URLs and affected stock symbols.
              Format: {
                  'articles': [
                      {
                          'title': str,
                          'url': str,
                          'summary': str,
                          'pub_date': str,
                          'display_time': str,  # Relative time like "4h ago", "6h ago"
                          'symbols': [str],  # List of stock symbols mentioned in the article
                          'provider': str
                      },
                      ...
                  ]
              }
    """
    url = "https://finance.yahoo.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Find script tags containing JSON data for the news sections
    script_tags = soup.find_all('script', {'type': 'application/json'})
    
    articles_data = []
    
    for script in script_tags:
        script_content = script.get_text()
        try:
            # Parse the JSON content
            json_data = json.loads(script_content)
            
            if 'body' in json_data:
                try:
                    body_content = json.loads(json_data['body'])
                    
                    # Look for data.main.stream structure (news articles)
                    if ('data' in body_content and 
                        isinstance(body_content['data'], dict) and 
                        'main' in body_content['data'] and
                        isinstance(body_content['data']['main'], dict) and
                        'stream' in body_content['data']['main']):
                        
                        stream_data = body_content['data']['main']['stream']
                        
                        if isinstance(stream_data, list) and len(stream_data) > 0:
                            for article_item in stream_data:
                                if 'content' in article_item:
                                    content = article_item['content']
                                    
                                    # Extract basic article information
                                    pub_date = content.get('pubDate', '')
                                    display_time = content.get('displayTime', '')
                                    
                                    # If display_time is empty or same as pub_date, calculate relative time
                                    if not display_time or display_time == pub_date:
                                        display_time = calculate_time_ago(pub_date)
                                    else:
                                        # If display_time is a timestamp, convert it to relative time
                                        if 'T' in display_time and ('Z' in display_time or '+' in display_time):
                                            display_time = calculate_time_ago(display_time)
                                    
                                    article_info = {
                                        'title': content.get('title', ''),
                                        'summary': content.get('summary', ''),
                                        'pub_date': pub_date,
                                        'display_time': display_time,
                                        'provider': '',
                                        'url': '',
                                        'symbols': []
                                    }
                                    
                                    # Get the article URL
                                    if 'clickThroughUrl' in content and content['clickThroughUrl']:
                                        if isinstance(content['clickThroughUrl'], dict):
                                            article_info['url'] = content['clickThroughUrl'].get('url', '')
                                        else:
                                            article_info['url'] = str(content['clickThroughUrl'])
                                    elif 'canonicalUrl' in content and content['canonicalUrl']:
                                        if isinstance(content['canonicalUrl'], dict):
                                            article_info['url'] = content['canonicalUrl'].get('url', '')
                                        else:
                                            article_info['url'] = str(content['canonicalUrl'])
                                    
                                    # Get provider information
                                    if 'provider' in content and content['provider']:
                                        article_info['provider'] = content['provider'].get('displayName', '')
                                    
                                    # Extract stock symbols if available
                                    if 'finance' in content and content['finance']:
                                        finance_data = content['finance']
                                        if ('stockTickers' in finance_data and 
                                            finance_data['stockTickers'] is not None and 
                                            isinstance(finance_data['stockTickers'], list)):
                                            symbols = [ticker['symbol'] for ticker in finance_data['stockTickers'] 
                                                      if isinstance(ticker, dict) and 'symbol' in ticker]
                                            article_info['symbols'] = symbols
                                    
                                    # Only add articles that have URLs
                                    if article_info['url']:
                                        articles_data.append(article_info)
                                
                except json.JSONDecodeError:
                    continue
                    
        except json.JSONDecodeError:
            continue
    
    return {'articles': articles_data}


def save_yahoo_news_to_json(filename=None):
    """
    Fetches the latest Yahoo Finance news and saves it to a JSON file.
    
    Args:
        filename (str, optional): Custom filename for the JSON file. 
                                If None, generates a timestamped filename.
    
    Returns:
        tuple: (success: bool, message: str, filename: str)
    """
    try:
        # Get the latest news articles
        news_data = get_yahoo_news_links()
        
        # Generate filename if not provided
        if filename is None:
            today_str = date.today().strftime("%Y%m%d")
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"articles/yahoo_finance_news_{today_str}_{timestamp}.json"
        
        # Ensure the articles directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save to JSON file
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=4, ensure_ascii=False)
        
        article_count = len(news_data.get('articles', []))
        message = f"Successfully saved {article_count} articles to {filename}"
        print(message)
        
        return True, message, filename
        
    except Exception as e:
        error_message = f"Error saving Yahoo Finance news: {e}"
        print(error_message)
        return False, error_message, filename if 'filename' in locals() else None
    
#TODO remove
save_yahoo_news_to_json()