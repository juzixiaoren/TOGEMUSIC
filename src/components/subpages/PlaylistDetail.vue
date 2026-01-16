<template>
  <div class="background">
    <HeaderTopAfterLogin :userId="userId" @logout="logout" class="header-top"></HeaderTopAfterLogin>
    <div v-if="message" class="message-box" :class="messageType">
      {{ message }}
    </div>
    <div class="home-content">
      <h2>{{ playlist.playlist_name }}</h2>
      <button @click="showImportDialog = true">导入歌曲</button>
      <div v-if="showImportDialog" class="dialog">
        <h3>导入歌曲</h3>
        <div class="import-tabs">
          <button :class="{ active: importMode === 'songs' }" @click="importMode = 'songs'">从歌曲选择</button>
          <button :class="{ active: importMode === 'playlists' }" @click="importMode = 'playlists'">从歌单选择</button>
        </div>
        
        <!-- 从歌曲选择 -->
        <div v-if="importMode === 'songs'" class="import-section">
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
        </div>

        <!-- 从歌单选择 -->
        <div v-if="importMode === 'playlists'" class="import-section">
          <h4>可用歌单:</h4>
          <ul class="playlist-select">
            <li v-for="playlist in otherPlaylists" :key="playlist.id" class="playlist-item">
              <div class="playlist-header">
                <button @click="toggleSourcePlaylistExpand(playlist.id)" class="expand-btn">
                  {{ expandedSourcePlaylist === playlist.id ? '▼' : '▶' }}
                </button>
                <span>{{ playlist.playlist_name }}</span>
                <button @click="selectAllFromSourcePlaylist(playlist.id)" class="select-all-btn">全选</button>
                <button @click="clearSelectionFromSourcePlaylist(playlist.id)" class="clear-btn">取消全选</button>
              </div>
              <ul v-if="expandedSourcePlaylist === playlist.id" class="songs-list">
                <li v-for="song in sourcePlaylistSongsMap[playlist.id] || []" :key="song.id">
                  <input type="checkbox" v-model="selectedSongs" :value="song.id">
                  {{ song.title }} - {{ song.artist }}
                </li>
              </ul>
            </li>
          </ul>
        </div>

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
  </div>
</template>

<script>
import axios from 'axios';
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';
export default {
  name: 'PlaylistDetail',
  components: {
    HeaderTopAfterLogin
  },
  data() {
    return {
      userId: localStorage.getItem('userId') || '未登录用户',
      playlist: {},
      playlistSongs: [],
      allSongs: [],
      otherPlaylists: [],
      users: [],
      showImportDialog: false,
      searchQuery: '',
      filterUser: '',
      sortBy: 'time_added',
      selectedSongs: [],
      importMode: 'songs',
      expandedSourcePlaylist: null,
      sourcePlaylistSongsMap: {},
      message: "",
      messageType: "", // 用于存储消息类型
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
    await this.loadOtherPlaylists();
  },
  methods: {
    logout() {
      localStorage.removeItem("token"); // 清除 token
      localStorage.removeItem("userId"); // 清除用户 ID
      this.updateUserId(); // 更新用户信息
      this.$router.push({ path: "/Login" }); // 跳转到登录页面
    },
    setMessage(content, type) {
      this.message = content;
      this.messageType = type; // 设置消息类型
      setTimeout(() => {
          this.message = "";
          this.messageType = "";
      }, 3000); // 3秒后清除消息提示
    },
    async loadPlaylist() {
      try {
        const response = await axios.get(`/playlists/${this.$route.params.id}`, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.playlist = response.data.playlist;
        this.playlistSongs = response.data.songs;
      } catch (error) {
        console.error('加载歌单失败', error);
        this.setMessage('加载歌单失败', 'error');
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
        this.setMessage('加载歌曲失败', 'error');
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
        this.setMessage('加载用户失败', 'error');
      }
    },
    async loadOtherPlaylists() {
      try {
        const response = await axios.get('/getAllPlaylists', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        // 排除当前歌单
        this.otherPlaylists = response.data.filter(p => p.id != this.$route.params.id);
      } catch (error) {
        console.error('加载其他歌单失败', error);
        this.setMessage('加载其他歌单失败', 'error');
      }
    },
    async toggleSourcePlaylistExpand(playlistId) {
      if (this.expandedSourcePlaylist === playlistId) {
        this.expandedSourcePlaylist = null;
      } else {
        this.expandedSourcePlaylist = playlistId;
        // 如果还没加载该歌单的歌曲，现在加载
        if (!this.sourcePlaylistSongsMap[playlistId]) {
          try {
            const response = await axios.get(`/playlists/${playlistId}`, {
              headers: { Authorization: localStorage.getItem('token') }
            });
            this.sourcePlaylistSongsMap[playlistId] = response.data.songs;
          } catch (error) {
            console.error(`加载歌单${playlistId}失败`, error);
            this.setMessage(`加载歌单失败`, 'error');
          }
        }
      }
    },
    selectAllFromSourcePlaylist(playlistId) {
      const songs = this.sourcePlaylistSongsMap[playlistId] || [];
      songs.forEach(song => {
        if (!this.selectedSongs.includes(song.id)) {
          this.selectedSongs.push(song.id);
        }
      });
    },
    clearSelectionFromSourcePlaylist(playlistId) {
      const songs = this.sourcePlaylistSongsMap[playlistId] || [];
      const songIds = songs.map(s => s.id);
      this.selectedSongs = this.selectedSongs.filter(id => !songIds.includes(id));
    },
    async importSongs() {
      if (this.selectedSongs.length === 0) {
        this.setMessage('请选择要导入的歌曲', 'warning');
        return;
      }
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
        console.error('导入歌曲失败', error);
        this.setMessage('导入歌曲失败: ' + error.response.data.message, 'error');
      }
    },
    async removeSong(songId) {
      try {
        await axios.delete(`/playlists/${this.$route.params.id}/songs/${songId}`, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        await this.loadPlaylist();
      } catch (error) {
        console.error('删除歌曲失败', error);
        this.setMessage('删除歌曲失败: ' + error.response.data.message, 'error');
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

.import-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.import-tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-weight: normal;
}

.import-tabs button.active {
  border-bottom-color: #007bff;
  color: #007bff;
  font-weight: bold;
}

.import-section {
  margin-bottom: 20px;
}

.playlist-select {
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