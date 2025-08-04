#!/usr/bin/env python3
"""
Demo script for SearchStateService - Intelligent Search State Management

This demo showcases:
- Database-backed search history and analytics
- Smart suggestions based on user patterns
- Favorites management with usage tracking
- Observer pattern for real-time state updates
- Search pattern analysis and predictions
- Comprehensive usage statistics
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.search_state_service import SearchStateService

def demo_observer(state_change):
    """Example observer function"""
    print(f"🔔 State Change: {state_change['query']} | Cities: {state_change['cities']} | Mode: {state_change['mode']}")

def populate_sample_data(service):
    """Populate the service with sample search data"""
    print("📊 Populating sample data...")
    
    # Sample searches to simulate user behavior
    sample_searches = [
        ("Tokyo", "city", 1),
        ("New York", "city", 1),
        ("London", "city", 1),
        ("Tokyo", "city", 1),  # Duplicate to show frequency
        ("Paris", "city", 1),
        ("compare: Tokyo, New York", "command", 2),
        ("weather: London", "command", 1),
        ("Tokyo", "city", 1),  # Another duplicate
        ("Berlin", "city", 1),
        ("compare: Paris, London", "command", 2),
        ("Sydney", "city", 1),
        ("weather: Tokyo", "command", 1),
        ("Moscow", "city", 1),
        ("compare: Tokyo, London, Paris", "command", 3),
        ("Rome", "city", 1),
    ]
    
    for query, search_type, result_count in sample_searches:
        service.add_to_history(query, search_type, result_count)
        time.sleep(0.1)  # Small delay to create different timestamps
    
    # Add some favorites
    favorites = ["Tokyo", "New York", "London", "Paris"]
    for city in favorites:
        service.add_to_favorites(city)
        # Simulate multiple uses for some cities
        if city in ["Tokyo", "London"]:
            service.add_to_favorites(city)
            service.add_to_favorites(city)
    
    print("✅ Sample data populated!")

def demo_smart_suggestions(service):
    """Demonstrate smart suggestions functionality"""
    print("\n🧠 Smart Suggestions Demo")
    print("=" * 40)
    
    test_queries = ["To", "Lon", "compare", "weather", "Par"]
    
    for query in test_queries:
        suggestions = service.get_smart_suggestions(query)
        print(f"\n🔍 Query: '{query}'")
        if suggestions:
            for i, suggestion in enumerate(suggestions[:5], 1):
                print(f"  {i}. {suggestion['icon']} {suggestion['text']} ({suggestion['type']}, score: {suggestion['score']})")
        else:
            print("  No suggestions found")

def demo_pattern_analysis(service):
    """Demonstrate search pattern analysis"""
    print("\n🎯 Search Pattern Analysis")
    print("=" * 40)
    
    patterns = service.analyze_search_patterns()
    if patterns:
        for i, pattern in enumerate(patterns, 1):
            print(f"  {i}. {pattern}")
    else:
        print("  No patterns detected yet")

def demo_favorites_management(service):
    """Demonstrate favorites management"""
    print("\n⭐ Favorites Management")
    print("=" * 40)
    
    favorites = service.get_favorites()
    if favorites:
        for fav in favorites:
            print(f"  ★ {fav['name']} (used {fav['use_count']} times, last: {fav['last_used']})")
    else:
        print("  No favorites yet")
    
    # Demo adding and removing favorites
    print("\n📝 Adding 'Barcelona' to favorites...")
    service.add_to_favorites("Barcelona")
    
    print("📝 Using 'Barcelona' again...")
    service.add_to_favorites("Barcelona")
    
    print("\n⭐ Updated favorites:")
    favorites = service.get_favorites()
    for fav in favorites:
        if fav['name'] == 'Barcelona':
            print(f"  ★ {fav['name']} (used {fav['use_count']} times)")

def demo_search_history(service):
    """Demonstrate search history functionality"""
    print("\n📚 Search History")
    print("=" * 40)
    
    history = service.get_search_history(limit=10)
    if history:
        for i, entry in enumerate(history, 1):
            timestamp = entry['timestamp'][:19] if entry['timestamp'] else 'Unknown'
            print(f"  {i}. {entry['query']} ({entry['search_type']}) - {timestamp}")
    else:
        print("  No search history yet")

def demo_usage_statistics(service):
    """Demonstrate usage statistics"""
    print("\n📊 Usage Statistics")
    print("=" * 40)
    
    stats = service.get_usage_statistics()
    
    print(f"  📈 Total searches: {stats['total_searches']}")
    print(f"  🌍 Unique cities: {stats['unique_cities']}")
    print(f"  🔥 Most popular type: {stats['most_popular_type']}")
    print(f"  📅 Avg searches/day: {stats['avg_searches_per_day']}")
    
    if stats['top_cities']:
        print("\n  🏆 Top Cities:")
        for i, city_stat in enumerate(stats['top_cities'], 1):
            print(f"    {i}. {city_stat['city']} ({city_stat['count']} searches)")

def demo_observer_pattern(service):
    """Demonstrate the observer pattern"""
    print("\n👁️ Observer Pattern Demo")
    print("=" * 40)
    
    # Register observer
    service.add_observer(demo_observer)
    
    print("\n📡 Registered observer. Performing searches...")
    
    # Simulate some searches
    test_searches = [
        ("Madrid", ["Madrid"], "single"),
        ("compare cities", ["Tokyo", "London"], "multi"),
        ("weather command", ["Paris"], "command")
    ]
    
    for query, cities, mode in test_searches:
        print(f"\n🔍 Searching: {query}")
        service.update_search(query, cities, mode)
        time.sleep(0.5)
    
    # Remove observer
    service.remove_observer(demo_observer)
    print("\n📡 Observer removed")

def demo_data_export_import(service):
    """Demonstrate data export and import"""
    print("\n💾 Data Export/Import Demo")
    print("=" * 40)
    
    # Export data
    print("📤 Exporting data...")
    exported_data = service.export_data()
    
    print(f"  ✅ Exported {len(exported_data['search_history'])} search entries")
    print(f"  ✅ Exported {len(exported_data['favorites'])} favorites")
    print(f"  ✅ Exported {len(exported_data['analytics'])} analytics patterns")
    
    # Save to file
    export_file = Path("data/search_backup.json")
    export_file.parent.mkdir(exist_ok=True)
    
    import json
    with open(export_file, 'w') as f:
        json.dump(exported_data, f, indent=2)
    
    print(f"  💾 Data saved to {export_file}")
    
    # Demo import (we'll just show the process without actually importing)
    print("\n📥 Import process available for data restoration")

def main():
    """Main demo function"""
    print("🚀 SearchStateService Demo")
    print("=" * 50)
    print("Intelligent Search State Management with Database Persistence")
    print("\nFeatures:")
    print("• 🧠 Smart suggestions based on user patterns")
    print("• 📊 Comprehensive search analytics")
    print("• ⭐ Favorites management with usage tracking")
    print("• 👁️ Observer pattern for real-time updates")
    print("• 🎯 Search pattern analysis and predictions")
    print("• 💾 Data export/import for backup")
    print("• 📚 Persistent search history")
    
    # Initialize service
    print("\n🔧 Initializing SearchStateService...")
    service = SearchStateService()
    
    try:
        # Run demos
        populate_sample_data(service)
        demo_search_history(service)
        demo_smart_suggestions(service)
        demo_pattern_analysis(service)
        demo_favorites_management(service)
        demo_usage_statistics(service)
        demo_observer_pattern(service)
        demo_data_export_import(service)
        
        print("\n✨ Demo completed successfully!")
        print("\n💡 Integration Tips:")
        print("• Use get_smart_suggestions() in your search autocomplete")
        print("• Register observers to sync UI with search state changes")
        print("• Leverage usage statistics for user insights")
        print("• Export data regularly for backup purposes")
        
        print("\n🗂️ Database location: data/search_state.db")
        print("📁 State file: data/search_state.json")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Save final state
        service.save_state()
        print("\n💾 Search state saved")

if __name__ == "__main__":
    main()