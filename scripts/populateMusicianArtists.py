#taking the musician artists from the Artists table and adding them in MusicianArtists table
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

def get_musician_artist_details(sp, artist_name):
    """Get additional details about a musician artist"""
    try:

        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1, market='US')
        
        if results['artists']['items']:
            artist = results['artists']['items'][0]
            popularity = artist['popularity']
            followers = artist['followers']['total']
            
            return {
                'popularity': popularity,
                'followers': followers
            }
        else:
            return {
                'popularity': 0,
                'followers': 0
            }
    
    except Exception as e:
        print(f"Error fetching details for {artist_name}: {e}")
        return {
            'popularity': 0,
            'followers': 0
        }

def populate_musician_artists():
    """Populate MusicianArtists table with details"""
    conn = mysql.connector.connect(**DB_CONNECTION)
    cursor = conn.cursor()
    
    try:
    
        cursor.execute("""
            SELECT artist_id, name 
            FROM Artists 
            WHERE type = 'MusicianArtist'
            AND artist_id NOT IN (SELECT artist_id FROM MusicianArtists)
        """)
        
        musician_artists = cursor.fetchall()
        
        if not musician_artists:
            print("No new musician artists found to process.")
            return
        
       
        sp = get_spotify_client()
        
    
        for artist_id, artist_name in musician_artists:
            print(f"Processing artist: {artist_name}")
            
        
            details = get_musician_artist_details(sp, artist_name)
            
           
            cursor.execute("""
                INSERT INTO MusicianArtists (artist_id, popularity, followers)
                VALUES (%s, %s, %s)
            """, (
                artist_id,
                details['popularity'],
                details['followers']
            ))
            
            print(f"Added details for {artist_name}")
        
        conn.commit()
        print(f"Successfully populated details for {len(musician_artists)} musician artists")
        
    except Exception as e:
        print(f"Error populating MusicianArtists: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def main():
    populate_musician_artists()

if __name__ == '__main__':
    main()
