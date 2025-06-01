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
    Load the page, wait for the #calls_oi_Total element, and return its text.
    If something goes wrong (timeout or block detection), return None.
    """
    try:
        page.goto(URL, timeout=60000)
        page.wait_for_selector("#calls_oi_Total", timeout=15000)
        calls_oi_text = page.query_selector("#calls_oi_Total").inner_text().strip()
        return calls_oi_text
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

        # (Optional) Emulate a desktop viewport size
        page.set_viewport_size({"width": 1280, "height": 800})

        while True:
            calls_oi = scrape_once(page)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if calls_oi:
                print(f"[{timestamp}] Calls OI Total: {calls_oi}")
                # Here you could save to MongoDB or a CSV/file if needed.
            else:
                print(f"[{timestamp}] Failed to scrape. Applying backoff.")
                # Exponential backoff or sleep longer before retrying
                time.sleep(60 * 5)  # Wait 5 minutes before retrying
                continue

            # Wait roughly 60 seconds, plus a 2–5 second random jitter
            sleep_time = 60 + random.uniform(2, 5)
            time.sleep(sleep_time)

        # browser.close()  # Unreachable in this infinite loop; handle shutdown externally.

if __name__ == "__main__":
    main()
