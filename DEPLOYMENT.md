# Deployment Guide for Tradepro Finder Toronto

## Prerequisites

1. Ubuntu 20.04 LTS server
2. Python 3.8+
3. Nginx
4. Redis
5. SSL certificate
6. Domain name pointing to your server

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx redis-server -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

## Step 2: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/tradeprofinder
sudo chown -R $USER:$USER /var/www/tradeprofinder

# Clone repository
git clone https://github.com/your-repo/tradepro-finder-toronto.git /var/www/tradeprofinder

# Create virtual environment
cd /var/www/tradeprofinder
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Environment Configuration

1. Copy `.env.example` to `.env`
2. Update all environment variables with production values
3. Generate a secure secret key:
   ```python
   python3 -c 'import secrets; print(secrets.token_hex(32))'
   ```

## Step 4: Database Setup

```bash
# Initialize database
flask db upgrade
```

## Step 5: Gunicorn Setup

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/tradeprofinder.service
```

Add the following content:

```ini
[Unit]
Description=Tradepro Finder Toronto
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tradeprofinder
Environment="PATH=/var/www/tradeprofinder/venv/bin"
ExecStart=/var/www/tradeprofinder/venv/bin/gunicorn --workers 4 --bind unix:tradeprofinder.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

## Step 6: Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/tradeprofinder
```

Add the following configuration:

```nginx
server {
    server_name tradeprofinder.ca www.tradeprofinder.ca;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/tradeprofinder/tradeprofinder.sock;
    }

    location /static/ {
        alias /var/www/tradeprofinder/static/;
    }

    location /uploads/ {
        alias /var/www/tradeprofinder/uploads/;
    }

    client_max_body_size 16M;
    keepalive_timeout 5;
    
    # SSL configuration will be added by Certbot
}
```

## Step 7: SSL Setup

```bash
sudo certbot --nginx -d tradeprofinder.ca -d www.tradeprofinder.ca
```

## Step 8: Start Services

```bash
# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Start application
sudo systemctl start tradeprofinder
sudo systemctl enable tradeprofinder

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 9: Monitoring Setup

1. Set up Sentry for error tracking
2. Configure Prometheus for metrics
3. Set up logging to external service (optional)

## Security Checklist

- [ ] All sensitive data is in `.env`
- [ ] SSL is properly configured
- [ ] Database backups are automated
- [ ] Rate limiting is enabled
- [ ] CSRF protection is enabled
- [ ] Input validation is implemented
- [ ] Error pages are configured
- [ ] Security headers are set
- [ ] File upload restrictions are in place
- [ ] Database connections are pooled

## Backup Strategy

1. Database backups daily
2. File backups weekly
3. Configuration backups on change
4. Store backups off-site

## Maintenance

1. Monitor logs daily
2. Check error rates
3. Review API usage
4. Update dependencies monthly
5. Rotate logs weekly
6. Check SSL certificate expiry

## Emergency Contacts

- Technical Support: support@tradeprofinder.ca
- Emergency Line: +1 (XXX) XXX-XXXX

## Rollback Procedure

1. Stop services:
   ```bash
   sudo systemctl stop tradeprofinder nginx
   ```

2. Restore from backup:
   ```bash
   ./restore_to_working_state.sh
   ```

3. Start services:
   ```bash
   sudo systemctl start tradeprofinder nginx
   ```
