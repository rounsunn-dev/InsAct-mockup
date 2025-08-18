import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()

class ComprehensiveSeedGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def clear_existing_data(self):
        """Clear existing databases for fresh start"""
        files_to_clear = [
            "problem_database.json",
            "generated_stories.json", 
            "seed_stories.json"
        ]
        
        for file in files_to_clear:
            if Path(file).exists():
                os.remove(file)
                print(f"🗑️ Deleted {file}")
    
    def generate_domain_opportunities(self, domain: str, count: int = 8) -> list:
        """Generate diverse opportunities for a specific domain"""
        
        domain_contexts = {
            "Healthcare": "medical care, patient experience, healthcare accessibility, medical technology, wellness",
            "Education": "learning, skill development, knowledge sharing, educational technology, academic support",
            "Finance": "personal finance, investment, payments, financial planning, money management",
            "Local Services": "community services, local businesses, neighborhood solutions, hyperlocal needs",
            "Technology": "software solutions, automation, digital transformation, tech innovation",
            "Agriculture": "farming, food production, rural technology, agricultural efficiency",
            "Transportation": "mobility, logistics, public transport, delivery services, travel",
            "Climate": "sustainability, environmental solutions, green technology, carbon reduction",
            "Employment": "job opportunities, gig economy, skill development, career advancement",
            "Real Estate": "property management, housing solutions, rental services, property technology"
        }
        
        context = domain_contexts.get(domain, "general business and technology solutions")
        
        prompt = f"""Generate {count} diverse market opportunities in the {domain} domain focused on {context}.

Each opportunity should be:
- Realistic and buildable by individuals or small teams
- Address real market gaps or user needs
- Have clear revenue potential
- Be accessible to people with basic to intermediate skills
- Cover different sub-areas within {domain}

For each opportunity, provide:
- "title": Opportunity name (under 55 chars)
- "opportunity_description": The market gap and potential (2-3 sentences)
- "target_audience": Who would use/pay for this
- "market_context": Why this opportunity exists now

Return as JSON array of {count} opportunities."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            opportunities = json.loads(content)
            return opportunities
            
        except Exception as e:
            print(f"Failed to generate {domain} opportunities: {e}")
            return []
    
    def convert_to_story_format(self, opportunity: dict, domain: str) -> dict:
        """Convert opportunity to story format using AI"""
        
        prompt = f"""Convert this opportunity into a compelling story format:

Opportunity: {opportunity.get('title', 'Unknown')}
Description: {opportunity.get('opportunity_description', '')}
Target: {opportunity.get('target_audience', '')}
Context: {opportunity.get('market_context', '')}
Domain: {domain}

Generate a JSON response with:
1. "title": Compelling headline (under 60 chars)
2. "domain": "{domain}"
3. "opportunity": The market opportunity (2-3 sentences, positive framing)
4. "gaps": What's missing in current solutions (2-3 sentences)
5. "solution": Specific project to fill the gap (2-3 sentences, actionable)
6. "preview": One-sentence hook (under 100 chars)

Focus on actionable opportunities for anyone to build, not just students.
Return only valid JSON."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            story_data = json.loads(content)
            
            # Add metadata
            story_data["id"] = random.randint(1000, 9999)
            story_data["generated_at"] = datetime.now().isoformat()
            story_data["source_type"] = "comprehensive_seed"
            
            return story_data
            
        except Exception as e:
            print(f"Failed to convert opportunity to story: {e}")
            return None
    
    def generate_comprehensive_seeds(self):
        """Generate comprehensive seed stories across all domains"""
        
        domains = [
            "Healthcare", "Education", "Finance", "Local Services", 
            "Technology", "Agriculture", "Transportation", "Climate",
            "Employment", "Real Estate"
        ]
        
        all_stories = []
        
        print("🌱 Generating comprehensive seed stories...")
        print("This will use ~50-60 AI requests to create exhaustive content")
        
        for domain in domains:
            print(f"\n📖 Generating {domain} opportunities...")
            
            # Generate 6-8 opportunities per domain
            opportunities = self.generate_domain_opportunities(domain, count=6)
            
            # Convert each opportunity to story format
            for i, opp in enumerate(opportunities):
                print(f"  Converting {i+1}/{len(opportunities)}: {opp.get('title', 'Unknown')[:40]}...")
                
                story = self.convert_to_story_format(opp, domain)
                if story:
                    all_stories.append(story)
                    print(f"    ✅ Created: {story.get('title', 'Untitled')}")
                else:
                    print(f"    ❌ Failed to create story")
        
        # Save all stories
        if all_stories:
            with open('seed_stories.json', 'w') as f:
                json.dump(all_stories, f, indent=2)
            
            print(f"\n🎉 Generated {len(all_stories)} comprehensive seed stories!")
            print(f"📊 Coverage: {len(domains)} domains with ~{len(all_stories)//len(domains)} stories each")
            print(f"💾 Saved to seed_stories.json")
            
            # Show domain distribution
            domain_count = {}
            for story in all_stories:
                domain = story.get('domain', 'Unknown')
                domain_count[domain] = domain_count.get(domain, 0) + 1
            
            print(f"\n📈 Domain Distribution:")
            for domain, count in sorted(domain_count.items()):
                print(f"  {domain}: {count} stories")
        
        return all_stories

def main():
    generator = ComprehensiveSeedGenerator()
    
    print("🚀 Comprehensive Seed Generation")
    print("=" * 50)
    
    # Ask for confirmation
    confirm = input("This will clear existing data and generate ~60 new stories using AI. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled")
        return
    
    # Clear existing data
    generator.clear_existing_data()
    
    # Generate comprehensive seeds
    stories = generator.generate_comprehensive_seeds()
    
    if stories:
        print(f"\n✅ Success! Generated {len(stories)} stories across 10 domains")
        print("🚀 Ready to launch with comprehensive content!")
    else:
        print("❌ Failed to generate stories")

if __name__ == "__main__":
    main()