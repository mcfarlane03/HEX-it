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
      '^/api': {
        target: 'http://127.0.0.1:8080', // Updated to match Flask backend
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: "app/static",
    emptyOutDir: true,
  },
  base: './', 
});