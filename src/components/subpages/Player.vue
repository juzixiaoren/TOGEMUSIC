<template>
  <div class="player">
    <h2>主播放房间</h2>
    <button @click="showSelectDialog = true">选择歌单</button>
    <div v-if="showSelectDialog" class="dialog">
      <h3>选择歌单并导入歌曲</h3>
      <div class="playlist-select">
        <h4>可用歌单:</h4>
        <ul class="playlist-list">
          <li v-for="playlist in playlists" :key="playlist.id" class="playlist-item">
            <div class="playlist-header">
              <button @click="togglePlaylistExpand(playlist.id)" class="expand-btn">
                {{ expandedPlaylist === playlist.id ? '▼' : '▶' }}
              </button>
              <span>{{ playlist.playlist_name }}</span>
              <button @click="selectAllFromPlaylist(playlist.id)" class="select-all-btn">全选</button>
              <button @click="clearSelectionFromPlaylist(playlist.id)" class="clear-btn">取消全选</button>
            </div>
            <ul v-if="expandedPlaylist === playlist.id" class="songs-list">
              <li v-for="song in playlistSongsMap[playlist.id] || []" :key="song.id">
                <input type="checkbox" v-model="selectedSongs" :value="song.id">
                {{ song.title }} - {{ song.artist }}
              </li>
            </ul>
          </li>
        </ul>
      </div>
      <button @click="importSelectedSongs">导入选中歌曲</button>
      <button @click="showSelectDialog = false">取消</button>
    </div>
    <div class="playlist-songs">
      <h3>播放列表</h3>
      <ul>
        <li v-for="song in displayPlaylist" :key="song.id" :class="{ playing: song.id === currentSong?.id }">
          <input type="checkbox" v-model="selectedForPlay" :value="song.id">
          {{ song.title }} - {{ song.artist }}
          <button @click="deleteSong(song.id)">删除</button>
        </li>
      </ul>
      <button @click="clearPlaylist">清除列表</button>
      <button @click="playSong">开始播放</button>
      <button @click="toggleShuffle">随机播放: {{ shuffle ? '开' : '关' }}</button>
    </div>
    <div class="player-controls" v-if="currentSong">
      <h3>正在播放: {{ currentSong.title }} - {{ currentSong.artist }}</h3>
      <button @click="prevSong">上一首</button>
      <button @click="nextSong">下一首</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Howl, Howler } from 'howler';
import io from 'socket.io-client';

// 增加 Howler 的 HTML5 音频池大小，避免池耗尽
Howler.html5PoolSize = 20;

