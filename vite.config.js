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
    port: 11451,
    proxy: {
      '/reverse': {
        target: 'http://localhost:19198', // 后端服务地址
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
