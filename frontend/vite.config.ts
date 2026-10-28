import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true, // le CORS de l'API n'autorise que ce port
    fs: {
      // les tilesets Kenney sont dans ../assets (partagés avec Tiled et l'API)
      allow: ['..'],
    },
  },
})
