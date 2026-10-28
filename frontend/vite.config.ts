import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // the API's CORS only allows this port
    fs: {
      // the Kenney tilesets are in ../assets (shared with Tiled and the API)
      allow: ['..'],
    },
  },
})
