import pymysql

# MySQL configuration
mysql_config = {
    'database': 'global_music_db',
    'user': 'sarahabellard',
    'password': 'sdcn2024',
    'host': 'localhost'
}

# Path to the audio file
audio_file_path = 'songblob.mp3'

# Connect to MySQL
connection = pymysql.connect(**mysql_config)

try:
    with connection.cursor() as cursor:
        # Step 1: Read the audio file as binary data
        with open(audio_file_path, 'rb') as file:
            audio_data = file.read()

        # Step 2: Fetch all song IDs from the Songs table
        cursor.execute("SELECT song_id FROM Songs")
        song_ids = cursor.fetchall()  # Fetch all song IDs

        # Step 3: Loop through each song ID and update the audio_blob column
        update_query = """
            UPDATE Songs
            SET audio_blob = %s
            WHERE song_id = %s;
        """

        for song_id_tuple in song_ids:
            song_id = song_id_tuple[0]  # Extract the song_id from the tuple
            cursor.execute(update_query, (audio_data, song_id))

        # Commit the changes
        connection.commit()
        print(f"Successfully updated {len(song_ids)} songs with audio blobs.")

finally:
    # Close the connection
    connection.close()