# import mysql.connector
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials

# SPOTIPY_CLIENT_ID = '8bea9279cb4c409f894b175789994e97'
# SPOTIPY_CLIENT_SECRET = 'e66e7d7775174b5d8df045491e428abb'

# DB_CONNECTION = {
#     'database': 'global_music_db',
#     'user': 'christa',
#     'password': 'sdcn2024',
#     'host': 'localhost'
# }

# def get_spotify_client():
#     """Initialize Spotify client"""
#     client_credentials_manager = SpotifyClientCredentials(
#         client_id=SPOTIPY_CLIENT_ID, 
#         client_secret=SPOTIPY_CLIENT_SECRET
#     )
#     return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# def get_tracks_for_audiobook(sp, audiobook_id):
#     """Fetch tracks (chapters) for a specific audiobook (album) from Spotify"""
#     try:
#         tracks = []
        
#         # Fetch album details (tracks) for the audiobook
#         album = sp.album(audiobook_id)
#         if 'tracks' in album:
#             for track in album['tracks']['items']:
#                 tracks.append({
#                     'chapter_number': track['track_number'],
#                     'duration_ms': track['duration_ms'],
#                     'audio_preview_url': track.get('preview_url', None),  # Make sure to set None if missing
#                     'release_date': track.get('album', {}).get('release_date', None)  # Handle missing or None
#                 })
        
#         return tracks

#     except Exception as e:
#         print(f"Error fetching tracks for audiobook {audiobook_id}: {e}")
#         return []

# def populate_chapters():
#     """Populate Chapters table with chapter details from Audiobooks"""
#     conn = mysql.connector.connect(**DB_CONNECTION)
#     cursor = conn.cursor(dictionary=True)
    
#     try:
#         # Get all audiobooks from the Audiobooks table
#         cursor.execute("""
#             SELECT audiobook_id, name
#             FROM Audiobooks
#         """)
        
#         audiobooks = cursor.fetchall()
        
#         if not audiobooks:
#             print("No audiobooks found in Audiobooks table.")
#             return
        
#         # Initialize Spotify client
#         sp = get_spotify_client()
        
#         # Process each audiobook
#         for audiobook in audiobooks:
#             print(f"Processing chapters for audiobook: {audiobook['name']}")
            
#             # Get tracks (chapters) for this audiobook
#             tracks = get_tracks_for_audiobook(sp, audiobook['audiobook_id'])
            
#             # Insert each track (chapter) into the Chapters table
#             for track in tracks:
#                 # Ensure release_date is a string or None (use default if missing)
#                 release_date = track['release_date'] if track['release_date'] else None
#                 audio_preview_url = track['audio_preview_url'] if track['audio_preview_url'] else None
                
#                 cursor.execute("""
#                     SELECT chapter_id
#                     FROM Chapters
#                     WHERE audiobook_id = %s AND chapter_number = %s
#                 """, (audiobook['audiobook_id'], track['chapter_number']))
                
#                 if not cursor.fetchone():  # Check if the chapter already exists
#                     cursor.execute("""
#                         INSERT INTO Chapters 
#                         (audiobook_id, chapter_number, duration_ms, audio_preview_url, release_date)
#                         VALUES (%s, %s, %s, %s, %s)
#                     """, (
#                         audiobook['audiobook_id'],
#                         track['chapter_number'],
#                         track['duration_ms'],
#                         audio_preview_url,  # Pass as None if missing
#                         release_date        # Pass as None if missing
#                     ))
#                     print(f"Added chapter {track['chapter_number']} for audiobook: {audiobook['name']}")
        
#         conn.commit()
#         print("Successfully populated Chapters table")
        
#     except Exception as e:
#         print(f"Error populating Chapters: {e}")
#         conn.rollback()
        
#     finally:
#         cursor.close()
#         conn.close()

# def main():
#     populate_chapters()

# if __name__ == '__main__':
#     main()
