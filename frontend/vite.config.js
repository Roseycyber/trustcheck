import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxies /api to the local FastAPI server during development so the
// frontend can call relative paths without CORS headaches.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
