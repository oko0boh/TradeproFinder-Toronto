#!/bin/bash

echo "Starting deployment process..."

# Check if we're on main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "Error: Not on main branch"
    exit 1
fi

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Clear cache
echo "Clearing application cache..."
if [ -d "instance/cache" ]; then
    rm -rf instance/cache/*
fi

# Collect static files (if applicable)
echo "Collecting static files..."
python manage.py collect_static

# Restart the application
echo "Restarting the application..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart tradepro-finder
else
    # Alternative restart command (e.g., for supervisor)
    sudo supervisorctl restart tradepro-finder
fi

# Check application status
echo "Checking application status..."
if command -v systemctl &> /dev/null; then
    systemctl status tradepro-finder
else
    supervisorctl status tradepro-finder
fi

echo "Deployment complete!"
