<template>
  <div class="player">
    <h2>主播放房间</h2>
    <button @click="showSelectDialog = true">选择歌单</button>
    <div v-if="showSelectDialog" class="dialog">
      <h3>选择歌单</h3>
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
      <button @click="startPlay">开始播放</button>
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
import { Howl } from 'howler';

export default {
  name: 'Player',
  data() {
    return {
      playlists: [],
      currentPlaylist: [],
      selectedPlaylist: null,
      showSelectDialog: false,
      playQueue: [],//播放队列
      selectedForPlay: [],
      currentIndex: 0,
      shuffle: false,
      currentSong: null,
      howl: null
    };
  },
  async mounted() {
    await this.loadPlaylists();
    await this.loadDefaultPlaylist();
  },
  methods: {
    async loadPlaylists() {
      try {
        const response = await axios.get('/playlists', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.playlists = response.data;
      } catch (error) {
        console.error('加载歌单失败', error);
      }
    },
    async loadDefaultPlaylist() {
      try {
        const response = await axios.get('/playlists/1', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.currentPlaylist = response.data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
      } catch (error) {
        console.error('加载默认歌单失败', error);
      }
    },
    async loadPlaylistSongs() {
      try {
        const response = await axios.get(`/playlists/${this.selectedPlaylist}`, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.currentPlaylist = response.data.songs;
        this.selectedForPlay = this.currentPlaylist.map(s => s.id);
        this.showSelectDialog = false;
      } catch (error) {
        console.error('加载歌单歌曲失败', error);
      }
    },
    startPlay() {
        this.playQueue = this.currentPlaylist.filter(
            s => this.selectedForPlay.includes(s.id)
        )

        if (this.playQueue.length === 0) return

        this.currentIndex = 0
        this.playSong(this.playQueue[0])
        },
    playSong(song) {
        if (this.howl) {
            this.howl.stop()
            this.howl.unload()
        }

        this.currentSong = song

        // 后端返回的 URL 带后缀
        this.howl = new Howl({
            src: [`http://localhost:19198/songs/${song.id}/file.${song.file_extension}`],
            html5: true,
            onloaderror: (id, err) => console.error('音频加载失败', err),
            onplayerror: (id, err) => {
            console.error('播放失败', err)
            this.howl.once('unlock', () => this.howl.play())
            },
            onend: () => this.nextSong()
        })

        this.howl.play()
        },
    nextSong() {
        if (this.playQueue.length === 0) return

        if (this.shuffle) {
            this.currentIndex = Math.floor(
            Math.random() * this.playQueue.length
            )
        } else {
            this.currentIndex =
            (this.currentIndex + 1) % this.playQueue.length
        }

        this.playSong(this.playQueue[this.currentIndex])
        },
    prevSong() {
        if (this.playQueue.length === 0) return

        this.currentIndex =
            (this.currentIndex - 1 + this.playQueue.length) %
            this.playQueue.length

        this.playSong(this.playQueue[this.currentIndex])
        },
    toggleShuffle() {
      this.shuffle = !this.shuffle;
    },
    updateProgress() {
      // 同步进度，可扩展为多人同步
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