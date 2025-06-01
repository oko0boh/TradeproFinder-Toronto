"""
Test routes for Tradepro Finder Toronto.
"""

def test_home_page(client):
    """Test home page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Tradepro Finder Toronto' in response.data

def test_search_api(client):
    """Test search API."""
    data = {
        'service': 'plumber',
        'location': 'Toronto'
    }
    response = client.post('/api/search', json=data)
    assert response.status_code == 200
    assert 'results' in response.get_json()

def test_contact_form(client):
    """Test contact form submission."""
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'message': 'Test message'
    }
    response = client.post('/api/contact', json=data)
    assert response.status_code == 200
    assert 'message' in response.get_json()
