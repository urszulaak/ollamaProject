import feedparser
from Updater import Updater

class RSSUpdater:
    def __init__(self, rss_url, limit=19):
        self.rss_url = rss_url
        self.limit = limit
        self.data = {}

    def fetch_rss(self):
        try:
            feed = feedparser.parse(self.rss_url)
            rss_dict = {}
            for entry in feed.entries[:self.limit]:
                title = entry.title
                description = getattr(entry, "summary", "")
                rss_dict[title] = description
            self.data = rss_dict
            return rss_dict
        except Exception as e:
            print("Error")
            self.data = {}
            return {}