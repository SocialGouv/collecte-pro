import neostandard from 'neostandard'
import pluginVue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import vitestPlugin from '@vitest/eslint-plugin'
import tsParser from '@typescript-eslint/parser'
import tsPlugin from '@typescript-eslint/eslint-plugin'

export default [
  {
    ignores: [
      'node_modules/**',
      'static/dist/**',
      'staticfiles/**',
      'static/src/utils/vuejs-datepicker-locale-fr.js',
    ],
  },

  // Base JavaScript Standard Style rules (flat-config successor to eslint-config-standard),
  // applied everywhere, including the <script> blocks of .vue files.
  ...neostandard({ env: ['browser', 'jquery'] }),

  // Vue 3 recommended rules.
  ...pluginVue.configs['flat/essential'],

  {
    // vue-eslint-parser handles .vue, .js and .ts alike, delegating <script> (or the whole
    // file, for non-.vue files) to the nested `parserOptions.parser` (the TypeScript parser).
    files: ['**/*.{js,ts,vue}'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 2018,
        sourceType: 'module',
        parser: tsParser,
      },
      globals: {
        assert: 'readonly',
        ...vitestPlugin.configs.env.languageOptions.globals,
      },
    },
    plugins: {
      '@typescript-eslint': tsPlugin,
      vitest: vitestPlugin,
    },
    rules: {
      ...vitestPlugin.configs.recommended.rules,
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
      'no-useless-return': 'off',
      '@stylistic/space-before-function-paren': 'off',
      '@stylistic/semi': 'off',
      'vitest/expect-expect': 'off',
      // Remove this rule to allow the non-breaking whitespace character (U+00A0) in a string template literal.
      'no-irregular-whitespace': ['error', { skipTemplates: true }],
      // Many existing identifiers mirror Django snake_case API field
      camelcase: 'warn',
      // Some components are intentionally single-word;
      'vue/multi-word-component-names': 'warn',
    },
  },
]
