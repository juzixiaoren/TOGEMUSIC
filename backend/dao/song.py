import sqlite3
import os
from contextlib import closing
import threading
import dao.config as config
class Song:
    def __init__(self):
        self.db_path = os.path.join(config.DB_PATH, config.DB_NAME)
        self.local = threading.local()
        self.get_conn().row_factory = sqlite3.Row  # 可选，返回 dict-like row
    def get_conn(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(
                self.db_path,
                timeout=10,
                check_same_thread=True
            )
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    def execute(self, query, params=()):
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.row_factory = sqlite3.Row
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
        return cursor.fetchone()
    
    def rotate_playlist_index(self):
        cursor = self.execute(
            "SELECT MAX(order_index) FROM playlist_songs WHERE playlist_id = 1"
        )
        max_index = cursor.fetchone()[0]

        if max_index is None:
            return

        tmp = max_index + 1

        try:
            # 使用统一的 self.get_conn() 事务
            with self.get_conn():
                # 将 order_index = 1 的歌移到最后
                self.get_conn().execute(
                    "UPDATE playlist_songs SET order_index = ? "
                    "WHERE playlist_id = 1 AND order_index = 1",
                    (tmp,)
                )

                # 其他 song 的 order_index 前移
                self.get_conn().execute(
                    "UPDATE playlist_songs SET order_index = order_index - 1 "
                    "WHERE playlist_id = 1 AND order_index > 1"
                )

        except Exception as e:
            print("rotate_playlist_index failed:", e)
            raise
    def mark_need_notify(self):
        self.get_conn().execute(
            "UPDATE room_play_state SET need_notify = 1 WHERE room_id = 1"
        )
        self.get_conn().commit()

    def fetch_and_clear_notify(self):
        cur = self.get_conn().execute(
            "SELECT need_notify FROM room_play_state WHERE room_id = 1"
        )
        row = cur.fetchone()
        if not row or row[0] == 0:
            return False

        self.get_conn().execute(
            "UPDATE room_play_state SET need_notify = 0 WHERE room_id = 1"
        )
        self.get_conn().commit()
        return True



    
    def start_next_song(self):
        import time
        now = int(time.time() * 1000)
        self.set_play_status(now, 1)
        