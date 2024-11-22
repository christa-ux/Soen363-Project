import os
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup

SPOTIPY_CLIENT_ID = '8bea9279cb4c409f894b175789994e97'
SPOTIPY_CLIENT_SECRET = 'e66e7d7775174b5d8df045491e428abb'

DB_CONNECTION = {
    'database': 'global_music_db',
    'user': 'christa',
    'password': 'sdcn2024',
    'host': 'localhost'
}

def get_spotify_client():
    """Initialize Spotify client"""
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID, 
        client_secret=SPOTIPY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_audiobook_artist_details(sp, artist_name):
    """Get additional details about an audiobook artist"""
    try:
        # Search for audiobooks by this artist/narrator
        results = sp.search(q=f'narrator:{artist_name}', type='audiobook', limit=50, market='US')
        total_books = len(results['audiobooks']['items'])
        
        # Create a biography based on available information
        biography = f"Professional audiobook narrator and voice artist. "
        if total_books > 0:
            biography += f"Has narrated {total_books} or more audiobooks on Spotify. "
            
            # Add genres they've worked with
            genres = set()
            for book in results['audiobooks']['items']:
                if 'categories' in book:
                    genres.update(book['categories'])
            
            if genres:
                biography += f"Specializes in {', '.join(list(genres)[:3])} genres. "
        
        return {
            'biography': biography,
            'total_books': total_books
        }
    
    except Exception as e:
        print(f"Error fetching details for {artist_name}: {e}")
        return {
            'biography': f"Professional audiobook narrator and voice artist.",
            'total_books': 0
        }

def populate_audiobook_artists():
    """Populate AudiobookArtists table with details"""
    conn = mysql.connector.connect(**DB_CONNECTION)
    cursor = conn.cursor()
    
    try:
        # Get all audiobook artists from Artists table
        cursor.execute("""
            SELECT artist_id, name 
            FROM Artists 
            WHERE type = 'AudiobookArtist'
            AND artist_id NOT IN (SELECT artist_id FROM AudiobookArtists)
        """)
        
        audiobook_artists = cursor.fetchall()
        
        if not audiobook_artists:
            print("No new audiobook artists found to process.")
            return
        
        # Initialize Spotify client
        sp = get_spotify_client()
        
        # Process each artist
        for artist_id, artist_name in audiobook_artists:
            print(f"Processing artist: {artist_name}")
            
            # Get additional details
            details = get_audiobook_artist_details(sp, artist_name)
            
            # Insert into AudiobookArtists table
            cursor.execute("""
                INSERT INTO AudiobookArtists (artist_id, biography, total_books)
                VALUES (%s, %s, %s)
            """, (
                artist_id,
                details['biography'],
                details['total_books']
            ))
            
            print(f"Added details for {artist_name}")
        
        conn.commit()
        print(f"Successfully populated details for {len(audiobook_artists)} audiobook artists")
        
    except Exception as e:
        print(f"Error populating AudiobookArtists: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def main():
    populate_audiobook_artists()

if __name__ == '__main__':
    main()