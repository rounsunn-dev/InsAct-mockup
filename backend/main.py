import os
import json
import random 
from openai import OpenAI
import pickle
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache for enriched stories
ENRICHED_CACHE = {}
CACHE_FILE = Path("enriched_cache.pkl")

app = FastAPI(title="InsAct API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    storyId: int

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class SearchRequest(BaseModel):
    query: str
    discover_opportunities: bool = False

def load_enrichment_cache():
    """Load cache from file"""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            pass
    return {}

def save_enrichment_cache():
    """Save cache to file"""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(ENRICHED_CACHE, f)
    except Exception as e:
        print(f"Failed to save cache: {e}")

def load_stories():
    """Load stories from seed file first, then generated file, then mock data"""
    # Try seed stories first (comprehensive database)
    seed_file = Path("seed_stories.json")
    if seed_file.exists():
        try:
            with open(seed_file, 'r') as f:
                stories = json.load(f)
            print(f"📚 Loaded {len(stories)} seed stories")
            return stories
        except Exception as e:
            print(f"Error loading seed stories: {e}")
    
    # Fallback to generated stories
    generated_file = Path("generated_stories.json")
    if generated_file.exists():
        try:
            with open(generated_file, 'r') as f:
                stories = json.load(f)
            print(f"📚 Loaded {len(stories)} generated stories")
            return stories
        except Exception as e:
            print(f"Error loading generated stories: {e}")
    
    # Final fallback to mock data
    try:
        from mock_data import MOCK_STORIES
        print("📚 Using mock stories as fallback")
        return MOCK_STORIES
    except ImportError:
        print("❌ No stories available")
        return []

# Load stories at startup
STORIES = load_stories()

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "InsAct API is running", 
        "version": "1.0.0",
        "stories_count": len(STORIES),
        "stories_source": "seed" if Path("seed_stories.json").exists() else "generated" if Path("generated_stories.json").exists() else "mock"
    }

# Health check
@app.get("/ping")
def ping():
    return {"message": "pong from backend 🚀"}

# Reload stories endpoint
@app.post("/reload-stories")
def reload_stories():
    """Reload stories from file"""
    STORIES = load_stories()
    return {
        "message": "Stories reloaded", 
        "count": len(STORIES),
        "source": "seed" if Path("seed_stories.json").exists() else "generated" if Path("generated_stories.json").exists() else "mock"
    }

# Get all stories for the feed
@app.get("/stories")
def get_stories():
    """Return all stories for the main feed"""
    return STORIES

