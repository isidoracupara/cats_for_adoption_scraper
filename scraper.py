import aiohttp
from bs4 import BeautifulSoup
import asyncio
import json

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def scrape_breeds(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        breeds = []
        try:
            # Find the div with the wire:snapshot attribute
            snapshot_div = soup.find("div", {"wire:snapshot": True})
            if snapshot_div:
                wire_snapshot = snapshot_div["wire:snapshot"]
                data = json.loads(wire_snapshot)
                raw_breeds = data["data"]["breeds"][0]
                breeds = [breed.replace(" ", "_").lower() for breed in raw_breeds]
        except Exception as e:
            print(f"Error parsing breeds: {e}")

        return breeds

async def scrape_website(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        titles = [item.text for item in soup.select('.some-css-selector')]

        return titles

async def scrape_multiple_websites(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))
        pages_content = await asyncio.gather(*tasks)

    results = []
    for html in pages_content:
        soup = BeautifulSoup(html, 'html.parser')
        titles = [item.text for item in soup.select('.some-css-selector')]
        results.append(titles)

    return results

async def get_breeds_and_scrape(base_url, exclude_breeds):
    all_breeds = await scrape_breeds(base_url + 'europese-korthaar')
    print(f"All breeds found: {all_breeds}")  # Debugging output
    breeds_to_scrape = [breed for breed in all_breeds if breed not in exclude_breeds]

    urls = [base_url + breed for breed in breeds_to_scrape]
    results = await scrape_multiple_websites(urls)

    return results

if __name__ == "__main__":
    base_url = 'https://www.adopteereendier.be/katten?ras='
    exclude_breeds = ['europese-korthaar']

    result = asyncio.run(get_breeds_and_scrape(base_url, exclude_breeds))
    print(result)
