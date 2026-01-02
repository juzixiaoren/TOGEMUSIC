<template>
  <div class="playlist-detail">
    <h2>{{ playlist.playlist_name }}</h2>
    <button @click="showImportDialog = true">导入歌曲</button>
    <div v-if="showImportDialog" class="dialog">
      <h3>导入歌曲</h3>
      <div>
        <input v-model="searchQuery" placeholder="搜索歌名或歌手">
        <select v-model="filterUser">
          <option value="">所有用户</option>
          <option v-for="user in users" :key="user.id" :value="user.id">{{ user.username }}</option>
        </select>
        <select v-model="sortBy">
          <option value="time_added">上传时间</option>
          <option value="title">歌名</option>
        </select>
      </div>
      <ul>
        <li v-for="song in filteredSongs" :key="song.id">
          <input type="checkbox" v-model="selectedSongs" :value="song.id">
          {{ song.title }} - {{ song.artist }} ({{ song.duration }})
        </li>
      </ul>
      <button @click="importSongs">确认导入</button>
      <button @click="showImportDialog = false">取消</button>
    </div>
    <ul>
      <li v-for="song in playlistSongs" :key="song.id">
        {{ song.title }} - {{ song.artist }}
        <button @click="removeSong(song.id)">删除</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PlaylistDetail',
  data() {
    return {
      playlist: {},
      playlistSongs: [],
      allSongs: [],
      users: [],
      showImportDialog: false,
      searchQuery: '',
      filterUser: '',
      sortBy: 'time_added',
      selectedSongs: []
    };
  },
  computed: {
    filteredSongs() {
      let songs = this.allSongs.filter(song => {
        const matchesSearch = song.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              song.artist.toLowerCase().includes(this.searchQuery.toLowerCase());
        const matchesUser = !this.filterUser || song.uploader_id == this.filterUser;
        return matchesSearch && matchesUser;
      });
      if (this.sortBy === 'time_added') {
        songs.sort((a, b) => new Date(b.time_added) - new Date(a.time_added));
      } else {
        songs.sort((a, b) => a.title.localeCompare(b.title));
      }
      return songs;
    }
  },
  async mounted() {
    await this.loadPlaylist();
    await this.loadAllSongs();
    await this.loadUsers();
  },
  methods: {
    async loadPlaylist() {
      try {
        const response = await axios.get(`/playlists/${this.$route.params.id}`, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.playlist = response.data.playlist;
        this.playlistSongs = response.data.songs;
      } catch (error) {
        console.error('加载歌单失败', error);
      }
    },
    async loadAllSongs() {
      try {
        const response = await axios.get('/songs', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.allSongs = response.data;
      } catch (error) {
        console.error('加载歌曲失败', error);
      }
    },
    async loadUsers() {
      try {
        const response = await axios.get('/users', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.users = response.data;
      } catch (error) {
        console.error('加载用户失败', error);
      }
    },
    async importSongs() {
      try {
        await axios.post(`/playlists/${this.$route.params.id}/songs`, {
          songIds: this.selectedSongs
        }, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.showImportDialog = false;
        this.selectedSongs = [];
        await this.loadPlaylist();
      } catch (error) {
        alert('导入歌曲失败: ' + error.response.data.message);
      }
    },
    async removeSong(songId) {
      try {
        await axios.delete(`/playlists/${this.$route.params.id}/songs/${songId}`, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        await this.loadPlaylist();
      } catch (error) {
        alert('删除歌曲失败: ' + error.response.data.message);
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
}
</style>