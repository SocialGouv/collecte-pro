import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    extensions: ['.mjs', '.js', '.mts', '.ts', '.jsx', '.tsx', '.json', '.vue'],
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['static/src/**/*.spec.{js,ts}'],
    exclude: ['**/node_modules/**', '**/staticfiles/**', '**/static/dist/**'],
    css: false,
  },
})
