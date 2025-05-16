import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: '/ecfr-analyzer/',     // <‑‑ repo name
  server: { proxy: { '/api': 'http://localhost:8000' } },
  define: {
    __API__: JSON.stringify(
      process.env.NODE_ENV === 'production'
        ? 'https://legendary-halibut-pwwxp7xvwxwf995.github.dev'   // backend URL (step 2)
        : '/api'
    )
  }
});
