import { fileURLToPath, URL } from 'url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  define: {
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
  },
  server: {
    proxy: {
      '^/api*': {
        target: 'http://localhost:5001/',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: "app/static",
    emptyOutDir: true,
  },
  base: './', 
});