import mysql.connector
import requests
import xml.etree.ElementTree as ET

conn = mysql.connector.connect(
    host="localhost",      
    user="despinakouli",    
    password="sdcn2024",    
    database="global_music_db"  
)

cursor = conn.cursor()

# Last.fm API key 
lastfm_api_key = "8685e88bb0de292f75ce800aff0a222c"

# Function to fetch top tracks for a country
def fetch_top_tracks(country):
    url = f"http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks&country={country}&api_key={lastfm_api_key}&format=xml"
    response = requests.get(url)
    return response.text 

# Function to insert the top tracks into the Songs table
def insert_top_tracks(country_name, xml_data):
    
    root = ET.fromstring(xml_data)

    cursor.execute("SELECT country_id FROM Countries WHERE country_name = %s", (country_name,))
    country_id = cursor.fetchone()[0]

    # Iterate through each track and insert the details into the Songs table
    for track in root.findall(".//track"):
        track_name = track.find("name").text
        rank = int(track.get("rank"))
        artist_name = track.find("artist/name").text

        # Insert artist into Artists table if it doesn't exist
        cursor.execute("SELECT artist_id FROM Artists WHERE name = %s", (artist_name,))
        artist = cursor.fetchone()
        if not artist:
            # Insert a new artist with null fields for unused attributes
            cursor.execute("""
                INSERT INTO Artists (name, image_url, spotify_url, type)
                VALUES (%s, NULL, NULL, 'MusicianArtist')
            """, (artist_name,))
            conn.commit()
            artist_id = cursor.lastrowid
        else:
            artist_id = artist[0]

        # Insert track into Songs table (with chart_rank and artist_id)
        cursor.execute("""
            INSERT INTO Songs (title, artist_id, chart_rank)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE chart_rank = %s
        """, (track_name, artist_id, rank, rank))
        conn.commit()
        print(f"Inserted: {track_name} by {artist_name}, rank {rank} for {country_name}")

# Get all countries from the database
cursor.execute("SELECT country_name FROM Countries")
countries = cursor.fetchall()

# Loop through each country and fetch top tracks
for country in countries:
    country_name = country[0]
    print(f"Fetching top tracks for {country_name}...")
    xml_data = fetch_top_tracks(country_name)
    insert_top_tracks(country_name, xml_data)

cursor.close()
conn.close()