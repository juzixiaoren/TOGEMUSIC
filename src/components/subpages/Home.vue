<template>
  <div class="home">
    <h1>TOGEMUSIC</h1>
    <nav>
      <router-link to="/UploadMusic">上传音乐</router-link>
      <router-link to="/Playlists">我的歌单</router-link>
      <router-link to="/Player">播放房间</router-link>
    </nav>
    <div class="recent-songs">
      <h2>最近上传的歌曲</h2>
      <ul>
        <li v-for="song in recentSongs" :key="song.id">
          {{ song.title }} - {{ song.artist }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Home',
  data() {
    return {
      recentSongs: []
    };
  },
  async mounted() {
    await this.loadRecentSongs();
  },
  methods: {
    async loadRecentSongs() {
      try {
        const response = await axios.get('/songs?limit=10', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.recentSongs = response.data;
      } catch (error) {
        console.error('加载最近歌曲失败', error);
      }
    }
  }
};
</script>

<style scoped>
.home {
  padding: 20px;
}
nav {
  margin-bottom: 20px;
}
nav a {
  margin-right: 10px;
}
</style>