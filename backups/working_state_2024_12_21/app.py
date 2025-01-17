from flask import Flask, jsonify, request, render_template, abort, make_response, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
import requests
from pymongo import MongoClient, ASCENDING
from datetime import datetime, timedelta
import json
from utils.sitemap_generator import SitemapGenerator
import jinja2
import os
from datetime import datetime
import hashlib
import logging
import sys
from logging.handlers import RotatingFileHandler
from api_monitor import APIMonitor
import time
from rollback_manager import RollbackManager
import io

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=10),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG level

# Configure logging
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.DEBUG)  # Set to DEBUG level
logger.addHandler(file_handler)

# Add a stream handler to see logs in console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(stream_handler)

logger.setLevel(logging.DEBUG)  # Set main logger to DEBUG level
logger.info('Tradepro Finder Toronto startup')

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Constants
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
GOOGLE_PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'
TORONTO_COORDS = {"latitude": 43.6532, "longitude": -79.3832}  # Toronto city center

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['tradepro_finder']
cached_results = db['cached_results']
user_submissions = db['user_submissions']
contact_requests = db['contact_requests']
service_providers = db['service_providers']

# Initialize rollback manager
rollback_manager = RollbackManager(db)

# Create indexes for better query performance
cached_results.create_index([("timestamp", ASCENDING)])
cached_results.create_index([("query_hash", ASCENDING)], unique=True)

# Initialize API Monitor
api_monitor = APIMonitor(os.getenv('MONGO_URI'))

# Load CSV data at startup
try:
    categories_df = pd.read_csv('data/tradepro_finder_toronto_keywords.csv')
    locations_df = pd.read_csv('data/tradepro_finder_cities.csv')
    logger.info('Successfully loaded CSV files')
except Exception as e:
    logger.error(f'Error loading CSV files: {str(e)}')
    categories_df = pd.DataFrame(columns=['Category'])
    locations_df = pd.DataFrame(columns=['Location'])

def get_places_data(query, location, page_token=None):
    """
    Fetch data from Google Places API V1 with proper error handling
    """
    try:
        # Check rate limit before making API call
        if not api_monitor.can_make_request():
            logger.warning("API rate limit reached")
            return {'error': 'Rate limit reached', 'rate_limited': True}
            
        logger.info(f'Making Places API call for query: {query}, location: {location}')
        
        # Use the new Places API v1 endpoint
        url = 'https://places.googleapis.com/v1/places:searchText'
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.primaryType,places.internationalPhoneNumber,places.websiteUri,places.id'
        }
        
        # Construct a more natural search query
        search_query = f"{query} near {location}"
        
        data = {
            'textQuery': search_query,
            'locationBias': {
                'circle': {
                    'center': {
                        'latitude': 43.6532,  # Toronto center
                        'longitude': -79.3832
                    },
                    'radius': 50000.0  # 50km radius to cover GTA
                }
            },
            'maxResultCount': 20,
            'languageCode': 'en'
        }
        
        if page_token:
            data['pageToken'] = page_token
            
        logger.info(f'API Request - URL: {url}')
        logger.info(f'API Request - Query: {search_query}')
        
        response = requests.post(url, headers=headers, json=data)
        logger.info(f'API Response Status: {response.status_code}')
        
        if response.status_code != 200:
            logger.error(f'Google Places API error: {response.status_code} - {response.text}')
            return None
            
        result = response.json()
        
        # Format the results
        formatted_results = {
            'places': [],
            'next_page_token': result.get('nextPageToken')
        }
        
        for place in result.get('places', []):
            formatted_place = {
                'name': place.get('displayName', {}).get('text', ''),
                'address': place.get('formattedAddress', ''),
                'rating': place.get('rating', 0),
                'user_ratings_total': place.get('userRatingCount', 0),
                'place_id': place.get('id', ''),
                'phone': place.get('internationalPhoneNumber', ''),
                'website': place.get('websiteUri', ''),
                'location': place.get('location', {})
            }
            formatted_results['places'].append(formatted_place)
            
        logger.info(f'Found {len(formatted_results["places"])} places')
        return formatted_results
        
    except Exception as e:
        logger.error(f'Error fetching places data: {str(e)}', exc_info=True)
        return None

