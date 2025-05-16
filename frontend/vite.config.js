// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // if you really need a non-root base (e.g. GitHub Pages), tweak this; otherwise "/" is fine
  plugins: [react()],
  base: "/ecfr-analyzer/",
  server: {
    proxy: {
      // anything your client does to /api/... will get forwarded
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        // keep the /api prefix so it hits e.g. http://localhost:8000/api/search
        secure: false,
      },
    },
  },
  define: {
    __API__: JSON.stringify(
      process.env.NODE_ENV === 'production'
        ? 'https://legendary-halibut-pwwxp7xvwxwf995-8000.app.github.dev'
        : ''
    )
  }
});
