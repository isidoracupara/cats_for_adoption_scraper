import aiohttp
from bs4 import BeautifulSoup
import asyncio
import json
import os

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
                breeds = [breed.strip().replace(" ", "-").lower() for breed in raw_breeds]
        except Exception as e:
            print(f"Error parsing breeds: {e}")

        return breeds

async def scrape_website(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        hrefs = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('https://www.adopteereendier.be/katten/')]

        return hrefs

async def scrape_multiple_websites(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))
        pages_content = await asyncio.gather(*tasks)

    hrefs = []
    for html in pages_content:
        soup = BeautifulSoup(html, 'html.parser')
        hrefs.extend([a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('https://www.adopteereendier.be/katten/')])

    return hrefs

async def get_breeds_and_scrape(base_url, filters):
    all_breeds = await scrape_breeds(base_url + '?ras=europese-korthaar')
    print(f"All breeds found: {all_breeds}")  # Debugging output

    exclude_breeds = filters.get('exclude_breeds', [])
    breeds_to_scrape = [breed for breed in all_breeds if breed not in exclude_breeds]

    urls = [build_url(base_url, {**filters, 'ras': breed}) for breed in breeds_to_scrape]
    hrefs = await scrape_multiple_websites(urls)

    # Save results as a text file
    save_hrefs_as_text(hrefs)

    return hrefs

def build_url(base_url, filters):
    filter_strings = [f"{key}={value}" for key, value in filters.items() if key != 'exclude_breeds']
    return base_url + "?" + "&".join(filter_strings)

def save_hrefs_as_text(hrefs):
    if not os.path.exists('scraped_results'):
        os.makedirs('scraped_results')

    with open('scraped_results/hrefs.txt', 'w', encoding='utf-8') as file:
        for href in hrefs:
            file.write(f"{href}\n")

# Default filters
DEFAULT_FILTERS = {
    'exclude_breeds': ['europese-korthaar', 'kruising-raskat', 'huiskat-langhaar', 'huiskat-korthaar'],
    'behavior_other_animals': 'andere_katten',
    'behavior_children': '6',
    'region': 'Vlaams-Brabant,Antwerpen',
    'type': 'knuffelkat,binnenkat'
}

if __name__ == "__main__":
    base_url = 'https://www.adopteereendier.be/katten'

    filters = DEFAULT_FILTERS

    url_with_filters = build_url(base_url, filters)
    result = asyncio.run(get_breeds_and_scrape(url_with_filters, filters))
    print("Scraped hrefs saved as a text file.")
