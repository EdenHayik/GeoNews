"""
RSS Feeds Configuration
High-quality news and intelligence sources
"""

RSS_FEEDS = {
    # Israel - Mainstream & Official
    "israel_mainstream": {
        "Ynet": {
            "url": "http://www.ynet.co.il/Integration/StoryRss2.xml",
            "language": "he",
            "category": "news"
        },
        "Haaretz": {
            "url": "https://www.haaretz.co.il/cmlink/1.1617539",
            "language": "he",
            "category": "news"
        },
        "Israel Defense": {
            "url": "https://www.israeldefense.co.il/rss.xml",
            "language": "he",
            "category": "military"
        },
        "ITIC": {
            "url": "https://www.terrorism-info.org.il/he/feed/",
            "language": "he",
            "category": "intelligence"
        },
    },
    
    # Israel - OSINT, Blogs & Niche
    "israel_osint": {
        "Abu Ali Express": {
            "url": "https://abualiexpress.com/feed/",
            "language": "he",
            "category": "intelligence"
        },
        "Rotter": {
            "url": "https://rotter.net/rss/scoops.xml",
            "language": "he",
            "category": "news"
        },
        "Nziv": {
            "url": "https://nziv.net/feed/",
            "language": "he",
            "category": "intelligence"
        },
    },
    
    # International - Strategy & Intel
    "international": {
        "Wall Street Journal": {
            "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
            "language": "en",
            "category": "news"
        },
        "The War Zone": {
            "url": "https://www.twz.com/feed",
            "language": "en",
            "category": "military"
        },
        "ISW": {
            "url": "https://www.understandingwar.org/feeds.xml",
            "language": "en",
            "category": "intelligence"
        },
        "Bellingcat": {
            "url": "https://www.bellingcat.com/feed/",
            "language": "en",
            "category": "intelligence"
        },
        "Al-Monitor": {
            "url": "https://www.al-monitor.com/rss",
            "language": "en",
            "category": "news"
        },
    }
}


def get_all_feeds():
    """Get flat list of all feeds with their metadata"""
    all_feeds = []
    for group_name, feeds in RSS_FEEDS.items():
        for feed_name, feed_data in feeds.items():
            all_feeds.append({
                "name": feed_name,
                "url": feed_data["url"],
                "language": feed_data["language"],
                "category": feed_data["category"],
                "group": group_name
            })
    return all_feeds


def get_feeds_by_language(language: str):
    """Get all feeds for a specific language"""
    all_feeds = get_all_feeds()
    return [f for f in all_feeds if f["language"] == language]


def get_feeds_by_category(category: str):
    """Get all feeds for a specific category"""
    all_feeds = get_all_feeds()
    return [f for f in all_feeds if f["category"] == category]

