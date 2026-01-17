<template>
  <div class="background">
    <HeaderTopAfterLogin :userId="userId" @logout="logout" class="header-top"></HeaderTopAfterLogin>
    <div v-if="message" class="message-box" :class="messageType">
      {{ message }}
    </div>
    <div class="home-content">
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
  </div>
</template>

<script>
import axios from 'axios';
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';

export default {
  name: 'Playlists',
  components: {
    HeaderTopAfterLogin
  },
  data() {
    return {
      userId: localStorage.getItem('userId') || '未登录用户',
      playlists: [],
      showCreateDialog: false,
      newPlaylistName: '',
      message: "",
      messageType: "", // 用于存储消息类型
    };
  },
  async mounted() {
    await this.loadPlaylists();
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
    async loadPlaylists() {
      try {
        const response = await axios.get('/getAllPlaylists', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.playlists = response.data;
      } catch (error) {
        console.error('加载歌单失败', error);
        this.setMessage('加载歌单失败', 'error');
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
        this.setMessage('创建歌单失败: ' + error.response.data.message, 'error');
        console.error('创建歌单失败', error);
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