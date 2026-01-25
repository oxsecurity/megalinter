import globals from "globals";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";

const reactRecommendedRules = reactPlugin.configs?.recommended?.rules ?? {};

export default tseslint.config(
  {
    name: "ignores",
    ignores: ["**/node_modules/**", "**/dist/**"],
  },
  ...tseslint.configs.recommended,
  {
    name: "react-ts",
    files: [
      "**/*.{ts,tsx,js,jsx}",
      "**/*.{ts,tsx,js,jsx}.cjs",
      "**/*.{ts,tsx,js,jsx}.mjs",
    ],
    plugins: {
      react: reactPlugin,
    },
    languageOptions: {
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.es2021,
      },
    },
    settings: {
      react: { version: "detect" },
    },
    rules: {
      ...reactRecommendedRules,
    },
  }
);