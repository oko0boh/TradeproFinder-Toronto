"""
Search Service for Tradepro Finder Toronto

This module handles search functionality with Google Places API integration and caching.
"""

import os
import logging
from typing import Dict, List, Any, Optional
# Update imports to use direct imports instead of utils package
from google_places_api import GooglePlacesAPI
from database_manager import DatabaseManager

# Configure logging
logger = logging.getLogger(__name__)

class SearchService:
    """Search service with Google Places API integration and caching."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, api_key: str = None):
        """Initialize the search service.
        
        Args:
            db_manager: Database manager instance
            api_key: Google Places API key
        """
        self.db_manager = db_manager or DatabaseManager()
        self.google_places = GooglePlacesAPI(api_key)
    
    def search_service_providers(self, category: str, location: str, query: str = "") -> List[Dict[str, Any]]:
        """Search for service providers with caching.
        
        Args:
            category: Service category
            location: Location for the search
            query: Optional additional search terms
            
        Returns:
            List of service providers matching the search criteria
        """
        logger.info(f"Searching for {category} in {location} with query: {query}")
        
        # First, check local database for exact matches
        local_results = self._search_local_database(category, location)
        
        # If we have sufficient local results, return them
        if len(local_results) >= 5:
            logger.info(f"Found {len(local_results)} results in local database")
            return local_results
        
        # Otherwise, try Google Places API with caching
        google_results, from_cache = self.google_places.search(query, category, location)
        
        # Store new Google results in local database (if they're not from cache)
        if google_results and not from_cache:
            self._store_google_results(google_results, category, location)
        
        # Combine and deduplicate results
        combined_results = self._combine_results(local_results, google_results)
        
        logger.info(f"Returning {len(combined_results)} combined results")
        return combined_results
    
    def _search_local_database(self, category: str, location: str) -> List[Dict[str, Any]]:
        """Search the local database for service providers.
        
        Args:
            category: Service category
            location: Location for the search
            
        Returns:
            List of service providers from local database
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Query the database for matching service providers
            cursor.execute('''
                SELECT name, category, location, address, phone, website, rating, reviews, image_url, timestamp
                FROM service_providers
                WHERE category = ? AND location = ?
            ''', (category, location))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "name": row[0],
                    "category": row[1],
                    "location": row[2],
                    "address": row[3],
                    "phone": row[4],
                    "website": row[5],
                    "rating": row[6],
                    "reviews": row[7],
                    "image_url": row[8],
                    "timestamp": row[9]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching local database: {str(e)}")
            return []
    
    def _store_google_results(self, results: List[Dict[str, Any]], category: str, location: str) -> None:
        """Store Google Places API results in the local database.
        
        Args:
            results: List of place results from Google Places API
            category: Service category
            location: Location for the search
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            for result in results:
                # Check if this business already exists
                cursor.execute('''
                    SELECT id FROM service_providers
                    WHERE name = ? AND address = ?
                ''', (result["name"], result["address"]))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute('''
                        UPDATE service_providers
                        SET rating = ?, reviews = ?, image_url = ?, timestamp = ?
                        WHERE id = ?
                    ''', (
                        result["rating"],
                        result["reviews"],
                        result["image_url"],
                        result["timestamp"],
                        existing[0]
                    ))
                else:
                    # Insert new record
                    cursor.execute('''
                        INSERT INTO service_providers
                        (name, category, location, address, phone, website, rating, reviews, image_url, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        result["name"],
                        category,
                        location,
                        result["address"],
                        result.get("phone", ""),
                        result.get("website", ""),
                        result["rating"],
                        result["reviews"],
                        result["image_url"],
                        result["timestamp"]
                    ))
            
            conn.commit()
            logger.info(f"Stored {len(results)} Google results in local database")
            
        except Exception as e:
            logger.error(f"Error storing Google results in database: {str(e)}")
    
    def _combine_results(self, local_results: List[Dict[str, Any]], google_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine and deduplicate results from local database and Google Places API.
        
        Args:
            local_results: Results from local database
            google_results: Results from Google Places API
            
        Returns:
            Combined and deduplicated list of results
        """
        # Create a set of business names from local results for deduplication
        local_names = {result["name"] for result in local_results}
        
        # Add Google results that aren't in local results
        combined = local_results.copy()
        for result in google_results:
            if result["name"] not in local_names:
                combined.append(result)
                local_names.add(result["name"])
        
        # Sort by rating (highest first)
        combined.sort(key=lambda x: x.get("rating", 0), reverse=True)
        
        return combined
