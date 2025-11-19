"""
Tests for music-related database functions in services.py.
We'll test functions that don't require external API calls first.
"""

from unittest.mock import patch
from database import services

def test_populate_genres_if_empty_when_empty(test_db):
    """
    Test: Can we populate genres when the table is empty?
    
    This test checks that:
    - populate_genres_if_empty() returns False when genres already exist (from init_database)
    - If we clear genres, it can populate them again
    """
    # Step 1: init_database() already populated genres, so this should return False
    result = services.populate_genres_if_empty()
    
    # Step 2: Should return False (genres already exist from init_database)
    assert result is False, "Should return False when genres already exist"
    
    # Step 3: Clear genres table to test the populate functionality
    from database.database import get_db_connection
    with get_db_connection() as conn:
        conn.execute('DELETE FROM genres')
        conn.commit()
    
    # Step 4: Now populate_genres_if_empty should work
    result2 = services.populate_genres_if_empty()
    assert result2 is True, "Should return True when genres are populated"
    
    # Step 5: Verify it doesn't populate again
    result3 = services.populate_genres_if_empty()
    assert result3 is False, "Should return False when genres already exist"

def test_populate_genres_if_empty_when_not_empty(test_db):
    """
    Test: Does populate_genres_if_empty() skip when genres already exist?
    
    This test checks that:
    - populate_genres_if_empty() returns False when genres table is not empty
    - It doesn't try to populate again
    """
    # Step 1: First populate genres
    services.populate_genres_if_empty()
    
    # Step 2: Try to populate again
    result = services.populate_genres_if_empty()
    
    # Step 3: Should return False (genres already exist)
    assert result is False, "Should return False when genres already exist"

def test_link_track_to_genre_with_existing_genre(test_db):
    """
    Test: Can we link a track to an existing genre?
    
    This test checks that:
    - We can create a track
    - We can link it to an existing genre (genres may already exist from init_database)
    - The function returns True on success
    """
    # Step 1: Create an artist and album (required for tracks)
    from database.database import get_db_connection
    with get_db_connection() as conn:
        # Create artist
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Test Artist',))
        artist_id = cursor.lastrowid
        
        # Create album
        cursor = conn.execute('INSERT INTO albums (title, artist_id) VALUES (?, ?)', 
                             ('Test Album', artist_id))
        album_id = cursor.lastrowid
        
        # Create track
        cursor = conn.execute('''
            INSERT INTO tracks (title, artist_id, album_id) 
            VALUES (?, ?, ?)
        ''', ('Test Track', artist_id, album_id))
        track_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Get or create a unique genre (use a unique name to avoid conflicts)
    unique_genre = 'test_unique_genre_12345'
    with get_db_connection() as conn:
        # Check if genre exists, if not create it
        genre_row = conn.execute('SELECT genre_id FROM genres WHERE name = ?', (unique_genre,)).fetchone()
        if genre_row:
            genre_id = genre_row['genre_id']
        else:
            cursor = conn.execute('INSERT INTO genres (name) VALUES (?)', (unique_genre,))
            genre_id = cursor.lastrowid
        conn.commit()
    
    # Step 3: Link track to genre
    result = services.link_track_to_genre(track_id, unique_genre)
    
    # Step 4: Should return True
    assert result is True, "Should return True when linking succeeds"
    
    # Step 5: Verify the link was created
    with get_db_connection() as conn:
        row = conn.execute('''
            SELECT * FROM track_genres 
            WHERE track_id = ? AND genre_id = ?
        ''', (track_id, genre_id)).fetchone()
        assert row is not None, "Track-genre link should exist in database"

def test_link_track_to_genre_creates_genre(test_db):
    """
    Test: Does link_track_to_genre() create a genre if it doesn't exist?
    
    This test checks that:
    - The function creates a new genre if it doesn't exist
    - It then links the track to that new genre
    """
    # Step 1: Create an artist, album, and track
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Test Artist 2',))
        artist_id = cursor.lastrowid
        
        cursor = conn.execute('INSERT INTO albums (title, artist_id) VALUES (?, ?)', 
                             ('Test Album 2', artist_id))
        album_id = cursor.lastrowid
        
        cursor = conn.execute('''
            INSERT INTO tracks (title, artist_id, album_id) 
            VALUES (?, ?, ?)
        ''', ('Test Track 2', artist_id, album_id))
        track_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Link track to a genre that doesn't exist yet
    result = services.link_track_to_genre(track_id, 'jazz')
    
    # Step 3: Should return True
    assert result is True, "Should return True when linking succeeds"
    
    # Step 4: Verify the genre was created and linked
    with get_db_connection() as conn:
        # Check genre exists
        genre_row = conn.execute('SELECT genre_id FROM genres WHERE name = ?', ('jazz',)).fetchone()
        assert genre_row is not None, "Genre 'jazz' should have been created"
        
        # Check link exists
        link_row = conn.execute('''
            SELECT * FROM track_genres 
            WHERE track_id = ? AND genre_id = ?
        ''', (track_id, genre_row['genre_id'])).fetchone()
        assert link_row is not None, "Track-genre link should exist"

