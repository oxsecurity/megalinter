const reactPlugin = require('eslint-plugin-react');

module.exports = [
  reactPlugin.configs.flat.recommended, // This is not a plugin object, but a shareable config object
];