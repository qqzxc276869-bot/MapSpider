import json
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        results = []
        def handle_response(response):
            try:
                if "amap.com" in response.url and ("poi" in response.url or "search" in response.url):
                    data = response.json()
                    # Amap often returns JSON directly for POI lookups inside the web search
                    if "data" in data and "poi_list" in data["data"]:
                        for poi in data["data"]["poi_list"]:
                            results.append(poi.get("name"))
            except Exception:
                pass
        
        page.on("response", handle_response)
        page.goto("https://ditu.amap.com/search?query=杭州市咖啡店", timeout=30000)
        page.wait_for_timeout(5000)
        print("Amap Results:", results)
        
        browser.close()

if __name__ == '__main__':
    run()