def cache_results(cache_key: str, results: dict) -> bool:
    """Cache search results with rollback support."""
    try:
        def cache_operation():
            new_doc = {
                'cache_key': cache_key,
                'results': results,
                'timestamp': datetime.utcnow(),
                'expiry': datetime.utcnow() + timedelta(days=180)
            }
            cached_results.replace_one(
                {'cache_key': cache_key},
                new_doc,
                upsert=True
            )

        def rollback_operation():
            cached_results.delete_one({'cache_key': cache_key})

        rollback_manager.add_operation(cache_operation, rollback_operation)
        rollback_manager.execute()
        return True
        
    except Exception as e:
        logger.error(f"Error caching results for {cache_key}: {str(e)}")
        return False

def clear_cache(cache_key: str = None) -> bool:
    """Clear cache with rollback support."""
    try:
        if cache_key:
            # Clear specific cache entry
            def clear_operation():
                cached_results.delete_one({'cache_key': cache_key})

            def rollback_operation():
                # Nothing to rollback for deletion
                pass

            rollback_manager.add_operation(clear_operation, rollback_operation)
            rollback_manager.execute()
        else:
            # Clear all cache
            def clear_operation():
                cached_results.delete_many({})

            def rollback_operation():
                # Nothing to rollback for deletion
                pass

            rollback_manager.add_operation(clear_operation, rollback_operation)
            rollback_manager.execute()

        return True

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return False

def get_cached_results(query_hash):
    """
    Retrieve cached results if they exist and are not expired
    """
    try:
        cache = cached_results.find_one({
            'cache_key': query_hash,
            'expiry': {'$gt': datetime.utcnow()}
        })
        if cache:
            logger.info(f"Cache hit for {query_hash}")
            logger.info(f"Cached results count: {len(cache['results'].get('results', []))}")
            logger.info(f"Cache timestamp: {cache['timestamp']}")
        else:
            logger.info(f"Cache miss for {query_hash}")
        return cache['results'] if cache else None
    except Exception as e:
        logger.error(f"Error retrieving cached results: {str(e)}", exc_info=True)
        return None

# Meta tag generation helper functions
def generate_meta_tags(service, location):
    """Generate optimized meta tags for service-location combinations."""
    service_title = service.replace('-', ' ').title()
    location_title = location.replace('-', ' ').title()
    
    return {
        'title': f'Top {service_title} in {location_title}, Toronto (2024) | TradePro Finder',
        'description': f'Find the best {service_title} in {location_title}, Toronto. ✓ Verified Professionals ✓ Free Quotes ✓ Available Now ✓ Local Experts.',
        'keywords': f'{service_title}, {location_title}, Toronto, professional {service_title}, local {service_title}, {service_title} near me',
        'robots': 'index, follow',
        'og:title': f'Best {service_title} in {location_title}, Toronto',
        'og:description': f'Connect with top-rated {service_title} in {location_title}, Toronto. Get free quotes and hire the best professionals for your needs.',
        'og:type': 'website',
        'og:url': f'https://tradeprofinder.toronto/{service}-in-{location}-toronto',
        'twitter:card': 'summary_large_image',
        'twitter:title': f'Best {service_title} in {location_title}, Toronto',
        'twitter:description': f'Find reliable {service_title} in {location_title}, Toronto. Book now and get free quotes from verified professionals.'
    }

