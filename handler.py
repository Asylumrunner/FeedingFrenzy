import asyncio
from calendar import timegm
from datetime import datetime, timedelta, timezone
from html import escape
import httpx
import feedparser
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    urls = event['feedTargets']
    gimme_everything = event.get('everything?', False)
    sourceEmail = event['sourceEmail']
    destEmail = event['destinationEmail']
    results = asyncio.run(read_feeds(urls))
    body_material = clean_feeds(results, gimme_everything)
    body = create_email_body(body_material)
    send_email(body, sourceEmail, destEmail)


    
async def read_feeds(urls: list):
    async with httpx.AsyncClient(timeout=10) as client:
        reads = [fetch_feed(client, url) for url in urls]
        results = await asyncio.gather(*reads, return_exceptions=True)
    return [result for result in results if not isinstance(result, Exception)]

async def fetch_feed(client: httpx.AsyncClient, url:str):
    response = await client.get(url)
    return feedparser.parse(response)

def clean_feeds(feeds, getEverything: bool = False):
    response = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for feed in feeds:
        feed_obj = {'name': feed.feed.get('title', "No Title Found"), 'entries': []}
        entries = feed.entries if getEverything else [
            entry for entry in feed.entries
            if _entry_is_recent(entry, cutoff)
        ]
        for entry in entries:
            feed_obj['entries'].append(
                {
                    'title': entry.get('title', "No Title Found"),
                    'author': entry.get('author', "No Author Found"),
                    'published': entry.get('published', ''),
                    'updated': entry.get('updated', ''),
                    'content': entry.content[0].value if 'content' in entry else entry.get('summary', '')
                }
            )
        response.append(feed_obj)
    return response

def _entry_is_recent(entry, cutoff):
    published_parsed = entry.get('published_parsed')
    updated_parsed = entry.get('updated_parsed')
    return (
        (published_parsed and datetime.fromtimestamp(timegm(published_parsed), tz=timezone.utc) >= cutoff) or
        (updated_parsed and datetime.fromtimestamp(timegm(updated_parsed), tz=timezone.utc) >= cutoff)
    )

def create_email_body(cleaned_feeds):
    sections = []
    for feed in cleaned_feeds:
        entries_html = []
        for entry in feed['entries']:
            entries_html.append(f"""
                <div style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 4px;">{escape(entry['title'])}</h3>
                    <p style="margin: 0 0 8px; color: #666; font-size: 12px;">
                        {escape(entry['author'])} &middot; {escape(entry['published'])}
                    </p>
                    <div>{entry['content']}</div>
                </div>
            """)
        sections.append(f"""
            <div style="margin-bottom: 32px;">
                <h2 style="border-bottom: 1px solid #ccc; padding-bottom: 4px;">{escape(feed['name'])}</h2>
                {''.join(entries_html) if entries_html else '<p>No entries.</p>'}
            </div>
        """)

    return f"""
        <html>
            <body style="font-family: sans-serif; max-width: 700px; margin: 0 auto;">
                {''.join(sections)}
            </body>
        </html>
    """

def send_email(email_body, email_from, email_to):
    ses = boto3.client('ses', region_name='us-west-1')
    try:
        response = ses.send_email(
            Source=email_from,
            Destination={
                'ToAddresses': [email_to]
            },
            Message={
                'Subject': {
                    'Data': f"Your Feed Summary For {datetime.today()}",
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': email_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error! {e.response['Error']['Message']}")

