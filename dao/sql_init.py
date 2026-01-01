import sqlite3
import os
from contextlib import closing
import dao.config as config

db_path = config.DB_PATH
db_name = config.DB_NAME


class SQLInit:
    def __init__(self, db_path, db_name):
        self.db_path = db_path
        self.db_name = db_name
        if not self.check_db_exists():
            self.create_db()
            self.create_tables()
    def check_db_exists(self):
        return os.path.exists(os.path.join(self.db_path, self.db_name))
    def create_db(self):
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        # create database file by opening and immediately closing connection
        with sqlite3.connect(os.path.join(self.db_path, self.db_name)):
            pass
    def create_tables(self):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            duration INTEGER,
            uploader_id INTEGER,
            file_path TEXT NOT NULL,
            time_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, artist)
            FOREIGN KEY (uploader_id) REFERENCES users(id)
        )
        """)
                conn.commit()
                cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
        """)
                conn.commit()
                cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creater_id INTEGER,
                playlist_name TEXT NOT NULL,
                UNIQUE(playlist_name),
                FOREIGN KEY (creater_id) REFERENCES users(id)
            );
        """)
                conn.commit()
                cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_songs(
                playlist_id INTEGER,
                song_id INTEGER,
                order_index INTEGER,
                PRIMARY KEY (playlist_id, song_id),
                UNIQUE(order_index, playlist_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id),
                FOREIGN KEY (song_id) REFERENCES songs(id)
                );
        """)
                
                conn.commit()
    def get_all_songs(self):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM songs")
                return cursor.fetchall()
    def get_song_list(self, playlist_name):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            SELECT S.title,S.artist,S.duration,U.username
            FROM playlists P
            JOIN playlist_songs PS ON P.id = PS.playlist_id
            JOIN songs S ON PS.song_id = S.id
            JOIN users U ON P.creater_id = U.id
            WHERE P.playlist_name = ?
            ORDER BY PS.order_index ASC
            """, (playlist_name,))
                return cursor.fetchall()
    def create_playlist(self,user_id,playlist_name):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            INSERT INTO playlists (creater_id, playlist_name)
            VALUES (?, ?)
        """, (user_id, playlist_name))
                conn.commit()
    def add_song_list(self,song_id,order_index,playlist_id):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            INSERT INTO playlist_songs (playlist_id, song_id, order_index)
            VALUES (?, ?, ?)
        """, (playlist_id, song_id, order_index))
                conn.commit()
    def add_song(self,title,artist,duration,file_path="",uploader_id=None):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            INSERT INTO songs (title, artist, duration, file_path, uploader_id)
            VALUES (?, ?, ?, ?, ?)
        """, (title, artist, duration, file_path, uploader_id))
                conn.commit()
    def add_user(self,username,password_hash):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))
                conn.commit()
    def check_user(self, username, password_hash):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
            SELECT 1 FROM users WHERE username = ? AND password_hash = ?
        """, (username, password_hash))
                user = cursor.fetchone()
                return user is not None
    def close(self):
        # connections are opened per-method using context managers; nothing to close
        return

    def get_all_playlists(self):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    SELECT p.id, p.playlist_name, p.creater_id, u.username
                    FROM playlists p
                    JOIN users u ON p.creater_id = u.id
                """)
                return cursor.fetchall()

    def get_playlist(self, playlist_id):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    SELECT p.id, p.playlist_name, p.creater_id, u.username
                    FROM playlists p
                    JOIN users u ON p.creater_id = u.id
                    WHERE p.id = ?
                """, (playlist_id,))
                return cursor.fetchone()

    def get_playlist_songs(self, playlist_id):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    SELECT s.id, s.title, s.artist, s.duration, s.file_path, u.username
                    FROM playlist_songs ps
                    JOIN songs s ON ps.song_id = s.id
                    JOIN users u ON s.uploader_id = u.id
                    WHERE ps.playlist_id = ?
                    ORDER BY ps.order_index
                """, (playlist_id,))
                return cursor.fetchall()

    def add_song_to_playlist(self, playlist_id, song_id):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                # Get max order_index
                cursor.execute("SELECT MAX(order_index) FROM playlist_songs WHERE playlist_id = ?", (playlist_id,))
                max_order = cursor.fetchone()[0] or 0
                cursor.execute("""
                    INSERT INTO playlist_songs (playlist_id, song_id, order_index)
                    VALUES (?, ?, ?)
                """, (playlist_id, song_id, max_order + 1))
                conn.commit()

    def remove_song_from_playlist(self, playlist_id, song_id):
        db_file = os.path.join(self.db_path, self.db_name)
        with sqlite3.connect(db_file) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("""
                    DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?
                """, (playlist_id, song_id))
                conn.commit()
if __name__ == "__main__":
    sql_init = SQLInit(db_path, db_name)

    # =========================
    # 1️⃣ 添加测试用户
    # =========================
    print("=== 添加用户 ===")
    users = [("alice", "123456"), ("bob", "password")]
    for username, pwd in users:
        try:
            sql_init.add_user(username, pwd)
            print(f"添加用户 {username} 成功")
        except sqlite3.IntegrityError:
            print(f"用户 {username} 已存在")

    # 检查用户登录
    print("=== 检查用户登录 ===")
    print("alice 登录:", sql_init.check_user("alice", "123456"))  # True
    print("bob 登录:", sql_init.check_user("bob", "wrongpass"))  # False

    # =========================
    # 2️⃣ 添加测试歌曲
    # =========================
    print("=== 添加歌曲 ===")
    songs_to_add = [
        ("Song A", "Artist 1", 210, "/path/to/song_a.mp3", 1),
        ("Song B", "Artist 2", 180, "/path/to/song_b.mp3", 1),
        ("Song C", "Artist 3", 240, "/path/to/song_c.mp3", 2)
    ]
    for title, artist, duration, path, uploader in songs_to_add:
        try:
            sql_init.add_song(title, artist, duration, path, uploader)
            print(f"添加歌曲 {title} 成功")
        except sqlite3.IntegrityError:
            print(f"歌曲 {title} 已存在")

    # 获取所有歌曲
    print("=== 所有歌曲 ===")
    all_songs = sql_init.get_all_songs()
    for song in all_songs:
        print(song)

    # =========================
    # 3️⃣ 创建播放列表
    # =========================
    print("=== 创建播放列表 ===")
    playlist_name = "MyPlaylist"
    try:
        sql_init.create_playlist(1, playlist_name)
        print(f"创建播放列表 {playlist_name} 成功")
    except sqlite3.IntegrityError:
        print(f"播放列表 {playlist_name} 已存在")

    # =========================
    # 4️⃣ 添加歌曲到播放列表
    # =========================
    print("=== 添加歌曲到播放列表 ===")
    playlist_id = 1  # 假设 MyPlaylist ID=1
    for order_index, song_id in enumerate([1, 2, 3], start=1):
        try:
            sql_init.add_song_list(song_id, order_index, playlist_id)
            print(f"歌曲 ID={song_id} 添加到播放列表 {playlist_name} 成功")
        except sqlite3.IntegrityError:
            print(f"歌曲 ID={song_id} 已在播放列表中")

    # =========================
    # 5️⃣ 查询播放列表歌曲
    # =========================
    print("=== 播放列表歌曲 ===")
    playlist_songs = sql_init.get_song_list(playlist_name)
    for title, artist, duration, username in playlist_songs:
        print(f"{title} - {artist} ({duration}s), 创建者: {username}")

    print("=== 测试完成 ===")
