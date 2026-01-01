<template>
  <div class="playlists">
    <el-card>
      <template #header>
        <div>歌单管理</div>
      </template>
      <el-button type="primary" @click="showCreateDialog = true">创建歌单</el-button>
      <el-table :data="playlists" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="playlist_name" label="歌单名"></el-table-column>
        <el-table-column prop="username" label="创建者"></el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button @click="$router.push(`/playlist/${scope.row.id}`)">查看</el-button>
            <el-button type="danger" @click="deletePlaylist(scope.row.id)" v-if="scope.row.creator_id === authStore.user.id">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" title="创建歌单">
      <el-form :model="createForm" :rules="rules" ref="createFormRef">
        <el-form-item label="歌单名" prop="name">
          <el-input v-model="createForm.name"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createPlaylist">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores'
import http from '../utils/http'

const authStore = useAuthStore()
const playlists = ref([])
const showCreateDialog = ref(false)
const createForm = ref({ name: '' })
const createFormRef = ref()

const rules = {
  name: [
    { required: true, message: '请输入歌单名', trigger: 'blur' }
  ]
}

const fetchPlaylists = async () => {
  try {
    const response = await http.get('/reverse/playlists')
    playlists.value = response.data
  } catch (error) {
    console.error(error)
  }
}

const createPlaylist = async () => {
  try {
    await createFormRef.value.validate()
    await http.post('/reverse/playlists', { name: createForm.value.name })
    showCreateDialog.value = false
    createForm.value.name = ''
    fetchPlaylists()
  } catch (error) {
    console.error(error)
  }
}

const deletePlaylist = async (id) => {
  try {
    await http.delete(`/reverse/playlists/${id}`)
    fetchPlaylists()
  } catch (error) {
    console.error(error)
  }
}

onMounted(fetchPlaylists)
</script>

<style scoped>
</style>