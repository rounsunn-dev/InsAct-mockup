import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class ProblemDatabase:
    def __init__(self, db_file: str = "problem_database.json"):
        self.db_file = Path(db_file)
        self.problems = self.load_database()
    
    def load_database(self) -> List[Dict]:
        """Load existing problems from database"""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                print(f"📚 Loaded {len(data)} problems from database")
                return data
            except Exception as e:
                print(f"Error loading database: {e}")
        
        print("📝 Creating new problem database")
        return []
    
    def generate_problem_id(self, title: str, domain: str) -> str:
        """Generate unique ID for a problem"""
        content = f"{title.lower().strip()}_{domain.lower().strip()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def add_problem(self, domain: str, title: str, problem: str, source: str, 
                   source_type: str = "user_input") -> Dict:
        """Add a new problem to database"""
        
        problem_id = self.generate_problem_id(title, domain)
        
        # Check if problem already exists
        existing = self.get_problem_by_id(problem_id)
        if existing:
            print(f"⚠️  Problem already exists: {title}")
            return existing
        
        new_problem = {
            "id": problem_id,
            "domain": domain.title(),
            "title": title.strip(),
            "problem": problem.strip(),
            "source": source,
            "source_type": source_type,  # user_input, reddit, manual, chat_suggestion
            "added_at": datetime.now().isoformat(),
            "story_generated": False,
            "user_votes": 0,  # For community feedback
            "tags": self.extract_tags(title + " " + problem)
        }
        
        self.problems.append(new_problem)
        self.save_database()
        print(f"✅ Added problem: {title} (ID: {problem_id})")
        return new_problem
    
    def extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from problem text"""
        keywords = ['ai', 'mobile', 'web', 'data', 'automation', 'api', 'ml', 'blockchain', 
                   'iot', 'cloud', 'security', 'social', 'marketplace', 'education']
        
        text_lower = text.lower()
        tags = [keyword for keyword in keywords if keyword in text_lower]
        return tags[:5]  # Limit to 5 tags
    
    def get_problem_by_id(self, problem_id: str) -> Optional[Dict]:
        """Get problem by ID"""
        return next((p for p in self.problems if p["id"] == problem_id), None)
    
    def get_problems_by_domain(self, domain: str) -> List[Dict]:
        """Get all problems for a specific domain"""
        return [p for p in self.problems if p["domain"].lower() == domain.lower()]
    
    def get_unprocessed_problems(self) -> List[Dict]:
        """Get problems that haven't had stories generated yet"""
        return [p for p in self.problems if not p.get("story_generated", False)]
    
    def mark_story_generated(self, problem_id: str):
        """Mark that a story has been generated for this problem"""
        problem = self.get_problem_by_id(problem_id)
        if problem:
            problem["story_generated"] = True
            self.save_database()
    
    def add_user_vote(self, problem_id: str, vote: int = 1):
        """Add user vote/feedback to a problem"""
        problem = self.get_problem_by_id(problem_id)
        if problem:
            problem["user_votes"] = problem.get("user_votes", 0) + vote
            self.save_database()
    
    def save_database(self):
        """Save problems to database file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.problems, f, indent=2)
    
    def add_from_chat_interaction(self, user_message: str, domain: str = "General"):
        """Extract and add problems mentioned in chat"""
        # Simple extraction - look for problem indicators
        problem_indicators = ["problem is", "issue with", "struggle with", "difficulty", "challenge"]
        
        message_lower = user_message.lower()
        for indicator in problem_indicators:
            if indicator in message_lower:
                # Extract the problem context
                title = f"User-suggested: {user_message[:50]}..."
                problem = f"Problem identified from chat: {user_message}"
                
                return self.add_problem(
                    domain=domain,
                    title=title,
                    problem=problem,
                    source="Chat Interaction",
                    source_type="chat_suggestion"
                )
        return None
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        total = len(self.problems)
        by_domain = {}
        by_source = {}
        unprocessed = len(self.get_unprocessed_problems())
        
        for problem in self.problems:
            domain = problem.get("domain", "Unknown")
            source_type = problem.get("source_type", "unknown")
            
            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_source[source_type] = by_source.get(source_type, 0) + 1
        
        return {
            "total_problems": total,
            "unprocessed_problems": unprocessed,
            "by_domain": by_domain,
            "by_source_type": by_source,
            "most_voted": sorted(self.problems, key=lambda x: x.get("user_votes", 0), reverse=True)[:3]
        }

# Global instance
problem_db = ProblemDatabase()