import sqlite3
import os
from contextlib import closing
import dao.config as config
class Song:
    def __init__(self):
        self.db_path = os.path.join(config.DB_PATH, config.DB_NAME)
        self.playlist_queue = []  # 内存中的播放队列
        self.load_playlist()  # 初始化时加载队列
    
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
    def get_play_status(self):
        cursor = self.execute("""
                            SELECT play_start_time ,is_playing
                            FROM room_play_state LIMIT 1
                            """)
        return cursor.fetchone()
    def set_play_status(self, play_start_time, is_playing):
        self.execute("""
                    UPDATE room_play_state
                    SET play_start_time = ?, is_playing = ?
                    """, (play_start_time, is_playing))
    def get_song_duration(self, song_id):
        cursor = self.execute("SELECT duration FROM songs WHERE id = ?", (song_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    def get_current_song_duration(self):
        cursor = self.execute("""
            SELECT s.duration FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = 1
            AND ps.order_index=1
        """)
        return cursor.fetchall()
    
    def rotate_playlist_index(self):
        cursor = self.execute(
            "SELECT MAX(order_index) FROM playlist_songs WHERE playlist_id = 1"
        )
        max_index = cursor.fetchone()[0]

        if max_index is None:
            return

        tmp = max_index + 1

        try:
            self.execute("BEGIN")

            self.execute(
                "UPDATE playlist_songs SET order_index = ? "
                "WHERE playlist_id = 1 AND order_index = 1",
                (tmp,)
            )

            self.execute(
                "UPDATE playlist_songs SET order_index = order_index - 1 "
                "WHERE playlist_id = 1 AND order_index > 1"
            )

            self.execute(
                "UPDATE playlist_songs SET order_index = ? WHERE playlist_id = 1 AND order_index = ?",
                (max_index, tmp)
            )

            self.execute("COMMIT")

        except Exception:
            self.execute("ROLLBACK")
            raise


    
    def start_next_song(self):
        import time
        now = int(time.time() * 1000)
        self.set_play_status(now, 1)
    def load_playlist(self):
        cursor = self.execute("""
            SELECT s.* FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = 1
            ORDER BY ps.order_index
        """)
        self.playlist_queue = cursor.fetchall()