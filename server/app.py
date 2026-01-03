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

def register_tasks():
    @scheduler.task('interval', id='check_song_end', seconds=1)
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

        # 获取新歌曲ID
        cursor = song_model.execute("""
            SELECT s.id FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = 1 AND ps.order_index = 1
        """)
        new_song = cursor.fetchone()
        new_song_id = new_song[0] if new_song else None

        socketio.emit('song_changed', {'new_song_id': new_song_id})
        print("🎵 song ended, switched to next")

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://127.0.0.1:11451", "http://localhost:11451"])
    app.config.from_object(Config)
    
    # 初始化数据库
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    
    # 初始化 APScheduler
    global scheduler
    if scheduler is None and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = APScheduler()
        scheduler.init_app(app)
        register_tasks()
        scheduler.start()
    
    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins=["http://127.0.0.1:11451", "http://localhost:11451"])
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=Config.DEBUG, port=Config.SERVER_PORT)
