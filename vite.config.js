import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
    root: 'apps/dashboard',
    build: {
        outDir: '../../dist',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'apps/dashboard/index.html'),
                about: resolve(__dirname, 'apps/dashboard/about.html')
            }
        }
    }
});
