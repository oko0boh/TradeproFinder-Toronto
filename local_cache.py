import sqlite3
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LocalCache:
    def __init__(self, db_path='local_cache.db'):
        self.db_path = db_path
        logger.info(f"Initializing LocalCache with database: {db_path}")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cached_results (
                    cache_key TEXT PRIMARY KEY,
                    results TEXT,
                    timestamp TIMESTAMP,
                    expiry TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info(f"Initialized cache database: {self.db_path}")

    def find_one(self, query):
        try:
            cache_key = query.get('cache_key')
            logger.info(f"[CACHE] Looking for key: {cache_key}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT results, timestamp, expiry FROM cached_results WHERE cache_key = ? AND expiry > ?',
                    (cache_key, datetime.utcnow().isoformat())
                )
                row = cursor.fetchone()
                if row:
                    expiry_date = datetime.fromisoformat(row[2])
                    time_left = expiry_date - datetime.utcnow()
                    logger.info(f"[CACHE] HIT! Key: {cache_key}, expires in {time_left.days} days")
                    return {
                        'results': json.loads(row[0]),
                        'timestamp': row[1]
                    }
                logger.info(f"[CACHE] MISS! Key: {cache_key}")
                return None
        except Exception as e:
            logger.error(f"[CACHE] Error retrieving from cache: {str(e)}")
            return None

    def replace_one(self, query, new_doc, upsert=True):
        try:
            cache_key = query.get('cache_key') or new_doc.get('cache_key')
            logger.info(f"[CACHE] Storing results for key: {cache_key}")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO cached_results (cache_key, results, timestamp, expiry) VALUES (?, ?, ?, ?)',
                    (
                        cache_key,
                        json.dumps(new_doc.get('results')),
                        new_doc.get('timestamp').isoformat(),
                        new_doc.get('expiry').isoformat()
                    )
                )
                conn.commit()
                logger.info(f"[CACHE] Successfully stored results for key: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"[CACHE] Error caching results: {str(e)}")
            return False

    def delete_one(self, query):
        try:
            cache_key = query.get('cache_key')
            logger.info(f"[CACHE] Deleting key: {cache_key}")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM cached_results WHERE cache_key = ?', (cache_key,))
                conn.commit()
                logger.info(f"[CACHE] Successfully deleted key: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"[CACHE] Error deleting from cache: {str(e)}")
            return False

    def create_index(self, *args, **kwargs):
        # SQLite automatically creates indexes for PRIMARY KEY
        pass