def generate_optimized_content(service, location):
    """Generate SEO-optimized content for service-location pages."""
    service_title = service.replace('-', ' ').title()
    location_title = location.replace('-', ' ').title()
    
    return {
        'intro': f'''Looking for professional {service_title} in {location_title}, Toronto? 
                    Our verified experts provide top-quality services at competitive prices. 
                    Get free quotes and book your service today!''',
        
        'why_choose': f'''
            <ul class="list-unstyled">
                <li><i class="fas fa-check text-success me-2"></i> Verified & Licensed {service_title}</li>
                <li><i class="fas fa-check text-success me-2"></i> Free, No-Obligation Quotes</li>
                <li><i class="fas fa-check text-success me-2"></i> Available 24/7 for Emergencies</li>
                <li><i class="fas fa-check text-success me-2"></i> Competitive Pricing</li>
                <li><i class="fas fa-check text-success me-2"></i> Satisfaction Guaranteed</li>
                <li><i class="fas fa-check text-success me-2"></i> Local {location_title} Experts</li>
            </ul>
        ''',
        
        'service_areas': f'''
            <p>We provide {service_title} services in:</p>
            <ul class="list-unstyled">
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> {location_title}</li>
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> North York</li>
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> Scarborough</li>
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> Etobicoke</li>
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> Downtown Toronto</li>
                <li><i class="fas fa-map-marker-alt text-danger me-2"></i> Greater Toronto Area</li>
            </ul>
        '''
    }

def generate_listing_schema(service, location, businesses):
    """Generate ItemList schema for service category pages."""
    service_title = service.replace('-', ' ').title()
    location_title = location.replace('-', ' ').title()
    
    items = []
    for idx, business in enumerate(businesses, 1):
        item = {
            "@type": "LocalBusiness",
            "@id": f"#{business.get('id', '')}",
            "name": business.get('displayName', {}).get('text', ''),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": business.get('formattedAddress', '')
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": business.get('location', {}).get('latitude', ''),
                "longitude": business.get('location', {}).get('longitude', '')
            },
            "url": f"https://tradeprofinder.toronto/{service}-in-{location}-toronto#{business.get('id', '')}",
            "telephone": business.get('phoneNumbers', [{}])[0].get('phoneNumber', '') if business.get('phoneNumbers') else '',
            "position": idx
        }
        
        if business.get('rating'):
            item.update({
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": business.get('rating', 0),
                    "reviewCount": business.get('userRatingCount', 0)
                }
            })
            
        items.append(item)
    
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": f"Best {service_title} in {location_title}, Toronto",
        "description": f"List of top-rated {service_title} professionals serving {location_title}, Toronto area.",
        "numberOfItems": len(items),
        "itemListElement": items
    }

# Initialize sitemap generator
sitemap_generator = SitemapGenerator()

@app.route('/')
def index():
    logger.info('Homepage accessed')
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        # Read categories from CSV and return as list
        categories = categories_df['Category'].tolist()
        logger.info(f'Returning {len(categories)} categories')
        return jsonify(categories)
    except Exception as e:
        logger.error(f'Error getting categories: {str(e)}')
        return jsonify([]), 500

@app.route('/api/locations', methods=['GET'])
def get_locations():
    try:
        # Read locations from CSV and return as list
        locations = locations_df['Location'].tolist()
        logger.info(f'Returning {len(locations)} locations')
        return jsonify(locations)
    except Exception as e:
        logger.error(f'Error getting locations: {str(e)}')
        return jsonify([]), 500

