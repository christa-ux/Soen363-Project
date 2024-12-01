from pymongo import MongoClient
import pymysql
import certifi
from datetime import datetime, date

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'sarahabellard',
    'password': 'sdcn2024',
    'database': 'global_music_db'
}

# MongoDB Atlas connection string
mongo_client = MongoClient(
    "mongodb+srv://sarah:sarah@soen-363.6f7xz.mongodb.net/?retryWrites=true&w=majority",
    tlsCAFile=certifi.where()  # Explicitly use certifi's CA certificates
)

# Test connection
mongo_db = mongo_client['global_music_db']
print("Connected to MongoDB successfully!")

# Connect to MySQL
mysql_conn = pymysql.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor(pymysql.cursors.DictCursor)


def migrate_table_to_collection(mysql_table, mongo_collection_name, transform=None):
    mysql_cursor.execute(f"SELECT * FROM {mysql_table}")
    rows = mysql_cursor.fetchall()

    # Create the MongoDB collection if it doesn't exist
    if mongo_collection_name not in mongo_db.list_collection_names():
        mongo_db.create_collection(mongo_collection_name)
        print(f"Created new MongoDB collection: {mongo_collection_name}")

    mongo_collection = mongo_db[mongo_collection_name]

    for row in rows:
        # Apply transformations (e.g., handle blobs, relationships, etc.)
        if transform:
            row = transform(row)
        # Convert dates to datetime.datetime
        row = convert_dates(row)
        mongo_collection.insert_one(row)

    print(f"Migrated {len(rows)} records from {mysql_table} to {mongo_collection_name}.")


# Helper function to transform datetime.date to datetime.datetime
def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    elif isinstance(obj, date) and not isinstance(obj, datetime):
        # Convert date to datetime
        return datetime.combine(obj, datetime.min.time())
    return obj

# Transform function to handle blobs in Songs
def transform_songs(row):
    if row.get('audio_blob'):
        # Convert binary blob to a hexadecimal string
        row['audio_blob'] = row['audio_blob'].hex()
    return row


# List of tables to migrate dynamically
tables_to_migrate = {
    'Artists': 'Artists',
    'AudiobookArtists': 'AudiobookArtists',
    'Audiobook_Owns': 'Audiobook_Owns',
    'Audiobooks': 'Audiobooks',
    'Chapters': 'Chapters',
    'Countries': 'Countries',
    'MusicianArtists': 'MusicianArtists',
    'Songs': 'Songs'
}

# Optional transformations (e.g., handle blobs for specific tables)
transformations = {
    'Songs': transform_songs
}

# Migrate Collections Dynamically
try:
    for mysql_table, mongo_collection_name in tables_to_migrate.items():
        transform = transformations.get(mysql_table, None)  # Apply transformation if available
        migrate_table_to_collection(mysql_table, mongo_collection_name, transform)
finally:
    # Close connections
    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()
