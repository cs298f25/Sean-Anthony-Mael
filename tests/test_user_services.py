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

