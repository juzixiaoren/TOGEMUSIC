import './assets/main.css';
import { createApp } from 'vue';
import ArcoVue from '@arco-design/web-vue';
import App from './App.vue';
import '@arco-design/web-vue/dist/arco.css';
import axios from 'axios';
import router from './router/index.js'; // 引入路由配置文件

// 配置 axios 基础 URL
// 使用 /api 前缀，通过 Nginx (生产环境) 或 Vite (开发环境) 代理转发到后端
// 这样可以自动适配 http/https 协议，解决 Mixed Content 问题
axios.defaults.baseURL = '/api';

// 创建 Vue 应用实例
const app = createApp(App);
// 使用插件
app.use(ArcoVue);
app.use(router); // 正确注册路由

// 挂载应用
app.mount('#app');