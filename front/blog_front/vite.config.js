import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import Components from 'unplugin-vue-components/vite'
import MotionResolver from 'motion-v/resolver'

// 与生产 Nginx 一致：页面请求 /geo/...，由服务端转到阿里云地图数据
const geoProxy = {
  '/geo': {
    target: 'https://geo.datav.aliyun.com',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/geo/, ''),
  },
}

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: geoProxy,
  },
  preview: {
    proxy: geoProxy,
  },
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
    Components({
      dts: true,
      resolvers: [
        MotionResolver()
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