def test_add_music_with_all_fields(test_db):
    """
    Test: Can we add music with all fields provided?
    
    This test checks that:
    - add_music() creates artist, album, and track
    - Returns a track_id
    - All data is saved correctly
    """
    # Step 1: Add music with all fields
    track_id = services.add_music(
        title='Test Song',
        artist='Test Artist',
        album='Test Album',
        genre='rock',
        year=2024,
        duration=180,
        metadata='{"key": "value"}'
    )
    
    # Step 2: Verify track_id was returned
    assert track_id is not None, "Should return a track_id"
    assert isinstance(track_id, int), "track_id should be an integer"
    
    # Step 3: Verify we can retrieve the music
    music = services.get_music(track_id)
    assert music is not None, "Music should exist in database"
    assert music['title'] == 'Test Song', "Title should match"
    assert music['duration'] == 180, "Duration should match"
    assert music['metadata'] == '{"key": "value"}', "Metadata should match"

def test_add_music_with_minimal_fields(test_db):
    """
    Test: Can we add music with only required fields (title and artist)?
    
    This test checks that:
    - add_music() works with just title and artist
    - Creates a default "Unknown Album" if no album provided
    - Returns a track_id
    """
    # Step 1: Add music with minimal fields
    track_id = services.add_music(
        title='Minimal Song',
        artist='Minimal Artist'
    )
    
    # Step 2: Verify track_id was returned
    assert track_id is not None, "Should return a track_id"
    
    # Step 3: Verify the track exists
    music = services.get_music(track_id)
    assert music is not None, "Music should exist"
    assert music['title'] == 'Minimal Song', "Title should match"
    
    # Step 4: Verify default album was created
    from database.database import get_db_connection
    with get_db_connection() as conn:
        album_row = conn.execute('''
            SELECT title FROM albums WHERE album_id = ?
        ''', (music['album_id'],)).fetchone()
        assert album_row['title'] == 'Unknown Album', "Should create default album"

def test_add_music_with_existing_artist(test_db):
    """
    Test: Does add_music() reuse existing artists?
    
    This test checks that:
    - If an artist already exists, it reuses the artist_id
    - Doesn't create duplicate artists
    """
    # Step 1: Create an artist first
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Existing Artist',))
        existing_artist_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Add music with the same artist name
    track_id = services.add_music(
        title='Song 1',
        artist='Existing Artist'
    )
    
    # Step 3: Add another track with the same artist
    track_id2 = services.add_music(
        title='Song 2',
        artist='Existing Artist'
    )
    
    # Step 4: Verify both tracks use the same artist_id
    music1 = services.get_music(track_id)
    music2 = services.get_music(track_id2)
    
    assert music1['artist_id'] == existing_artist_id, "Should reuse existing artist"
    assert music2['artist_id'] == existing_artist_id, "Should reuse existing artist"
    assert music1['artist_id'] == music2['artist_id'], "Both tracks should use same artist"

def test_get_music_existing_track(test_db):
    """
    Test: Can we retrieve music by track_id?
    
    This test checks that:
    - get_music() returns the correct track data
    - All fields are present
    """
    # Step 1: Add a track
    track_id = services.add_music(
        title='Retrievable Song',
        artist='Retrievable Artist',
        duration=240
    )
    
    # Step 2: Retrieve the track
    music = services.get_music(track_id)
    
    # Step 3: Verify all data
    assert music is not None, "Music should be retrieved"
    assert music['track_id'] == track_id, "track_id should match"
    assert music['title'] == 'Retrievable Song', "Title should match"
    assert music['duration'] == 240, "Duration should match"

def test_get_music_nonexistent_track(test_db):
    """
    Test: What happens when we try to get a track that doesn't exist?
    
    This test checks that:
    - get_music() returns None for non-existent tracks
    - Doesn't raise an error
    """
    # Step 1: Try to get a non-existent track
    music = services.get_music(99999)
    
    # Step 2: Should return None
    assert music is None, "Should return None for non-existent tracks"

