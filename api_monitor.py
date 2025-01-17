"""API Usage Monitoring and Rate Limiting Module."""
import os
import json
from datetime import datetime, timedelta
import logging
from database_manager import DatabaseManager, SQLiteDatabase

# Configure logging
logger = logging.getLogger(__name__)

class APIMonitor:
    def __init__(self, monthly_limit=200):
        """Initialize API Monitor with monthly limit."""
        self.monthly_limit = monthly_limit
        self.db = DatabaseManager()
        self.api_db = SQLiteDatabase('api_usage.db')
        self._init_tables()
        
    def _init_tables(self):
        self.api_db.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_name TEXT,
                endpoint TEXT,
                request_time TIMESTAMP,
                response_time INTEGER,
                status_code INTEGER,
                error TEXT
            )
        ''')
    
    def log_request(self, api_name, endpoint, response_time, status_code, error=None):
        """Log an API request with its details."""
        try:
            self.api_db.insert('api_usage', {
                'api_name': api_name,
                'endpoint': endpoint,
                'request_time': datetime.utcnow().isoformat(),
                'response_time': response_time,
                'status_code': status_code,
                'error': error
            })
            logger.info(f"Logged API request: {api_name} - {endpoint}")
        except Exception as e:
            logger.error(f"Failed to log API request: {str(e)}")
    
    def get_monthly_usage(self):
        """Get current month's API usage statistics."""
        current_month = datetime.utcnow().strftime('%Y-%m')
        
        try:
            # Get total requests this month
            result = self.api_db.fetch_one('''
                SELECT COUNT(*) 
                FROM api_usage 
                WHERE strftime('%Y-%m', request_time) = ?
            ''', (current_month,))
            
            total_requests = result[0] if result else 0
            
            # Calculate remaining quota
            remaining = self.monthly_limit - total_requests
            
            return {
                "month": current_month,
                "total_requests": total_requests,
                "remaining_quota": remaining,
                "usage_percent": round((total_requests / self.monthly_limit * 100), 2)
            }
        except Exception as e:
            logger.error(f"Failed to get monthly usage: {str(e)}")
            return {
                "month": current_month,
                "total_requests": 0,
                "remaining_quota": self.monthly_limit,
                "usage_percent": 0
            }
    
    def can_make_request(self):
        """Check if we can make a new API request based on quota."""
        usage = self.get_monthly_usage()
        if not usage:
            return False
        
        # Allow request if we haven't exceeded monthly limit
        return usage["remaining_quota"] > 0
    
    def get_usage_analytics(self, days=30):
        """Get detailed API usage analytics for the past N days."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            results = self.api_db.execute('''
                SELECT 
                    STRFTIME('%Y-%m-%d', request_time) AS date,
                    COUNT(*) AS count,
                    AVG(response_time) AS avg_response_time
                FROM api_usage
                WHERE request_time >= ?
                GROUP BY date
                ORDER BY date ASC
            ''', (start_date,)).fetchall()
            
            # Format results
            analytics = {}
            for result in results:
                date = result[0]
                analytics[date] = {
                    "api_requests": result[1],
                    "avg_response_time": round(result[2], 3)
                }
            
            return analytics
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {str(e)}")
            return None
    
    def export_monthly_report(self, output_dir="reports"):
        """Export monthly API usage report to JSON file."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            usage = self.get_monthly_usage()
            analytics = self.get_usage_analytics()
            
            report = {
                "monthly_summary": usage,
                "daily_analytics": analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            filename = f"api_usage_{usage['month']}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Monthly report exported to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export monthly report: {str(e)}")
            return None
