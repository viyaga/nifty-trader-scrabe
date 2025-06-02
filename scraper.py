#scraper.py

import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://www.niftytrader.in/nse-option-chain/nifty"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

def scrape_once(page):
    """
    Load the page, wait for the #calls_oi_Total element, and return the relevant OI values.
    If something goes wrong (timeout or block detection), return None.
    """
    try:
        page.goto(URL, timeout=60000)
        page.wait_for_selector("#calls_oi_Total", timeout=15000)

        calls_oi_text = page.query_selector("#calls_oi_Total").inner_text().strip()
        puts_oi_text = page.query_selector("#puts_oi_Total").inner_text().strip()
        calls_change_oi_text = page.query_selector("#calls_change_oi_Total").inner_text().strip()
        puts_change_oi_text = page.query_selector("#puts_change_oi_Total").inner_text().strip()

        return {
            "calls_oi": calls_oi_text,
            "puts_oi": puts_oi_text,
            "calls_change_oi": calls_change_oi_text,
            "puts_change_oi": puts_change_oi_text,
        }

    except PlaywrightTimeoutError:
        print("Timeout or element not found. Possible block or slow network.")
        return None

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set realistic headers
        page.set_extra_http_headers({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-IN,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp"
        })

        # Emulate desktop viewport
        page.set_viewport_size({"width": 1280, "height": 800})

        while True:
            oi_data = scrape_once(page)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            if oi_data:
                print(f"[{timestamp}] Calls OI: {oi_data['calls_oi']}, Puts OI: {oi_data['puts_oi']}, "
                      f"Calls Change OI: {oi_data['calls_change_oi']}, Puts Change OI: {oi_data['puts_change_oi']}")
                # Save to DB or file here if needed
            else:
                print(f"[{timestamp}] Failed to scrape. Applying backoff.")
                time.sleep(60 * 5)  # Wait 5 minutes before retrying
                continue

            # Wait around 60 seconds with jitter
            sleep_time = 60 + random.uniform(2, 5)
            time.sleep(sleep_time)

        # browser.close() — Unreachable unless you handle shutdown gracefully

if __name__ == "__main__":
    main()
