from startup_scraper import StartupScraper

scraper = StartupScraper()

# Test startup scraping
startups = scraper.scrape_product_hunt_startups(["healthcare", "climate"])
print(f"Found {len(startups)} startups:")

for startup in startups[:3]:
    print(f"\n- {startup['name']} ({startup['domain']})")
    print(f"  Description: {startup['description']}")
    print(f"  Pathway: {startup['pathway']}")

# Test GitHub projects
projects = scraper.scrape_github_projects(["healthcare", "climate"])
print(f"\nFound {len(projects)} GitHub projects:")

for project in projects[:2]:
    print(f"\n- {project['name']} ⭐{project['stars']}")
    print(f"  Description: {project['description']}")