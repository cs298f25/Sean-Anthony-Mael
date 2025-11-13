"""
Tests for Flask API endpoints.
We'll test the HTTP endpoints that the frontend calls.
"""

import sys
from pathlib import Path

# Also add src directory to path so weather module can be found
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.app import app
from database import services

def test_get_user_endpoint_success(test_db):
    """
    Test: Can we successfully GET a user through the API endpoint?
    
    This test checks that:
    - We can create a user
    - We can retrieve that user via the GET /api/users/<user_id> endpoint
    - The response has the correct status code (200)
    - The response contains the correct user data
    """
    # Step 1: Create a user using the service function
    user_id = services.create_user(name="API Test User", latitude=40.7128, longitude=-74.0060)
    
    # Step 2: Use Flask's test client to make a GET request to the endpoint
    with app.test_client() as client:
        response = client.get(f'/api/users/{user_id}')
    
    # Step 3: Check the response status code (200 = success)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Step 4: Parse the JSON response
    data = response.get_json()
    
    # Step 5: Verify the response contains the correct user data
    assert data is not None, "Response should contain JSON data"
    assert data['user_id'] == user_id, "User ID should match"
    assert data['name'] == "API Test User", "Name should match"
    assert data['latitude'] == 40.7128, "Latitude should match"
    assert data['longitude'] == -74.0060, "Longitude should match"