# Get single story by ID
@app.get("/stories/{story_id}")
def get_story(story_id: int):
    """Return a specific story by ID"""
    story = next((s for s in STORIES if s["id"] == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

# Simple search (backward compatibility)
@app.get("/search")
def search_stories(q: str):
    """Simple search stories by query string"""
    if not q:
        return STORIES
    
    query_lower = q.lower()
    filtered_stories = []
    
    for story in STORIES:
        story_text = f"{story.get('title', '')} {story.get('preview', '')} {story.get('domain', '')} {story.get('opportunity', story.get('problem', ''))}".lower()
        
        if query_lower in story_text:
            filtered_stories.append(story)
    
    return filtered_stories

# Smart search with optional story generation
@app.post("/search-smart")
def smart_search_with_generation(search_request: SearchRequest):
    """Smart search with optional new story generation"""
    query = search_request.query
    
    if not query:
        return {"existing_stories": STORIES, "total_existing": len(STORIES), "new_stories_generated": False}
    
    # Enhanced search terms with AI (minimal usage)
    search_terms = [query.lower()]
    
    try:
        # Only use AI enhancement if we have many stories (cost control)
        if len(STORIES) > 20:
            search_prompt = f"User searched: '{query}'. Suggest 3 related keywords. Return comma-separated, no explanations."
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": search_prompt}],
                max_tokens=20,
                temperature=0.3
            )
            
            ai_keywords = response.choices[0].message.content.strip().split(',')
            search_terms.extend([kw.strip().lower() for kw in ai_keywords[:3] if kw.strip()])
    except Exception as e:
        # Continue with basic search silently
        pass
    
    # Search existing stories
    existing_matches = []
    for story in STORIES:
        story_text = f"{story.get('title', '')} {story.get('preview', '')} {story.get('domain', '')} {story.get('opportunity', story.get('problem', ''))}".lower()
        
        if any(term in story_text for term in search_terms):
            existing_matches.append(story)
    
    # Generate new story ONLY if no matches and discovery enabled
    new_stories_generated = False
    if len(existing_matches) == 0 and search_request.discover_opportunities:
        try:
            # Check if similar title already exists
            similar_exists = any(query.lower() in s.get('title', '').lower() for s in STORIES)
            
            if not similar_exists:
                discovery_prompt = f"""Based on search "{query}", create 1 market opportunity.

Format as JSON:
- "title": Opportunity name (under 60 chars)
- "domain": Category  
- "opportunity": Market gap (2 sentences)
- "gaps": What's missing in current solutions (2 sentences)
- "solution": Specific project to build (2 sentences)
- "preview": Hook (under 100 chars)

Return only valid JSON."""

                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": discovery_prompt}],
                    max_tokens=400,
                    temperature=0.8
                )
                
                content = response.choices[0].message.content.strip()
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                new_story = json.loads(content)
                new_story["id"] = random.randint(10000, 99999)
                new_story["generated_at"] = datetime.now().isoformat()
                new_story["source_type"] = "search_generated"
                
                # Add to stories list and save
                STORIES.append(new_story)
                
                # Save to appropriate file
                stories_file = "seed_stories.json" if Path("seed_stories.json").exists() else "generated_stories.json"
                with open(stories_file, 'w') as f:
                    json.dump(STORIES, f, indent=2)
                
                # Add to search results
                existing_matches.insert(0, new_story)
                new_stories_generated = True
                
        except Exception as e:
            # Fail silently
            pass
    
    return {
        "existing_stories": existing_matches[:15],
        "total_existing": len(existing_matches),
        "new_stories_generated": new_stories_generated,
        "search_enhanced": True
    }

