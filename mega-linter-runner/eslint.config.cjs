const { FlatCompat } = require('@eslint/eslintrc');
const js = require('@eslint/js');

// Newer versions of @eslint/js include a 'name' property in their config objects,
// which is valid in flat config but causes FlatCompat's legacy eslintrc validator
// to reject the config with "Unexpected top-level property 'name'".
// Strip it before passing to FlatCompat to maintain compatibility.
const stripFlatConfigOnly = ({ name: _n, ...cfg }) => cfg;

const compat = new FlatCompat({
    baseDirectory: __dirname,
    recommendedConfig: stripFlatConfigOnly(js.configs.recommended),
    allConfig: stripFlatConfigOnly(js.configs.all),
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
