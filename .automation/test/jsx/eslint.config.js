const react = require('eslint-plugin-react');

module.exports = {
    files: ['**/*.{js,jsx,mjs,cjs,ts,tsx}'],
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
