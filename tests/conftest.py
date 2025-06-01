"""
Test configuration for Tradepro Finder Toronto.
"""

import pytest
from app import create_app
from database_manager import DatabaseManager

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create test database."""
    db = DatabaseManager(app)
    return db
