<template>
  <div class="home">
    <el-container>
      <el-header>
        <el-menu :default-active="$route.path" class="el-menu-demo" mode="horizontal" @select="handleSelect">
          <el-menu-item index="/home">首页</el-menu-item>
          <el-menu-item index="/upload" v-if="authStore.isLoggedIn">上传音乐</el-menu-item>
          <el-menu-item index="/playlists" v-if="authStore.isLoggedIn">歌单管理</el-menu-item>
          <el-menu-item index="/player" v-if="authStore.isLoggedIn">播放房间</el-menu-item>
          <el-sub-menu index="user" v-if="authStore.isLoggedIn">
            <template #title>{{ authStore.user?.username }}</template>
            <el-menu-item index="logout">登出</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/login" v-else>登录</el-menu-item>
        </el-menu>
      </el-header>
      <el-main>
        <div v-if="!authStore.isLoggedIn">
          <h1>欢迎来到 TOGEMUSIC</h1>
          <p>多人在线听歌平台</p>
          <el-button type="primary" @click="$router.push('/login')">开始使用</el-button>
        </div>
        <div v-else>
          <h1>欢迎回来，{{ authStore.user?.username }}</h1>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card>
                <template #header>
                  <div>上传音乐</div>
                </template>
                <p>上传你的音乐文件</p>
                <el-button type="primary" @click="$router.push('/upload')">去上传</el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card>
                <template #header>
                  <div>歌单管理</div>
                </template>
                <p>创建和管理你的歌单</p>
                <el-button type="primary" @click="$router.push('/playlists')">去管理</el-button>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card>
                <template #header>
                  <div>播放房间</div>
                </template>
                <p>进入多人播放房间</p>
                <el-button type="primary" @click="$router.push('/player')">进入房间</el-button>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleSelect = (key) => {
  if (key === 'logout') {
    authStore.logout()
    router.push('/login')
  } else {
    router.push(key)
  }
}
</script>

<style scoped>
.home {
  height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: #fff;
}

.el-menu {
  border-bottom: none;
}

.el-main {
  padding: 20px;
}
</style>