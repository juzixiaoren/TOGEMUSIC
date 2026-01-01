import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';
import Home from '../components/Home.vue';
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import UploadMusic from '../components/UploadMusic.vue';
import Playlists from '../components/Playlists.vue';
import PlaylistDetail from '../components/PlaylistDetail.vue';
import PlayerRoom from '../components/PlayerRoom.vue';

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    component: Home
  },
  {
    path: '/login',
    component: Login
  },
  {
    path: '/register',
    component: Register
  },
  {
    path: '/upload',
    component: UploadMusic,
    meta: { requiresAuth: true }
  },
  {
    path: '/playlists',
    component: Playlists,
    meta: { requiresAuth: true }
  },
  {
    path: '/playlist/:id',
    component: PlaylistDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/player',
    component: PlayerRoom,
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;