def test_get_artist_by_name_existing(test_db):
    """
    Test: Can we find an artist by name?
    
    This test checks that:
    - get_artist_by_name() returns the correct artist
    - Returns artist_id and name
    """
    # Step 1: Create an artist
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Findable Artist',))
        artist_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Find the artist
    artist = services.get_artist_by_name('Findable Artist')
    
    # Step 3: Verify the data
    assert artist is not None, "Artist should be found"
    assert artist['artist_id'] == artist_id, "artist_id should match"
    assert artist['name'] == 'Findable Artist', "Name should match"

def test_get_artist_by_name_nonexistent(test_db):
    """
    Test: What happens when we try to find an artist that doesn't exist?
    
    This test checks that:
    - get_artist_by_name() returns None for non-existent artists
    - Doesn't raise an error
    """
    # Step 1: Try to find a non-existent artist
    artist = services.get_artist_by_name('Non Existent Artist')
    
    # Step 2: Should return None
    assert artist is None, "Should return None for non-existent artists"

# Tests for API-dependent functions (using mocking)

def test_fetch_and_store_tracks_by_artist_success(test_db):
    """
    Test: Can we fetch and store tracks by artist when API call succeeds?
    
    This test checks that:
    - The function calls the music API
    - Stores tracks in the database
    - Returns the stored tracks
    """
    # Step 1: Create an artist first
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Mock Artist',))
        artist_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Mock the music API response
    mock_tracks_data = [
        {'name': 'Track 1', 'duration': 180},
        {'name': 'Track 2', 'duration': 200}
    ]
    
    with patch('database.services.music.get_artist_top_tracks', return_value=mock_tracks_data):
        # Step 3: Call the function
        result = services.fetch_and_store_tracks_by_artist(artist_id, 'Mock Artist')
    
    # Step 4: Verify tracks were stored and returned
    assert len(result) == 2, "Should return 2 tracks"
    assert all('track_id' in track for track in result), "All tracks should have track_id"
    assert all('title' in track for track in result), "All tracks should have title"
    
    # Step 5: Verify tracks exist in database
    with get_db_connection() as conn:
        tracks = conn.execute('SELECT * FROM tracks WHERE artist_id = ?', (artist_id,)).fetchall()
        assert len(tracks) == 2, "Should have 2 tracks in database"

def test_fetch_and_store_tracks_by_artist_api_failure(test_db):
    """
    Test: What happens when the API call fails?
    
    This test checks that:
    - The function handles API failures gracefully
    - Returns an empty list
    - Doesn't crash
    """
    # Step 1: Create an artist
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Failing Artist',))
        artist_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Mock API to raise an exception
    with patch('database.services.music.get_artist_top_tracks', side_effect=Exception("API Error")):
        # Step 3: Call the function
        result = services.fetch_and_store_tracks_by_artist(artist_id, 'Failing Artist')
    
    # Step 4: Should return empty list
    assert result == [], "Should return empty list on API failure"

def test_fetch_and_store_artists_by_genre_success(test_db):
    """
    Test: Can we fetch and store artists by genre when API call succeeds?
    
    This test checks that:
    - The function calls the music API
    - Stores artists in the database
    - Returns the stored artists
    """
    # Step 1: Mock the music API response
    mock_artist_names = ['Artist 1', 'Artist 2', 'Artist 3']
    
    with patch('database.services.music.get_top_artists_by_genre', return_value=mock_artist_names):
        # Step 2: Call the function
        result = services.fetch_and_store_artists_by_genre('rock')
    
    # Step 3: Verify artists were stored and returned
    assert len(result) <= 15, "Should return at most 15 artists (as per code limit)"
    assert all('artist_id' in artist for artist in result), "All artists should have artist_id"
    assert all('name' in artist for artist in result), "All artists should have name"
    
    # Step 4: Verify artists exist in database
    from database.database import get_db_connection
    with get_db_connection() as conn:
        artists = conn.execute('SELECT * FROM artists WHERE name IN (?, ?, ?)', 
                              ('Artist 1', 'Artist 2', 'Artist 3')).fetchall()
        assert len(artists) == 3, "Should have 3 artists in database"

def test_fetch_and_store_artists_by_genre_api_failure(test_db):
    """
    Test: What happens when the API call fails for artists by genre?
    
    This test checks that:
    - The function handles API failures gracefully
    - Returns an error dict
    """
    # Step 1: Mock API to raise an exception
    with patch('database.services.music.get_top_artists_by_genre', side_effect=Exception("API Error")):
        # Step 2: Call the function
        result = services.fetch_and_store_artists_by_genre('rock')
    
    # Step 3: Should return error info
    assert len(result) > 0, "Should return error information"
    assert 'error' in result[0], "Should contain error information"

