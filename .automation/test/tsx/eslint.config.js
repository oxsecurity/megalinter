const reactPlugin = require('eslint-plugin-react');
const tsParser = require('@typescript-eslint/parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');

module.exports = [
    {
        files: ['**/*.{ts,tsx,mtsx,cts}'],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                ecmaVersion: 2022,
                sourceType: 'module',
                ecmaFeatures: { jsx: true },
            },
        },
        plugins: {
            react: reactPlugin,
            '@typescript-eslint': tsPlugin,
        },
        rules: {
            ...reactPlugin.configs.flat.recommended.rules,
            ...tsPlugin.configs.recommended.rules,
        },
        settings: { react: { version: 'detect' } },
    },
];