# Cached story enrichment
@app.get("/stories/{story_id}/enriched")
def get_enriched_story(story_id: int):
    """Get cached enriched story or generate new one"""
    global ENRICHED_CACHE
    
    # Load cache if empty
    if not ENRICHED_CACHE:
        ENRICHED_CACHE = load_enrichment_cache()

     # ✅ CHECK CACHE FIRST
    if story_id in ENRICHED_CACHE:
        return ENRICHED_CACHE[story_id]
    
    # Find base story
    story = next((s for s in STORIES if s["id"] == story_id), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    print(f"🤖 Generating new enriched story for ID {story_id} (will cache)")
    
    try:
        # Enrichment_prompt
        enrichment_prompt = f"""You are a business analyst providing comprehensive market research. Expand this opportunity:

        Title: {story.get('title', '')}
        Domain: {story.get('domain', '')}
        Opportunity: {story.get('opportunity', story.get('problem', ''))}

        Provide detailed analysis as JSON:
        {{
        "related_startups": [
            {{"name": "Real Company Name", "description": "Detailed description", "approach": "Their unique approach", "funding": "Series A/B/etc", "market_position": "Leader/Challenger/Niche"}}
        ],
        "market_insights": "Comprehensive market analysis including size ($X billion), growth rate (X% CAGR), key trends, regulatory landscape, and future outlook",
        "implementation_guide": [
            "Phase 1: Market research and user validation (2-4 weeks)",
            "Phase 2: MVP development with core features (6-8 weeks)", 
            "Phase 3: Beta testing with 50+ users (4 weeks)",
            "Phase 4: Fundraising and team expansion",
            "Phase 5: Scale and market penetration"
        ],
        "success_metrics": "Detailed KPIs: user acquisition cost, lifetime value, retention rates, revenue per user, market share targets",
        "potential_challenges": [
            "Regulatory compliance: Solution - Partner with legal experts early",
            "User acquisition: Solution - Content marketing and partnerships",
            "Technical scalability: Solution - Cloud-first architecture"
        ],
        "competitive_landscape": "Analysis of 3-4 main competitors, their strengths/weaknesses, and differentiation opportunities",
        "revenue_model": "Detailed revenue streams: subscription ($X/month), transaction fees (X%), enterprise sales ($X/year)"
        }}

        Make it comprehensive and actionable for entrepreneurs."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": enrichment_prompt}],
            max_tokens=800,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '').replace('```', '').strip()
        
        enriched_data = json.loads(content)
        
        enriched_story = {
            **story,
            "enriched": True,
            "enrichment": enriched_data,
            "enriched_at": datetime.now().isoformat()
        }
        
        # Cache the result
        ENRICHED_CACHE[story_id] = enriched_story
        save_enrichment_cache()  # Persist to file

        return enriched_story
        
    except Exception as e:
        print(f"Enrichment failed: {e}")
        fallback = {**story, "enriched": False, "enrichment_error": str(e)}
        ENRICHED_CACHE[story_id] = fallback  # Cache even failures
        return fallback
    
@app.post("/clear-cache")
def clear_enrichment_cache():
    global ENRICHED_CACHE
    ENRICHED_CACHE = {}
    return {"message": "Cache cleared", "was_cached": len(ENRICHED_CACHE)}

# Free chat with smart templates
@app.post("/chat")
def chat_with_story(chat_data: ChatMessage):
    """Handle chat with smart template responses (minimal AI usage)"""
    
    # Find the story being discussed
    story = next((s for s in STORIES if s["id"] == chat_data.storyId), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Generate smart response using templates (FREE)
    response_text = generate_smart_response(chat_data.message, story)
    
    return ChatResponse(
        response=response_text,
        timestamp=datetime.now().isoformat()
    )

def generate_smart_response(message: str, story: Dict) -> str:
    """Generate responses using smart templates (FREE)"""
    
    message_lower = message.lower()
    domain = story.get("domain", "").lower()
    title = story.get("title", "this opportunity")
    
    # Skill-related questions
    if any(word in message_lower for word in ["skills", "tech", "technology", "learn", "how to build"]):
        tech_responses = {
            "healthcare": "Key technologies: Web/mobile development, healthcare APIs (FHIR), data privacy compliance (HIPAA), database management. Start with React/Node.js basics, then learn healthcare-specific regulations and APIs.",
            "education": "Key technologies: Learning management systems, analytics, user experience design, mobile development. Focus on React/Firebase, learning analytics, and educational psychology principles.",
            "finance": "Key technologies: Fintech APIs, security protocols, payment processing, data analytics. Learn about PCI compliance, banking APIs, and financial regulations alongside web development.",
            "local services": "Key technologies: Geolocation APIs, marketplace logic, mobile-first design, payment systems. Start with location-based services and local business needs analysis.",
            "agriculture": "Key technologies: IoT sensors, data analytics, mobile apps for rural areas, weather APIs. Focus on practical solutions that work with limited internet connectivity.",
            "real estate": "Key technologies: Property management systems, virtual tours, CRM integration, mapping APIs. Learn about property data APIs and real estate workflow automation.",
            "transportation": "Key technologies: GPS/mapping APIs, route optimization, mobile development, real-time data processing. Focus on logistics and user experience for mobility solutions.",
            "climate": "Key technologies: Environmental data APIs, IoT sensors, data visualization, sustainability metrics. Learn about carbon tracking and environmental monitoring systems.",
            "employment": "Key technologies: Job matching algorithms, skill assessment tools, profile management, communication platforms. Focus on connecting people with opportunities efficiently.",
            "technology": "Key technologies: Depends on the specific solution - could involve APIs, automation tools, data processing, or specialized development frameworks."
        }
        
        return tech_responses.get(domain, f"For {domain} projects: Start with web/mobile development fundamentals, learn domain-specific APIs and regulations, focus on user experience and practical problem-solving. Build MVPs and test with real users early.")
    
    # Getting started questions
    elif any(word in message_lower for word in ["start", "begin", "first step", "where to start"]):
        return f"To start with {title}: 1) Research existing solutions and identify specific gaps, 2) Interview 10-15 potential users to validate the problem, 3) Define your minimum viable product (MVP), 4) Choose simple, proven technologies, 5) Build a basic prototype, 6) Test with real users and iterate based on feedback."
    
    # Market/business questions
    elif any(word in message_lower for word in ["market", "business", "customers", "revenue", "money"]):
        market_insights = {
            "healthcare": "Healthcare market values solutions that improve patient outcomes and reduce costs. Focus on compliance, data security, and measurable health improvements. Revenue models include B2B sales to clinics, subscription fees, or per-transaction pricing.",
            "education": "Education market seeks personalized, accessible learning solutions. Revenue models include subscriptions, course fees, B2B sales to institutions, or freemium models with premium features.",
            "finance": "Fintech market rewards trust, security, and simplicity. Start with a narrow use case, ensure regulatory compliance, and build user trust gradually. Revenue through transaction fees, subscriptions, or premium features.",
            "local services": "Local services market values convenience and reliability. Revenue through commission on transactions, subscription fees for businesses, or advertising from local providers.",
            "agriculture": "Agriculture market focuses on efficiency and cost reduction. Revenue through equipment sharing fees, data insights subscriptions, or marketplace commissions.",
            "real estate": "Real estate market values efficiency and transparency. Revenue through transaction fees, subscription services for professionals, or premium listing features.",
            "transportation": "Transportation market seeks efficiency and cost reduction. Revenue through ride/delivery commissions, subscription fees, or premium route optimization features.",
            "climate": "Sustainability market growing rapidly with regulatory support. Revenue through compliance reporting fees, carbon credit trading, or sustainability consulting services.",
            "employment": "Employment market values successful matches and skill development. Revenue through placement fees, premium job listings, or subscription services for enhanced features.",
            "technology": "Technology market varies widely - focus on solving specific user problems with clear value propositions. Revenue depends on the specific solution and target market."
        }
        
        base_advice = f"The {domain} market has significant opportunities due to digital transformation needs. "
        domain_advice = market_insights.get(domain, "Focus on solving real user problems with simple, reliable solutions.")
        
        return base_advice + domain_advice + " Start by validating demand through user interviews, then build and test incrementally."
    
    # Implementation questions
    elif any(word in message_lower for word in ["implement", "build", "develop", "create"]):
        return f"For implementing {title}: Use proven technology stacks, start with core functionality only, prioritize user experience over features, ensure mobile responsiveness, plan for scalability but don't over-engineer initially. Launch quickly and improve based on user feedback."
    
    # Challenges/problems
    elif any(word in message_lower for word in ["challenge", "difficult", "problem", "hard"]):
        return f"Common challenges with {title}: User acquisition, technical complexity, regulatory requirements, and market competition. Overcome these by starting small, focusing on one user segment, building strategic partnerships, and staying close to your users' needs."
    
    # Default response
    else:
        return f"Great question about {title}! This {domain} opportunity has strong potential. The key is identifying the specific gap in current solutions and building something users actually need. What specific aspect interests you most - the technical implementation, market approach, or user validation?"

# Get available domains
@app.get("/domains")
def get_domains():
    """Get list of available story domains"""
    domains = list(set([story.get("domain", "Unknown") for story in STORIES]))
    return {"domains": sorted(domains)}

# Health check
@app.get("/health")
def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "stories_loaded": len(STORIES),
        "domains_available": len(set([story.get("domain", "Unknown") for story in STORIES])),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "seed_stories_exist": Path("seed_stories.json").exists(),
        "generated_stories_exist": Path("generated_stories.json").exists(),
        "cached_enrichments": len(ENRICHED_CACHE),
        "timestamp": datetime.now().isoformat()
    }