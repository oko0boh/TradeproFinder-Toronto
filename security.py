"""
Security module for Tradepro Finder Toronto.
"""

from functools import wraps
from flask import request, abort, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_seasurf import SeaSurf
from werkzeug.security import generate_password_hash, check_password_hash
import re

# Initialize security extensions
csrf = SeaSurf()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def init_security(app):
    """Initialize security features."""
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; font-src 'self' https:;"
        return response

def validate_input(data, rules):
    """Validate input data against rules."""
    errors = []
    
    for field, value in data.items():
        if field in rules:
            rule = rules[field]
            
            # Required check
            if rule.get('required', False) and not value:
                errors.append(f"{field} is required")
                continue
            
            # Type check
            if 'type' in rule:
                if rule['type'] == 'email' and not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    errors.append(f"{field} must be a valid email")
                elif rule['type'] == 'phone' and not re.match(r"^\+?1?\d{9,15}$", value):
                    errors.append(f"{field} must be a valid phone number")
            
            # Length check
            if 'min_length' in rule and len(value) < rule['min_length']:
                errors.append(f"{field} must be at least {rule['min_length']} characters")
            if 'max_length' in rule and len(value) > rule['max_length']:
                errors.append(f"{field} must be at most {rule['max_length']} characters")
            
            # Pattern check
            if 'pattern' in rule and not re.match(rule['pattern'], value):
                errors.append(f"{field} has an invalid format")
    
    return errors

def require_api_key(f):
    """Decorator to require API key for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config['API_KEY']:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

# Input validation rules
CONTACT_FORM_RULES = {
    'name': {
        'required': True,
        'min_length': 2,
        'max_length': 100,
        'pattern': r'^[a-zA-Z\s\-\']+$'
    },
    'email': {
        'required': True,
        'type': 'email'
    },
    'phone': {
        'required': True,
        'type': 'phone'
    },
    'message': {
        'required': True,
        'min_length': 10,
        'max_length': 1000
    }
}

QUOTE_REQUEST_RULES = {
    'name': {
        'required': True,
        'min_length': 2,
        'max_length': 100,
        'pattern': r'^[a-zA-Z\s\-\']+$'
    },
    'email': {
        'required': True,
        'type': 'email'
    },
    'phone': {
        'required': True,
        'type': 'phone'
    },
    'service_type': {
        'required': True
    },
    'description': {
        'required': True,
        'min_length': 10,
        'max_length': 2000
    }
}

PRO_REGISTRATION_RULES = {
    'business_name': {
        'required': True,
        'min_length': 2,
        'max_length': 100
    },
    'owner_name': {
        'required': True,
        'min_length': 2,
        'max_length': 100,
        'pattern': r'^[a-zA-Z\s\-\']+$'
    },
    'email': {
        'required': True,
        'type': 'email'
    },
    'phone': {
        'required': True,
        'type': 'phone'
    },
    'service_types': {
        'required': True
    },
    'license_number': {
        'required': True,
        'pattern': r'^[A-Z0-9\-]+$'
    }
}
