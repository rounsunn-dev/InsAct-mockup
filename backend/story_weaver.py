import os
import json
from openai import OpenAI
from typing import List, Dict, Tuple
from scrapers.reddit_scraper import RedditProblemScraper
from scrapers.startup_scraper import StartupScraper
from scrapers.research_scraper import ResearchScraper
from dotenv import load_dotenv
import random
from datetime import datetime
from problem_database import problem_db
load_dotenv()

class StoryWeaver:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.reddit_scraper = RedditProblemScraper()
        self.startup_scraper = StartupScraper()
        self.research_scraper = ResearchScraper()
    
    def scrape_all_data(self, domains: List[str] = None) -> Dict:
        """Scrape problems, startups, and research for given domains"""
        if not domains:
            domains = ["healthcare", "climate"]
        
        print("🔍 Scraping all data sources...")
        
        # Get all data
        problems = self.reddit_scraper.scrape_problems(domains)
        startups = self.startup_scraper.scrape_product_hunt_startups(domains)
        github_projects = self.startup_scraper.scrape_github_projects(domains)
        arxiv_papers = self.research_scraper.scrape_arxiv_papers(domains)
        scholar_papers = self.research_scraper.scrape_google_scholar(domains)
        ieee_papers = self.research_scraper.scrape_ieee_papers(domains)
        
        # Combine research sources
        research = arxiv_papers + scholar_papers + ieee_papers
        pathway_sources = startups + github_projects
        
        print(f"📊 Scraped: {len(problems)} problems, {len(pathway_sources)} pathways, {len(research)} research papers")
        
        return {
            "problems": problems,
            "pathways": pathway_sources,
            "research": research
        }
    
    def match_related_content(self, data: Dict, domain: str) -> List[Tuple]:
        """Match problems with related pathways and research within a domain"""
        domain_problems = [p for p in data["problems"] if p["domain"].lower() == domain.lower()]
        domain_pathways = [p for p in data["pathways"] if p["domain"].lower() == domain.lower()]
        domain_research = [r for r in data["research"] if r["domain"].lower() == domain.lower()]
        
        matches = []
        
        # Create matches: each problem gets a pathway and research if available
        for i in range(min(4, len(domain_problems))):  # Limit to 4 stories per domain
            problem = domain_problems[i] if i < len(domain_problems) else None
            pathway = domain_pathways[i % len(domain_pathways)] if domain_pathways else None
            research = domain_research[i % len(domain_research)] if domain_research else None
            
            if problem:  # At minimum we need a problem
                matches.append((problem, pathway, research))
        
        print(f"🔗 Created {len(matches)} matches for {domain}")
        return matches
    
    def generate_story_with_ai(self, problem: Dict, pathway: Dict = None, research: Dict = None) -> Dict:
        """Use ChatGPT to weave problem + pathway + research into a cohesive story"""
        
        # Build context for AI
        context_parts = []
        
        if problem:
            problem_text = problem.get('problem', problem.get('selftext', problem.get('title', 'Unknown problem')))
            context_parts.append(f"PROBLEM: {problem.get('title', 'Unknown')}\nDescription: {problem_text}")
        
        if pathway:
            pathway_desc = pathway.get('description', pathway.get('pathway', 'Unknown solution attempt'))
            context_parts.append(f"CURRENT SOLUTION: {pathway.get('name', 'Unknown')}\nDescription: {pathway_desc}")
        
        if research:
            research_desc = research.get('abstract', research.get('research_approach', 'Unknown research'))
            context_parts.append(f"RESEARCH: {research.get('title', 'Unknown')}\nDetails: {research_desc}")
        
        context = "\n\n".join(context_parts)
        
        # AI prompt for story generation
        prompt = f"""You are an expert at identifying market opportunities and gaps for student projects. Given information about a problem, current solutions, and research, create a compelling story that reveals a specific buildable opportunity.

{context}

Generate a JSON response with these exact fields:
1. "title": Compelling headline capturing the opportunity (under 60 chars)
2. "domain": The domain (Healthcare, Climate, AI, etc.)
3. "problem": Clear 2-3 sentence problem statement focusing on the real pain point
4. "pathway": What's currently being tried (mention companies/research, 2-3 sentences)
5. "solution": Specific gap and student project opportunity (2-3 sentences, be concrete about what to build)
6. "preview": One-sentence hook under 100 chars

Focus on:
- Identifying specific gaps in current approaches
- Suggesting realistic, buildable projects for students
- Being actionable and exciting
- Realistic scope for a student project

Return only valid JSON."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            # Parse AI response
            story_text = response.choices[0].message.content.strip()
            
            # Clean up response (remove markdown if present)
            if story_text.startswith('```json'):
                story_text = story_text.replace('```json', '').replace('```', '').strip()
            
            # Try to parse as JSON
            try:
                story_data = json.loads(story_text)
                
                # Add metadata
                story_data["id"] = random.randint(1000, 9999)
                story_data["generated_at"] = datetime.now().isoformat()
                story_data["sources"] = {
                    "problem_source": problem.get("source", "Unknown") if problem else None,
                    "pathway_source": pathway.get("source", "Unknown") if pathway else None,
                    "research_source": research.get("source", "Unknown") if research else None
                }
                
                return story_data
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse AI response as JSON: {e}")
                print(f"Raw response: {story_text}")
                return None
                
        except Exception as e:
            print(f"AI story generation failed: {e}")
            return None
    
    def generate_stories(self, domains: List[str] = None, max_stories_per_domain: int = 3) -> List[Dict]:
        """Complete pipeline: scrape data → match content → generate AI stories"""
        if not domains:
            domains = ["healthcare", "climate"]
        
        print("🤖 Starting AI-powered story generation pipeline...")
        
        # Step 1: Scrape all data
        all_data = self.scrape_all_data(domains)
        
        stories = []
        
        # Step 2: Generate stories for each domain
        for domain in domains:
            print(f"\n📖 Generating {domain} stories...")
            
            # Step 3: Match related content
            matches = self.match_related_content(all_data, domain)
            
            # Step 4: Generate AI stories
            for i, (problem, pathway, research) in enumerate(matches[:max_stories_per_domain]):
                print(f"  🎯 Generating story {i+1}/{min(len(matches), max_stories_per_domain)}...")
                
                story = self.generate_story_with_ai(problem, pathway, research)
                if story:
                    stories.append(story)
                    print(f"  ✅ Generated: {story.get('title', 'Untitled')}")
                else:
                    print(f"  ❌ Failed to generate story")
        
        print(f"\n🎉 Generated {len(stories)} total stories!")
        return stories


    def generate_stories_incremental(self, domains: List[str] = None, max_new_stories: int = 3) -> List[Dict]:
        """Generate stories only for unprocessed problems"""
        print("🔄 Starting incremental story generation...")
        
        # Get unprocessed problems from database
        unprocessed = problem_db.get_unprocessed_problems()
        
        if not unprocessed:
            print("✅ No new problems to process")
            return []
        
        print(f"📝 Found {len(unprocessed)} unprocessed problems")
        
        # Filter by domains if specified
        if domains:
            unprocessed = [p for p in unprocessed if p["domain"].lower() in [d.lower() for d in domains]]
            print(f"🎯 Filtered to {len(unprocessed)} problems in domains: {domains}")
        
        stories = []
        
        # Get some pathway and research data for context
        try:
            startups = self.startup_scraper.scrape_product_hunt_startups(domains or ["education", "healthcare"])
            research = self.research_scraper.scrape_google_scholar(domains or ["education", "healthcare"])
        except:
            startups = []
            research = []
        
        # Process each unprocessed problem
        for i, problem in enumerate(unprocessed[:max_new_stories]):
            print(f"🎯 Processing problem {i+1}/{min(len(unprocessed), max_new_stories)}: {problem['title']}")
            
            # Find related pathways and research (simplified for now)
            domain_lower = problem["domain"].lower()
            
            # Get a relevant startup/pathway
            relevant_startup = next(
                (s for s in startups if s.get("domain", "").lower() == domain_lower), 
                {"name": f"Sample {problem['domain']} Solution", 
                "description": f"Current approaches in {problem['domain']} are addressing similar challenges but gaps remain."}
            )
            
            # Get relevant research
            relevant_research = next(
                (r for r in research if r.get("domain", "").lower() == domain_lower),
                {"title": f"{problem['domain']} Research Insights", 
                "abstract": f"Recent research in {problem['domain']} shows opportunities for innovation."}
            )
            
            # Generate story with AI
            story = self.generate_story_with_ai(problem, relevant_startup, relevant_research)
            
            if story:
                stories.append(story)
                # Mark as processed in database
                problem_db.mark_story_generated(problem["id"])
                print(f"  ✅ Generated: {story.get('title', 'Untitled')}")
            else:
                print(f"  ❌ Failed to generate story")
        
        print(f"\n🎉 Generated {len(stories)} new stories from unprocessed problems!")
        return stories

    def save_stories_to_file(self, stories: List[Dict], filename: str = "generated_stories.json", append: bool = True):
        """Save generated stories to JSON file with append option"""
        from pathlib import Path
        
        existing_stories = []
        
        if append and Path(filename).exists():
            try:
                with open(filename, 'r') as f:
                    existing_stories = json.load(f)
                print(f"📚 Found {len(existing_stories)} existing stories")
            except Exception as e:
                print(f"Error reading existing stories: {e}")
        
        # Combine existing + new stories (avoid duplicates by title)
        existing_titles = {story.get('title', '') for story in existing_stories}
        new_stories = [story for story in stories if story.get('title', '') not in existing_titles]
        
        all_stories = existing_stories + new_stories
        
        with open(filename, 'w') as f:
            json.dump(all_stories, f, indent=2)
        
        print(f"💾 Saved {len(all_stories)} total stories ({len(new_stories)} new, {len(existing_stories)} existing)")
        return len(new_stories)

if __name__ == "__main__":
    # Test the complete pipeline
    weaver = StoryWeaver()
    stories = weaver.generate_stories(domains=["healthcare", "climate"], max_stories_per_domain=2)
    
    # Display results
    print("\n" + "="*80)
    print("🚀 GENERATED INSACT STORIES")
    print("="*80)
    
    for i, story in enumerate(stories, 1):
        print(f"\n{i}. {story.get('title', 'Untitled')}")
        print(f"   Domain: {story.get('domain', 'Unknown')}")
        print(f"   Preview: {story.get('preview', 'No preview')}")
        print(f"   Problem: {story.get('problem', 'No problem')[:100]}...")
        print(f"   Sources: {story.get('sources', {})}")
    
    # Save to file
    weaver.save_stories_to_file(stories)