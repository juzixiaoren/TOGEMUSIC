from flask import Blueprint, request, jsonify, send_from_directory
from flask import send_file, abort, current_app
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
    source_playlist_id = data.get('sourcePlaylistId', None)
    
    added_count = 0
    skipped_count = 0
    
    # 如果指定了源歌单，从源歌单获取歌曲
    if source_playlist_id:
        source_songs = playlist_model.get_playlist_songs(source_playlist_id)
        # 从源歌单中按选中的歌曲ID导入
        for song in source_songs:
            if song[0] in song_ids:  # song[0] 是 song_id
                try:
                    playlist_model.add_song_to_playlist(playlist_id, song[0])
                    added_count += 1
                except Exception as e:
                    # 捕获UNIQUE约束冲突或其他错误，继续处理其他歌曲
                    print(f"跳过歌曲 {song[0]}: {str(e)}")
                    skipped_count += 1
    else:
        # 直接从歌曲ID列表导入
        for song_id in song_ids:
            try:
                playlist_model.add_song_to_playlist(playlist_id, song_id)
                added_count += 1
            except Exception as e:
                # 捕获UNIQUE约束冲突或其他错误，继续处理其他歌曲
                print(f"跳过歌曲 {song_id}: {str(e)}")
                skipped_count += 1
    
    return jsonify({
        'message': f'导入成功: {added_count}首歌曲' + (f'，跳过: {skipped_count}首重复歌曲' if skipped_count > 0 else ''),
        'added': added_count,
        'skipped': skipped_count
    }), 200

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
    songs=playlist_model.get_playlist_songs(1)
    if(not songs or len(songs)==0):
        return jsonify({'status':False, 'message': 'No songs in playlist'}), 400
    now_time=int(time.time()*1000+2*1000)
    song_model.set_play_status(now_time, 1)
    return jsonify({'status':True, 'message': 'Request play successful'}), 200

@music_bp.route('/clearplaylist', methods=['GET'])
def clear_playlist():
    playlist_model.clear_playlist(1)
    return jsonify({'message': 'Playlist cleared', 'success': True}), 200

@music_bp.route('/removesongfromplaylist', methods=['POST'])
def remove_song_from_playlist_request():
    data = request.get_json()
    song_id = data.get('song_id')
    
    # 获取当前播放列表
    now_songs = playlist_model.get_playlist_songs(1)
    
    if not now_songs or len(now_songs) == 0:
        # 如果删除前列表为空，直接返回错误
        return jsonify({'message': '删除错误', 'success': False, 'is_playing': False}), 200
    
    # 检查删除的是否是当前播放的歌曲（order_index=1 的歌曲）
    is_playing_song = len(now_songs) > 0 and now_songs[0][0] == song_id
    
    # 从播放列表中删除歌曲
    playlist_model.remove_song_from_playlist(1, song_id)
    
    # 获取 socketio 实例
    socketio = current_app.extensions.get('socketio')
    
    if is_playing_song:
        # 如果删除的是当前播放的歌曲，切换下一首歌
        song_model.rotate_playlist_index()
        song_model.start_next_song()
        song_model.mark_need_notify()
        
        # 获取新的播放列表用于广播
        updated_songs = playlist_model.get_playlist_songs(1)
        songs_data = [dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], s)) for s in updated_songs]
        
        # 广播所有人切歌并更新歌单
        if socketio:
            socketio.emit('song_deleted_and_changed', {
                'deleted_song_id': song_id,
                'new_song_id': songs_data[0]['id'] if songs_data else None,
                'new_song': dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], updated_songs[0])) if updated_songs else None,
                'playlist': songs_data
            }, room=None)
    else:
        # 如果删除的不是当前播放的歌曲，重新调整顺序索引
        playlist_model.reset_index(1, song_id)
        
        # 获取更新后的播放列表
        updated_songs = playlist_model.get_playlist_songs(1)
        songs_data = [dict(zip(['id', 'title', 'artist', 'duration', 'uploader_id', 'file_path', 'file_extension', 'time_added'], s)) for s in updated_songs]
        
        # 广播歌单更新（不切歌）
        if socketio:
            socketio.emit('playlist_updated', {
                'deleted_song_id': song_id,
                'playlist': songs_data
            }, room=None)
    
    return jsonify({
        'message': 'Song removed from playlist',
        'success': True,
        'is_playing': is_playing_song
    }), 200

