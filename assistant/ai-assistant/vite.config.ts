import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks for better caching
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select'],
          utils: ['lucide-react', 'clsx', 'tailwind-merge'],
        },
        // Optimize chunk size
        chunkSizeWarningLimit: 1000,
      },
    },
    // Increase chunk size limit and optimize
    chunkSizeWarningLimit: 1000,
    sourcemap: false, // Disable sourcemaps in production to save memory
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
  server: {
    // Optimize dev server memory usage
    hmr: {
      overlay: false, // Disable error overlay to save memory
    },
  },
})

