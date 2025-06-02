from fastapi import FastAPI
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import uvicorn

URL = "https://www.niftytrader.in/nse-option-chain/nifty"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

app = FastAPI()

async def scrape_oi_data():
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

            calls_oi = (await page.query_selector("#calls_oi_Total")).inner_text()
            puts_oi = (await page.query_selector("#puts_oi_Total")).inner_text()
            calls_change_oi = (await page.query_selector("#calls_change_oi_Total")).inner_text()
            puts_change_oi = (await page.query_selector("#puts_change_oi_Total")).inner_text()

            # Await inner_text() since it's a coroutine
            calls_oi = await calls_oi
            puts_oi = await puts_oi
            calls_change_oi = await calls_change_oi
            puts_change_oi = await puts_change_oi

            return {
                "success": True,
                "calls_oi": calls_oi.strip(),
                "puts_oi": puts_oi.strip(),
                "calls_change_oi": calls_change_oi.strip(),
                "puts_change_oi": puts_change_oi.strip()
            }

        except PlaywrightTimeoutError:
            return {"success": False, "error": "Timeout or selector not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await browser.close()

@app.get("/nifty-oi")
async def trigger_scrape():
    result = await scrape_oi_data()
    return JSONResponse(content=result)

if __name__ == "__main__":
    uvicorn.run("scraper_api:app", host="0.0.0.0", port=8000, reload=True)
