<template>
  <div class="upload-music">
    <el-card>
      <template #header>
        <div>上传音乐</div>
      </template>
      <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
        <input type="file" ref="fileInput" multiple accept="audio/*" @change="handleFileSelect" style="display: none">
        <el-button type="primary" @click="$refs.fileInput.click()">选择文件</el-button>
        <p>或拖拽文件到此处</p>
      </div>
      <div v-if="files.length > 0" class="file-list">
        <h3>待上传文件</h3>
        <el-table :data="files" style="width: 100%">
          <el-table-column prop="name" label="文件名" width="200"></el-table-column>
          <el-table-column label="默认歌名">
            <template #default="scope">
              <el-input v-model="scope.row.title" :placeholder="getDefaultTitle(scope.row)"></el-input>
            </template>
          </el-table-column>
          <el-table-column label="默认歌手">
            <template #default="scope">
              <el-input v-model="scope.row.artist" :placeholder="getDefaultArtist(scope.row)"></el-input>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="danger" @click="removeFile(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="success" @click="uploadFiles" :loading="uploading">上传</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import http from '../utils/http'

const files = ref([])
const uploading = ref(false)
const fileInput = ref()

const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

const handleDrop = (event) => {
  event.preventDefault()
  const droppedFiles = Array.from(event.dataTransfer.files)
  addFiles(droppedFiles)
}

const addFiles = (newFiles) => {
  newFiles.forEach(file => {
    if (file.type.startsWith('audio/')) {
      files.value.push({
        file,
        name: file.name,
        title: '',
        artist: ''
      })
    }
  })
}

const getDefaultTitle = (file) => {
  return file.name.replace(/\.[^/.]+$/, "")
}

const getDefaultArtist = (file) => {
  // 这里可以解析文件元数据，但前端无法直接解析，需要后端处理
  return '未知歌手'
}

const removeFile = (index) => {
  files.value.splice(index, 1)
}

const uploadFiles = async () => {
  if (files.value.length === 0) return

  uploading.value = true
  try {
    const formData = new FormData()
    files.value.forEach(item => {
      formData.append('files', item.file)
      formData.append('titles', item.title || getDefaultTitle(item))
      formData.append('artists', item.artist || getDefaultArtist(item))
    })

    await http.post('/reverse/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    files.value = []
    // Show success message
  } catch (error) {
    console.error(error)
    // Handle error
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed #d9d9d9;
  padding: 20px;
  text-align: center;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #409eff;
}

.file-list {
  margin-top: 20px;
}
</style>