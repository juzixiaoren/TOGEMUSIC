from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
import os
import bcrypt
import jwt
import datetime
from mutagen import File as MutagenFile
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from dao.sql_init import SQLInit
from dao import config

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'data')

db_path = config.DB_PATH
db_name = config.DB_NAME
db = SQLInit(db_path, db_name)

# 播放状态
current_playlist = []
current_song_index = 0
is_playing = False
current_time = 0

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        db.add_user(username, hashed.decode('utf-8'))
        return jsonify({'message': 'User registered successfully'}), 201
    except:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = db.check_user(username, password)
    if user:
        token = generate_token(username)
        return jsonify({'token': token, 'user': {'username': username}})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    files = request.files.getlist('files')
    titles = request.form.getlist('titles')
    artists = request.form.getlist('artists')

    if not files:
        return jsonify({'error': 'No files provided'}), 400

    uploaded_songs = []
    for i, file in enumerate(files):
        if file and file.filename:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 解析元数据
            try:
                audio = MutagenFile(file_path)
                duration = audio.info.length if audio else 0
                default_title = titles[i] if i < len(titles) and titles[i] else filename.rsplit('.', 1)[0]
                default_artist = artists[i] if i < len(artists) and artists[i] else 'Unknown'
            except:
                duration = 0
                default_title = filename.rsplit('.', 1)[0]
                default_artist = 'Unknown'

            db.add_song(default_title, default_artist, duration, file_path, user_id)
            uploaded_songs.append({
                'title': default_title,
                'artist': default_artist,
                'duration': duration
            })

    return jsonify({'message': 'Files uploaded successfully', 'songs': uploaded_songs}), 201

@app.route('/songs', methods=['GET'])
def get_songs():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    songs = db.get_all_songs()
    return jsonify(songs), 200

@app.route('/playlists', methods=['GET'])
def get_playlists():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    playlists = db.get_all_playlists()
    return jsonify(playlists), 200

@app.route('/playlists', methods=['POST'])
def create_playlist():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name required'}), 400

    db.create_playlist(user_id, name)
    return jsonify({'message': 'Playlist created'}), 201

@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    playlist = db.get_playlist(playlist_id)
    songs = db.get_playlist_songs(playlist_id)
    return jsonify({'playlist': playlist, 'songs': songs}), 200

@app.route('/playlists/<int:playlist_id>/import', methods=['POST'])
def import_songs(playlist_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.get_json()
    song_ids = data.get('song_ids', [])
    for song_id in song_ids:
        db.add_song_to_playlist(playlist_id, song_id)
    return jsonify({'message': 'Songs imported'}), 200

@app.route('/player/playlist', methods=['GET'])
def get_player_playlist():
    # 返回 ID=1 的歌单
    songs = db.get_playlist_songs(1)
    return jsonify(songs), 200

@app.route('/player/songs', methods=['DELETE'])
def remove_player_songs():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token required'}), 401
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.get_json()
    song_ids = data.get('song_ids', [])
    for song_id in song_ids:
        db.remove_song_from_playlist(1, song_id)
    return jsonify({'message': 'Songs removed'}), 200

@app.route('/music/<path:filename>')
def serve_music(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@socketio.on('join')
def handle_join(data):
    join_room('player_room')
    emit('sync', {
        'current_song_index': current_song_index,
        'is_playing': is_playing,
        'current_time': current_time
    })

@socketio.on('play')
def handle_play(data):
    global is_playing
    is_playing = True
    emit('sync', {
        'current_song_index': current_song_index,
        'is_playing': is_playing,
        'current_time': current_time
    }, room='player_room')

@socketio.on('pause')
def handle_pause(data):
    global is_playing
    is_playing = False
    emit('sync', {
        'current_song_index': current_song_index,
        'is_playing': is_playing,
        'current_time': current_time
    }, room='player_room')

@socketio.on('next')
def handle_next(data):
    global current_song_index
    current_song_index = (current_song_index + 1) % len(current_playlist)
    emit('sync', {
        'current_song_index': current_song_index,
        'is_playing': is_playing,
        'current_time': 0
    }, room='player_room')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)