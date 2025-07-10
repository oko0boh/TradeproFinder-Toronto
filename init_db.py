"""
Database initialization script for Tradepro Finder Toronto.
This script creates and seeds the necessary database files for the application.
"""

import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory):
    """Ensure the directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def init_service_providers_db():
    """Initialize the service providers database."""
    ensure_directory_exists('data')
    
    conn = sqlite3.connect('data/service_providers.db')
    cursor = conn.cursor()
    
    # Create service_providers table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS service_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            location TEXT,
            address TEXT,
            phone TEXT,
            website TEXT,
            rating REAL,
            reviews INTEGER,
            image_url TEXT,
            timestamp TEXT
        )
    ''')
    
    # Create quote_requests table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quote_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            service TEXT,
            location TEXT,
            description TEXT,
            timestamp TEXT
        )
    ''')
    
    # Check if the table is empty
    cursor.execute('SELECT COUNT(*) FROM service_providers')
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Seed with comprehensive business data across different categories and locations
        sample_data = [
            # Plumbing Services
            ('Toronto Plumbing Experts', 'Plumbing', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('GTA Plumbing Solutions', 'Plumbing', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Scarborough Plumbing Pros', 'Plumbing', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Etobicoke Plumbing Services', 'Plumbing', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09'),
            ('Mississauga Plumbing Co', 'Plumbing', 'Mississauga', '654 Dundas St E, Mississauga', '905-555-5678', 'https://example.com', 4.5, 75, '', '2025-07-09'),
            
            # Electrical Services
            ('GTA Electricians', 'Electrical', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Downtown Electric', 'Electrical', 'Downtown Toronto', '987 Bay St, Toronto', '416-555-6789', 'https://example.com', 4.8, 110, '', '2025-07-09'),
            ('Scarborough Electric Co', 'Electrical', 'Scarborough', '321 Markham Rd, Toronto', '416-555-8901', 'https://example.com', 4.6, 85, '', '2025-07-09'),
            ('Etobicoke Electrical Services', 'Electrical', 'Etobicoke', '789 The Queensway, Toronto', '416-555-9012', 'https://example.com', 4.9, 130, '', '2025-07-09'),
            ('Mississauga Electrical Pros', 'Electrical', 'Mississauga', '456 Hurontario St, Mississauga', '905-555-0123', 'https://example.com', 4.8, 115, '', '2025-07-09'),
            
            # HVAC Services
            ('Fast HVAC Services', 'HVAC', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09'),
            ('Toronto HVAC Solutions', 'HVAC', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('North York Heating & Cooling', 'HVAC', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Scarborough HVAC Experts', 'HVAC', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Mississauga Heating & Air', 'HVAC', 'Mississauga', '654 Dundas St E, Mississauga', '905-555-5678', 'https://example.com', 4.5, 75, '', '2025-07-09'),
            
            # Painting Services
            ('Quality Painting Co', 'Painting', 'Mississauga', '654 Dundas St E, Mississauga', '905-555-5678', 'https://example.com', 4.5, 75, '', '2025-07-09'),
            ('Toronto Painting Pros', 'Painting', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('North York Painters', 'Painting', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Scarborough Painting Services', 'Painting', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Etobicoke Painting Co', 'Painting', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09'),
            
            # Roofing Services
            ('Reliable Roofing', 'Roofing', 'Downtown Toronto', '987 Bay St, Toronto', '416-555-6789', 'https://example.com', 4.8, 110, '', '2025-07-09'),
            ('North York Roofing Co', 'Roofing', 'North York', '654 Finch Ave, Toronto', '416-555-7890', 'https://example.com', 4.7, 90, '', '2025-07-09'),
            ('Scarborough Roofing Solutions', 'Roofing', 'Scarborough', '321 Markham Rd, Toronto', '416-555-8901', 'https://example.com', 4.6, 85, '', '2025-07-09'),
            ('Etobicoke Roofing Experts', 'Roofing', 'Etobicoke', '789 The Queensway, Toronto', '416-555-9012', 'https://example.com', 4.9, 130, '', '2025-07-09'),
            ('Mississauga Roofing Pros', 'Roofing', 'Mississauga', '456 Hurontario St, Mississauga', '905-555-0123', 'https://example.com', 4.8, 115, '', '2025-07-09'),
            
            # Landscaping Services
            ('Expert Landscaping', 'Landscaping', 'North York', '654 Finch Ave, Toronto', '416-555-7890', 'https://example.com', 4.7, 90, '', '2025-07-09'),
            ('Toronto Landscaping Design', 'Landscaping', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('Scarborough Lawn & Garden', 'Landscaping', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Etobicoke Landscaping Co', 'Landscaping', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09'),
            ('Mississauga Garden Experts', 'Landscaping', 'Mississauga', '654 Dundas St E, Mississauga', '905-555-5678', 'https://example.com', 4.5, 75, '', '2025-07-09'),
            
            # Flooring Services
            ('Precision Flooring', 'Flooring', 'Scarborough', '321 Markham Rd, Toronto', '416-555-8901', 'https://example.com', 4.6, 85, '', '2025-07-09'),
            ('Toronto Flooring Solutions', 'Flooring', 'Downtown Toronto', '987 Bay St, Toronto', '416-555-6789', 'https://example.com', 4.8, 110, '', '2025-07-09'),
            ('North York Flooring Experts', 'Flooring', 'North York', '654 Finch Ave, Toronto', '416-555-7890', 'https://example.com', 4.7, 90, '', '2025-07-09'),
            ('Etobicoke Flooring Co', 'Flooring', 'Etobicoke', '789 The Queensway, Toronto', '416-555-9012', 'https://example.com', 4.9, 130, '', '2025-07-09'),
            ('Mississauga Flooring Pros', 'Flooring', 'Mississauga', '456 Hurontario St, Mississauga', '905-555-0123', 'https://example.com', 4.8, 115, '', '2025-07-09'),
            
            # Renovation Services
            ('Home Renovation Pros', 'Renovation', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Toronto Renovation Co', 'Renovation', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('North York Home Renovations', 'Renovation', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Etobicoke Renovation Services', 'Renovation', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09'),
            ('Mississauga Renovation Experts', 'Renovation', 'Mississauga', '654 Dundas St E, Mississauga', '905-555-5678', 'https://example.com', 4.5, 75, '', '2025-07-09'),
            
            # Kitchen Renovation
            ('Modern Kitchen Design', 'Kitchen Renovation', 'Etobicoke', '789 The Queensway, Toronto', '416-555-9012', 'https://example.com', 4.9, 130, '', '2025-07-09'),
            ('Toronto Kitchen Experts', 'Kitchen Renovation', 'Downtown Toronto', '987 Bay St, Toronto', '416-555-6789', 'https://example.com', 4.8, 110, '', '2025-07-09'),
            ('North York Kitchen Renovations', 'Kitchen Renovation', 'North York', '654 Finch Ave, Toronto', '416-555-7890', 'https://example.com', 4.7, 90, '', '2025-07-09'),
            ('Scarborough Kitchen Design', 'Kitchen Renovation', 'Scarborough', '321 Markham Rd, Toronto', '416-555-8901', 'https://example.com', 4.6, 85, '', '2025-07-09'),
            ('Mississauga Kitchen Pros', 'Kitchen Renovation', 'Mississauga', '456 Hurontario St, Mississauga', '905-555-0123', 'https://example.com', 4.8, 115, '', '2025-07-09'),
            
            # Bathroom Renovation
            ('Bathroom Remodeling Pros', 'Bathroom Renovation', 'Mississauga', '456 Hurontario St, Mississauga', '905-555-0123', 'https://example.com', 4.8, 115, '', '2025-07-09'),
            ('Toronto Bathroom Design', 'Bathroom Renovation', 'Downtown Toronto', '123 King St W, Toronto', '416-555-1234', 'https://example.com', 4.8, 120, '', '2025-07-09'),
            ('North York Bathroom Experts', 'Bathroom Renovation', 'North York', '456 Yonge St, Toronto', '416-555-2345', 'https://example.com', 4.7, 95, '', '2025-07-09'),
            ('Scarborough Bathroom Renovations', 'Bathroom Renovation', 'Scarborough', '789 Kennedy Rd, Toronto', '416-555-3456', 'https://example.com', 4.9, 150, '', '2025-07-09'),
            ('Etobicoke Bathroom Remodeling', 'Bathroom Renovation', 'Etobicoke', '321 Bloor St W, Toronto', '416-555-4567', 'https://example.com', 4.6, 80, '', '2025-07-09')
        ]
        
        cursor.executemany('''
            INSERT INTO service_providers (name, category, location, address, phone, website, rating, reviews, image_url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        
        logger.info(f"Seeded service_providers table with {len(sample_data)} records")
    
    conn.commit()
    conn.close()
    logger.info("Service providers database initialized successfully")

def init_search_cache_db():
    """Initialize the search cache database."""
    ensure_directory_exists('data')
    
    conn = sqlite3.connect('data/search_cache.db')
    cursor = conn.cursor()
    
    # Create search_cache table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT,
            location TEXT,
            results TEXT,
            timestamp TEXT,
            UNIQUE(service, location)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Search cache database initialized successfully")

def init_all_databases():
    """Initialize all databases."""
    try:
        init_service_providers_db()
        init_search_cache_db()
        logger.info("All databases initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing databases: {str(e)}")

if __name__ == "__main__":
    init_all_databases()
