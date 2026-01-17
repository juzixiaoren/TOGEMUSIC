import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';

// 注意：axios 的 baseURL 已在 main.js 中配置
// 这里保持引入以便在路由守卫中使用

// 引入路由组件
import Home from '../components/subpages/Home.vue';
import Login from '../components/subpages/LandingPage.vue';
import Register from '../components/subpages/RegisterPage.vue';
import UploadMusic from '../components/subpages/UploadMusic.vue';
import Playlists from '../components/subpages/Playlists.vue';
import PlaylistDetail from '../components/subpages/PlaylistDetail.vue';
import Player from '../components/subpages/Player.vue';

// 定义路由
const routes = [
  {
    path: '/',
    redirect: '/Home', // 默认重定向到主页
  },
  {
    path: '/Login',
    component: Login,
  },
  {
    path: '/Register',
    component: Register,
  },
  {
    path: '/Home',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/UploadMusic',
    component: UploadMusic,
    meta: { requiresAuth: true },
  },
  {
    path: '/Playlists',
    component: Playlists,
    meta: { requiresAuth: true },
  },
  {
    path: '/Playlist/:id',
    component: PlaylistDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/Player',
    component: Player,
    meta: { requiresAuth: true },
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 导航守卫
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem("token"); // 获取 token
  const role = localStorage.getItem("role"); // 获取用户角色

  if (to.meta.requiresAuth) {
    if (!token) {
      // 如果没有 token，跳转到登录页面
      next({ path: "/Login" });
    } else {
      try {
        // 验证 token 是否有效
        await axios.get("/protected", {
          headers: { Authorization: token },
        });

        // 检查是否需要角色权限
        if (to.meta.roles && !to.meta.roles.includes(role)) {
          alert("您没有权限访问该页面");
          next(false); // 阻止跳转
        } else {
          next(); // 允许跳转
        }
      } catch (error) {
        console.error("Token 验证失败:", error);
        alert("您的账号已在其他设备登录，请重新登录");
        localStorage.removeItem("token"); // 清除无效的 token
        next({ path: "/Login" }); // 跳转到登录页面
      }
    }
  } else {
    next(); // 不需要登录的页面直接放行
  }
});

export default router;