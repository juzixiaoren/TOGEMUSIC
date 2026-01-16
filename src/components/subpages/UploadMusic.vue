<template>
  <div class="background">
    <HeaderTopAfterLogin :userId="userId" @logout="logout" class="header-top"></HeaderTopAfterLogin>
    <div v-if="message" class="message-box" :class="messageType">
      {{ message }}
    </div>
    <div class="home-content">
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
  </div>
</template>

<script>
import axios from 'axios';
import jsmediatags from 'jsmediatags/dist/jsmediatags.min.js';
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';
export default {
  components: {
    HeaderTopAfterLogin
  },
  name: 'UploadMusic',
  data() {
    return {
      userId: localStorage.getItem('userId') || '未登录用户',
      files: [],
      uploading: false,
      message: "",
      messageType: "", // 用于存储消息类型
    };
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
          const nameGuess = this.smartParseFilename(file.name);
          
          const rawData = {
            file,
            name: file.name,
            title: nameGuess.title,   // 初始值：文件名猜测
            artist: nameGuess.artist, // 初始值：文件名猜测
            duration: '加载中...',
            durationSec: 0
          };
          
          // 2. 【关键步骤】推入数组，并立即获取 Vue 生成的“响应式对象”
          // push 返回的是新数组长度，我们需要取最后一个元素
          this.files.push(rawData);
          const reactiveFile = this.files[this.files.length - 1];

          // 3. 独立执行：获取时长 (使用原生 Audio，速度快)
          this.parseDuration(file, reactiveFile);

          // 4. 独立执行：获取标签 (使用 jsmediatags，速度稍慢)
          this.parseTags(file, reactiveFile);
        }
      }
    },

    // 辅助：智能文件名解析
    smartParseFilename(filename) {
      const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
      const parts = nameWithoutExt.split(/\s*[-–]\s*/); // 尝试按横杠分割
      if (parts.length >= 2) {
        return { artist: parts[0], title: parts[1] };
      }
      return { title: nameWithoutExt, artist: '' };
    },

    // 任务 A：只负责获取时长 (原生 Audio)
    parseDuration(file, targetObject) {
      const url = URL.createObjectURL(file);
      const audio = new Audio(url);
      
      audio.onloadedmetadata = () => {
        // 直接修改传入的 targetObject (它是响应式的，界面会立即变)
        targetObject.durationSec = audio.duration;
        targetObject.duration = this.formatDuration(audio.duration);
        URL.revokeObjectURL(url);
      };
      
      audio.onerror = () => {
        targetObject.duration = '未知';
      };
    },

    // 任务 B：只负责获取标签 (jsmediatags)
    parseTags(file, targetObject) {
      // 如果库没加载好，直接跳过
      if (!jsmediatags) return;

      jsmediatags.read(file, {
        onSuccess: (tag) => {
          const tags = tag.tags;
          // 只有当解析出有效内容时，才覆盖原本的文件名猜测
          if (tags.title) {
            targetObject.title = tags.title;
          }
          if (tags.artist) {
            targetObject.artist = tags.artist;
          }
        },
        onError: (error) => {
          console.warn('标签读取失败，保留原文件名:', error.type);
        }
      });
    },

    formatDuration(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
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
        // 使用用户可能修改过的 title 和 artist
        formData.append(`titles[${index}]`, fileData.title); 
        formData.append(`artists[${index}]`, fileData.artist || '未知艺术家');
        formData.append(`durations[${index}]`, fileData.durationSec ? Math.floor(fileData.durationSec * 1000) : 0);
      });
      try {
        await axios.post('/upload', formData, {
          headers: { Authorization: localStorage.getItem('token') }
        });
        this.setMessage('上传成功！', 'success');
        this.files = [];
      } catch (error) {
        alert('上传失败: ' + (error.response?.data?.message || error.message));
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