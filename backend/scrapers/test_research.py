from research_scraper import ResearchScraper

scraper = ResearchScraper()

# Test ArXiv papers
print("=== ArXiv Papers ===")
arxiv_papers = scraper.scrape_arxiv_papers(["healthcare", "climate"])
print(f"Found {len(arxiv_papers)} ArXiv papers:")

for paper in arxiv_papers[:2]:
    print(f"\n- {paper['title']}")
    print(f"  Domain: {paper['domain']}")
    print(f"  Abstract: {paper['abstract'][:100]}...")
    print(f"  Published: {paper['published']}")

# Test curated research
print("\n=== Google Scholar Papers ===")
scholar_papers = scraper.scrape_google_scholar(["healthcare", "climate"])
print(f"Found {len(scholar_papers)} Scholar papers:")

for paper in scholar_papers[:2]:
    print(f"\n- {paper['title']}")
    print(f"  Citations: {paper['citations']}")
    print(f"  Abstract: {paper['abstract'][:100]}...")

# Test IEEE papers
print("\n=== IEEE Papers ===")
ieee_papers = scraper.scrape_ieee_papers(["healthcare", "climate"])
print(f"Found {len(ieee_papers)} IEEE papers:")

for paper in ieee_papers[:2]:
    print(f"\n- {paper['title']}")
    print(f"  Research Approach: {paper['research_approach'][:100]}...")