"""
Tests for user-related database functions.
We'll test creating users and retrieving them.
"""

from database import services

def test_create_user(test_db):
    """
    Test 1: Can we create a user?
    
    This test checks that:
    - create_user() returns a user_id (a string)
    - The user_id is not empty
    """
    # Create a user with a name
    user_id = services.create_user(name="Test User")
    
    # Assert that we got a user_id back
    assert user_id is not None, "create_user should return a user_id"
    assert isinstance(user_id, str), "user_id should be a string"
    assert len(user_id) > 0, "user_id should not be empty"
    
    # UUIDs are typically 36 characters long (with dashes)
    # But we'll just check it's not empty

def test_create_user_and_get_user(test_db):
    """
    Test 2: Can we create a user and then retrieve it?
    
    This test checks that:
    - We can create a user
    - We can retrieve that same user using the user_id
    - The retrieved user has the correct information
    """
    # Step 1: Create a user with specific data
    name = "Alice"
    latitude = 40.7128  # New York coordinates
    longitude = -74.0060
    
    user_id = services.create_user(name=name, latitude=latitude, longitude=longitude)
    
    # Step 2: Retrieve the user we just created
    user = services.get_user(user_id)
    
    # Step 3: Check that we got the user back
    assert user is not None, "get_user should return the user we just created"
    
    # Step 4: Check that the data matches what we put in
    assert user['name'] == name, f"User name should be '{name}'"
    assert user['user_id'] == user_id, "User ID should match"
    assert user['latitude'] == latitude, "Latitude should match"
    assert user['longitude'] == longitude, "Longitude should match"

def test_update_user_location(test_db):
    """
    Test 3: Can we update a user's location?
    
    This test checks that:
    - We can create a user with an initial location
    - We can update that user's location to new coordinates
    - The updated location is saved correctly
    """
    # Step 1: Create a user with an initial location
    initial_lat = 40.7128   # New York
    initial_lon = -74.0060
    user_id = services.create_user(name="Bob", latitude=initial_lat, longitude=initial_lon)
    
    # Step 2: Verify the initial location was saved
    user = services.get_user(user_id)
    assert user['latitude'] == initial_lat, "Initial latitude should be saved"
    assert user['longitude'] == initial_lon, "Initial longitude should be saved"
    
    # Step 3: Update to a new location
    new_lat = 34.0522   # Los Angeles
    new_lon = -118.2437
    services.update_user_location(user_id, new_lat, new_lon)
    
    # Step 4: Retrieve the user again and check the location was updated
    updated_user = services.get_user(user_id)
    assert updated_user['latitude'] == new_lat, "Latitude should be updated"
    assert updated_user['longitude'] == new_lon, "Longitude should be updated"
    
    # Step 5: Make sure the name didn't change (it shouldn't)
    assert updated_user['name'] == "Bob", "Name should remain unchanged"