def test_fetch_and_store_artists_by_genre_no_results(test_db):
    """
    Test: What happens when API returns no artists?
    
    This test checks that:
    - The function handles empty API responses
    - Returns an error dict
    """
    # Step 1: Mock API to return empty list
    with patch('database.services.music.get_top_artists_by_genre', return_value=[]):
        # Step 2: Call the function
        result = services.fetch_and_store_artists_by_genre('nonexistent')
    
    # Step 3: Should return error info
    assert len(result) > 0, "Should return error information"
    assert 'error' in result[0], "Should contain error information"

def test_get_and_store_tracks_for_artist_by_name_existing_artist(test_db):
    """
    Test: Can we get tracks for an artist by name when artist exists?
    
    This test checks that:
    - The function finds the artist
    - Calls fetch_and_store_tracks_by_artist
    - Returns the tracks
    """
    # Step 1: Create an artist
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', ('Named Artist',))
        artist_id = cursor.lastrowid
        conn.commit()
    
    # Step 2: Mock the fetch_and_store_tracks_by_artist function
    mock_tracks = [
        {'track_id': 1, 'title': 'Track 1', 'artist_name': 'Named Artist'},
        {'track_id': 2, 'title': 'Track 2', 'artist_name': 'Named Artist'}
    ]
    
    with patch('database.services.fetch_and_store_tracks_by_artist', return_value=mock_tracks):
        # Step 3: Call the function
        result = services.get_and_store_tracks_for_artist_by_name('Named Artist')
    
    # Step 4: Should return the tracks
    assert len(result) == 2, "Should return 2 tracks"
    assert result == mock_tracks, "Should return the mocked tracks"

def test_get_and_store_tracks_for_artist_by_name_nonexistent_artist(test_db):
    """
    Test: What happens when artist doesn't exist?
    
    This test checks that:
    - The function returns empty list when artist not found
    - Doesn't crash
    """
    # Step 1: Call with non-existent artist
    result = services.get_and_store_tracks_for_artist_by_name('Non Existent Artist')
    
    # Step 2: Should return empty list
    assert result == [], "Should return empty list for non-existent artist"

def test_fetch_and_store_chart_tracks_success(test_db):
    """
    Test: Can we fetch and store chart tracks when API call succeeds?
    
    This test checks that:
    - The function calls the music API
    - Stores tracks in the database
    - Returns the stored tracks (limited to 20)
    """
    # Step 1: Mock the music API response
    mock_chart_tracks = [
        {'artist': 'Chart Artist 1', 'name': 'Chart Track 1', 'duration': 180},
        {'artist': 'Chart Artist 2', 'name': 'Chart Track 2', 'duration': 200},
        {'artist': 'Chart Artist 3', 'name': 'Chart Track 3', 'duration': 220}
    ]
    
    with patch('database.services.music.get_chart_top_tracks', return_value=mock_chart_tracks):
        # Step 2: Call the function
        result = services.fetch_and_store_chart_tracks()
    
    # Step 3: Verify tracks were stored and returned
    assert len(result) == 3, "Should return 3 tracks"
    assert len(result) <= 20, "Should return at most 20 tracks (as per code limit)"
    assert all('track_id' in track for track in result), "All tracks should have track_id"
    assert all('title' in track for track in result), "All tracks should have title"
    assert all('artist' in track for track in result), "All tracks should have artist"
    
    # Step 4: Verify tracks exist in database
    from database.database import get_db_connection
    with get_db_connection() as conn:
        tracks = conn.execute('SELECT COUNT(*) FROM tracks').fetchone()[0]
        assert tracks == 3, "Should have 3 tracks in database"

def test_fetch_and_store_chart_tracks_api_failure(test_db):
    """
    Test: What happens when the chart tracks API call fails?
    
    This test checks that:
    - The function handles API failures gracefully
    - Returns an empty list
    """
    # Step 1: Mock API to raise an exception
    with patch('database.services.music.get_chart_top_tracks', side_effect=Exception("API Error")):
        # Step 2: Call the function
        result = services.fetch_and_store_chart_tracks()
    
    # Step 3: Should return empty list
    assert result == [], "Should return empty list on API failure"

