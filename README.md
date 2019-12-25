# FeedingFrenzy
An AWS Lambda-based python application which consolidates RSS feeds and provides a daily email digest


## TODO:
* Implement AWS Lambda framework
* Create a list of feeds to pull from
* Implement code which actually goes and scrapes RSS feeds (parallelize, I think)
* Check against some sort of datastore (DB?) to avoid grabbing duplicate stories
* Compile scraped stories into singular report
* Email report to me