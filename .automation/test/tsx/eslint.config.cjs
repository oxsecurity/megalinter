const tsParser = require('@typescript-eslint/parser');

module.exports = [
    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
                ecmaVersion: 12,
                sourceType: 'module',
            },
        },
        rules: {
            'no-var': 'error',
        },
    },
];
