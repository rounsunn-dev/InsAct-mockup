import os
from dotenv import load_dotenv
from reddit_scraper import RedditProblemScraper

# Load environment variables
load_dotenv()

# Test the scraper
scraper = RedditProblemScraper()
problems = scraper.scrape_problems(domains=["healthcare", "climate"])

print(f"Found {len(problems)} problems:")
for i, problem in enumerate(problems[:3]):  # Show first 3
    print(f"\n{i+1}. Domain: {problem['domain']}")
    print(f"   Title: {problem['title']}")
    print(f"   Problem: {problem['problem'][:100]}...")
    print(f"   Source: {problem['source']}")