import concurrent.futures
from reader import read_rss_feed
from env_reader import import_rss_feed_urls

def lambda_handler(event, context):
    main()

def main():
    urls = import_rss_feed_urls()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(read_rss_feed, urls)
    
    cleaned_data = []

    for feed in concurrent.futures.as_completed(results):
        cleaned_data.extend(feed)
    
    populate_datastore(cleaned_data)
    email_summary(cleaned_data)