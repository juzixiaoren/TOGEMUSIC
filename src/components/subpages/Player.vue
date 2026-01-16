<template>
  <div class="background">
    <HeaderTopAfterLogin :userId="userId" @logout="logout" class="header-top"></HeaderTopAfterLogin>
    <div v-if="message" class="message-box" :class="messageType">
      {{ message }}
    </div>
    <div class="home-content">
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
  </div>
</template>

<script>
import axios from 'axios';
import { Howl, Howler } from 'howler';
import io from 'socket.io-client';
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';
// 增加 Howler 的 HTML5 音频池大小，避免池耗尽
Howler.html5PoolSize = 20;

let isInitializing = false; // 初始化锁，防止并发调用
let globalHowl = null;
export default {
  name: 'Player',
  components: {
    HeaderTopAfterLogin
  },
  data() {
    return {
      userId: localStorage.getItem('userId') || '未登录用户',
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
      selectedSongs: [],
      message: "",
      messageType: "", // 用于存储消息类型
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
    this.userId = localStorage.getItem("userId") || "未登录用户"; // 获取用户 ID
    // 仅在组件挂载时建立连接，并强制使用 polling，避免 Werkzeug WebSocket 500
    this.socket = io('http://localhost:19198', { transports: ['polling'] });

    await Promise.all([this.loadPlaylists(), this.loadDefaultPlaylist()]);
    setTimeout(() => {
      this.startPlay();
    }, 1000);

    // 监听后端歌曲切换事件
    this.socket.on('song_changed', async (data) => {
      this.setMessage(`🎵 正在播放: ${data.title} - ${data.artist}`, 'success');

      // 根据 new_song_id 找到歌曲对象
      const newSong = this.currentPlaylist.find(s => s.id === data.new_song_id);
      if (!newSong) {
        this.setMessage('播放的歌曲不在当前播放列表中，无法播放', 'error');
        return;
      }

      // 仅在收到广播后：旋转展示顺序并播放新首位
      this.rotatePlaylistTo(data.new_song_id);
      await this.playSong(this.currentPlaylist[0], 0);  // offset=0
    });

    // 监听后端播放列表打乱事件
    this.socket.on('playlist_shuffled', (data) => {
      this.setMessage('🔀 播放列表已打乱', 'success');
      if (data && data.songs) {
        this.currentPlaylist = data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
      }
    });

    // 监听歌曲被删除且需要切歌的事件（删除的是正在播放的歌曲）
    this.socket.on('song_deleted_and_changed', async (data) => {
      const { deleted_song_id, new_song_id, new_song, playlist } = data;
      
      // 更新播放列表
      this.currentPlaylist = playlist;
      this.selectedForPlay = this.selectedForPlay.filter(id => id !== deleted_song_id);
      
      if (new_song && new_song_id) {
        // 旋转播放列表让新歌在最前面
        this.rotatePlaylistTo(new_song_id);
        this.setMessage(`🎵 歌曲已删除，自动切歌: ${new_song.title} - ${new_song.artist}`, 'success');
        
        // 立即播放新歌
        try {
          await this.playSong(this.currentPlaylist[0], 0);
        } catch (error) {
          console.error('切歌失败:', error);
        }
      } else {
        this.setMessage('⚠️ 歌曲已删除，播放列表已清空', 'warning');
        this.cleanupAudio();
        this.currentSong = null;
      }
    });

    // 监听歌曲被删除但不是当前播放歌曲的事件（只更新列表）
    this.socket.on('playlist_updated', (data) => {
      const { deleted_song_id, playlist } = data;
      
      // 更新播放列表
      this.currentPlaylist = playlist;
      this.selectedForPlay = this.selectedForPlay.filter(id => id !== deleted_song_id);
      
      this.setMessage('🎵 歌曲已从列表删除', 'success');
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
    setMessage(content, type) {
      this.message = content;
      this.messageType = type; // 设置消息类型
      setTimeout(() => {
          this.message = "";
          this.messageType = "";
      }, 3000); // 3秒后清除消息提示
    },
    logout() {
      localStorage.removeItem("token"); // 清除 token
      localStorage.removeItem("userId"); // 清除用户 ID
      this.updateUserId(); // 更新用户信息
      this.$router.push({ path: "/Login" }); // 跳转到登录页面
    },
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
        this.setMessage('加载歌单失败', 'error');
      }
    },

    async loadDefaultPlaylist() {
      try {
        const response = await axios.get('/playlists/1', { headers: this.getAuthHeader() });
        this.currentPlaylist = response.data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
      } catch (error) {
        this.setMessage('加载默认歌单失败', 'error');
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
            this.setMessage(`歌单${playlistId}的歌曲加载完成`, 'success');
          } catch (error) {
            this.setMessage(`加载歌单${playlistId}失败`, 'error');
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
        this.setMessage('导入歌曲成功', 'success');
      } catch (error) {
        this.setMessage('导入歌曲失败', 'error');
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
            this.setMessage('后端仍未开始播放，放弃同步', 'warning');
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
        this.setMessage('启动播放失败', 'error');
      }
    },

    async playSong(song, offset = 0) {
      if (isInitializing) {
        this.setMessage("播放初始化中，忽略重复调用", "warning");
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
            this.setMessage(`🎵 已加载: ${song.title} - ${song.artist}`, 'success');
            if (offset > 0) globalHowl.seek(offset);
            
            // 尝试执行播放
            const playPromise = globalHowl.play();
            if (playPromise && playPromise.catch) {
              playPromise.catch(e => {
                alert("浏览器阻止了自动播放，请点击页面任意位置以解锁音频播放");
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
            this.setMessage(`加载歌曲失败: ${song.title}`, 'error');
            isInitializing = false; 
          }
        });
      }
      catch (error) {
        console.error('播放歌曲失败', error);
        this.setMessage('播放歌曲失败', 'error');
        isInitializing = false; 
      }
    },
    setMessage(content, type) {
            this.message = content;
            this.messageType = type; // 设置消息类型
            setTimeout(() => {
                this.message = "";
                this.messageType = "";
            }, 3000); // 3秒后清除消息提示
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
          this.setMessage('清除播放列表失败: ' + (response.data.message || '未知错误'), 'error');
        }
      }
      catch (error) {
        console.error('清除播放列表失败', error);
        this.setMessage('清除播放列表失败', 'error');
      }
    },

    async deleteSong(songId) {
      try {
        const response = await axios.post('/removesongfromplaylist', {
          playlist_id: 1, // 主播放房间的歌单ID为1
          song_id: songId
        }, {
          headers: this.getAuthHeader()
        });
        
        if (response.data.success) {
          // 等待后端广播事件，不在这里本地处理
          // 由 socket 事件监听器处理列表更新
          this.setMessage('歌曲已删除', 'success');
        } else {
          this.setMessage(response.data.message || '删除失败', 'error');
        }
      } catch (error) {
        console.error('删除歌曲失败', error);
        this.setMessage('删除歌曲失败', 'error');
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
            this.setMessage('切换到下一首歌成功', 'success');
          }
        });
      } catch (error) {
        this.setMessage('切换歌曲失败', 'error');
      }
    },

    async prevSong() {
      try {
        // 通过 websocket 请求后端切换到上一首歌
        this.socket?.emit('request_prev_song', {}, (response) => {
          if (response && response.success) {
            this.setMessage('切换到上一首歌成功', 'success');
          }
        });
      } catch (error) {
        this.setMessage('切换歌曲失败', 'error');
      }
    },

    toggleShuffle() {
      this.shuffle = !this.shuffle;
      if (this.shuffle) {
        // 打乱播放列表
        this.socket?.emit('request_shuffle_playlist', {}, (response) => {
          if (response && response.success) {
            this.setMessage('播放列表已打乱', 'success');
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

.home-content {
  position: relative;
  top: 120px; /* 距离顶部的高度 */
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 150px); /* 减去头部高度 */
  width: 90%;
}
.message-box {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
    width: 80%;
    max-width: 600px;
    color: white;
}

.message-box.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message-box.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.message-box.warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}

</style>