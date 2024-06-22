import discord
import os
import schedule
import time
from scraper import get_breeds_and_scrape, build_url, save_hrefs_to_file, load_hrefs_from_file, DEFAULT_FILTERS
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not DISCORD_BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Environment variables DISCORD_BOT_TOKEN and CHANNEL_ID must be set")

CHANNEL_ID = int(CHANNEL_ID)


intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def check_for_new_urls():
    base_url = 'https://www.adopteereendier.be/katten'
    filters = DEFAULT_FILTERS
    url_with_filters = build_url(base_url, filters)

    new_hrefs = await get_breeds_and_scrape(url_with_filters, filters)
    tracked_hrefs = load_hrefs_from_file()

    new_urls = set(new_hrefs) - tracked_hrefs
    removed_urls = tracked_hrefs - set(new_hrefs)

    if new_urls:
        channel = client.get_channel(CHANNEL_ID)
        for url in new_urls:
            embed = discord.Embed(
                title="New Cat Available for Adoption!",
                description=f"A new cat that fits your filters has just been put up for adoption!",
                url=url,
                color=discord.Color.blue()
            )
            embed.add_field(name="Link", value=f"[View Cat]({url})")
            await channel.send(embed=embed)

    save_hrefs_to_file(new_hrefs)

async def scheduler_task():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    schedule.every(5).minutes.do(lambda: asyncio.ensure_future(check_for_new_urls()))
    client.loop.create_task(scheduler_task())

client.run(TOKEN)
