import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  server: {
    port: 5173,
    hmr: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
