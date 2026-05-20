import { defineConfig } from 'eslint';

export default defineConfig([
    {
        files: ['**/*.jsx'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },
        },
    },
]);
