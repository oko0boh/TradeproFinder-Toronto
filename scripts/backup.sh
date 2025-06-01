#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/tradepro-finder"
DB_NAME="tradepro_finder"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://your-backup-bucket"  # Replace with your S3 bucket

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
pg_dump "$DB_NAME" > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Backup uploads directory
echo "Backing up uploads..."
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" /var/www/tradepro-finder/uploads

# Backup configuration files
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" /etc/tradepro-finder

# Upload to S3 (if configured)
if command -v aws &> /dev/null; then
    echo "Uploading to S3..."
    aws s3 sync "$BACKUP_DIR" "$S3_BUCKET/$(date +%Y/%m/%d)"
fi

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -type f -mtime +7 -delete

echo "Backup completed successfully!"
