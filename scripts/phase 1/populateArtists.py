import os
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

def insert_artists(artists):
    """Insert artists into MySQL database"""
    conn = mysql.connector.connect(**DB_CONNECTION)
    cursor = conn.cursor()
    
    try:
        for artist in artists:
            # Check if artist already exists
            cursor.execute("SELECT artist_id FROM Artists WHERE name = %s AND type = %s", 
                         (artist['name'], artist['type']))
            if not cursor.fetchone():  # Only insert if artist doesn't exist
                cursor.execute("""
                    INSERT INTO Artists (name, image_url, spotify_url, type)
                    VALUES (%s, %s, %s, %s)
                """, (
                    artist['name'],
                    artist['image_url'],
                    artist['spotify_url'],
                    artist['type']
                ))
        
        conn.commit()
        print(f"Inserted artists successfully.")
    
    except Exception as e:
        print(f"Error inserting artists: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def fetch_music_artists(sp):
    """Fetch music artists from Spotify playlists"""
    artists = []
    seen_artist_ids = set()
    
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
                if not item['track']:
                    continue
                    
                for artist in item['track']['artists']:
                    if artist['id'] not in seen_artist_ids:
                        artist_details = sp.artist(artist['id'])
                        
                        artist_info = {
                            'name': artist_details['name'],
                            'image_url': artist_details['images'][0]['url'] if artist_details['images'] else None,
                            'spotify_url': artist_details['external_urls']['spotify'],
                            'type': 'MusicianArtist'
                        }
                        
                        artists.append(artist_info)
                        seen_artist_ids.add(artist['id'])
        
        except Exception as e:
            print(f"Error fetching playlist {playlist_id}: {e}")
    
    return artists

def fetch_audiobook_artists(sp):
    """Fetch audiobook artists/narrators from Spotify"""
    artists = []
    seen_narrator_names = set()
    
    # Search queries for popular audiobook categories
    search_queries = [
        'bestseller audiobook',
        'popular audiobook',
        'fiction audiobook',
        'nonfiction audiobook',
        'self help audiobook'
    ]
    
    for query in search_queries:
        try:
            # Search for audiobooks
            results = sp.search(q=query, type='audiobook', limit=50, market='US')
            
            for item in results['audiobooks']['items']:
                # Get narrators/authors
                for narrator in item.get('narrators', []):
                    if narrator['name'] not in seen_narrator_names:
                        artist_info = {
                            'name': narrator['name'],
                            'image_url': None,  # Spotify doesn't provide narrator images
                            'spotify_url': f"https://open.spotify.com/search/{narrator['name']}/audiobooks",
                            'type': 'AudiobookArtist'
                        }
                        
                        artists.append(artist_info)
                        seen_narrator_names.add(narrator['name'])
                
                # Add authors as AudiobookArtists as well
                if 'authors' in item:
                    for author in item['authors']:
                        if author not in seen_narrator_names:
                            artist_info = {
                                'name': author,
                                'image_url': None,
                                'spotify_url': f"https://open.spotify.com/search/{author}/audiobooks",
                                'type': 'AudiobookArtist'
                            }
                            
                            artists.append(artist_info)
                            seen_narrator_names.add(author)
        
        except Exception as e:
            print(f"Error fetching audiobook artists for query '{query}': {e}")
    
    return artists

def main():
    # Initialize Spotify client
    sp = get_spotify_client()
    
    # Fetch both types of artists
    music_artists = fetch_music_artists(sp)
    print(f"Found {len(music_artists)} music artists")
    
    audiobook_artists = fetch_audiobook_artists(sp)
    print(f"Found {len(audiobook_artists)} audiobook artists")
    
    # Combine and insert all artists
    all_artists = music_artists + audiobook_artists
    print(f"Inserting total of {len(all_artists)} artists")
    insert_artists(all_artists)

if __name__ == '__main__':
    main()