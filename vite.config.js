import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/reverse': {
        target: 'http://localhost:5000', // 后端服务地址
        changeOrigin: true,
        pathRewrite: { '^/reverse': '' },
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
