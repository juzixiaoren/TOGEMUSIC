<template>
  <div class="playlist-detail">
    <el-card>
      <template #header>
        <div>{{ playlist?.playlist_name }}</div>
      </template>
      <el-button type="primary" @click="showImportDialog = true">导入歌曲</el-button>
      <el-button type="success" @click="addToPlayer">加入播放列表</el-button>
      <el-table :data="songs" style="width: 100%; margin-top: 20px;" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="title" label="歌名"></el-table-column>
        <el-table-column prop="artist" label="歌手"></el-table-column>
        <el-table-column prop="username" label="上传者"></el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button type="danger" @click="removeSong(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showImportDialog" title="导入歌曲" width="80%">
      <el-input v-model="searchQuery" placeholder="搜索歌名或歌手" style="margin-bottom: 20px;"></el-input>
      <el-select v-model="uploaderFilter" placeholder="按上传者筛选" style="margin-bottom: 20px;">
        <el-option label="全部" value=""></el-option>
        <el-option v-for="user in uniqueUploaders" :key="user" :label="user" :value="user"></el-option>
      </el-select>
      <el-table :data="filteredSongs" style="width: 100%;" @selection-change="handleImportSelectionChange" ref="importTable">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="title" label="歌名"></el-table-column>
        <el-table-column prop="artist" label="歌手"></el-table-column>
        <el-table-column prop="username" label="上传者"></el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importSongs">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMusicStore } from '../stores'
import http from '../utils/http'

const route = useRoute()
const musicStore = useMusicStore()

const playlist = ref(null)
const songs = ref([])
const allSongs = ref([])
const showImportDialog = ref(false)
const searchQuery = ref('')
const uploaderFilter = ref('')
const selectedSongs = ref([])
const importSelectedSongs = ref([])

const filteredSongs = computed(() => {
  return allSongs.value.filter(song => {
    const matchesSearch = song.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         song.artist.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesUploader = !uploaderFilter.value || song.username === uploaderFilter.value
    return matchesSearch && matchesUploader
  })
})

const uniqueUploaders = computed(() => {
  const uploaders = new Set(allSongs.value.map(song => song.username))
  return Array.from(uploaders)
})

const fetchPlaylist = async () => {
  try {
    const response = await http.get(`/reverse/playlists/${route.params.id}`)
    playlist.value = response.data.playlist
    songs.value = response.data.songs
  } catch (error) {
    console.error(error)
  }
}

const fetchAllSongs = async () => {
  try {
    const response = await http.get('/reverse/songs')
    allSongs.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const handleSelectionChange = (selection) => {
  selectedSongs.value = selection
}

const handleImportSelectionChange = (selection) => {
  importSelectedSongs.value = selection
}

const removeSong = async (songId) => {
  try {
    await http.delete(`/reverse/playlists/${route.params.id}/songs/${songId}`)
    fetchPlaylist()
  } catch (error) {
    console.error(error)
  }
}

const importSongs = async () => {
  try {
    const songIds = importSelectedSongs.value.map(song => song.id)
    await http.post(`/reverse/playlists/${route.params.id}/import`, { song_ids: songIds })
    showImportDialog.value = false
    fetchPlaylist()
  } catch (error) {
    console.error(error)
  }
}

const addToPlayer = () => {
  musicStore.setCurrentPlaylist(songs.value)
  // Navigate to player or show message
}

onMounted(() => {
  fetchPlaylist()
  fetchAllSongs()
})
</script>

<style scoped>
</style>