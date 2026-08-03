import asyncio
from calendar import timegm
from datetime import datetime, timedelta, timezone
import httpx
import feedparser
import pprint

def lambda_handler(event, context):
    urls = event['feedTargets']
    gimme_everything = event.get('everything?', False)
    results = asyncio.run(read_feeds(urls))

    pprint.pp(clean_feeds(results, gimme_everything))

    
async def read_feeds(urls: list):
    async with httpx.AsyncClient() as client:
        reads = [fetch_feed(client, url) for url in urls]    
        results = await asyncio.gather(*reads)
    return results

async def fetch_feed(client: httpx.AsyncClient, url:str):
    response = await client.get(url)
    return feedparser.parse(response)

def clean_feeds(feeds, getEverything: False):
    response = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for feed in feeds:
        feed_obj = {'name': feed.get('title', "No Title Found"), 'entries': []}
        entries = feed.entries if getEverything else [
            entry for entry in feed.entries
            if entry.get('published_parsed') and (datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc) >= cutoff 
                                                  or datetime.fromtimestamp(timegm(entry.updated_parsed), tz=timezone.utc) >= cutoff)
        ]
        for entry in entries:
            feed_obj['entries'].append(
                {
                    'title': entry.get('title', "No Title Found"),
                    'author': entry.get('author', "No Author Found"),
                    'published': entry.published,
                    'updated': entry.updated,
                    'content': entry.content[0].value
                }
            )
        response.append(feed_obj)
    return response



lambda_handler({'feedTargets': ['https://www.blogofarcanesecrets.com/feed'], 'everything?': True}, None)