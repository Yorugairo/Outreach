import {defineConfig} from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {dedupe: ['react', 'react-dom', 'remotion']},
  server: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
    fs: {allow: ['..']},
    proxy: {
      '/api': 'http://127.0.0.1:4317',
      '/media': 'http://127.0.0.1:4317',
    },
  },
  preview: {host: '127.0.0.1', port: 4173, strictPort: true},
  test: {environment: 'jsdom'},
});
