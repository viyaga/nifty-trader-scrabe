import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://www.niftytrader.in/nse-option-chain/nifty"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

async def scrape_once():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_extra_http_headers({
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-IN,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp"
        })
        await page.set_viewport_size({"width": 1280, "height": 800})

        try:
            await page.goto(URL, timeout=60000)
            await page.wait_for_selector("#calls_oi_Total", timeout=15000)

            calls_oi = await page.inner_text("#calls_oi_Total")
            puts_oi = await page.inner_text("#puts_oi_Total")
            calls_change_oi = await page.inner_text("#calls_change_oi_Total")
            puts_change_oi = await page.inner_text("#puts_change_oi_Total")

            return {
                "calls_oi": calls_oi.strip(),
                "puts_oi": puts_oi.strip(),
                "calls_change_oi": calls_change_oi.strip(),
                "puts_change_oi": puts_change_oi.strip(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }

        except PlaywrightTimeoutError:
            return None
        finally:
            await browser.close()
