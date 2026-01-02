import { defineConfig } from 'vite'

export default defineConfig({
  // 使用相對 base，避免綁死 repo 名稱（GitHub Pages subpath 也可正常載入）
  base: './',
})