@app.route('/api/search', methods=['GET'])
def search_businesses():
    try:
        logger.info('Search request received')
        category = request.args.get('category')
        location = request.args.get('location')
        page_token = request.args.get('pageToken')
        force_refresh = request.args.get('force_refresh', '').lower() == 'true'
        
        logger.info(f'Search parameters - Category: {category}, Location: {location}, PageToken: {page_token}, Force Refresh: {force_refresh}')
        
        if not category or not location:
            logger.warning('Missing required search parameters')
            return jsonify({'error': 'Category and location are required'}), 400

        # Create cache key
        cache_key = f"{category}_{location}_{page_token or 'first'}"
        logger.info(f'Cache key: {cache_key}')
        
        # Check rate limit before proceeding
        if not force_refresh and not api_monitor.can_make_request():
            logger.warning("API rate limit reached, attempting to serve cached results")
            cached_results = get_cached_results(cache_key)
            if cached_results and cached_results.get('results'):
                logger.info("Serving cached results due to rate limit")
                return jsonify(cached_results)
            logger.error("No cached results available and rate limit reached")
            return jsonify({
                'error': 'Rate limit reached, no cached results available',
                'retry_after': '1 hour'
            }), 429
        
        # Try to get cached results only if not forcing refresh
        if not page_token and not force_refresh:
            cached_results = get_cached_results(cache_key)
            if cached_results and cached_results.get('results'):
                logger.info(f'Returning cached results with {len(cached_results.get("results", []))} items')
                return jsonify(cached_results)
            logger.info('No valid cached results found, making API call')
        
        # Get results from Google Places API
        results = get_places_data(category, location, page_token)
        
        if not results:
            logger.error('Failed to get results from Google Places API')
            return jsonify({'error': 'Failed to fetch results'}), 500
            
        if not results['places']:
            logger.warning(f'No results found for category: {category}, location: {location}')
            # Don't cache empty results
            return jsonify({'results': [], 'next_page_token': None})
            
        logger.info(f'Found {len(results["places"])} results from API')
        for idx, result in enumerate(results['places']):
            logger.info(f'Result {idx + 1}: {result["name"]} - {result["address"]}')
            
        # Cache only non-empty results (first page only)
        if not page_token and results['places']:
            cache_results(cache_key, results)
            
        return jsonify(results)
        
    except Exception as e:
        logger.error(f'Search error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit-inquiry', methods=['POST'])
def submit_inquiry():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['name', 'email', 'phone', 'message', 'businessName']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Add timestamp and status
        data['timestamp'] = datetime.utcnow()
        data['status'] = 'new'
        
        # Insert into MongoDB
        result = user_submissions.insert_one(data)
        
        if not result.inserted_id:
            return jsonify({'error': 'Failed to save inquiry'}), 500

        return jsonify({
            'message': 'Inquiry submitted successfully',
            'inquiry_id': str(result.inserted_id)
        })

    except Exception as e:
        logger.error(f'Error submitting inquiry: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/sitemap.xml')
def sitemap():
    """Generate and serve sitemap.xml"""
    try:
        logger.info('Generating sitemap.xml')
        
        # Get all categories and locations
        categories = categories_df['Category'].tolist()
        locations = locations_df['Location'].tolist()
        
        # Generate URLs for all service-location combinations
        urls = []
        # Add homepage
        urls.append({
            'loc': 'https://tradeprofinder.toronto/',
            'lastmod': datetime.now().strftime('%Y-%m-%d'),
            'priority': '1.0'
        })
        
        # Add service-location pages
        for category in categories:
            for location in locations:
                urls.append({
                    'loc': f'https://tradeprofinder.toronto/{category.lower()}-{location.lower()}',
                    'lastmod': datetime.now().strftime('%Y-%m-%d'),
                    'priority': '0.8'
                })
        
        # Create sitemap XML
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url in urls:
            xml += '  <url>\n'
            xml += f'    <loc>{url["loc"]}</loc>\n'
            xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'
            xml += f'    <priority>{url["priority"]}</priority>\n'
            xml += '  </url>\n'
        
        xml += '</urlset>'
        
        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        return response
        
    except Exception as e:
        logger.error(f'Error generating sitemap: {str(e)}')
        return 'Error generating sitemap', 500

@app.route('/robots.txt')
def robots():
    """Serve robots.txt file"""
    return """
User-agent: *
Allow: /
Sitemap: https://tradeprofinder.toronto/sitemap.xml
"""

