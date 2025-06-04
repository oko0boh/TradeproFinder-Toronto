"""
WSGI entry point for Tradepro Finder Toronto.
"""

import os
from dotenv import load_dotenv
from application import create_app

# Load environment variables
load_dotenv()

# Create application instance
flask_instance = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    flask_instance.run()
