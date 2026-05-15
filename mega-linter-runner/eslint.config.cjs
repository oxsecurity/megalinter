const { FlatCompat } = require('@eslint/eslintrc');
const js = require('@eslint/js');

const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: js.configs.recommended,
    allConfig: js.configs.all,
});

module.exports = [
    ...compat.config({
        env: {
            node: true,
            commonjs: true,
            es2021: true,
            mocha: true,
        },
        extends: 'eslint:recommended',
        parserOptions: {
            ecmaVersion: 2021,
            sourceType: 'module',
        },
        rules: {
            'no-unused-vars': ['error', { caughtErrors: 'none' }],
        },
    }),
];
