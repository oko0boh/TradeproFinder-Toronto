#!/bin/bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data

# Initialize databases if needed
python -c "
from app import create_app
from database_manager import DatabaseManager
app = create_app('production')
with app.app_context():
    db = DatabaseManager()
"

echo "Build completed successfully"
