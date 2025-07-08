"""
Routes for Tradepro Finder Toronto.
"""

from flask import Blueprint, render_template, jsonify, request, abort, send_from_directory
import os
import json
import sqlite3
import logging
from datetime import datetime

# Create blueprint
main = Blueprint('main', __name__)

# Helper functions
def load_categories():
    """Load service categories from database."""
    categories = []
    try:
        conn = sqlite3.connect('data/service_providers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM service_providers ORDER BY category')
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        logging.error(f"Error loading categories: {str(e)}")
    return categories

def load_locations():
    """Load locations from database."""
    locations = []
    try:
        conn = sqlite3.connect('data/service_providers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT location FROM service_providers ORDER BY location')
        locations = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        logging.error(f"Error loading locations: {str(e)}")
    return locations

def generate_service_links(categories, locations):
    """Generate service links for SEO."""
    links = []
    for category in categories[:5]:  # Limit to top 5 categories
        for location in locations[:5]:  # Limit to top 5 locations
            slug = f"top-{category.lower().replace(' ', '-')}-in-{location.lower().replace(' ', '-')}"
            title = f"Top {category} in {location}"
            links.append({
                'slug': slug,
                'title': title
            })
    return links

def get_service_providers(category, location):
    """Get service providers from database."""
    providers = []
    try:
        conn = sqlite3.connect('data/service_providers.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM service_providers WHERE category = ? AND location = ? LIMIT 10',
            (category, location)
        )
        providers = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        logging.error(f"Error getting service providers: {str(e)}")
    return providers

# Cache for service pages
service_page_cache = {}

# Routes
@main.route('/')
def index():
    """Serve the main page."""
    categories = load_categories()
    locations = load_locations()
    service_links = generate_service_links(categories, locations)
    return render_template('index.html', 
                         categories=categories, 
                         locations=locations,
                         service_links=service_links)

@main.route('/service/<slug>')
def service_page(slug):
    """Serve a service page."""
    # Check if page is in cache
    if slug in service_page_cache:
        return service_page_cache[slug]
    
    try:
        # Parse slug into components
        # Example: "top-cleaning-services-services-in-kensington-market"
        parts = slug.split('-')
        
        # Find the index of 'in' to separate location
        if 'in' in parts:
            in_index = parts.index('in')
            location_parts = parts[in_index + 1:]
            category_parts = parts[1:in_index]  # Skip the first part (top, best, etc)
        else:
            abort(404)
            
        # Reconstruct category and location
        category = ' '.join(category_parts).replace('-', ' ')
        location = ' '.join(location_parts).replace('-', ' ')
        
        # Title case them
        category = category.title()
        location = location.title()
        
        # Get service providers
        providers = get_service_providers(category, location)
        
        if not providers:
            abort(404)
            
        # Render template
        page = render_template(
            'service.html',
            category=category,
            location=location,
            providers=providers
        )
        
        # Cache the page
        service_page_cache[slug] = page
        
        return page
        
    except Exception as e:
        logging.error(f"Error serving service page: {str(e)}")
        abort(404)

@main.route('/api/categories')
def get_categories():
    """API endpoint to get list of service categories."""
    categories = load_categories()
    return jsonify(categories)

@main.route('/api/locations')
def get_locations():
    """API endpoint to get list of locations."""
    locations = load_locations()
    return jsonify(locations)

@main.route('/api/search', methods=['GET'])
def search():
    """Search for businesses based on category and location."""
    category = request.args.get('category')
    location = request.args.get('location')
    
    if not category or not location:
        return jsonify({'error': 'Missing required parameters'}), 400
        
    try:
        # Check cache first
        conn = sqlite3.connect('data/search_cache.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try to get from cache
        cursor.execute(
            'SELECT results, timestamp FROM search_cache WHERE service = ? AND location = ?',
            (category, location)
        )
        
        cache_row = cursor.fetchone()
        
        if cache_row:
            # Check if cache is still valid (less than 24 hours old)
            timestamp = datetime.fromisoformat(cache_row['timestamp'])
            now = datetime.now()
            
            if (now - timestamp).total_seconds() < 86400:  # 24 hours
                results = json.loads(cache_row['results'])
                conn.close()
                return jsonify(results)
        
        # Get service providers from database
        providers = get_service_providers(category, location)
        
        # Format results
        results = {
            'category': category,
            'location': location,
            'providers': providers,
            'total': len(providers)
        }
        
        # Cache results
        cursor.execute(
            'INSERT OR REPLACE INTO search_cache (service, location, results, timestamp) VALUES (?, ?, ?, ?)',
            (category, location, json.dumps(results), datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/submit-quote', methods=['POST'])
def submit_quote():
    """Submit a quote request."""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone', 'service', 'location', 'description']
    
    # Validate input
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
            
    try:
        # Save to database
        conn = sqlite3.connect('data/service_providers.db')
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO quote_requests 
            (name, email, phone, service, location, description, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['name'],
                data['email'],
                data['phone'],
                data['service'],
                data['location'],
                data['description'],
                datetime.now().isoformat()
            )
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Quote request submitted successfully'})
        
    except Exception as e:
        logging.error(f"Error submitting quote: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/register-professional', methods=['POST'])
def register_professional():
    """Register a new professional."""
    data = request.get_json()
    
    required_fields = ['name', 'email', 'phone', 'company', 'service', 'location', 'description']
    
    # Validate input
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Missing required field: {field}'}), 400
            
    try:
        # Save to database
        conn = sqlite3.connect('data/service_providers.db')
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO professional_registrations 
            (name, email, phone, company, service, location, description, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['name'],
                data['email'],
                data['phone'],
                data['company'],
                data['service'],
                data['location'],
                data['description'],
                datetime.now().isoformat(),
                'pending'
            )
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Registration submitted successfully'})
        
    except Exception as e:
        logging.error(f"Error registering professional: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/sitemap.xml')
def sitemap():
    """Serve the sitemap."""
    return send_from_directory('static', 'sitemap.xml')

@main.route('/robots.txt')
def robots():
    """Serve robots.txt."""
    return send_from_directory('static', 'robots.txt')
