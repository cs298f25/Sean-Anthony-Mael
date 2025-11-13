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

def test_create_user_endpoint(test_db):
    """
    Test: Can we create a user through the POST /api/users endpoint?
    
    This test checks that:
    - We can POST JSON data to create a user
    - The response has the correct status code (201 = created)
    - The response contains the user_id and user data
    - The user was actually created in the database
    """
    # Step 1: Prepare the data to send in the POST request
    user_data = {
        'name': 'Frank',
        'latitude': 37.7749,  # San Francisco
        'longitude': -122.4194
    }
    
    # Step 2: Use Flask's test client to make a POST request
    with app.test_client() as client:
        response = client.post(
            '/api/users',
            json=user_data,  # Flask automatically converts this to JSON
            content_type='application/json'
        )
    
    # Step 3: Check the response status code (201 = created)
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"
    
    # Step 4: Parse the JSON response
    data = response.get_json()
    
    # Step 5: Verify the response structure
    assert data is not None, "Response should contain JSON data"
    assert 'user_id' in data, "Response should contain user_id"
    assert 'user' in data, "Response should contain user object"
    
    # Step 6: Verify the user data matches what we sent
    user = data['user']
    assert user['name'] == 'Frank', "Name should match"
    assert user['latitude'] == 37.7749, "Latitude should match"
    assert user['longitude'] == -122.4194, "Longitude should match"
    
    # Step 7: Verify we can retrieve the user using the returned user_id
    user_id = data['user_id']
    retrieved_user = services.get_user(user_id)
    assert retrieved_user is not None, "User should exist in database"
    assert retrieved_user['name'] == 'Frank', "User name should be saved correctly"

def test_get_user_endpoint_not_found(test_db):
    """
    Test: What happens when we GET a user that doesn't exist?
    
    This test checks that:
    - The endpoint returns 404 (Not Found) for non-existent users
    - The response contains an error message
    - The API handles errors gracefully
    """
    # Step 1: Try to get a user with a fake/non-existent user_id
    fake_user_id = "non-existent-user-id-12345"
    
    # Step 2: Use Flask's test client to make a GET request
    with app.test_client() as client:
        response = client.get(f'/api/users/{fake_user_id}')
    
    # Step 3: Check the response status code (404 = Not Found)
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}"
    
    # Step 4: Parse the JSON response
    data = response.get_json()
    
    # Step 5: Verify the error message
    assert data is not None, "Response should contain JSON data"
    assert 'error' in data, "Response should contain an error field"
    assert data['error'] == 'User not found', "Error message should be 'User not found'"

