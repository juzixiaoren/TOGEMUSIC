import sqlite3
import os
from contextlib import closing
import dao.config as config

class Song:
    def __init__(self):
        self.db_path = os.path.join(config.DB_PATH, config.DB_NAME)
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute(self, query, params=()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor
    
    def get_all_songs(self):
        cursor = self.execute("SELECT * FROM songs")
        return cursor.fetchall()
    
    def get_song_by_id(self, song_id):
        cursor = self.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        return cursor.fetchone()
    
    def add_song(self, title, artist, duration, file_path, uploader_id, file_extension):
        self.execute("INSERT INTO songs (title, artist, duration, file_path, uploader_id, file_extension) VALUES (?, ?, ?, ?, ?, ?)",
                     (title, artist, duration, file_path, uploader_id, file_extension))