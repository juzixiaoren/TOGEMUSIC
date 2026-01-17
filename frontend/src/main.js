import './assets/main.css';
import { createApp } from 'vue';
import ArcoVue from '@arco-design/web-vue';
import App from './App.vue';
import '@arco-design/web-vue/dist/arco.css';
import axios from 'axios';
import router from './router/index.js'; // 引入路由配置文件

// 配置 axios 基础 URL
// Docker 环境中通过服务名访问，本地开发通过 localhost:8034
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
axios.defaults.baseURL = isLocalhost ? 'http://localhost:8034' : 'http://backend:8034';

// 创建 Vue 应用实例
const app = createApp(App);
// 使用插件
app.use(ArcoVue);
app.use(router); // 正确注册路由

// 挂载应用
app.mount('#app');