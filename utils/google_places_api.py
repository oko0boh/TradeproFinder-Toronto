"""
Google Places API Integration with 6-month caching

This module handles Google Places API requests with a caching system that:
1. Checks for cached results before making API calls
2. Stores API results in the database for future use
3. Only refreshes cached results after 6 months
"""

import os
import json
import sqlite3
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)

class GooglePlacesAPI:
    """Google Places API client with caching functionality."""
    
    def __init__(self, api_key: str = None, db_path: str = 'service_providers.db'):
        """Initialize the Google Places API client.
        
        Args:
            api_key: Google Places API key. If None, will try to get from environment.
            db_path: Path to the SQLite database for caching.
        """
        self.api_key = api_key or os.environ.get('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            logger.warning("No Google Places API key provided. API calls will fail.")
        
        self.db_path = db_path
        self._ensure_cache_table()
    
    def _ensure_cache_table(self) -> None:
        """Ensure the API cache table exists in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cache table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS google_places_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_google_places_cache_query 
            ON google_places_cache (query, category, location)
        ''')
        
        conn.commit()
        conn.close()
    
    def search(self, query: str, category: str, location: str) -> Tuple[List[Dict[str, Any]], bool]:
        """Search for places using Google Places API with caching.
        
        Args:
            query: Search query string
            category: Business category
            location: Location for the search
            
        Returns:
            Tuple containing (list of place results, whether results came from cache)
        """
        # Check cache first
        cached_results = self._get_from_cache(query, category, location)
        if cached_results:
            logger.info(f"Using cached results for query: {query} in {location}")
            return cached_results, True
        
        # If not in cache or expired, call API
        if not self.api_key:
            logger.error("Cannot make API call: No Google Places API key available")
            return [], False
            
        logger.info(f"Calling Google Places API for query: {query} in {location}")
        api_results = self._call_places_api(query, category, location)
        
        # Cache the results
        if api_results:
            self._store_in_cache(query, category, location, api_results)
            
        return api_results, False
    
    def _get_from_cache(self, query: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Get results from cache if they exist and are not expired.
        
        Args:
            query: Search query string
            category: Business category
            location: Location for the search
            
        Returns:
            List of place results if found in cache and not expired, otherwise empty list
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate expiration date (6 months ago)
        six_months_ago = (datetime.now() - timedelta(days=180)).isoformat()
        
        cursor.execute('''
            SELECT response, timestamp FROM google_places_cache
            WHERE query = ? AND category = ? AND location = ? AND timestamp > ?
        ''', (query, category, location, six_months_ago))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            response_data, timestamp = result
            return json.loads(response_data)
        
        return []
    
    def _store_in_cache(self, query: str, category: str, location: str, results: List[Dict[str, Any]]) -> None:
        """Store API results in cache.
        
        Args:
            query: Search query string
            category: Business category
            location: Location for the search
            results: List of place results to cache
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store with current timestamp
        timestamp = datetime.now().isoformat()
        response_json = json.dumps(results)
        
        cursor.execute('''
            INSERT INTO google_places_cache (query, category, location, response, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, category, location, response_json, timestamp))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cached {len(results)} results for query: {query} in {location}")
    
    def _call_places_api(self, query: str, category: str, location: str) -> List[Dict[str, Any]]:
        """Call Google Places API and format the results.
        
        Args:
            query: Search query string
            category: Business category
            location: Location for the search
            
        Returns:
            List of formatted place results
        """
        try:
            # Construct the search query
            search_query = f"{category} in {location}"
            if query:
                search_query = f"{query} {search_query}"
                
            # Call Google Places API - Text Search
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": search_query,
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return []
            
            # Format the results
            formatted_results = []
            for place in data.get("results", []):
                formatted_place = self._format_place_result(place)
                if formatted_place:
                    formatted_results.append(formatted_place)
            
            # Handle pagination if needed
            next_page_token = data.get("next_page_token")
            if next_page_token:
                # Could implement pagination here if needed
                pass
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error calling Google Places API: {str(e)}")
            return []
    
    def _format_place_result(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format a Google Places API result into our standard format.
        
        Args:
            place: Google Places API place result
            
        Returns:
            Formatted place dictionary or None if invalid
        """
        try:
            # Extract and format the place data
            formatted_place = {
                "name": place.get("name", ""),
                "address": place.get("formatted_address", ""),
                "phone": "",  # Requires a details request to get phone
                "website": "",  # Requires a details request to get website
                "rating": place.get("rating", 0.0),
                "reviews": place.get("user_ratings_total", 0),
                "image_url": "",
                "timestamp": datetime.now().isoformat()
            }
            
            # Get photo reference if available
            if place.get("photos") and len(place["photos"]) > 0:
                photo_reference = place["photos"][0].get("photo_reference")
                if photo_reference:
                    formatted_place["image_url"] = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.api_key}"
            
            # Get place ID for potential details lookup
            place_id = place.get("place_id")
            if place_id:
                formatted_place["place_id"] = place_id
                
                # Optionally fetch additional details (phone, website)
                # This would require an additional API call per place
                # details = self._get_place_details(place_id)
                # if details:
                #     formatted_place["phone"] = details.get("phone", "")
                #     formatted_place["website"] = details.get("website", "")
            
            return formatted_place
            
        except Exception as e:
            logger.error(f"Error formatting place result: {str(e)}")
            return None
    
    def _get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get additional details for a place (optional, requires extra API call).
        
        Args:
            place_id: Google Places API place ID
            
        Returns:
            Dictionary with additional place details
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,website",
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.error(f"API error getting place details: {data.get('status')}")
                return {}
                
            result = data.get("result", {})
            return {
                "phone": result.get("formatted_phone_number", ""),
                "website": result.get("website", "")
            }
            
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return {}
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Public method to get place details.
        
        Args:
            place_id: Google Places API place ID
            
        Returns:
            Dictionary with place details
        """
        return self._get_place_details(place_id)
