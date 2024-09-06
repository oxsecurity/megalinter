const react = require('eslint-plugin-react');
const globals = require('globals');

module.exports = {
    files: ['**/*.{js,jsx,mjs,cjs,ts,tsx}'],
    env: {
        browser: true,
        es2021: true
    },
    globals: {
        ...globals.browser,
      },
    extends: [
        "eslint:recommended",
        "plugin:react/recommended"
    ],
    parserOptions: {
        ecmaFeatures: {
            jsx: true
        },
        ecmaVersion: 12,
        sourceType: "module"
    },
    plugins: [
        react
    ],
    rules: {
    }
}
