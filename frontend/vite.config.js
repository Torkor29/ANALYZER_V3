import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
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
