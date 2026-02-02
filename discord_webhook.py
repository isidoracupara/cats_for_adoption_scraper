import requests
import os
import re
import schedule
import time
from scraper import get_breeds_and_scrape, build_url, save_hrefs_to_file, load_hrefs_from_file, DEFAULT_FILTERS
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Ensure environment variables are set
if not WEBHOOK_URL:
    raise ValueError("Environment variable WEBHOOK_URL must be set")

async def check_for_new_urls():
    base_url = 'https://www.adopteereendier.be/katten'
    filters = DEFAULT_FILTERS

    new_hrefs = await get_breeds_and_scrape(base_url, filters)
    tracked_hrefs = load_hrefs_from_file()

    new_urls = set(new_hrefs) - tracked_hrefs
    removed_urls = tracked_hrefs - set(new_hrefs)

    if new_urls:
        for url in new_urls:
            cat_name = re.sub(r"\d+", "", url.split("/")[-1].replace("-", " ").title())
            message = f""" \n\n
            ✨🐱✨ **A new cat that fits your filters has just been put up for adoption!** ✨🐱✨
            Meet **{cat_name}**! 🐾💖
            {url}
            """
            response = requests.post(WEBHOOK_URL, json={"content": message})
            if response.status_code != 204:
                print(f"Failed to send webhook: {response.status_code}, {response.text}")


            message2 = {
                "content": f"""

            ✨🐱✨ **A new cat that fits your filters has just been put up for adoption!** ✨🐱✨
            Meet **{cat_name}**! 🐾💖
            [Click here to view the cat!]({url}) 🐾💖
            """,
                "embeds": [
                    {
                        "title": f"Meet {cat_name} 🐱",
                        "url": url,
                        "description": "Click to view this cat’s adoption page 🐾",
                    }
                ]
            }


    save_hrefs_to_file(tracked_hrefs | new_urls)

async def main():
    await check_for_new_urls()

if __name__ == "__main__":
    asyncio.run(main())
