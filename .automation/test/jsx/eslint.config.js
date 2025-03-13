const reactPlugin = require('eslint-plugin-react');

module.exports = [
    {
        files: ['**/*.{js,mjs,cjs,jsx,mjsx,ts,tsx,mtsx}'],
        ...reactPlugin.configs.flat.recommended, // This is not a plugin object, but a shareable config object
    }
];