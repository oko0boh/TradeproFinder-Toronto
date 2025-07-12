#!/usr/bin/env python3
"""
Test script for Google Places API integration.

This script allows you to test the Google Places API integration and caching system.
It can be used to verify that the API is working correctly and that results are being cached.

Usage:
    python test_google_places_api.py search <category> <location> [query]
    python test_google_places_api.py clear-cache
"""

import os
import sys
import json
import sqlite3
from utils.google_places_api import GooglePlacesAPI
from utils.search_service import SearchService
from database_manager import DatabaseManager

def test_search(category, location, query=""):
    """Test the search functionality with Google Places API."""
    print(f"Testing search for {category} in {location} with query: {query}")
    
    # Get API key from environment
    api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("Warning: No GOOGLE_PLACES_API_KEY found in environment variables.")
        print("API calls will fail without a valid API key.")
    
    # Initialize components
    db_manager = DatabaseManager()
    google_places = GooglePlacesAPI(api_key=api_key)
    search_service = SearchService(db_manager=db_manager, api_key=api_key)
    
    # Test direct Google Places API call
    print("\n1. Testing direct Google Places API call...")
    results, from_cache = google_places.search(query, category, location)
    print(f"Found {len(results)} results directly from Google Places API")
    print(f"Results from cache: {from_cache}")
    
    if results:
        print(f"First result: {results[0]['name']} ({results[0]['address']})")
    
    # Test search service (hybrid approach)
    print("\n2. Testing search service (hybrid approach)...")
    providers = search_service.search_service_providers(category, location, query)
    print(f"Found {len(providers)} providers using hybrid search")
    
    if providers:
        print(f"First provider: {providers[0]['name']} ({providers[0]['address']})")
    
    # Test caching
    print("\n3. Testing caching (second call should use cache)...")
    results2, from_cache2 = google_places.search(query, category, location)
    print(f"Second call - Results from cache: {from_cache2}")
    
    return True

def clear_cache():
    """Clear the Google Places API cache."""
    print("Clearing Google Places API cache...")
    
    try:
        conn = sqlite3.connect('service_providers.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='google_places_cache'
        ''')
        
        if cursor.fetchone():
            # Get count before deletion
            cursor.execute('SELECT COUNT(*) FROM google_places_cache')
            count = cursor.fetchone()[0]
            print(f"Found {count} cached API responses")
            
            # Delete all records
            cursor.execute('DELETE FROM google_places_cache')
            conn.commit()
            print(f"Deleted {count} cached API responses")
        else:
            print("Cache table does not exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
        return False

def print_usage():
    """Print usage instructions."""
    print("Usage:")
    print("  Test search:    python test_google_places_api.py search <category> <location> [query]")
    print("  Clear cache:    python test_google_places_api.py clear-cache")
    print("\nExamples:")
    print("  python test_google_places_api.py search Plumbers 'Downtown Toronto'")
    print("  python test_google_places_api.py search Electricians Mississauga 'emergency'")
    print("  python test_google_places_api.py clear-cache")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "search" and len(sys.argv) >= 4:
        category = sys.argv[2]
        location = sys.argv[3]
        query = sys.argv[4] if len(sys.argv) > 4 else ""
        
        if test_search(category, location, query):
            print("\nSearch test completed successfully")
        else:
            print("\nSearch test failed")
            sys.exit(1)
    
    elif command == "clear-cache":
        if clear_cache():
            print("Cache cleared successfully")
        else:
            print("Failed to clear cache")
            sys.exit(1)
    
    else:
        print_usage()
        sys.exit(1)
