import js from "@eslint/js";
import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";

const browserGlobals = {
  console: "readonly",
  document: "readonly",
  window: "readonly",
  Node: "readonly",
};

export default [
  {
    ignores: ["dist/**"],
  },
  {
    files: ["frontend/src/**/*.js", "static/js/**/*.js"],
    ...js.configs.recommended,
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: browserGlobals,
    },
    rules: {
      ...js.configs.recommended.rules,
      "no-unused-vars": "off",
    },
  },
  {
    files: ["frontend/src/**/*.ts", "frontend/src/**/*.tsx"],
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
      ecmaVersion: "latest",
      sourceType: "module",
      globals: browserGlobals,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      "no-unused-vars": "off",
    },
  },
];
