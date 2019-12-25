import boto3

def import_rss_feed_urls():
    list_of_feed_urls = []

    s3 = boto3.client('s3')
    response = s3.get_object(Bucket='feedingfrenzy', Key='rss_feeds.txt')
    if response:
        string_body = response['Body'].read().decode("utf-8")
        list_of_feed_urls = string_body.split(',')
    
    return list_of_feed_urls
