import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In production the React app is mounted at /browse/ inside the merged
// Sphinx site (see infra/deploy-site.sh and .github/workflows/deploy-site.yml).
// In dev it serves from the root of :3001, so `base` is conditional.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/browse/' : '/',

  plugins: [
    react({
      // The codebase still uses .js extensions for files that contain JSX.
      include: '**/*.{js,jsx}',
    }),
  ],

  // The codebase is full of JSX inside .js files. Tell esbuild (which runs
  // before plugin-react's Babel pass) to parse src/**/*.js as JSX.
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.[jt]sx?$/,
    exclude: [],
  },

  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },

  server: {
    port: 3002,
    host: true,
    open: false,
    strictPort: true,
  },

  build: {
    // deploy-site.sh / deploy-site.yml expect web/packages/app/build/* to exist.
    outDir: 'build',
    emptyOutDir: true,
    sourcemap: false,
    // Match the legacy CRA-with-rewire output paths so existing Sphinx
    // templates that reference /browse/static/{js,css}/main.{js,css} keep working.
    rollupOptions: {
      output: {
        entryFileNames: 'static/js/main.js',
        chunkFileNames: 'static/js/[name]-[hash].js',
        assetFileNames: (info) => {
          const name = info.name ?? '';
          if (name.endsWith('.css')) return 'static/css/main.css';
          if (/\.(woff2?|ttf|otf|eot)$/.test(name)) return 'static/fonts/[name][extname]';
          if (/\.(png|jpg|jpeg|gif|svg|ico)$/.test(name)) return 'static/media/[name][extname]';
          return 'static/[name][extname]';
        },
      },
    },
  },
}));
