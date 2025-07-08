# Railway Deployment Setup Guide

## Environment Variables

When deploying to Railway via GitHub integration, you'll need to set up the following environment variables in the Railway dashboard:

### Required Environment Variables

1. **GOOGLE_PLACES_API_KEY**
   - Your Google Places API key for location services
   - This is required for the application to function properly

2. **FLASK_ENV**
   - Set to `production` for deployment
   - Controls Flask application environment

### Optional Environment Variables

3. **FLASK_DEBUG**
   - Set to `0` for production deployment
   - Controls debug mode (should be off in production)

4. **PYTHONUNBUFFERED**
   - Set to `1` to ensure Python output is sent straight to the terminal without buffering
   - Helpful for viewing logs in real-time

## How to Set Environment Variables in Railway

1. Go to your project in the Railway dashboard
2. Click on the "Variables" tab
3. Add each environment variable with its corresponding value
4. Click "Add" after entering each variable
5. Railway will automatically redeploy your application with the new environment variables

## Deployment Process

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python application
3. The `railway.toml` configuration will be used to:
   - Run the build command: `python generate_seo_pages.py`
   - Start the application with: `gunicorn wsgi:flask_instance --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
4. Railway will provide a generated URL for your application

## Troubleshooting

If your application fails to deploy:

1. Check the Railway logs for specific error messages
2. Verify all required environment variables are set correctly
3. Make sure your `requirements.txt` file includes all necessary dependencies
4. Confirm your `Procfile` and `railway.toml` are configured correctly
