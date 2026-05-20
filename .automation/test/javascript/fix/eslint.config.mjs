import { defineConfig } from 'eslint';
import js from '@eslint/js';
import globals from 'globals';

export default defineConfig({
    files: ['**/*.js'],
    languageOptions: {
        ecmaVersion: 2021,
        sourceType: 'commonjs',
        globals: {
            ...globals.node,
            ...globals.commonjs,
        },
    },
    rules: {
        ...js.configs.recommended.rules,
    },
});
