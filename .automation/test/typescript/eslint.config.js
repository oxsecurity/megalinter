import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    name: "ignores",
    ignores: ["**/node_modules/**", "**/dist/**"],
  },
  ...tseslint.configs.recommended,
  {
    name: "browser-ts",
    files: ["**/*.{ts,tsx,js}", "**/*.{ts,tsx,js}.cjs", "**/*.{ts,tsx,js}.mjs"],
    languageOptions: {
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
      },
      globals: {
        ...globals.browser,
        ...globals.es2021,
      },
    },
    rules: {},
  }
);