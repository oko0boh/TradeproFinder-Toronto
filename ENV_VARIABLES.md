# Environment Variables for TradeproFinder-Toronto

This document lists all the environment variables required for the application to function properly.

## Required Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `GOOGLE_PLACES_API_KEY` | Your Google Places API key | `YOUR_API_KEY` |
| `FLASK_ENV` | Flask environment (development/production) | `production` |
| `FLASK_APP` | Flask application entry point | `wsgi.py` |
| `PORT` | Port for the application to run on | `10000` |

## Security Best Practices

1. **Never commit your actual API keys or credentials to the repository**
2. **Always use environment variables for sensitive information**
3. **Regularly rotate your API keys**
4. **Restrict API key usage in Google Cloud Console**:
   - Limit to specific APIs
   - Set usage quotas
   - Restrict to specific domains/IPs

## Setting Up in Render

In the Render dashboard:
1. Go to Environment section
2. Add each variable listed above
3. For sensitive variables like API keys, Render will automatically mask them

## Local Development

For local development:
1. Create a `.env` file in the project root (this file is gitignored)
2. Add the variables in this format:
```
GOOGLE_PLACES_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_APP=wsgi.py
PORT=5008
```
