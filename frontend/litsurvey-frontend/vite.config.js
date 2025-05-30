import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/extract-info': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/upload_pdf': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/fetch_and_store': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/bibtex': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    }
  }
});
