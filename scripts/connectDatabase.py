# this script populates the Tracks table
import os
import mysql.connector
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

SPOTIPY_CLIENT_ID = '8bea9279cb4c409f894b175789994e97'
SPOTIPY_CLIENT_SECRET = 'e66e7d7775174b5d8df045491e428abb'

DB_CONNECTION = {
    'database': 'global_music_db',
    'user': 'despinakouli',
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


def main():
    # Initialize Spotify client
    sp = get_spotify_client()


if __name__ == '__main__':
    main()