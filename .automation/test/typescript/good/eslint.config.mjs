import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import globals from 'globals';

export default defineConfig({
    files: ['**/*.ts'],
    plugins: {
        '@typescript-eslint': tseslint.plugin,
    },
    languageOptions: {
        parser: tseslint.parser,
        ecmaVersion: 2021,
        sourceType: 'module',
        globals: globals.browser,
    },
    rules: {},
});