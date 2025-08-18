import praw
import os
from typing import List, Dict
from datetime import datetime

class RedditProblemScraper:
    def __init__(self):
        # You'll need Reddit API credentials (free)
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID", "your_client_id"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", "your_secret"),
            user_agent="InsAct-scraper/1.0"
        )
    
    def scrape_problems(self, domains: List[str] = None) -> List[Dict]:
        """Scrape problems from relevant subreddits"""
        if not domains:
            domains = ["healthcare", "climate", "technology", "education"]
        
        subreddits = {
            "healthcare": ["HealthIT", "medicine", "healthcare"],
            "climate": ["climatechange", "environment", "sustainability"],
            "technology": ["programming", "startups", "entrepreneur"],
            "education": ["education", "teaching", "EdTech"]
        }
        
        problems = []
        
        for domain in domains:
            print(f"Scraping {domain} problems...")
            
            for subreddit_name in subreddits.get(domain, []):
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get hot posts from the last week
                    for post in subreddit.hot(limit=10):
                        if len(post.selftext) > 100:  # Filter for substantial posts
                            problems.append({
                                "domain": domain.title(),
                                "title": post.title,
                                "problem": post.selftext[:500] + "...",
                                "source": f"r/{subreddit_name}",
                                "url": f"https://reddit.com{post.permalink}",
                                "score": post.score,
                                "scraped_at": datetime.now().isoformat()
                            })
                
                except Exception as e:
                    print(f"Error scraping r/{subreddit_name}: {e}")
                    continue
        
        return problems