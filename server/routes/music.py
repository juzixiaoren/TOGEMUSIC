from flask import Blueprint, request, jsonify, send_from_directory
from flask import send_file, abort
from models.song import Song
from models.playlist import Playlist
from models.user import User
import os
import time
music_bp = Blueprint('music', __name__)

# 获取项目根目录，确保无论从哪里运行，路径都正确
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')

song_model = Song()
playlist_model = Playlist()
user_model = User()

def verify_token(token):
    return user_model.query_token(token)

@music_bp.route('/upload', methods=['POST'])
def upload_music():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No token provided'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'message': 'Invalid token'}), 401

    # 打印调试信息
    print("=== request.form ===")
    for k, v in request.form.items():
        print(f"{k} -> {v}")
    print("=== request.files ===")
    for f in request.files:
        print(f"{f} -> {request.files[f].filename}")

    files = request.files.getlist('files')

    # 按下标动态读取 titles, artists, durations
    titles, artists, durations = [], [], []
    i = 0
    while True:
        t_key = f'titles[{i}]'
        a_key = f'artists[{i}]'
        d_key = f'durations[{i}]'

        t_val = request.form.get(t_key)
        a_val = request.form.get(a_key)
        d_val = request.form.get(d_key)

        # 都没有就结束
        if t_val is None and a_val is None and d_val is None:
            break

        titles.append(t_val or '')
        artists.append(a_val or '')
        try:
            durations.append(int(d_val))
        except (TypeError, ValueError):
            durations.append(0)
        i += 1

    for i, file in enumerate(files):
        if file and file.filename:
            filename = file.filename
            file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
            file_path = os.path.join(UPLOADS_DIR, filename)
            os.makedirs(UPLOADS_DIR, exist_ok=True)
            file.save(file_path)

            # 防止索引越界
            title = titles[i] if i < len(titles) else filename.rsplit('.', 1)[0]
            artist = artists[i] if i < len(artists) else ''
            duration = durations[i] if i < len(durations) else 0

            print(f"Saving song: {title}, {artist}, {duration}ms, {file_path}")
            song_model.add_song(title, artist, duration, file_path, user_id, file_extension)

    return jsonify({'message': 'Upload successful'}), 200


@music_bp.route('/songs', methods=['GET'])
def get_songs():
    songs = song_model.get_all_songs()
    return jsonify([dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], song)) for song in songs]), 200

@music_bp.route('/playlists', methods=['GET'])
def get_playlists():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if user_id is None:
        return jsonify({'message': 'Invalid token'}), 401
    playlists = playlist_model.get_default_playlists()
    return jsonify([dict(zip(['id', 'creater_id', 'playlist_name'], p)) for p in playlists]), 200
@music_bp.route('/getAllPlaylists', methods=['GET'])
def get_all_playlists():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    if user_id is None:
        return jsonify({'message': 'Invalid token'}), 401
    playlists = playlist_model.get_all_playlists()
    return jsonify([dict(zip(['id', 'creater_id', 'playlist_name'], p)) for p in playlists]), 200
@music_bp.route('/playlists', methods=['POST'])
def create_playlist():
    token = request.headers.get('Authorization')
    user_id = verify_token(token)
    data = request.get_json()
    name = data.get('name')
    playlist_model.create_playlist(user_id, name)
    return jsonify({'message': 'Playlist created'}), 201

@music_bp.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = playlist_model.get_playlist(playlist_id)
    songs = playlist_model.get_playlist_songs(playlist_id)
    return jsonify({
        'playlist': dict(zip(['id', 'creater_id', 'playlist_name'], playlist)),
        'songs': [dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], s)) for s in songs]
    }), 200

@music_bp.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_songs_to_playlist(playlist_id):
    data = request.get_json()
    song_ids = data.get('songIds', [])
    for song_id in song_ids:
        playlist_model.add_song_to_playlist(playlist_id, song_id)
    return jsonify({'message': 'Songs added'}), 200

@music_bp.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    playlist_model.remove_song_from_playlist(playlist_id, song_id)
    return jsonify({'message': 'Song removed'}), 200

@music_bp.route('/songs/<int:song_id>/file.<ext>', methods=['GET'])
def get_song_file(song_id, ext):
    song = song_model.get_song_by_id(song_id)
    if not song:
        abort(404, description='Song not found')

    file_path = os.path.join(UPLOADS_DIR, os.path.basename(song[5]))
    print(file_path)
    
    # 验证请求的后缀和文件实际后缀一致
    if not file_path.endswith(f'.{ext}'):
        abort(400, description='File extension mismatch')

    return send_file(
        file_path,
        conditional=True  # 支持 Range 请求
    )

@music_bp.route('/users', methods=['GET'])
def get_users():
    # 简化，获取所有用户
    users = user_model.execute("SELECT id, username FROM users").fetchall()
    return jsonify([{'id': u[0], 'username': u[1]} for u in users]), 200
@music_bp.route('/getplaystatus', methods=['GET'])
def get_play_status():
    status = song_model.get_play_status()
    server_now = int(time.time() * 1000)
    status = {
        'play_start_time': status[0],
        'is_playing': status[1],
        'server_now': server_now
    }
    return jsonify(status), 200
@music_bp.route('/getplaysongs', methods=['GET'])
def get_play_songs():
    songs=playlist_model.get_playlist_songs(1)
    return jsonify([dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], song)) for song in songs]), 200
@music_bp.route('/requestplay', methods=['POST'])
def request_play():
    now_time=int(time.time()*1000+2*1000)
    song_model.set_play_status(now_time, 1)
    return jsonify({'status':True, 'message': 'Request play successful'}), 200

