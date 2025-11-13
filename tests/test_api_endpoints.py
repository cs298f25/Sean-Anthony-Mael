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

def test_update_user_location_endpoint(test_db):
    """
    Test: Can we update a user's location through the PUT /api/users/<user_id>/location endpoint?
    
    This test checks that:
    - We can update a user's location via PUT request
    - The response has the correct status code (200)
    - The location is actually updated in the database
    - The response contains the updated user data
    """
    # Step 1: Create a user first
    user_id = services.create_user(name="Grace", latitude=40.7128, longitude=-74.0060)
    
    # Step 2: Prepare new location data
    new_location = {
        'latitude': 47.6062,  # Seattle
        'longitude': -122.3321
    }
    
    # Step 3: Use Flask's test client to make a PUT request
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/location',
            json=new_location,
            content_type='application/json'
        )
    
    # Step 4: Check the response status code (200 = success)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Step 5: Parse the JSON response
    data = response.get_json()
    
    # Step 6: Verify the location was updated
    assert data is not None, "Response should contain JSON data"
    assert data['latitude'] == 47.6062, "Latitude should be updated"
    assert data['longitude'] == -122.3321, "Longitude should be updated"
    assert data['name'] == "Grace", "Name should remain unchanged"
    
    # Step 7: Verify the update persisted in the database
    updated_user = services.get_user(user_id)
    assert updated_user['latitude'] == 47.6062, "Latitude should be saved in database"
    assert updated_user['longitude'] == -122.3321, "Longitude should be saved in database"

def test_update_user_name_endpoint(test_db):
    """
    Test: Can we update a user's name through the PUT /api/users/<user_id>/name endpoint?
    
    This test checks that:
    - We can update a user's name via PUT request
    - The response has the correct status code (200)
    - The name is actually updated in the database
    - The response contains the updated user data
    - Other fields (like location) remain unchanged
    """
    # Step 1: Create a user first with a name and location
    user_id = services.create_user(name="Henry", latitude=34.0522, longitude=-118.2437)
    
    # Step 2: Prepare new name data
    new_name_data = {
        'name': 'Henry Updated'
    }
    
    # Step 3: Use Flask's test client to make a PUT request
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/name',
            json=new_name_data,
            content_type='application/json'
        )
    
    # Step 4: Check the response status code (200 = success)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Step 5: Parse the JSON response
    data = response.get_json()
    
    # Step 6: Verify the name was updated
    assert data is not None, "Response should contain JSON data"
    assert data['name'] == 'Henry Updated', "Name should be updated"
    assert data['latitude'] == 34.0522, "Latitude should remain unchanged"
    assert data['longitude'] == -118.2437, "Longitude should remain unchanged"
    
    # Step 7: Verify the update persisted in the database
    updated_user = services.get_user(user_id)
    assert updated_user['name'] == 'Henry Updated', "Name should be saved in database"
    assert updated_user['latitude'] == 34.0522, "Location should remain unchanged"

def test_update_user_location_missing_fields(test_db):
    """
    Test: What happens when we try to update location with missing required fields?
    
    This test checks that:
    - The endpoint returns 400 (Bad Request) when latitude is missing
    - The endpoint returns 400 (Bad Request) when longitude is missing
    - The endpoint returns 400 (Bad Request) when both are missing
    - The response contains an appropriate error message
    """
    # Step 1: Create a user first
    user_id = services.create_user(name="Iris", latitude=40.7128, longitude=-74.0060)
    
    # Step 2: Try to update location with missing latitude
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/location',
            json={'longitude': -122.4194},  # Missing latitude
            content_type='application/json'
        )
    
    # Step 3: Should return 400 (Bad Request)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.get_json()
    assert data['error'] == 'latitude and longitude are required', "Error message should indicate missing fields"
    
    # Step 4: Try to update location with missing longitude
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/location',
            json={'latitude': 37.7749},  # Missing longitude
            content_type='application/json'
        )
    
    # Step 5: Should return 400 (Bad Request)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.get_json()
    assert data['error'] == 'latitude and longitude are required', "Error message should indicate missing fields"
    
    # Step 6: Try to update location with both fields missing
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/location',
            json={},  # Empty JSON - both fields missing
            content_type='application/json'
        )
    
    # Step 7: Should return 400 (Bad Request)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.get_json()
    assert data['error'] == 'latitude and longitude are required', "Error message should indicate missing fields"
    
    # Step 8: Verify the user's location was NOT changed (should still be original)
    user = services.get_user(user_id)
    assert user['latitude'] == 40.7128, "Location should not have changed"
    assert user['longitude'] == -74.0060, "Location should not have changed"

