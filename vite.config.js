import { defineConfig } from 'vite';

export default defineConfig({
    root: 'apps/dashboard',
    build: {
        outDir: '../../dist',
        emptyOutDir: true
    }
});