def test_fetch_and_store_similar_artists_success(test_db):
    """
    Test: Can we fetch and store similar artists when API call succeeds?
    
    This test checks that:
    - The function calls the music API
    - Stores artists in the database
    - Returns the stored artists
    """
    # Step 1: Mock the music API response
    mock_similar_artists = ['Similar Artist 1', 'Similar Artist 2', 'Similar Artist 3']
    
    with patch('database.services.music.get_similar_artists', return_value=mock_similar_artists):
        # Step 2: Call the function
        result = services.fetch_and_store_similar_artists('Original Artist')
    
    # Step 3: Verify artists were stored and returned
    assert len(result) == 3, "Should return 3 artists"
    assert all('artist_id' in artist for artist in result), "All artists should have artist_id"
    assert all('name' in artist for artist in result), "All artists should have name"
    
    # Step 4: Verify artists exist in database
    from database.database import get_db_connection
    with get_db_connection() as conn:
        artists = conn.execute('SELECT * FROM artists WHERE name IN (?, ?, ?)', 
                              ('Similar Artist 1', 'Similar Artist 2', 'Similar Artist 3')).fetchall()
        assert len(artists) == 3, "Should have 3 artists in database"

def test_fetch_and_store_similar_artists_api_failure(test_db):
    """
    Test: What happens when the similar artists API call fails?
    
    This test checks that:
    - The function handles API failures gracefully
    - Returns an empty list
    """
    # Step 1: Mock API to raise an exception
    with patch('database.services.music.get_similar_artists', side_effect=Exception("API Error")):
        # Step 2: Call the function
        result = services.fetch_and_store_similar_artists('Some Artist')
    
    # Step 3: Should return empty list
    assert result == [], "Should return empty list on API failure"

def test_fetch_and_store_tracks_by_genre_success(test_db):
    """
    Test: Can we fetch and store tracks by genre when API calls succeed?
    
    This test checks that:
    - The function populates genres if needed
    - Fetches artists for the genre
    - Fetches tracks for those artists
    - Links tracks to the genre
    - Returns the tracks (limited to 20)
    """
    # Step 1: Mock the music API responses
    mock_artists = [
        {'artist_id': 1, 'name': 'Genre Artist 1'},
        {'artist_id': 2, 'name': 'Genre Artist 2'}
    ]
    mock_tracks = [
        {'track_id': 1, 'title': 'Genre Track 1', 'artist_name': 'Genre Artist 1'},
        {'track_id': 2, 'title': 'Genre Track 2', 'artist_name': 'Genre Artist 2'}
    ]
    
    # Mock the chain of function calls
    with patch('database.services.populate_genres_if_empty', return_value=True), \
         patch('database.services.fetch_and_store_artists_by_genre', return_value=mock_artists), \
         patch('database.services.fetch_and_store_tracks_by_artist', return_value=mock_tracks), \
         patch('database.services.link_track_to_genre', return_value=True):
        # Step 2: Call the function
        result = services.fetch_and_store_tracks_by_genre('rock', max_artists=2)
    
    # Step 3: Verify tracks were returned
    assert len(result) <= 20, "Should return at most 20 tracks (as per code limit)"
    assert all('track_id' in track for track in result), "All tracks should have track_id"

def test_fetch_and_store_tracks_by_genre_no_artists(test_db):
    """
    Test: What happens when no artists are found for a genre?
    
    This test checks that:
    - The function handles the case when no artists are found
    - Returns an empty list
    """
    # Step 1: Mock to return no artists
    with patch('database.services.populate_genres_if_empty', return_value=True), \
         patch('database.services.fetch_and_store_artists_by_genre', return_value=[]):
        # Step 2: Call the function
        result = services.fetch_and_store_tracks_by_genre('nonexistent', max_artists=2)
    
    # Step 3: Should return empty list
    assert result == [], "Should return empty list when no artists found"

def test_fetch_and_store_tracks_by_genre_artist_error(test_db):
    """
    Test: What happens when fetch_and_store_artists_by_genre returns an error?
    
    This test checks that:
    - The function handles error responses from the artists API
    - Returns an empty list
    """
    # Step 1: Mock to return error response
    error_response = [{'error': 'No artists found for genre', 'genre': 'invalid'}]
    
    with patch('database.services.populate_genres_if_empty', return_value=True), \
         patch('database.services.fetch_and_store_artists_by_genre', return_value=error_response):
        # Step 2: Call the function
        result = services.fetch_and_store_tracks_by_genre('invalid', max_artists=2)
    
    # Step 3: Should return empty list
    assert result == [], "Should return empty list when artists API returns error"