let isInitializing = false; // 初始化锁，防止并发调用
let globalHowl = null;
export default {
  name: 'Player',
  data() {
    return {
      playlists: [],
      currentPlaylist: [],
      selectedPlaylist: null,
      showSelectDialog: false,
      selectedForPlay: [],
      socket: null,
      shuffle: false,
      currentSong: null,
      expandedPlaylist: null,
      playlistSongsMap: {},
      selectedSongs: []
    };
  },
  // 计算属性：真正要播放的队列（只包含勾选的）
  computed: {
    playQueue() {
      return this.currentPlaylist.filter(song => this.selectedForPlay.includes(song.id));
    },
    displayPlaylist() {
    if (!this.currentSong) return this.currentPlaylist;
    const remaining = this.currentPlaylist.filter(s => s.id !== this.currentSong.id);
    return [this.currentSong, ...remaining];
  }
  },
  async mounted() {
    // 仅在组件挂载时建立连接，并强制使用 polling，避免 Werkzeug WebSocket 500
    this.socket = io('http://localhost:19198', { transports: ['polling'] });

    await Promise.all([this.loadPlaylists(), this.loadDefaultPlaylist()]);
    setTimeout(() => {
      this.startPlay();
    }, 1000);

    // 监听后端歌曲切换事件
    this.socket.on('song_changed', async (data) => {
      console.log('🎵 后端切歌事件:', data);

      // 根据 new_song_id 找到歌曲对象
      const newSong = this.currentPlaylist.find(s => s.id === data.new_song_id);
      if (!newSong) {
        console.warn("找不到歌曲 ID:", data.new_song_id);
        return;
      }

      // 仅在收到广播后：旋转展示顺序并播放新首位
      this.rotatePlaylistTo(data.new_song_id);
      await this.playSong(this.currentPlaylist[0], 0);  // offset=0
    });

    // 监听后端播放列表打乱事件
    this.socket.on('playlist_shuffled', (data) => {
      console.log('🔀 播放列表已打乱:', data);
      if (data && data.songs) {
        this.currentPlaylist = data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
      }
    });
  },
  beforeUnmount() {
    if (globalHowl) {
      globalHowl.stop();
      globalHowl.unload();
      globalHowl = null;
    }
    if (this.socket) {
      this.socket.disconnect(); // 断开Socket连接
      this.socket = null;
    }
  },
  beforeDestroy() {
    this.cleanupAudio();
  },
  methods: {
    // 统一获取 Header
    // 将指定歌曲旋转到当前列表首位（只改变展示顺序，不改勾选状态）
    rotatePlaylistTo(songId) {
      if (!Array.isArray(this.currentPlaylist) || this.currentPlaylist.length === 0) return;
      const idx = this.currentPlaylist.findIndex(s => s.id === songId);
      if (idx <= 0) {
        if (idx === 0) this.currentSong = this.currentPlaylist[0];
        return;
      }
      const head = this.currentPlaylist.slice(idx);
      const tail = this.currentPlaylist.slice(0, idx);
      this.currentPlaylist = [...head, ...tail];
      this.currentSong = this.currentPlaylist[0];
    },
    cleanupAudio() {
      if (globalHowl) {
        console.log("正在彻底销毁音频实例...");
        globalHowl.off();      // 1. 移除所有事件监听（重要！）
        globalHowl.stop();     // 2. 停止播放
        globalHowl.unload();   // 3. 释放资源并从池中移除
        globalHowl = null;     // 4. 清空引用
      }
    },
    getAuthHeader() {
      return { Authorization: localStorage.getItem('token') };
    },

    async loadPlaylists() {
      try {
        const response = await axios.get('/playlists', { headers: this.getAuthHeader() });
        this.playlists = response.data;
      } catch (error) {
        console.error('加载歌单失败', error);
      }
    },

    async loadDefaultPlaylist() {
      try {
        const response = await axios.get('/playlists/1', { headers: this.getAuthHeader() });
        this.currentPlaylist = response.data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
      } catch (error) {
        console.error('加载默认歌单失败', error);
      }
    },

    async togglePlaylistExpand(playlistId) {
      if (this.expandedPlaylist === playlistId) {
        this.expandedPlaylist = null;
      } else {
        this.expandedPlaylist = playlistId;
        // 如果还没加载该歌单的歌曲，现在加载
        if (!this.playlistSongsMap[playlistId]) {
          try {
            const response = await axios.get(`/playlists/${playlistId}`, { headers: this.getAuthHeader() });
            this.playlistSongsMap[playlistId] = response.data.songs;
            console.log(`加载歌单${playlistId}的歌曲`, response.data.songs);
          } catch (error) {
            console.error(`加载歌单${playlistId}失败`, error);
          }
        }
      }
    },

    selectAllFromPlaylist(playlistId) {
      const songs = this.playlistSongsMap[playlistId] || [];
      songs.forEach(song => {
        if (!this.selectedSongs.includes(song.id)) {
          this.selectedSongs.push(song.id);
        }
      });
    },

    clearSelectionFromPlaylist(playlistId) {
      const songs = this.playlistSongsMap[playlistId] || [];
      const songIds = songs.map(s => s.id);
      this.selectedSongs = this.selectedSongs.filter(id => !songIds.includes(id));
    },

    async importSelectedSongs() {
      if (this.selectedSongs.length === 0) {
        alert('请选择要导入的歌曲');
        return;
      }
      try {
        await axios.post('/playlists/1/songs', {
          songIds: this.selectedSongs
        }, { headers: this.getAuthHeader() });
        await this.loadDefaultPlaylist();
        this.showSelectDialog = false;
        this.selectedSongs = [];
        alert('导入成功');
      } catch (error) {
        console.error('导入歌曲失败', error);
        alert('导入歌曲失败');
      }
    },

    async startPlay() {
      try {
        let res = await axios.get('/getplaystatus', { headers: this.getAuthHeader() });
        let status = res.data;

        if (status.is_playing === 0) {
          await this.requestPlay();
          await new Promise(r => setTimeout(r, 500)); // 增加一点缓冲时间
          res = await axios.get('/getplaystatus', { headers: this.getAuthHeader() });
          status = res.data;
          if(status.is_playing===0)
          {
            console.warn('后端仍未开始播放，放弃同步');
            return;
          }
        }

        const song = this.currentPlaylist[0];
      if (!song) return;


      console.log('开始同步服务器进度...');
      const serverNow = status['server_now'];
      const startTime = new Date(status['play_start_time']).getTime();
      const offset = Math.max(0, Math.floor((serverNow - startTime) / 1000));
      this.playSong(song, offset);
    } catch (error) {
        console.error('启动播放失败', error);
      }
    },

    async playSong(song, offset = 0) {
      if (isInitializing) {
        console.log("正在初始化中，忽略重复调用");
        return;
      }
      try {
        // --- 强制清理 ---
        if (globalHowl) {
          console.log("清理旧实例...");
          globalHowl.stop();
          globalHowl.unload(); 
          globalHowl = null;
        }

        this.currentSong = song;
        const audioUrl = `http://localhost:19198/songs/${song.id}/file.${song.file_extension}`;

        // --- 创建新实例 ---
        globalHowl = new Howl({
          src: [audioUrl],
          html5: true,
          format: [song.file_extension],
          onload: () => {
            console.log("加载成功，准备播放");
            if (offset > 0) globalHowl.seek(offset);
            
            // 尝试执行播放
            const playPromise = globalHowl.play();
            if (playPromise && playPromise.catch) {
              playPromise.catch(e => {
                console.warn("自动播放被拦截，点击页面解锁", e);
                // 监听全局点击解锁
                const unlock = () => {
                  globalHowl?.play();
                  document.removeEventListener('click', unlock);
                };
                document.addEventListener('click', unlock);
              });
            }
          },
          onend: () => {
            isInitializing = false; // 结束后解锁
          },
          onloaderror: (id, err) => {
            console.error("加载失败:", err);
            isInitializing = false; 
          }
        });
      }
      catch (error) {
        console.error('播放歌曲失败', error);
        isInitializing = false; 
      }
    },

    async clearPlaylist() {
      try {
        const response = await axios.get('/clearplaylist', {
          headers: this.getAuthHeader()
        });
          if(response.data.success){
          this.currentPlaylist = [];
          this.selectedForPlay = [];
          this.currentSong = null;
          this.cleanupAudio();
        }
        else{
          alert('清除播放列表失败: ' + (response.data.message || '未知错误'));
        }
      }
      catch (error) {
        console.error('清除播放列表失败', error);
      }
    },

    async deleteSong(songId) {
      try {
        await axios.post('/removesongfromplaylist', {
          playlist_id: 1, // 假设主播放房间的歌单ID为1
          song_id: songId
        }, {
          headers: this.getAuthHeader()
        });
        // 从当前播放列表中移除歌曲
        this.currentPlaylist = this.currentPlaylist.filter(s => s.id !== songId);
        this.selectedForPlay = this.selectedForPlay.filter(id => id !== songId);
      } catch (error) {
        console.error('删除歌曲失败', error);
      }
    },

    requestPlay() {
      return axios.post('/requestplay', {
        song_ids: this.selectedForPlay
      }, {
        headers: this.getAuthHeader()
      });
    },

    async nextSong() {
      try {
        // 通过 websocket 请求后端切换到下一首歌
        this.socket?.emit('request_next_song', {}, (response) => {
          if (response && response.success) {
            console.log('切换到下一首歌成功');
          }
        });
      } catch (error) {
        console.error('切换歌曲失败', error);
      }
    },

    async prevSong() {
      try {
        // 通过 websocket 请求后端切换到上一首歌
        this.socket?.emit('request_prev_song', {}, (response) => {
          if (response && response.success) {
            console.log('切换到上一首歌成功');
          }
        });
      } catch (error) {
        console.error('切换歌曲失败', error);
      }
    },

    toggleShuffle() {
      this.shuffle = !this.shuffle;
      if (this.shuffle) {
        // 打乱播放列表
        this.socket?.emit('request_shuffle_playlist', {}, (response) => {
          if (response && response.success) {
            console.log('播放列表已打乱');
          }
        });
      }
    }
  }
};
</script>

<style scoped>
.dialog {
  position: fixed;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  background: white;
  padding: 20px;
  border: 1px solid #ccc;
  overflow: auto;
  z-index: 1000;
}

.playlist-select {
  margin: 20px 0;
}

.playlist-list {
  list-style: none;
  padding: 0;
  max-height: 400px;
  overflow-y: auto;
}

.playlist-item {
  border: 1px solid #ddd;
  margin-bottom: 10px;
  border-radius: 4px;
}

.playlist-header {
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
  background: #f5f5f5;
  cursor: pointer;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  width: 20px;
}

.select-all-btn, .clear-btn {
  padding: 5px 10px;
  font-size: 12px;
  margin-left: auto;
}

.songs-list {
  list-style: none;
  padding: 10px;
  background: #fafafa;
  max-height: 200px;
  overflow-y: auto;
}

.songs-list li {
  padding: 5px;
  margin: 5px 0;
}

.songs-list input {
  margin-right: 10px;
}

.playing {
  background: yellow;
}
</style>