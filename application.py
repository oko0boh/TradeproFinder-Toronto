from flask import Flask, jsonify, request, render_template, abort, make_response, send_from_directory, redirect
from flask_cors import CORS
import os
import sys
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from config import config
from security import init_security, validate_input, CONTACT_FORM_RULES, QUOTE_REQUEST_RULES, PRO_REGISTRATION_RULES
from error_handlers import init_error_handling
from database_manager import DatabaseManager
from local_cache import LocalCache
from api_monitor import APIMonitor
from rollback_manager import RollbackManager
import logging
from logging.handlers import RotatingFileHandler
import traceback
from datetime import datetime, timedelta
import json

def create_app(config_name='development'):
    """Create Flask application."""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_security(app)
    init_error_handling(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {"origins": app.config['CORS_ORIGINS']}
    })
    
    # Initialize database
    db = DatabaseManager(app)
    
    # Initialize cache
    cache = LocalCache(app)
    
    # Initialize API monitor
    api_monitor = APIMonitor(app)

    @app.before_request
    def before_request():
        """Pre-request processing."""
        # Force HTTPS in production
        if not request.is_secure and app.config['ENV'] == 'production':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    @app.after_request
    def after_request(response):
        """Post-request processing."""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.route('/')
    def index():
        """Serve the main page."""
        return render_template('index.html')

    @app.route('/about')
    def about():
        """Serve the about page."""
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        """Serve the contact page."""
        return render_template('contact.html')

    @app.route('/api/search', methods=['POST'])
    def search():
        """Handle search requests."""
        data = request.get_json()
        
        if not data or 'service' not in data or 'location' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        try:
            # Check cache first
            cache_key = f"search:{data['service']}:{data['location']}"
            cached_results = cache.get(cache_key)
            
            if cached_results:
                return jsonify(cached_results), 200
                
            # Perform search
            results = api_monitor.search_places(
                service=data['service'],
                location=data['location']
            )
            
            # Cache results
            cache.set(cache_key, results, timeout=3600)
            
            return jsonify(results), 200
            
        except Exception as e:
            app.logger.error(f"Search error: {str(e)}")
            return jsonify({'error': 'Search failed'}), 500

    @app.route('/api/contact', methods=['POST'])
    def submit_contact():
        """Handle contact form submission."""
        data = request.get_json()
        
        # Validate input
        errors = validate_input(data, CONTACT_FORM_RULES)
        if errors:
            return jsonify({'errors': errors}), 400
            
        try:
            db.save_contact_request(data)
            return jsonify({'message': 'Contact request submitted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Error saving contact request: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/quote', methods=['POST'])
    def submit_quote_request():
        """Handle quote request submission."""
        data = request.get_json()
        
        # Validate input
        errors = validate_input(data, QUOTE_REQUEST_RULES)
        if errors:
            return jsonify({'errors': errors}), 400
            
        try:
            db.save_quote_request(data)
            return jsonify({'message': 'Quote request submitted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Error saving quote request: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/register-pro', methods=['POST'])
    def register_professional():
        """Handle professional registration."""
        data = request.get_json()
        
        # Validate input
        errors = validate_input(data, PRO_REGISTRATION_RULES)
        if errors:
            return jsonify({'errors': errors}), 400
            
        try:
            db.save_pro_registration(data)
            return jsonify({'message': 'Registration submitted successfully'}), 200
        except Exception as e:
            app.logger.error(f"Error saving professional registration: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/sitemap.xml')
    def sitemap():
        """Serve the sitemap."""
        return send_from_directory(app.static_folder, 'sitemap.xml')

    @app.route('/robots.txt')
    def robots():
        """Serve robots.txt."""
        return send_from_directory(app.static_folder, 'robots.txt')

    return app

# Set up logging
# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('logs/app.log')  # Log to file
    ]
)
logger = logging.getLogger(__name__)

# Print a visible marker when the app starts
print("\n" + "="*50)
print("Starting Tradepro Finder Toronto")
print("Log messages will appear below")
print("="*50 + "\n")

# Create logger
logger.setLevel(logging.INFO)  # Set to INFO level

# Configure logging
file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
file_handler.setLevel(logging.INFO)  # Set to INFO level
logger.addHandler(file_handler)

# Add a stream handler to see logs in console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)  # Set main logger to INFO level
logger.info('Tradepro Finder Toronto startup')

# Load environment variables
load_dotenv()

# Constants
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
if not GOOGLE_PLACES_API_KEY:
    logger.error("Google Places API key not found in environment variables")
else:
    logger.info("Google Places API key loaded successfully")

GOOGLE_PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'
TORONTO_COORDS = {"latitude": 43.6532, "longitude": -79.3832}  # Toronto city center

# Initialize database manager
db = DatabaseManager()

# Initialize API monitor
api_monitor = APIMonitor()

# Initialize rollback manager
rollback_manager = RollbackManager()

def load_categories():
    """Load list of service categories from file"""
    try:
        # Read categories from CSV file
        categories = []
        with open('data/tradepro_finder_toronto_keywords.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = row['Category'].strip()
                if category and category not in categories:
                    categories.append(category)
        
        # Sort categories alphabetically
        categories.sort()
        return categories
    except Exception as e:
        print(f"Error loading categories: {str(e)}")
        traceback.print_exc()
        return []

def load_locations():
    """Load list of locations from file"""
    try:
        # Read locations from CSV file
        locations = []
        with open('data/tradepro_finder_cities.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                location = row['Location'].strip()
                if location and location not in locations:
                    locations.append(location)
        
        # Sort locations alphabetically
        locations.sort()
        return locations
    except Exception as e:
        print(f"Error loading locations: {str(e)}")
        traceback.print_exc()
        return []

# Load CSV data
try:
    # Load categories
    categories_file = os.path.join(os.path.dirname(__file__), 'data', 'tradepro_finder_toronto_keywords.csv')
    categories_df = pd.read_csv(categories_file)
    CATEGORIES = categories_df['Category'].tolist()  # Use Category column directly
    logger.info(f'Successfully loaded {len(CATEGORIES)} categories')
    logger.info(f'Categories: {CATEGORIES}')

    # Load locations
    locations_file = os.path.join(os.path.dirname(__file__), 'data', 'tradepro_finder_cities.csv')
    locations_df = pd.read_csv(locations_file)
    LOCATIONS = locations_df['Location'].tolist()
    logger.info(f'Successfully loaded {len(LOCATIONS)} locations')
    logger.info(f'Locations: {LOCATIONS}')

except Exception as e:
    logger.error(f'Error loading CSV data: {str(e)}')
    CATEGORIES = []
    LOCATIONS = []

# Initialize contact requests database
contact_db = sqlite3.connect('contact_requests.db')
contact_db.execute('''
    CREATE TABLE IF NOT EXISTS contact_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT,
        business_address TEXT,
        user_name TEXT,
        user_email TEXT,
        user_phone TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Initialize quote requests database
quote_db = SQLiteDatabase('quote_requests.db')
quote_db.execute('''
    CREATE TABLE IF NOT EXISTS quote_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_type TEXT,
        description TEXT,
        preferred_date TEXT,
        budget TEXT,
        location TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Initialize pro registration database
def init_service_providers_db():
    """Initialize the service providers database"""
    try:
        conn = sqlite3.connect('service_providers.db')
        cursor = conn.cursor()
        
        # Drop existing table if it exists
        cursor.execute('DROP TABLE IF EXISTS service_providers')
        
        # Create fresh table
        cursor.execute('''
            CREATE TABLE service_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                services TEXT NOT NULL,
                locations TEXT NOT NULL,
                license TEXT,
                insurance TEXT,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Service providers database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        if conn:
            conn.close()
        raise e

def init_search_cache_db():
    """Initialize the search cache database"""
    try:
        conn = sqlite3.connect('search_cache.db')
        cursor = conn.cursor()
        
        # Create table for caching search results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_results_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                location TEXT NOT NULL,
                search_query TEXT NOT NULL,
                places_data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                UNIQUE(service, location)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Search cache database initialized successfully")
    except Exception as e:
        print(f"Error initializing search cache database: {str(e)}")
        if conn:
            conn.close()
        raise e

# Initialize all databases when app starts
with app.app_context():
    init_service_providers_db()
    init_search_cache_db()

# Initialize pro registration database
pro_db = SQLiteDatabase('pro_registration.db')
pro_db.execute('''
    CREATE TABLE IF NOT EXISTS pro_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT,
        service_types TEXT,
        years_experience INTEGER,
        license_number TEXT,
        insurance_info TEXT,
        website TEXT,
        address TEXT,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

def get_db_connection(db_name):
    """Get a database connection"""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def get_cached_search_results(service, location):
    """Get cached search results if they exist and haven't expired"""
    try:
        conn = sqlite3.connect('search_cache.db')
        cursor = conn.cursor()
        
        # Get cached results that haven't expired
        cursor.execute('''
            SELECT places_data, cached_at, expires_at 
            FROM search_results_cache 
            WHERE service = ? AND location = ? AND expires_at > datetime('now')
        ''', (service, location))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
        
    except Exception as e:
        print(f"Error getting cached results: {str(e)}")
        if conn:
            conn.close()
        return None

def cache_search_results(service, location, places_data):
    """Cache search results for 6 months"""
    try:
        conn = sqlite3.connect('search_cache.db')
        cursor = conn.cursor()
        
        # Calculate expiration date (6 months from now)
        six_months_later = datetime.now() + timedelta(days=180)
        
        # Store or update cached results
        cursor.execute('''
            INSERT OR REPLACE INTO search_results_cache 
            (service, location, search_query, places_data, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            service,
            location,
            f"{service} in {location}",
            json.dumps(places_data),
            six_months_later.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error caching results: {str(e)}")
        if conn:
            conn.close()

def search_places(service, location):
    """Search for places using cache first, then Google Places API if needed"""
    try:
        # Check cache first
        cached_results = get_cached_search_results(service, location)
        if cached_results:
            print(f"Using cached results for {service} in {location}")
            return cached_results
        
        # If not in cache, call Google Places API
        print(f"Calling Google Places API for {service} in {location}")
        
        # Construct the search query
        query = f"{service} in {location}"
        
        # Call Google Places API (using your existing API call code)
        places_result = get_places_data(query, location)
        
        # Process and format the results
        places_data = places_result.get('places', [])
        
        # Cache the results
        cache_search_results(service, location, places_data)
        
        return places_data
        
    except Exception as e:
        print(f"Error in search_places: {str(e)}")
        traceback.print_exc()
        return []

# Cache for service pages
service_page_cache = {}

@app.route('/')
def index():
    """Serve the main page"""
    categories = load_categories()
    locations = load_locations()
    service_links = generate_service_links(categories, locations)
    return render_template('index.html', 
                         categories=categories, 
                         locations=locations,
                         service_links=service_links)

@app.route('/service/<slug>')
def service_page(slug):
    """Serve a service page"""
    # Check cache first
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
            # Fallback if 'in' is not found
            location_parts = [parts[-1]]  # Take last part as location
            category_parts = parts[1:-2]  # Skip first and last two parts
        
        # Remove common words from category
        common_words = {
            'services', 'contractors', 'professionals', 'service',
            'contractor', 'professional', 'and', 'the'
        }
        category_parts = [p for p in category_parts if p not in common_words]
        
        # Reconstruct category and location
        category = ' '.join(category_parts).title()
        location = ' '.join(location_parts).title()
        
        # Verify category and location exist
        categories = load_categories()
        locations = load_locations()
        
        # Find closest matching category
        matched_category = None
        for c in categories:
            if category.lower() in c.lower() or c.lower() in category.lower():
                matched_category = c
                break
        
        # Find closest matching location
        matched_location = None
        for l in locations:
            if location.lower() in l.lower() or l.lower() in location.lower():
                matched_location = l
                break
        
        if not matched_category or not matched_location:
            abort(404)
        
        # Generate page content
        meta_description = generate_meta_description(matched_category, matched_location)
        service_description = generate_service_description(matched_category, matched_location)
        
        # Search for businesses
        search_results = get_places_data(f"{matched_category} in {matched_location}", matched_location)
        
        # Render template
        page = render_template('service_page.html',
                         title=f"Best {matched_category} Services in {matched_location}",
                         meta_description=meta_description,
                         service_description=service_description,
                         category=matched_category,
                         location=matched_location,
                         search_results=search_results)
        
        # Cache the page
        service_page_cache[slug] = page
        
        return page
        
    except Exception as e:
        print(f"Error generating service page: {str(e)}")
        traceback.print_exc()
        abort(404)

@app.route('/api/categories')
def get_categories():
    """API endpoint to get list of service categories"""
    categories = load_categories()
    if not categories:
        return jsonify({'error': 'Error loading categories'}), 500
    return jsonify(categories)

@app.route('/api/locations')
def get_locations():
    """API endpoint to get list of locations"""
    locations = load_locations()
    if not locations:
        return jsonify({'error': 'Error loading locations'}), 500
    return jsonify(locations)

def get_places_data(query, location, page_token=None, get_total=False):
    """
    Fetch data from Google Places API V1 with proper error handling
    """
    try:
        print("\n=== PLACES API REQUEST ===")
        print(f"Query: {query}")
        print(f"Location: {location}")
        print(f"Page Token: {page_token}")
        print(f"Get Total: {get_total}")
        
        # Check if API key is set
        if not GOOGLE_PLACES_API_KEY:
            print("Error: Google Places API key is not set")
            return {'error': 'Google Places API key is not configured'}
        
        # Check API rate limit
        if check_api_rate_limit():
            print("Rate limit exceeded")
            return {'error': 'API rate limit exceeded', 'rate_limited': True}

        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.websiteUri,places.internationalPhoneNumber,places.regularOpeningHours,places.primaryType,places.types,nextPageToken'
        }
        print("Headers:", headers)

        # Prepare request body
        data = {
            'textQuery': f"{query} in {location}",
            'locationBias': {
                'circle': {
                    'center': {
                        'latitude': 43.6532,  # Toronto's latitude
                        'longitude': -79.3832  # Toronto's longitude
                    },
                    'radius': 50000.0  # 50km radius
                }
            },
            'maxResultCount': 20 if get_total else 10,
            'languageCode': 'en'
        }
        
        if page_token:
            data['pageToken'] = page_token
            
        print("Request Data:", json.dumps(data, indent=2))
        print("API URL:", GOOGLE_PLACES_API_URL)
        
        # Make API request
        print("Making API request...")
        response = requests.post(GOOGLE_PLACES_API_URL, headers=headers, json=data)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Log API usage
        api_monitor.log_request('places', 'searchText', 0, response.status_code)
        
        if response.status_code == 200:
            results = response.json()
            print("Raw Response:", json.dumps(results, indent=2))
            
            if not results.get('places'):
                print("Warning: No places found in response")
                return {
                    'places': [],
                    'next_page_token': None
                }
            
            # Transform the response to match the expected format
            places = []
            for place in results.get('places', []):
                # Get business hours
                opening_hours = place.get('regularOpeningHours', {})
                periods = opening_hours.get('periods', [])
                
                # Check if currently open
                now = datetime.now()
                current_day = now.weekday()
                current_time = now.strftime('%H:%M')
                
                is_open = False
                for period in periods:
                    if period.get('open', {}).get('day') == current_day:
                        open_time = period.get('open', {}).get('time', '')
                        close_time = period.get('close', {}).get('time', '')
                        if open_time <= current_time <= close_time:
                            is_open = True
                            break

                transformed_place = {
                    'name': place.get('displayName', {}).get('text', 'Name not available'),
                    'address': place.get('formattedAddress', 'Address not available'),
                    'rating': place.get('rating'),
                    'reviews': place.get('userRatingCount'),
                    'website': place.get('websiteUri'),
                    'phone': place.get('internationalPhoneNumber'),
                    'business_type': place.get('primaryType', '').replace('_', ' ').title(),
                    'types': [t.replace('_', ' ').title() for t in place.get('types', [])],
                    'opening_hours': {
                        'open_now': is_open,
                        'periods': periods
                    } if opening_hours else None,
                    'location': place.get('location', {})
                }
                places.append(transformed_place)
            
            print(f"Transformed {len(places)} places")
            for place in places:
                print(f"- {place['name']}: {place['address']}")
            
            # Get next page token from response
            next_page_token = results.get('nextPageToken')
            print(f"Next page token: {next_page_token}")
            
            return {
                'places': places,
                'next_page_token': next_page_token
            }
        else:
            error_msg = f"API request failed with status code: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {json.dumps(error_details)}"
            except:
                error_msg += f" - {response.content.decode('utf-8', errors='ignore')}"
            print(f"API Error: {error_msg}")
            return {'error': error_msg}

    except Exception as e:
        error_msg = f"Error fetching places data: {str(e)}"
        print(f"Exception: {error_msg}")
        traceback.print_exc()
        return {'error': error_msg}

def check_api_rate_limit():
    """Check if we've exceeded our monthly API rate limit"""
    try:
        usage = api_monitor.get_monthly_usage()
        if usage and usage.get('remaining_quota', 0) <= 0:
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to get monthly usage: {str(e)}")
        return False  # If we can't check the rate limit, assume we haven't hit it

def get_cached_results(query_hash, page=1):
    """
    Retrieve cached results if they exist and are not expired
    page: Page number to retrieve (1-based)
    """
    try:
        result = db.cache_results.fetch_one('''
            SELECT results, timestamp, expiry, next_page_token, total_results 
            FROM cached_results 
            WHERE cache_key = ? AND page_number = ? AND expiry > ?
        ''', (query_hash, page, datetime.utcnow().isoformat()))
        
        if result:
            cached_data = json.loads(result[0])
            logger.info(f"Cache hit for {query_hash} page {page}")
            logger.info(f"Cached results count: {len(cached_data.get('places', []))}")
            return {
                'results': cached_data,
                'timestamp': result[1],
                'next_page_token': result[3],
                'total_results': result[4]
            }
        return None
    except Exception as e:
        logger.error(f"Error retrieving cached results: {str(e)}")
        return None

def cache_results(cache_key: str, results: dict, page: int, next_page_token: str = None) -> bool:
    """Cache search results with pagination support."""
    try:
        def cache_operation():
            new_doc = {
                'cache_key': cache_key,
                'results': json.dumps(results),
                'page_number': page,
                'next_page_token': next_page_token,
                'total_results': len(results.get('places', [])),
                'timestamp': datetime.utcnow().isoformat(),
                'expiry': (datetime.utcnow() + timedelta(days=180)).isoformat()
            }
            
            db.cache_results.execute('''
                INSERT OR REPLACE INTO cached_results 
                (cache_key, results, page_number, next_page_token, total_results, timestamp, expiry) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_doc['cache_key'],
                new_doc['results'],
                new_doc['page_number'],
                new_doc['next_page_token'],
                new_doc['total_results'],
                new_doc['timestamp'],
                new_doc['expiry']
            ))
            logger.info(f"Successfully cached results for {cache_key} page {page}")

        def rollback_operation():
            db.cache_results.execute(
                'DELETE FROM cached_results WHERE cache_key = ? AND page_number = ?',
                (cache_key, page)
            )
            logger.info(f"Rolled back cache operation for {cache_key} page {page}")

        rollback_manager.add_operation(cache_operation, rollback_operation)
        rollback_manager.execute()
        return True
    except Exception as e:
        logger.error(f"Error caching results for {cache_key}: {str(e)}")
        return False

@app.route('/api/search', methods=['GET'])
def search():
    """Search for businesses based on category and location"""
    try:
        # Get search parameters
        category = request.args.get('category')
        location = request.args.get('location')
        page_token = request.args.get('page_token')
        current_count = int(request.args.get('current_count', '0'))
        
        print(f"\n=== SEARCH REQUEST ===")
        print(f"Category: {category}")
        print(f"Location: {location}")
        print(f"Page Token: {page_token}")
        print(f"Current Count: {current_count}")
        
        if not category or not location:
            return jsonify({'error': 'Category and location are required'}), 400
        
        # Generate search query
        query = f"{category}"
        
        # Get all results for total count on first page
        if not page_token:
            print("Getting total count...")
            all_results = get_places_data(query, location, get_total=True)
            if 'error' in all_results:
                print(f"Error getting total count: {all_results['error']}")
                return jsonify(all_results), 400
            total_results = min(len(all_results.get('places', [])), 20)  # Cap at 20
            print(f"Total results found (capped at 20): {total_results}")
        else:
            # For subsequent pages, use the count from the first page
            total_results = min(int(request.args.get('total_results', 0)), 20)  # Cap at 20
        
        # Get paginated results
        print("Getting paginated results...")
        results = get_places_data(query, location, page_token)
        
        if 'error' in results:
            print(f"Error from Places API: {results['error']}")
            return jsonify(results), 400
        
        # Get places from the response
        places = results.get('places', [])
        next_page_token = results.get('next_page_token')
        
        # Update current count
        new_count = current_count + len(places)
        
        # Check if we should show more results (if we haven't shown all results yet)
        has_more = new_count < total_results and next_page_token is not None
        
        # Prepare response
        response = {
            'places': places,
            'total_results': total_results,
            'has_more': has_more,
            'next_page': next_page_token,
            'current_count': new_count
        }
        
        print("\n=== SEARCH RESPONSE ===")
        print(f"Total Results (capped at 20): {total_results}")
        print(f"Places in this page: {len(places)}")
        print(f"Current total shown: {new_count}")
        print(f"Has more: {has_more}")
        print(f"Next page token: {None if not has_more else next_page_token}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-quote', methods=['POST'])
def submit_quote_request():
    """Submit a quote request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'service', 'location', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Connect to database
        conn = get_db_connection('contact_requests.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert the quote request
        cursor.execute('''
            INSERT INTO quote_requests (name, email, phone, service, location, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            data['phone'],
            data['service'],
            data['location'],
            data['description']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Quote request submitted successfully'}), 200
        
    except Exception as e:
        print(f"Error submitting quote: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/register-professional', methods=['POST'])
def register_professional():
    """Register a new professional"""
    conn = None
    try:
        data = request.get_json()
        print(f"Received registration data: {data}")
        
        # Validate required fields
        required_fields = ['businessName', 'contactName', 'email', 'phone', 'services', 'locations', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate services and locations are lists
        if not isinstance(data['services'], list) or not isinstance(data['locations'], list):
            return jsonify({'error': 'Services and locations must be lists'}), 400
        
        # Connect to database
        conn = sqlite3.connect('service_providers.db')
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        services_json = json.dumps(data['services'])
        locations_json = json.dumps(data['locations'])
        
        print("Inserting data into database...")
        # Insert the professional registration
        cursor.execute('''
            INSERT INTO service_providers (
                business_name, contact_name, email, phone, services, locations,
                license, insurance, description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['businessName'],
            data['contactName'],
            data['email'],
            data['phone'],
            services_json,
            locations_json,
            data.get('license', ''),
            data.get('insurance', ''),
            data['description']
        ))
        
        conn.commit()
        print("Data inserted successfully")
        
        # Verify the insertion
        cursor.execute('SELECT * FROM service_providers WHERE email = ?', (data['email'],))
        result = cursor.fetchone()
        print(f"Verification query result: {result}")
        
        conn.close()
        return jsonify({'message': 'Professional registration submitted successfully'}), 200
        
    except Exception as e:
        print(f"Error registering professional: {str(e)}")
        traceback.print_exc()
        if conn:
            conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        port = int(os.getenv('PORT', 5008))  # Changed port to 5008
        logger.info('Starting application with configuration:')
        logger.info(f'Debug mode: {True}')
        logger.info(f'Starting Flask application on port {port}')
        app.run(host='127.0.0.1', port=port, debug=True)
            
    except Exception as e:
        logger.error(f'Failed to start the application: {str(e)}')
        raise
