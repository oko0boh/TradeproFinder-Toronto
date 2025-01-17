"""Service links generation utility"""
import random
from typing import List, Dict
import re

def get_service_icon(category: str) -> str:
    """Get the appropriate icon for a service category"""
    icons = {
        'Cleaning': 'fa-broom',
        'Insulation': 'fa-temperature-low',
        'Drywall': 'fa-layer-group',
        'Masonry': 'fa-th',
        'Electrician': 'fa-bolt',
        'Flooring': 'fa-border-all',
        'Moving': 'fa-truck',
        'Home Renovation': 'fa-hammer',
        'Carpenter': 'fa-hammer',
        'Glass': 'fa-wine-glass',
        'Roofing': 'fa-home',
        'Window': 'fa-window-maximize'
    }
    
    # Find the best matching category
    for key in icons:
        if key.lower() in category.lower():
            return icons[key]
    return 'fa-tools'  # Default icon

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def format_display_title(category: str, location: str) -> str:
    """Format the display title for a service link"""
    prefixes = [
        'Top',
        'Professional',
        'Reliable',
        'Local',
        'Expert',
        'Affordable'
    ]
    
    suffixes = [
        'Services',
        'Contractors',
        'Professionals',
        'Services Services'  # For cases like "Cleaning Services Services"
    ]
    
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    
    # Format: "Top Cleaning Services in Kensington Market"
    return f"{prefix} {category} {suffix} in {location}"

def generate_title_variation(category: str, location: str) -> Dict[str, str]:
    """Generate a title variation for a category and location"""
    display_title = format_display_title(category, location)
    
    return {
        'display_title': display_title,
        'slug': slugify(display_title),
        'category': category,
        'location': location,
        'icon': get_service_icon(category)
    }

def generate_service_links(categories: List[str], locations: List[str], count: int = 50) -> List[Dict[str, str]]:
    """Generate service links for the homepage"""
    links = []
    used_combinations = set()
    
    # Prioritize larger cities with more categories
    main_locations = [
        'Toronto', 'Mississauga', 'Brampton', 'Markham', 'Vaughan',
        'Richmond Hill', 'Oakville', 'Burlington', 'Oshawa', 'Ajax'
    ]
    
    popular_categories = [
        'Cleaning', 'Plumbing', 'Electrical', 'HVAC', 'Painting',
        'Carpentry', 'Roofing', 'Landscaping', 'Moving', 'Renovation',
        'Flooring', 'Drywall', 'Masonry', 'Window', 'Glass'
    ]
    
    # First, generate links for popular combinations
    for location in main_locations:
        if location not in locations:
            continue
        for category in popular_categories:
            if category not in categories:
                continue
            if len(links) >= count:
                break
            if (category, location) not in used_combinations:
                link = generate_title_variation(category, location)
                links.append(link)
                used_combinations.add((category, location))
    
    # Fill remaining slots with random combinations
    while len(links) < count:
        category = random.choice(categories)
        location = random.choice(locations)
        if (category, location) not in used_combinations:
            link = generate_title_variation(category, location)
            links.append(link)
            used_combinations.add((category, location))
    
    return links

def generate_meta_description(category: str, location: str) -> str:
    """Generate meta description for a service page"""
    templates = [
        f"Find the best {category} services in {location}. Trusted professionals, competitive prices, and top-quality service guaranteed.",
        f"Looking for reliable {category} services in {location}? Get connected with top-rated professionals in your area.",
        f"Expert {category} services in {location}. Read reviews, compare quotes, and hire the best professionals for your needs.",
        f"Discover trusted {category} professionals in {location}. Quality service, fair prices, and satisfaction guaranteed."
    ]
    return random.choice(templates)

def generate_service_description(category: str, location: str) -> str:
    """Generate service description for a category and location"""
    return f"""
    <h1>Professional {category} Services in {location}</h1>
    <p>Looking for reliable {category} services in {location}? You've come to the right place. 
    Our platform connects you with trusted {category} professionals who serve the {location} area.</p>
    
    <h2>Why Choose Our {category} Professionals?</h2>
    <ul>
        <li>Experienced and licensed professionals</li>
        <li>Competitive pricing and free quotes</li>
        <li>Quality workmanship guaranteed</li>
        <li>Available for both residential and commercial projects</li>
        <li>Emergency services available</li>
    </ul>
    
    <h2>Services Available in {location}</h2>
    <p>Our {category} professionals in {location} offer a comprehensive range of services to meet your needs. 
    Whether you need routine maintenance, emergency repairs, or a complete installation, our experts are here to help.</p>
    
    <h2>How It Works</h2>
    <ol>
        <li>Browse through our list of verified {category} professionals</li>
        <li>Compare ratings, reviews, and services</li>
        <li>Request free quotes from multiple providers</li>
        <li>Choose the best professional for your needs</li>
    </ol>
    """
