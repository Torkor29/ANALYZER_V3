import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/download_report': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/filter_stats': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/status': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})


