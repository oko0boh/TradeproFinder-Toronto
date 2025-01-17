#!/bin/bash

# Restore to working state from December 21, 2024
echo "Restoring to working state from December 21, 2024..."

# Stop the Flask application if running
echo "Stopping Flask application..."
pkill -f "python.*flask run" || true

# Backup current state before restore
echo "Backing up current state..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p "backups/pre_restore_${timestamp}"
cp app.py rollback_manager.py "backups/pre_restore_${timestamp}/"
cp -r templates "backups/pre_restore_${timestamp}/"

# Restore files from working state
echo "Restoring files..."
cp backups/working_state_2024_12_21/app.py .
cp backups/working_state_2024_12_21/rollback_manager.py .
cp backups/working_state_2024_12_21/index.html templates/

# Clear cache if needed
echo "Note: You may want to clear the cache if there are consistency issues."
echo "To clear cache, use the /api/clear-cache endpoint."

echo "Restore completed. Please restart the Flask application."
