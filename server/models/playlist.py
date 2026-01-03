import sqlite3
import os
from contextlib import closing
import dao.config as config

class Playlist:
    def __init__(self):
        self.db_path = os.path.join(config.DB_PATH, config.DB_NAME)
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute(self, query, params=()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor
    
    def get_all_playlists(self):
        cursor = self.execute("SELECT * FROM playlists WHERE id != 1")
        return cursor.fetchall()
    
    def get_playlist(self, playlist_id):
        cursor = self.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,))
        return cursor.fetchone()
    
    def create_playlist(self, user_id, name):
        self.execute("INSERT INTO playlists (creater_id, playlist_name) VALUES (?, ?)", (user_id, name))
    
    def get_playlist_songs(self, playlist_id):
        cursor = self.execute("""
            SELECT s.* FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = ?
            ORDER BY ps.order_index
        """, (playlist_id,))
        return cursor.fetchall()
    
    def add_song_to_playlist(self, playlist_id, song_id):
        # Get max order_index
        cursor = self.execute("SELECT MAX(order_index) FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
        max_order = cursor.fetchone()[0] or 0
        self.execute("INSERT INTO playlist_songs (playlist_id, song_id, order_index) VALUES (?, ?, ?)",
                     (playlist_id, song_id, max_order + 1))
    
    def remove_song_from_playlist(self, playlist_id, song_id):
        self.execute("DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?", (playlist_id, song_id))