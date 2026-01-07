from flask import Flask
import dao.config as dao_config
from dao.sql_init import SQLInit
database = SQLInit(dao_config.DB_PATH, dao_config.DB_NAME)
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_socketio import SocketIO
from server.config import Config
import sys
import os
import random
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from routes.auth import auth_bp
from routes.music import music_bp

scheduler = None
socketio = SocketIO()

import time
from models.song import Song
song_model = Song()

def now_ms():
    return int(time.time() * 1000)
def notify_loop():
    while True:
        socketio.sleep(0.5)  # SocketIO 专用 sleep

        if not song_model.fetch_and_clear_notify():
            continue

        # 查询当前播放歌曲
        cursor = song_model.execute("""
            SELECT s.id FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = 1 AND ps.order_index = 1
        """)
        row = cursor.fetchone()
        song_id = row[0] if row else None

        socketio.emit(
            'song_changed',
            {'new_song_id': song_id},
            room=None
        )

        # 同步广播最新的播放列表顺序（保持 order_index 显示一致）
        cursor = song_model.execute("""
            SELECT s.id, s.title, s.artist, s.duration, s.uploader_id, s.file_path, s.file_extension, s.time_added
            FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = 1
            ORDER BY ps.order_index
        """)
        songs_rows = cursor.fetchall()
        songs_data = [dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], r)) for r in songs_rows]
        socketio.emit('playlist_shuffled', {'songs': songs_data}, room=None)

        print(f"📢 广播切歌：{song_id}，已同步播放列表顺序，共 {len(songs_data)} 首")
            
def register_tasks():
    @scheduler.task('interval', id='check_song_end', seconds=3)
    def check_song_end():
        status = song_model.get_play_status()
        # 没在播放，直接跳过
        if not status or status[1] != 1:
            return
        song_duration = song_model.get_current_song_duration()
        if not song_duration:
            print("No current song duration found")
            return

        end_time = status[0] + song_duration[0]
        print("结束时间：" + str(end_time), "当前时间：" + str(now_ms()), "歌曲时长：" + str(song_duration[0]))

        # ❸ 时间没到
        if now_ms() < end_time:
            return

        # 到点了，只允许一次
        song_model.rotate_playlist_index()
        song_model.start_next_song()
        song_model.mark_need_notify()
        print("🎵 song ended, switched to next")

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://127.0.0.1:11451", "http://localhost:11451"])
    app.config.from_object(Config)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)

    # 初始化 APScheduler
    global scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    register_tasks()
    scheduler.start()

    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins=["*"])

    # 启动后台广播任务
    socketio.start_background_task(notify_loop)

    # ===== WebSocket 事件处理 =====
    @socketio.on('request_next_song')
    def handle_next_song(data=None):
        try:
            song_model.rotate_playlist_index()
            song_model.start_next_song()
            song_model.mark_need_notify()
            return {'success': True}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    @socketio.on('request_prev_song')
    def handle_prev_song(data=None):
        try:
            cursor = song_model.execute("SELECT MAX(order_index) FROM playlist_songs WHERE playlist_id = 1")
            max_index = cursor.fetchone()[0]
            if max_index is None:
                return {'success': False, 'error': 'Playlist is empty'}

            with song_model.get_conn():
                # 移最后一首到最前面
                song_model.get_conn().execute(
                    "UPDATE playlist_songs SET order_index = 0 WHERE playlist_id = 1 AND order_index = ?", (max_index,)
                )
                # 其他歌曲整体后移
                song_model.get_conn().execute(
                    "UPDATE playlist_songs SET order_index = order_index + 1 WHERE playlist_id = 1 AND order_index >= 1"
                )
                # 放回第一
                song_model.get_conn().execute(
                    "UPDATE playlist_songs SET order_index = 1 WHERE playlist_id = 1 AND order_index = 0"
                )
                song_model.get_conn().commit()

            song_model.start_next_song()
            song_model.mark_need_notify()
            return {'success': True}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    @socketio.on('request_shuffle_playlist')
    def handle_shuffle_playlist(data=None):
        try:
            # 获取除了第一首歌之外的歌曲
            cursor = song_model.execute("""
                SELECT song_id FROM playlist_songs 
                WHERE playlist_id = 1 AND order_index > 1
                ORDER BY order_index
            """)
            songs = cursor.fetchall()
            if not songs:
                return {'success': True, 'message': 'Playlist has only one song or is empty'}

            song_ids = [s[0] for s in songs]
            random.shuffle(song_ids)
            with song_model.get_conn():
                for idx, song_id in enumerate(song_ids, start=2):
                    song_model.get_conn().execute(
                        "UPDATE playlist_songs SET order_index = ? WHERE playlist_id = 1 AND song_id = ?", (idx, song_id)
                    )

            # 广播新顺序
            cursor = song_model.execute("""
                SELECT s.id, s.title, s.artist, s.duration, s.uploader_id, s.file_path, s.file_extension, s.time_added
                FROM songs s
                JOIN playlist_songs ps ON s.id = ps.song_id
                WHERE ps.playlist_id = 1
                ORDER BY ps.order_index
            """)
            shuffled_songs = cursor.fetchall()
            songs_data = [dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], s)) for s in shuffled_songs]

            socketio.emit('playlist_shuffled', {'songs': songs_data}, room=None)
            return {'success': True, 'songs': songs_data}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=Config.SERVER_PORT, debug=Config.DEBUG)