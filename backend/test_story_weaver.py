from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from pathlib import Path
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="InsAct API", version="1.0.0")

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class ChatMessage(BaseModel):
    message: str
    storyId: int

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class SearchQuery(BaseModel):
    query: str

def load_stories():
    """Load stories from generated file or fallback to mock data"""
    stories_file = Path("generated_stories.json")
    if stories_file.exists():
        try:
            with open(stories_file, 'r') as f:
                stories = json.load(f)
            print(f"📚 Loaded {len(stories)} generated stories")
            return stories
        except Exception as e:
            print(f"Error loading generated stories: {e}")
    
    # Fallback to mock data
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
        "stories_source": "generated" if Path("generated_stories.json").exists() else "mock"
    }

# Health check
@app.get("/ping")
def ping():
    return {"message": "pong from backend 🚀"}

# Reload stories endpoint (useful for development)
@app.post("/reload-stories")
def reload_stories():
    """Reload stories from file"""
    global STORIES
    STORIES = load_stories()
    return {
        "message": "Stories reloaded", 
        "count": len(STORIES),
        "source": "generated" if Path("generated_stories.json").exists() else "mock"
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

# AI-powered search endpoint
@app.get("/search")
def search_stories(q: str):
    """AI-enhanced search for stories"""
    if not q:
        return STORIES
    
    query_lower = q.lower()
    
    # First: Simple keyword matching
    keyword_matches = []
    for story in STORIES:
        if (query_lower in story.get("title", "").lower() or 
            query_lower in story.get("preview", "").lower() or 
            query_lower in story.get("domain", "").lower() or
            query_lower in story.get("problem", "").lower() or
            query_lower in story.get("solution", "").lower()):
            keyword_matches.append(story)
    
    # If we have keyword matches, return them
    if keyword_matches:
        return keyword_matches
    
    # If no keyword matches, use AI to find semantic matches
    try:
        # Use ChatGPT to understand the search intent and match to domains/topics
        search_prompt = f"""Given this search query: "{q}"

Available story domains and topics:
{[story.get('domain') + ': ' + story.get('title', '') for story in STORIES[:5]]}

Which domains or story types would best match this search? Respond with just the most relevant domain names (Healthcare, Climate, AI, etc.) separated by commas, or "none" if no match.

Search query: {q}
Best matching domains:"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": search_prompt}],
            max_tokens=50,
            temperature=0.3
        )
        
        suggested_domains = response.choices[0].message.content.strip().lower()
        
        # Match stories based on AI suggestions
        ai_matches = []
        for story in STORIES:
            story_domain = story.get("domain", "").lower()
            if story_domain in suggested_domains:
                ai_matches.append(story)
        
        return ai_matches if ai_matches else STORIES
        
    except Exception as e:
        print(f"AI search failed: {e}")
        # Fallback to returning all stories
        return STORIES

# AI-powered chat endpoint
@app.post("/chat")
def chat_with_story(chat_data: ChatMessage):
    """Handle chat messages with ChatGPT integration"""
    
    # Find the story being discussed
    story = next((s for s in STORIES if s["id"] == chat_data.storyId), None)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Create context-aware prompt for ChatGPT
    context_prompt = f"""You are an AI assistant helping students explore a specific project opportunity. 

Story Context:
- Title: {story.get('title', 'Unknown')}
- Domain: {story.get('domain', 'Unknown')}
- Problem: {story.get('problem', 'No problem description')}
- Current Pathway: {story.get('pathway', 'No pathway description')}
- Opportunity: {story.get('solution', 'No solution description')}

User Question: {chat_data.message}

Provide a helpful, specific response about this opportunity. Focus on:
- Practical implementation advice
- Required technical skills
- Getting started steps
- Market insights
- Related technologies or approaches

Keep your response concise (2-3 sentences) and actionable."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": context_prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"ChatGPT API failed: {e}")
        # Fallback to intelligent mock responses
        message_lower = chat_data.message.lower()
        
        if "problem" in message_lower:
            ai_response = f"The core problem in {story.get('domain', 'this area')} is: {story.get('problem', 'Not specified')}"
        elif "solution" in message_lower or "opportunity" in message_lower:
            ai_response = f"The opportunity here is: {story.get('solution', 'Not specified')}"
        elif "skills" in message_lower or "tech" in message_lower or "how" in message_lower:
            domain = story.get('domain', '').lower()
            if 'healthcare' in domain:
                ai_response = "Key skills: Python/JavaScript, healthcare APIs, data privacy (HIPAA), and basic medical workflow understanding. Start with a simple prototype using public health datasets."
            elif 'climate' in domain:
                ai_response = "Key skills: Data visualization, API integration, carbon accounting basics, and web development. Begin by connecting to existing carbon calculation APIs."
            else:
                ai_response = "Key skills: Full-stack development, database design, and domain expertise. Start with user research and build a minimal viable product (MVP)."
        elif "start" in message_lower or "begin" in message_lower:
            ai_response = f"To get started with {story.get('title', 'this project')}: 1) Research existing solutions and their limitations, 2) Define your MVP scope, 3) Choose your tech stack, and 4) build a simple prototype."
        else:
            ai_response = f"Great question about {story.get('title', 'this opportunity')}! The key is identifying the specific gap between what exists and what's needed in {story.get('domain', 'this space')}."
    
    return ChatResponse(
        response=ai_response,
        timestamp=datetime.now().isoformat()
    )

# Generate new stories endpoint (triggers scraping and AI generation)
@app.post("/generate-stories")
def generate_new_stories():
    """Trigger story generation pipeline"""
    try:
        from story_weaver import StoryWeaver
        
        weaver = StoryWeaver()
        new_stories = weaver.generate_stories(domains=["healthcare", "climate", "ai"], max_stories_per_domain=2)
        
        # Save to file
        weaver.save_stories_to_file(new_stories)
        
        # Reload stories in memory
        global STORIES
        STORIES = load_stories()
        
        return {
            "message": "New stories generated successfully",
            "count": len(new_stories),
            "domains": ["healthcare", "climate", "ai"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

# Get available domains
@app.get("/domains")
def get_domains():
    """Get list of available story domains"""
    domains = list(set([story.get("domain", "Unknown") for story in STORIES]))
    return {"domains": domains}

# Health check with full system status
@app.get("/health")
def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "stories_loaded": len(STORIES),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "generated_stories_exist": Path("generated_stories.json").exists(),
        "timestamp": datetime.now().isoformat()
    }