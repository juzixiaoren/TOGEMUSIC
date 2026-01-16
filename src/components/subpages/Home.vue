<template>
  <div class="background">
    <HeaderTopAfterLogin :userId="userId" @logout="logout" class="header-top"></HeaderTopAfterLogin>
    <div v-if="message" class="message-box" :class="messageType">
      {{ message }}
    </div>
    <div class="home-content">
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
  </div>
</template>

<script>
import axios from 'axios';
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';
export default {
  name: 'Home',
  data() {
    return {
      userId: localStorage.getItem('userId') || '未登录用户',
      recentSongs: [],
      message: "",
      messageType: "", // 用于存储消息类型
    };
  },
  components: {
    HeaderTopAfterLogin
  },
  async mounted() {
    await this.loadRecentSongs();
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
    async loadRecentSongs() {
      try {
        const response = await axios.get('/songs?limit=10', {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.recentSongs = response.data;
      } catch (error) {
        this.setMessage('加载最近歌曲失败', 'error');
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