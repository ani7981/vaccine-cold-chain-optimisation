import { resolve } from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true
      },
      '/ws': {
        target: 'ws://127.0.0.1:8001',
        ws: true
      }
    }
  },
  build: {
    rollupOptions: {
      input: {
        index: resolve(import.meta.dirname, 'index.html'),
        landing: resolve(import.meta.dirname, 'landing.html'),
        overview: resolve(import.meta.dirname, 'overview.html'),
        shipments: resolve(import.meta.dirname, 'shipments.html'),
        shipment: resolve(import.meta.dirname, 'shipment.html'),
        map: resolve(import.meta.dirname, 'map.html'),
        problems: resolve(import.meta.dirname, 'problems.html'),
        problem: resolve(import.meta.dirname, 'problem.html'),
        history: resolve(import.meta.dirname, 'history.html'),
        fleet: resolve(import.meta.dirname, 'fleet.html'),
        technical: resolve(import.meta.dirname, 'technical.html'),
        settings: resolve(import.meta.dirname, 'settings.html'),
        syringe: resolve(import.meta.dirname, 'syringe.html'),
        syringe3d: resolve(import.meta.dirname, 'syringe-3d.html'),
      }
    }
  },
  plugins: [
    {
      name: 'html-rewrite',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (!req.url) return next();
          const parsedUrl = new URL(req.url, 'http://localhost:5173');
          let pathname = parsedUrl.pathname;
          
          if (pathname.startsWith('/@') || pathname.startsWith('/node_modules') || pathname.startsWith('/api')) {
            return next();
          }
          if (pathname === '/' || pathname === '/index' || pathname === '/index.html') {
            req.url = '/landing.html' + parsedUrl.search;
          } else if (pathname === '/problems' || pathname === '/problems/') {
            req.url = '/problems.html' + parsedUrl.search;
          } else if (pathname === '/shipments' || pathname === '/shipments/') {
            req.url = '/shipments.html' + parsedUrl.search;
          } else if (pathname.startsWith('/shipments/') && pathname.split('/')[2]) {
            const id = pathname.split('/')[2];
            req.url = `/shipment.html?id=${id}`;
          } else if (pathname.startsWith('/problems/') && pathname.split('/')[2]) {
            const id = pathname.split('/')[2];
            req.url = `/problem.html?id=${id}`;
          } else if (pathname === '/problem-detail' || pathname === '/problem-detail.html') {
            req.url = '/problem.html' + parsedUrl.search;
          } else if (pathname === '/shipment-detail' || pathname === '/shipment-detail.html') {
            req.url = '/shipment.html' + parsedUrl.search;
          } else if (!pathname.includes('.')) {
            req.url = `${pathname}.html` + parsedUrl.search;
          }
          next();
        });
      }
    }
  ]
});
