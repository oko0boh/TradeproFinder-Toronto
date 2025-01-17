"""
Error handling and logging configuration for Tradepro Finder Toronto.
"""

import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
from flask import render_template, jsonify, current_app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_error_handling(app):
    """Initialize error handling and logging."""
    
    # Set up Sentry if DSN is configured
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=app.config['FLASK_ENV']
        )
    
    # Set up logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_SIZE'],
        backupCount=app.config['LOG_BACKUPS']
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(file_handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.logger.info('Tradepro Finder Toronto startup')
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to access this resource'
            }), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def ratelimit_error(error):
        if request.is_json:
            return jsonify({
                'error': 'Too Many Requests',
                'message': 'Rate limit exceeded'
            }), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Server Error: %s', str(error))
        app.logger.error('Traceback: %s', traceback.format_exc())
        
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error('Unhandled Exception: %s', str(error))
        app.logger.error('Traceback: %s', traceback.format_exc())
        
        if current_app.config['DEBUG']:
            raise error
        
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('errors/500.html'), 500