def test_update_user_name_missing_field(test_db):
    """
    Test: What happens when we try to update name with missing or empty name?
    
    This test checks that:
    - The endpoint returns 400 (Bad Request) when name is missing
    - The endpoint returns 400 (Bad Request) when name is empty string
    - The response contains an appropriate error message
    - The user's name was NOT changed
    """
    # Step 1: Create a user first
    user_id = services.create_user(name="Jack", latitude=40.7128, longitude=-74.0060)
    
    # Step 2: Try to update name with missing name field
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/name',
            json={},  # Empty JSON - name field missing
            content_type='application/json'
        )
    
    # Step 3: Should return 400 (Bad Request)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.get_json()
    assert data['error'] == 'name is required', "Error message should indicate name is required"
    
    # Step 4: Try to update name with empty string
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{user_id}/name',
            json={'name': ''},  # Empty string
            content_type='application/json'
        )
    
    # Step 5: Should return 400 (Bad Request)
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    data = response.get_json()
    assert data['error'] == 'name is required', "Error message should indicate name is required"
    
    # Step 6: Verify the user's name was NOT changed (should still be original)
    user = services.get_user(user_id)
    assert user['name'] == "Jack", "Name should not have changed"

def test_update_user_visit_endpoint(test_db):
    """
    Test: Can we update a user's visit timestamp through the PUT /api/users/<user_id>/visit endpoint?
    
    This test checks that:
    - We can update a user's visit timestamp via PUT request
    - The response has the correct status code (200)
    - The timestamp is actually updated
    - The response contains the updated user data
    """
    # Step 1: Create a user first
    user_id = services.create_user(name="Kelly")
    
    # Step 2: Get the initial timestamp
    initial_user = services.get_user(user_id)
    initial_timestamp = initial_user['last_updated']
    
    # Step 3: Use Flask's test client to make a PUT request
    with app.test_client() as client:
        response = client.put(f'/api/users/{user_id}/visit')
    
    # Step 4: Check the response status code (200 = success)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    # Step 5: Parse the JSON response
    data = response.get_json()
    
    # Step 6: Verify the response contains user data
    assert data is not None, "Response should contain JSON data"
    assert data['user_id'] == user_id, "User ID should match"
    assert data['name'] == "Kelly", "Name should remain unchanged"
    
    # Step 7: Verify the timestamp was updated
    new_timestamp = data['last_updated']
    assert new_timestamp is not None, "Timestamp should exist"
    assert new_timestamp >= initial_timestamp, "New timestamp should be >= initial timestamp"
    
    # Step 8: Verify the update persisted in the database
    updated_user = services.get_user(user_id)
    assert updated_user['last_updated'] >= initial_timestamp, "Timestamp should be updated in database"

def test_update_location_nonexistent_user(test_db):
    """
    Test: What happens when we try to update location for a user that doesn't exist?
    
    This test checks that:
    - The endpoint returns 404 (Not Found) for non-existent users
    - The response contains an error message
    - The API handles this error case gracefully
    """
    # Step 1: Try to update location for a fake/non-existent user
    fake_user_id = "non-existent-user-12345"
    location_data = {
        'latitude': 40.7128,
        'longitude': -74.0060
    }
    
    # Step 2: Use Flask's test client to make a PUT request
    with app.test_client() as client:
        response = client.put(
            f'/api/users/{fake_user_id}/location',
            json=location_data,
            content_type='application/json'
        )
    
    # Step 3: Check the response status code (404 = Not Found)
    assert response.status_code == 404, f"Expected status 404, got {response.status_code}"
    
    # Step 4: Parse the JSON response
    data = response.get_json()
    
    # Step 5: Verify the error message
    assert data is not None, "Response should contain JSON data"
    assert 'error' in data, "Response should contain an error field"
    assert data['error'] == 'User not found', "Error message should be 'User not found'"

