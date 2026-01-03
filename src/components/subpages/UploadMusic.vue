<template>
  <div class="upload-music">
    <h2>上传音乐</h2>
    <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
      <input type="file" ref="fileInput" multiple accept="audio/*" @change="handleFileSelect" style="display: none">
      <button @click="$refs.fileInput.click()">选择文件或拖拽上传</button>
      <p>支持 mp3, flac 等格式</p>
    </div>
    <div v-if="files.length > 0" class="file-list">
      <h3>上传文件列表</h3>
      <table>
        <thead>
          <tr>
            <th>文件名</th>
            <th>歌名</th>
            <th>歌手</th>
            <th>时长</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(file, index) in files" :key="index">
            <td>{{ file.name }}</td>
            <td><input v-model="file.title" placeholder="歌名"></td>
            <td><input v-model="file.artist" placeholder="歌手"></td>
            <td>{{ file.duration || '加载中...' }}</td>
            <td><button @click="removeFile(index)">删除</button></td>
          </tr>
        </tbody>
      </table>
      <button @click="uploadFiles" :disabled="uploading">确认上传</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UploadMusic',
  data() {
    return {
      files: [],
      uploading: false
    };
  },
  methods: {
    handleFileSelect(event) {
      this.addFiles(event.target.files);
    },
    handleDrop(event) {
      event.preventDefault();
      this.addFiles(event.dataTransfer.files);
    },
    addFiles(fileList) {
      for (let file of fileList) {
        if (file.type.startsWith('audio/')) {
          const fileData = {
            file,
            title: file.name.replace(/\.[^/.]+$/, ''), // 默认歌名
            artist: '', // 默认歌手，可从元数据获取
            duration: null,
            durationSec: null    // 秒数, 用于上传
          };
          this.getAudioMetadata(file).then(metadata => {
          fileData.artist = metadata.artist || '';
          fileData.durationSec = metadata.duration || 0;
          fileData.duration = metadata.duration ? this.formatDuration(metadata.duration) : '';
        });
          this.files.push(fileData);
        }
      }
    },
    getAudioMetadata(file) {
      return new Promise((resolve) => {
        const audio = new Audio(URL.createObjectURL(file));
        audio.onloadedmetadata = () => {
          resolve({ duration: audio.duration });
        };
        audio.onerror = () => resolve({});
      });
    },
    formatDuration(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    removeFile(index) {
      this.files.splice(index, 1);
    },
    async uploadFiles() {
      this.uploading = true;
      const formData = new FormData();
      this.files.forEach((fileData, index) => {
        formData.append('files', fileData.file);
        formData.append(`titles[${index}]`, fileData.title);
        formData.append(`artists[${index}]`, fileData.artist);
        formData.append(`durations[${index}]`, fileData.durationSec ? Math.floor(fileData.durationSec * 1000) : 0);
      });
      try {
        await axios.post('/upload', formData, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        alert('上传成功');
        this.files = [];
      } catch (error) {
        alert('上传失败: ' + error.response.data.message);
      }
      this.uploading = false;
    }
  }
};
</script>

<style scoped>
.upload-area {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
}
.file-list {
  margin-top: 20px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
}
</style>