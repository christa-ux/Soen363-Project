#this script populates the Tracks table
import os
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

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

def insert_tracks(tracks):
    """Insert tracks into MySQL database"""
    conn = mysql.connector.connect(**DB_CONNECTION)
    cursor = conn.cursor()
    
    try:
        for track in tracks:
            cursor.execute("""
                INSERT INTO Tracks (name, popularity, duration_ms, release_date)
                VALUES (%s, %s, %s, %s)
            """, (
                track['name'], 
                track['popularity'], 
                track['duration_ms'], 
                track['release_date']
            ))
        
        conn.commit()
        print(f"Inserted {len(tracks)} tracks successfully.")
    
    except Exception as e:
        print(f"Error inserting tracks: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def fetch_spotify_tracks(sp):
    """Fetch tracks from multiple Spotify sources"""
    tracks = []
    
    # Different methods to get more specific tracks
    playlists = [
        '37i9dQZF1DXcBWIGoYBM5M',  # Today's Top Hits
        '37i9dQZF1DWUZv12GM5cFk',  # Global Top 50
        '37i9dQZF1DX0XUsuxWHRQd',  # Rap Caviar
        '37i9dQZF1DXaDhF5qzsCHg'   # RapCaviar Latin
    ]
    
    for playlist_id in playlists:
        try:
            results = sp.playlist_tracks(playlist_id)
            
            for item in results['items']:
                track = item['track']
                
                # Parse release date
                release_date = None
                try:
                    release_date = datetime.strptime(
                        track['album']['release_date'], 
                        '%Y-%m-%d'
                    ).date()
                except (ValueError, KeyError):
                    try:
                        release_date = datetime.strptime(
                            track['album']['release_date'], 
                            '%Y'
                        ).date()
                    except:
                        pass
                
                track_info = {
                    'name': track['name'],
                    'popularity': track['popularity'],
                    'duration_ms': track['duration_ms'],
                    'release_date': release_date
                }
                
                # Avoid duplicates
                if track_info not in tracks:
                    tracks.append(track_info)
        
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
    
    return tracks

def main():
    # Initialize Spotify client
    sp = get_spotify_client()
    
    # Fetch and insert tracks
    tracks = fetch_spotify_tracks(sp)
    insert_tracks(tracks)

if __name__ == '__main__':
    main()
