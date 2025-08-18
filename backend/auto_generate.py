from story_weaver import StoryWeaver
from problem_database import problem_db

def auto_generate_new_stories():
    """Check for unprocessed problems and generate stories automatically"""
    
    print("🤖 Auto-generating stories for unprocessed problems...")
    
    # Check if there are unprocessed problems
    stats = problem_db.get_stats()
    unprocessed_count = stats["unprocessed_problems"]
    
    print(f"🔍 Found {unprocessed_count} unprocessed problems")
    
    if unprocessed_count == 0:
        print("✅ No new problems to process")
        print("\n💡 To add problems, run: python add_problem.py")
        return 0
    
    # Show what will be processed
    unprocessed = problem_db.get_unprocessed_problems()
    print("\n📝 Problems to be processed:")
    for i, problem in enumerate(unprocessed, 1):
        print(f"  {i}. {problem['title']} ({problem['domain']})")
    
    # Ask for confirmation
    proceed = input(f"\n🎯 Generate stories for these {len(unprocessed)} problems? (y/n): ")
    if proceed.lower() != 'y':
        print("❌ Cancelled")
        return 0
    
    # Generate stories for unprocessed problems
    print("\n🚀 Starting story generation...")
    weaver = StoryWeaver()
    new_stories = weaver.generate_stories_incremental(
        domains=None,  # Process all domains
        max_new_stories=len(unprocessed)  # Process all unprocessed
    )
    
    if new_stories:
        # Save with append
        new_count = weaver.save_stories_to_file(new_stories, append=True)
        print(f"\n🎉 Generated and saved {len(new_stories)} new stories!")
        
        # Show what was generated
        print("\n📚 Generated stories:")
        for i, story in enumerate(new_stories, 1):
            print(f"  {i}. {story.get('title', 'Untitled')} ({story.get('domain', 'Unknown')})")
            print(f"     Preview: {story.get('preview', 'No preview')}")
        
        print(f"\n💾 Stories appended to generated_stories.json")
        print("🔄 Restart your backend to see new stories in the app!")
        
        return len(new_stories)
    else:
        print("❌ No stories were generated")
        return 0

def show_status():
    """Show current database and story status"""
    stats = problem_db.get_stats()
    
    print("📊 Current Status:")
    print(f"  Total problems in database: {stats['total_problems']}")
    print(f"  Unprocessed problems: {stats['unprocessed_problems']}")
    print(f"  Domains: {list(stats['by_domain'].keys())}")
    print(f"  Source types: {list(stats['by_source_type'].keys())}")
    
    # Check generated stories file
    from pathlib import Path
    import json
    
    stories_file = Path("generated_stories.json")
    if stories_file.exists():
        try:
            with open(stories_file, 'r') as f:
                stories = json.load(f)
            print(f"  Generated stories in file: {len(stories)}")
            
            # Show domains in stories
            story_domains = list(set([s.get('domain', 'Unknown') for s in stories]))
            print(f"  Story domains: {story_domains}")
        except:
            print("  Generated stories file: Error reading")
    else:
        print("  Generated stories file: Not found")

if __name__ == "__main__":
    print("🏠 InsAct Auto Story Generator")
    print("=" * 40)
    
    print("1. Generate stories for unprocessed problems")
    print("2. Show current status")
    print("3. Exit")
    
    choice = input("\nChoose (1/2/3): ")
    
    if choice == "1":
        generated_count = auto_generate_new_stories()
        if generated_count > 0:
            print(f"\n✅ Success! Generated {generated_count} new stories")
    elif choice == "2":
        show_status()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
        
    print("\n" + "=" * 40)