def is_valid_service_location(service, location):
    """Validate if service and location combination exists in our data."""
    try:
        # Convert service and location to lowercase for case-insensitive comparison
        service = service.lower().strip()
        location = location.lower().strip()
        
        # Handle plural/singular forms
        if not service.endswith('s'):
            service += 's'  # Convert singular to plural
            
        # Handle Toronto neighborhoods
        if location.endswith('-toronto'):
            location = location.replace('-toronto', '')
        
        # Get valid services and locations, converting to lowercase
        valid_services = [s.lower().strip() for s in categories_df['Category'].tolist()]
        valid_locations = [l.lower().strip() for l in locations_df['Location'].tolist()]
        
        # Special case: if location contains 'etobicoke', it's valid since it's a Toronto district
        if 'etobicoke' in location:
            location = 'toronto'
        
        # Debug logging
        logger.debug(f"Checking service: {service}")
        logger.debug(f"Valid services: {valid_services}")
        logger.debug(f"Checking location: {location}")
        logger.debug(f"Valid locations: {valid_locations}")
        
        is_valid = service in valid_services and (location in valid_locations or location == 'toronto')
        logger.info(f"Service-location validation result: {is_valid}")
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating service-location: {str(e)}")
        return False

def get_location_coordinates(location):
    """Get coordinates for a location in Toronto."""
    # For now, return default Toronto coordinates
    # You can enhance this later with actual geocoding
    return {
        'lat': '43.653225',
        'lng': '-79.383186'
    }

