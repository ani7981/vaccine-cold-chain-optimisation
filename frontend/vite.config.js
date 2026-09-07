import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173
  },
  plugins: [
    {
      name: 'html-rewrite',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (!req.url) return next();
          const parsedUrl = new URL(req.url, 'http://localhost:5173');
          let pathname = parsedUrl.pathname;
          
          if (pathname === '/') {
            req.url = '/landing.html' + parsedUrl.search;
          } else if (!pathname.includes('.')) {
            if (pathname.startsWith('/shipments/')) {
              const id = pathname.split('/')[2];
              req.url = `/shipment.html?id=${id}`;
            } else if (pathname.startsWith('/problems/')) {
              const id = pathname.split('/')[2];
              req.url = `/problem.html?id=${id}`;
            } else {
              req.url = `${pathname}.html` + parsedUrl.search;
            }
          }
          next();
        });
      }
    }
  ]
});
