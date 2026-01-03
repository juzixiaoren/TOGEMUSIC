<template>
  <div class="playlists">
    <h2>我的歌单</h2>
    <button @click="showCreateDialog = true">创建歌单</button>
    <div v-if="showCreateDialog" class="dialog">
      <input v-model="newPlaylistName" placeholder="歌单名称">
      <button @click="createPlaylist">确认</button>
      <button @click="showCreateDialog = false">取消</button>
    </div>
    <ul>
      <li v-for="playlist in playlists" :key="playlist.id">
        <router-link :to="`/Playlist/${playlist.id}`">{{ playlist.playlist_name }}</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Playlists',
  data() {
    return {
      playlists: [],
      showCreateDialog: false,
      newPlaylistName: ''
    };
  },
  async mounted() {
    await this.loadPlaylists();
  },
  methods: {
    async loadPlaylists() {
      try {
        const response = await axios.get('/getAllPlaylists', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.playlists = response.data;
      } catch (error) {
        console.error('加载歌单失败', error);
      }
    },
    async createPlaylist() {
      try {
        await axios.post('/playlists', {
          name: this.newPlaylistName
        }, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.showCreateDialog = false;
        this.newPlaylistName = '';
        await this.loadPlaylists();
      } catch (error) {
        alert('创建歌单失败: ' + error.response.data.message);
      }
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
</style>