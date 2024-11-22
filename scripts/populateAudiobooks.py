#in this table i added some audiobooks made by each of the audiobook artists in AudiobookArtists table
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

def get_audiobooks_for_artist(sp, artist_name):
    """Fetch audiobooks for a specific artist from Spotify"""
    try:
        audiobooks = []
        offset = 0
        limit = 50
        
        while True:
            results = sp.search(
                q=f'narrator:{artist_name}',
                type='audiobook',
                limit=limit,
                offset=offset,
                market='US'
            )
            
            if not results['audiobooks']['items']:
                break
                
            for book in results['audiobooks']['items']:
  
                narrators = book.get('narrators', [])
                for narrator in narrators:
                
                    if isinstance(narrator, dict) and 'name' in narrator:
                        if narrator['name'].lower() == artist_name.lower():
                            audiobooks.append({
                                'name': book['name'],
                                'description': book.get('description', ''),
                                'total_chapters': len(book.get('chapters', {}).get('items', []))
                            })
                            break  
            
            offset += limit
            if offset >= results['audiobooks']['total']:
                break
                
        return audiobooks
    
    except Exception as e:
        print(f"Error fetching audiobooks for {artist_name}: {e}")
        return []


def populate_audiobooks():
    """Populate Audiobooks table with details"""
    conn = mysql.connector.connect(**DB_CONNECTION)
    cursor = conn.cursor(dictionary=True)
    
    try:
      
        cursor.execute("""
            SELECT a.artist_id, a.name 
            FROM Artists a
            JOIN AudiobookArtists aa ON a.artist_id = aa.artist_id
            WHERE a.type = 'AudiobookArtist'
        """)
        
        audiobook_artists = cursor.fetchall()
        
        if not audiobook_artists:
            print("No audiobook artists found in AudiobookArtists table.")
            return
        
     
        sp = get_spotify_client()
        
    
        for artist in audiobook_artists:
            print(f"Processing audiobooks for artist: {artist['name']}")
            
          
            audiobooks = get_audiobooks_for_artist(sp, artist['name'])
            
       
            for book in audiobooks:
           
                cursor.execute("""
                    SELECT audiobook_id 
                    FROM Audiobooks 
                    WHERE name = %s AND artist_id = %s
                """, (book['name'], artist['artist_id']))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO Audiobooks 
                        (name, description, total_chapters, artist_id)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        book['name'],
                        book['description'],
                        book['total_chapters'],
                        artist['artist_id']
                    ))
                    
                    print(f"Added audiobook: {book['name']}")
        
        conn.commit()
        print("Successfully populated Audiobooks table")
        
    except Exception as e:
        print(f"Error populating Audiobooks: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

def main():
    populate_audiobooks()

if __name__ == '__main__':
    main()