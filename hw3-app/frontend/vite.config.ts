// import { defineConfig } from 'vite'
// import { svelte } from '@sveltejs/vite-plugin-svelte'

// // https://vite.dev/config/
// export default defineConfig(({ mode }) => ({
//   plugins: [svelte()],
//   server: mode === 'development' ? {
//     proxy: {
//       '/api': {
//         target: 'http://backend:8000',
//         changeOrigin: true,
//         secure: false,
//         configure: (proxy, options) => {
//           proxy.on('proxyReq', (proxyReq, req, res) => {
//             console.log('Proxying request:', req.url)
//           })
//         }
//       },
//     },
//   } : undefined,
// }))
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/me': 'http://localhost:8000',
      '/login': 'http://localhost:8000',
      '/logout': 'http://localhost:8000',
      '/authorize': 'http://localhost:8000',
    }
  }
});
