import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    assetsDir: "django-assets",
    rollupOptions: {
      input: {
        app: resolve("./frontend/src/main.tsx"),
      },
    },
  },
  plugins: [tailwindcss()],
  test: {
    environment: "jsdom",
    exclude: [
      "**/node_modules/**",
      "**/.git/**",
      "**/.worktrees/**",
      "**/dist/**",
      "**/staticfiles/**",
    ],
    globals: true,
    setupFiles: [resolve("./frontend/src/test/setup.ts")],
  },
});
