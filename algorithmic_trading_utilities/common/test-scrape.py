import csv
import os
import time
import warnings
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

warnings.filterwarnings("ignore", category=DeprecationWarning)

TARGET_URL = "https://www.ft.com/content/ece272c3-de7e-47ac-ae1e-2d125d6ada80"

# ---- replace with real cookies if not using CSV ----
HARD_CODED_COOKIES = [
    {"name": "FTSession", "value": "YOUR_FTSESSION", "domain": ".ft.com", "path": "/", "secure": True},
    {"name": "ft-access-decision-policy", "value": "GRANTED_ZEPHR_SEARCH_1_30_VARIANT", "domain": ".ft.com", "path": "/", "secure": False},
    {"name": "subscriptionToken", "value": "YOUR_SUBSCRIPTION_TOKEN", "domain": ".ft.com", "path": "/", "secure": True},
]

def load_cookies():
    if os.path.exists("Valid.csv"):
        cookies = []
        with open("Valid.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("name") or not row.get("value"):
                    continue
                cookies.append({
                    "name": row["name"],
                    "value": row["value"],
                    "domain": row.get("domain", ".ft.com"),
                    "path": row.get("path", "/")
                })
        return cookies
    return HARD_CODED_COOKIES

def main():
    cookies = load_cookies()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # remove this line if you want to see browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # visit each domain first
    visited = set()
    for c in cookies:
        domain = c.get("domain", ".ft.com").lstrip(".")
        if domain not in visited:
            try:
                driver.get(f"https://{domain}/")
                time.sleep(1)
                visited.add(domain)
            except Exception as e:
                print(f"Could not visit {domain}: {e}")

        try:
            driver.add_cookie(c)
            print(f"Added cookie: {c['name']} for {c.get('domain')}")
        except Exception as e:
            print(f"Failed to add {c['name']}: {e}")

    # reload target after cookies are added
    driver.get(TARGET_URL)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
    except Exception:
        print("⚠️ Article tag not found — may still be paywalled.")

    html = driver.page_source
    with open("output_crewai_tools.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Saved full page source to output_crewai_tools.html")
    print("🔎 Cookies now in browser:", [c["name"] for c in driver.get_cookies()])

    driver.quit()

if __name__ == "__main__":
    main()
