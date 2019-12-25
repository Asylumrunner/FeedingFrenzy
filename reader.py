import feedparser

def read_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    return [trim_entry(entry) for entry in feed.entries]

def trim_entry(entry):
    return {
        'date': "{}/{}/{}".format(entry.published_parsed.tm_year, entry.published_parsed.tm_mon, entry.published_parsed.tm_mday),
        'title': entry.title,
        'link': entry.link,
        'author': entry.author,
        'summary': entry.summary
    }