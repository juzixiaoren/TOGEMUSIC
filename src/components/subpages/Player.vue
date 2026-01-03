<template>
  <div class="player">
    <h2>主播放房间</h2>
    <button @click="showSelectDialog = true">选择歌单</button>
    <div v-if="showSelectDialog" class="dialog">
      <h3 v-if="playlists.length > 0">选择歌单</h3>
      <h3 v-else>没有可用的歌单</h3>
      <ul>
        <li v-for="playlist in playlists" :key="playlist.id">
          <input type="radio" v-model="selectedPlaylist" :value="playlist.id">
          {{ playlist.playlist_name }}
        </li>
      </ul>
      <button @click="loadPlaylistSongs">确认</button>
      <button @click="showSelectDialog = false">取消</button>
    </div>
    <div class="playlist-songs">
      <h3>播放列表</h3>
      <ul>
        <li v-for="(song, index) in currentPlaylist" :key="song.id" :class="{ playing: index === currentIndex }">
          <input type="checkbox" v-model="selectedForPlay" :value="song.id">
          {{ song.title }} - {{ song.artist }}
        </li>
      </ul>
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

// 连接到后端SocketIO
const socket = io('http://localhost:19198');
export default {
  name: 'Player',
  data() {
    return {
      playlists: [],
      currentPlaylist: [],
      selectedPlaylist: null,
      showSelectDialog: false,
      // playQueue 应该根据 currentPlaylist 和 selectedForPlay 动态计算
      selectedForPlay: [],
      currentIndex: 0,
      shuffle: false,
      currentSong: null,
    };
  },
  // 计算属性：真正要播放的队列（只包含勾选的）
  computed: {
    playQueue() {
      return this.currentPlaylist.filter(song => this.selectedForPlay.includes(song.id));
    }
  },
  async mounted() {
    await Promise.all([this.loadPlaylists(), this.loadDefaultPlaylist()]);
    setTimeout(() => {
      this.startPlay();
    }, 1000);

    // 监听后端歌曲切换事件
    socket.on('song_changed', (data) => {
      console.log('后端切换歌曲:', data);
      this.startPlay(); // 重新同步播放状态
    });
  },
  beforeUnmount() {
    if (globalHowl) {
      globalHowl.stop();
      globalHowl.unload();
      globalHowl = null;
    }
    socket.disconnect(); // 断开Socket连接
  },
  beforeDestroy() {
    this.cleanupAudio();
  },
  methods: {
    // 统一获取 Header
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

    async loadPlaylistSongs() {
      try {
        const response = await axios.get(`/playlists/${this.selectedPlaylist}`, { headers: this.getAuthHeader() });
        this.currentPlaylist = response.data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
        this.showSelectDialog = false;
      } catch (error) {
        console.error('加载歌单歌曲失败', error);
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

    requestPlay() {
      return axios.post('/requestplay', {
        song_ids: this.selectedForPlay
      }, {
        headers: this.getAuthHeader()
      });
    },

    nextSong() {
      if (this.playQueue.length === 0) return;

      if (this.shuffle) {
        this.currentIndex = Math.floor(Math.random() * this.playQueue.length);
      } else {
        this.currentIndex = (this.currentIndex + 1) % this.playQueue.length;
      }
    },

    prevSong() {
      if (this.playQueue.length === 0) return;
      this.currentIndex = (this.currentIndex - 1 + this.playQueue.length) % this.playQueue.length;
    },

    toggleShuffle() {
      this.shuffle = !this.shuffle;
    }
  }
};
</script>

<style scoped>
.dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border: 1px solid #ccc;
}
.playing {
  background: yellow;
}
</style>