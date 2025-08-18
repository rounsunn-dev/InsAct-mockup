from problem_database import problem_db

def interactive_problem_entry():
    print("🏠 Add a Local Problem to InsAct Database")
    print("="*45)
    
    domain = input("Domain (Healthcare/Climate/Education/etc.): ")
    title = input("Problem Title: ")
    problem = input("Problem Description: ")
    source = input("Source (College/Neighbors/Friends/etc.): ")
    
    new_problem = problem_db.add_problem(domain, title, problem, source, "user_input")
    
    print(f"✅ Added to database: {new_problem['title']}")
    print(f"🆔 Problem ID: {new_problem['id']}")
    
    # Show stats
    stats = problem_db.get_stats()
    print(f"\n📊 Database Stats:")
    print(f"   Total problems: {stats['total_problems']}")
    print(f"   Unprocessed: {stats['unprocessed_problems']}")
    print(f"   Domains: {list(stats['by_domain'].keys())}")

def bulk_add_problems():
    """Add multiple problems at once"""
    sample_problems = [
        ("Education", "Group project coordination chaos", "Students can't coordinate group projects effectively", "College Friends"),
        ("Local Services", "Neighborhood delivery coordination", "Neighbors want to coordinate food deliveries but it's messy", "Neighborhood"),
        ("Student Life", "Shared textbook tracking", "Tracking shared textbooks in dorms is impossible", "Dorm Friends"),
    ]
    
    print("🚀 Adding sample local problems...")
    for domain, title, problem, source in sample_problems:
        problem_db.add_problem(domain, title, problem, source, "manual_entry")
    
    print("✅ Sample problems added!")

if __name__ == "__main__":
    print("1. Add single problem")
    print("2. Add sample problems")
    print("3. Show database stats")
    
    choice = input("Choose (1/2/3): ")
    
    if choice == "1":
        interactive_problem_entry()
    elif choice == "2":
        bulk_add_problems()
    elif choice == "3":
        stats = problem_db.get_stats()
        print(f"\n📊 Problem Database Stats:")
        print(f"Total: {stats['total_problems']}")
        print(f"Unprocessed: {stats['unprocessed_problems']}")
        print(f"By domain: {stats['by_domain']}")
        print(f"By source: {stats['by_source_type']}")