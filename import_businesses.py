#!/usr/bin/env python3
"""
Business Data Import Tool for Tradepro Finder Toronto

This script allows you to import business data from CSV files into the service_providers database.
It helps maintain a comprehensive database of businesses without relying on external APIs.

Usage:
    python import_businesses.py path/to/your/csv_file.csv

CSV Format:
    name,category,location,address,phone,website,rating,reviews,image_url,timestamp
    "Business Name","Category","Location","Address","Phone","Website",4.5,100,"image_url","2025-07-10"
"""

import os
import sys
import csv
import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory):
    """Ensure the directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def import_from_csv(csv_file):
    """Import business data from a CSV file into the service_providers database."""
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return False
    
    # Ensure data directory exists
    ensure_directory_exists('data')
    
    # Connect to database
    conn = sqlite3.connect('data/service_providers.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
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
    
    # Read CSV and import data
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            
            # Validate header
            expected_header = ['name', 'category', 'location', 'address', 'phone', 'website', 'rating', 'reviews', 'image_url', 'timestamp']
            if not all(col.lower() in [h.lower() for h in header] for col in expected_header):
                logger.error(f"CSV header does not match expected format. Expected: {expected_header}")
                return False
            
            # Import data
            businesses = []
            for row in reader:
                if len(row) >= 10:
                    # Convert rating and reviews to appropriate types
                    try:
                        rating = float(row[6])
                        reviews = int(row[7])
                    except ValueError:
                        rating = 0.0
                        reviews = 0
                    
                    # Use provided timestamp or current time
                    timestamp = row[9] if row[9] else datetime.now().isoformat()
                    
                    businesses.append((
                        row[0],  # name
                        row[1],  # category
                        row[2],  # location
                        row[3],  # address
                        row[4],  # phone
                        row[5],  # website
                        rating,  # rating
                        reviews, # reviews
                        row[8],  # image_url
                        timestamp # timestamp
                    ))
            
            # Insert data
            cursor.executemany('''
                INSERT INTO service_providers 
                (name, category, location, address, phone, website, rating, reviews, image_url, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', businesses)
            
            conn.commit()
            logger.info(f"Successfully imported {len(businesses)} businesses from {csv_file}")
            return True
            
    except Exception as e:
        logger.error(f"Error importing data: {str(e)}")
        return False
    finally:
        conn.close()

def export_to_csv(output_file):
    """Export all business data to a CSV file."""
    # Connect to database
    conn = sqlite3.connect('data/service_providers.db')
    cursor = conn.cursor()
    
    try:
        # Get all businesses
        cursor.execute('SELECT name, category, location, address, phone, website, rating, reviews, image_url, timestamp FROM service_providers')
        businesses = cursor.fetchall()
        
        # Write to CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'category', 'location', 'address', 'phone', 'website', 'rating', 'reviews', 'image_url', 'timestamp'])
            writer.writerows(businesses)
        
        logger.info(f"Successfully exported {len(businesses)} businesses to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return False
    finally:
        conn.close()

def create_sample_csv(output_file):
    """Create a sample CSV file with the correct format."""
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'category', 'location', 'address', 'phone', 'website', 'rating', 'reviews', 'image_url', 'timestamp'])
        writer.writerow(['Sample Business', 'Plumbing', 'Downtown Toronto', '123 Main St, Toronto', '416-555-1234', 'https://example.com', '4.8', '120', '', datetime.now().isoformat()])
    
    logger.info(f"Created sample CSV file: {output_file}")
    return True

def print_usage():
    """Print usage instructions."""
    print("Usage:")
    print("  Import businesses from CSV:  python import_businesses.py import path/to/your/csv_file.csv")
    print("  Export businesses to CSV:    python import_businesses.py export path/to/output.csv")
    print("  Create a sample CSV file:    python import_businesses.py sample path/to/sample.csv")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'import' and len(sys.argv) == 3:
        if import_from_csv(sys.argv[2]):
            print("Import successful!")
        else:
            print("Import failed. Check the logs for details.")
    
    elif command == 'export' and len(sys.argv) == 3:
        if export_to_csv(sys.argv[2]):
            print("Export successful!")
        else:
            print("Export failed. Check the logs for details.")
    
    elif command == 'sample' and len(sys.argv) == 3:
        if create_sample_csv(sys.argv[2]):
            print("Sample CSV created successfully!")
        else:
            print("Failed to create sample CSV.")
    
    else:
        print_usage()
        sys.exit(1)
