import os
from openai import OpenAI
from problem_database import problem_db
from dotenv import load_dotenv
import json

load_dotenv()

class OpportunityScout:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def discover_opportunities(self, focus_area: str, target_audience: str, location: str = "India") -> list:
        """Use AI to discover market opportunities in a specific area"""
        
        prompt = f"""You are an expert market opportunity scout. Find 5 UNEXPLORED MARKET OPPORTUNITIES (not problems) in {focus_area} for {target_audience} in {location}.

Focus on:
- Market GAPS where current solutions don't exist or are inadequate
- Opportunities that students/young professionals can realistically build
- Monetizable opportunities with clear revenue potential
- Local/regional advantages that can be leveraged

For each opportunity, provide:
1. "domain": Category (Healthcare, EdTech, Local Services, etc.)
2. "title": Compelling opportunity title (under 60 chars)
3. "opportunity": The market gap/opportunity (2-3 sentences)
4. "market_size": Who would pay for this and why
5. "why_now": Why this opportunity exists now
6. "barriers": What's preventing others from solving this

Format as JSON array of 5 opportunities.

Focus area: {focus_area}
Target audience: {target_audience}
Location: {location}

Return only valid JSON array."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            opportunities = json.loads(content)
            return opportunities
            
        except Exception as e:
            print(f"Error discovering opportunities: {e}")
            return []
    
    def add_opportunities_to_database(self, opportunities: list, source: str = "AI Discovery"):
        """Add discovered opportunities to problem database"""
        added_count = 0
        
        for opp in opportunities:
            try:
                # Convert opportunity format to problem database format
                problem_data = problem_db.add_problem(
                    domain=opp.get("domain", "Unknown"),
                    title=opp.get("title", "Unknown Opportunity"),
                    problem=f"OPPORTUNITY: {opp.get('opportunity', '')} Market: {opp.get('market_size', '')} Timing: {opp.get('why_now', '')}",
                    source=source,
                    source_type="ai_discovery"
                )
                added_count += 1
                print(f"✅ Added: {opp.get('title', 'Unknown')}")
            except Exception as e:
                print(f"❌ Failed to add: {opp.get('title', 'Unknown')} - {e}")
        
        return added_count

def interactive_opportunity_discovery():
    """Interactive opportunity discovery session"""
    scout = OpportunityScout()
    
    print("🔍 AI Opportunity Discovery")
    print("=" * 40)
    
    focus_area = input("Focus area (Healthcare, Education, Local Services, etc.): ")
    target_audience = input("Target audience (College students, Small business, Youth, etc.): ")
    location = input("Location (India, specific city, global) [India]: ") or "India"
    
    print(f"\n🤖 Discovering opportunities in {focus_area} for {target_audience} in {location}...")
    
    opportunities = scout.discover_opportunities(focus_area, target_audience, location)
    
    if opportunities:
        print(f"\n🎯 Found {len(opportunities)} opportunities:")
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp.get('title', 'Unknown')}")
            print(f"   Domain: {opp.get('domain', 'Unknown')}")
            print(f"   Opportunity: {opp.get('opportunity', 'No description')[:100]}...")
        
        add_to_db = input(f"\n💾 Add these {len(opportunities)} opportunities to database? (y/n): ")
        if add_to_db.lower() == 'y':
            added = scout.add_opportunities_to_database(opportunities, f"AI Discovery - {focus_area}")
            print(f"✅ Added {added} opportunities to database")
            print("💡 Run 'python auto_generate.py' to generate stories!")
    else:
        print("❌ No opportunities discovered")

if __name__ == "__main__":
    interactive_opportunity_discovery()