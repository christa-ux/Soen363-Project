import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import mysql.connector
from datetime import datetime
import time

def connect_to_database():
    """Establish connection to MySQL database"""
    return mysql.connector.connect(
        host="localhost",
        user="christa",
        password="sdcn2024",
        database="global_music_db"
    )

def get_spotify_client():
    """Initialize Spotify client with credentials"""
    client_credentials_manager = SpotifyClientCredentials(
        client_id='8bea9279cb4c409f894b175789994e97',
        client_secret='e66e7d7775174b5d8df045491e428abb'
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def fetch_audiobooks():
    """Fetch audiobook information from the Audiobooks table"""
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
   
    cursor.execute("""
        SELECT audiobook_id,  name
        FROM Audiobooks 
    """)
    audiobooks = cursor.fetchall()
   
    cursor.close()
    conn.close()
    return audiobooks

def find_spotify_audiobook(sp, audiobook_name):
    """Search for an audiobook on Spotify and return its ID"""
    try:
        # Search for the audiobook with both title and artist name
        query = f"audiobook:{audiobook_name}" 
        results = sp.search(q=query, type='show', limit=1)
       
        if results['shows']['items']:
            show=results['shows']['items'][0]
            show_id=show['id']
       
            episodes=sp.show_episodes(show_id)
            return show_id, episodes
        
        return None, None
       
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while searching for {audiobook_name}: {e}")
        return None, None

def store_chapters(audiobook_id, episodes):
    """Fetch chapters for an audiobook and store them in the database"""
    try:
        
       
        conn = connect_to_database()
        cursor = conn.cursor()
       
        # Prepare insert statement
        insert_query = """
            INSERT INTO Chapters
            (audiobook_id, chapter_number, duration_ms, audio_preview_url, release_date)
            VALUES (%s, %s, %s, %s, %s)
        """
       
        total_chapters=len(episodes['items'])

        # Process each chapter
        for idx, episode in enumerate(episodes['items'], 1):
            chapter_data = (
                audiobook_id,
                idx,
                episode['duration_ms'],
                episode.get('audio_preview_url'),
                datetime.strptime(episode['release_date'], '%Y-%m-%d').date()
            )
           
            try:
                cursor.execute(insert_query, chapter_data)
                conn.commit()
                print(f"Successfully inserted chapter {idx} for audiobook {audiobook_id}")
            except mysql.connector.Error as err:
                print(f"Error inserting chapter {idx} for audiobook {audiobook_id}: {err}")
                conn.rollback()
       
        # Update total_chapters in Audiobooks table
        update_query = """
            UPDATE Audiobooks
            SET total_chapters = %s
            WHERE audiobook_id = %s
        """
        cursor.execute(update_query, total_chapters, audiobook_id)
        conn.commit()
       
        cursor.close()
        conn.close()
       
    except Exception as e:
       print (f"unexpected error storing chapters for audiobook {audiobook_id}: {e}")

def main():
    # Initialize Spotify client
    sp = get_spotify_client()
   
    # Fetch audiobooks from database
    audiobooks = fetch_audiobooks()
   
    # Process each audiobook
    for audiobook in audiobooks:
        print(f"Processing audiobook: {audiobook['name']}")
       
        # Find audiobook on Spotify
        show_id, episodes = find_spotify_audiobook(sp, audiobook['name'])
       
        if show_id and episodes:
            print(f"Found Spotify ID: {show_id}")
            store_chapters(audiobook['audiobook_id'], episodes)
            print(f"Completed processing audiobook: {audiobook['name']}\n")
        else:
            print(f"Could not find audiobook '{audiobook['name']}' on Spotify\n")
       
        # Add a small delay to avoid hitting API rate limits
        time.sleep(1)

if __name__ == "__main__":
    main()