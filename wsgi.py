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

# For Render.com deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    flask_instance.run(host='0.0.0.0', port=port, debug=False)