@app.route('/<service>-in-<location>-toronto')
@app.route('/<service>-in-<location>')
@app.route('/<service>-<location>')
def service_location_page(service, location):
    try:
        # Validate service and location
        if not is_valid_service_location(service, location):
            logger.warning(f"Invalid service-location combination: {service}-{location}")
            abort(404)
            
        # Get page number from query params, default to 1
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Results per page
        
        # Format search query
        search_query = f"{service} in {location}"
        
        # Generate cache key
        query_hash = hashlib.md5(search_query.encode()).hexdigest()
        
        # Try to get cached results
        cached_data = get_cached_results(query_hash)
        if cached_data:
            results = cached_data.get('places', [])
        else:
            # Fetch from Google Places API
            api_results = get_places_data(search_query, f"{location}")
            if api_results and 'places' in api_results:
                # Cache the results
                cache_results(query_hash, api_results)
                results = api_results.get('places', [])
            else:
                results = []

        # Paginate results
        total_results = len(results)
        total_pages = (total_results + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = results[start_idx:end_idx]

        # Generate meta tags and schema
        meta_tags = generate_meta_tags(service, location)
        schema = generate_listing_schema(service, location, paginated_results)
        
        # Generate optimized content
        content = generate_optimized_content(service, location)

        return render_template(
            'service_location.html',
            service=service,
            location=location,
            results=paginated_results,
            page=page,
            total_pages=total_pages,
            meta_tags=meta_tags,
            schema=schema,
            content=content
        )
    except Exception as e:
        logger.error(f"Error in service_location_page: {str(e)}")
        abort(500)

# Add API usage monitoring endpoints
@app.route('/api/usage')
def api_usage():
    """Get current API usage statistics."""
    usage = api_monitor.get_monthly_usage()
    if usage:
        return jsonify(usage)
    return jsonify({"error": "Failed to get API usage"}), 500

@app.route('/api/analytics')
def api_analytics():
    """Get detailed API usage analytics."""
    days = request.args.get('days', default=30, type=int)
    analytics = api_monitor.get_usage_analytics(days)
    if analytics:
        return jsonify(analytics)
    return jsonify({"error": "Failed to get API analytics"}), 500

@app.route('/api/export-report')
def export_report():
    """Export monthly API usage report."""
    report_path = api_monitor.export_monthly_report()
    if report_path:
        return jsonify({"message": "Report exported successfully", "path": report_path})
    return jsonify({"error": "Failed to export report"}), 500

# Contact and Details routes
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'message', 'businessName', 'placeId']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Store in MongoDB
        contact_requests.insert_one({
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'message': data['message'],
            'business_name': data['businessName'],
            'place_id': data['placeId'],
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/service-request', methods=['POST'])
def service_request():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address', 'service_needed', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Store in MongoDB
        user_submissions.insert_one({
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'service_needed': data['service_needed'],
            'description': data['description'],
            'timestamp': datetime.utcnow(),
            'status': 'new'
        })
        
        return jsonify({'success': True, 'message': 'Service request submitted successfully'})
    except Exception as e:
        app.logger.error(f"Error processing service request: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process service request. Please try again.'}), 500

@app.route('/api/pro-signup', methods=['POST'])
def pro_signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'business_name', 'owner_name', 'email', 'phone', 
            'address', 'services', 'years_experience', 'service_areas'
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        # Validate services and service_areas are not empty lists
        if not data.get('services'):
            return jsonify({'success': False, 'error': 'Please select at least one service'}), 400
        if not data.get('service_areas'):
            return jsonify({'success': False, 'error': 'Please select at least one service area'}), 400
        
        # Store in MongoDB
        db.service_providers.insert_one({
            'business_name': data['business_name'],
            'owner_name': data['owner_name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'services': data['services'],
            'license_number': data.get('license_number', ''),  # Optional
            'years_experience': data['years_experience'],
            'insurance_info': data.get('insurance_info', ''),  # Optional
            'service_areas': data['service_areas'],
            'status': 'pending',
            'timestamp': datetime.utcnow()
        })
        
        return jsonify({
            'success': True, 
            'message': 'Your application has been submitted successfully! We will review your information and contact you soon.'
        })
    except Exception as e:
        app.logger.error(f"Error processing pro signup: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Failed to process your application. Please try again.'
        }), 500

@app.route('/admin/service-providers', methods=['GET'])
def view_service_providers():
    try:
        # Get all service providers from MongoDB
        providers = list(db.service_providers.find({}, {'_id': 0}))
        
        # Convert datetime objects to string for JSON serialization
        for provider in providers:
            if 'timestamp' in provider:
                provider['timestamp'] = provider['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Return as formatted HTML
        return render_template('admin/providers.html', providers=providers)
    except Exception as e:
        app.logger.error(f"Error fetching service providers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/service-requests', methods=['GET'])
def view_service_requests():
    try:
        # Get all service requests from MongoDB
        requests = list(user_submissions.find({}, {'_id': 0}))
        
        # Convert datetime objects to string for JSON serialization
        for request in requests:
            if 'timestamp' in request:
                request['timestamp'] = request['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Return as formatted HTML
        return render_template('admin/requests.html', requests=requests)
    except Exception as e:
        app.logger.error(f"Error fetching service requests: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Legal pages routes
@app.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

@app.route('/terms')
def terms():
    return render_template('legal/terms.html')

@app.route('/faq')
def faq():
    return render_template('legal/faq.html')

@app.route('/sitemap.xml')
def sitemap_xml():
    try:
        return send_from_directory('static', 'sitemap.xml')
    except Exception as e:
        logger.error(f'Error serving sitemap.xml: {str(e)}')
        abort(404)

@app.route('/robots.txt')
def robots_txt():
    try:
        return send_from_directory('static', 'robots.txt')
    except Exception as e:
        logger.error(f'Error serving robots.txt: {str(e)}')
        abort(404)

if __name__ == '__main__':
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configuration logging
        logger.info('Starting application with configuration:')
        logger.info(f'Debug mode: {app.debug}')
        
        # Try different ports if 5002 is in use
        ports = [5002, 5003, 5004, 5005]
        
        for port in ports:
            try:
                logger.info(f'Attempting to start Flask application on port {port}')
                app.run(host='0.0.0.0', port=port, debug=True)
                break  # If successful, exit the loop
            except OSError as e:
                if e.errno == 48:  # Address already in use
                    logger.warning(f'Port {port} is already in use, trying next port')
                    continue
                else:
                    raise  # Re-raise if it's a different error
        else:
            logger.error('All ports are in use. Please free up one of the ports and try again.')
            
    except Exception as e:
        logger.error(f'Failed to start the application: {str(e)}')
        raise
