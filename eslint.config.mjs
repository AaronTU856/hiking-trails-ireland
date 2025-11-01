import js from "@eslint/js";
import globals from "globals";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: {
      globals: {
        ...globals.browser,   // gives you window, document, fetch, etc.
        L: "readonly",         // Leaflet
        bootstrap: "readonly", // Bootstrap JS
        console: "readonly",   // prevent console from erroring
      },
    },
  },
]);
