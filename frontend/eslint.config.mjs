import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import eslintConfigPrettier from "eslint-config-prettier";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  eslintConfigPrettier,

  {
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "react/react-in-jsx-scope": "off",
    },
  },

  globalIgnores([
    ".next/**",
    "src/generated/api/endpoints/**",
    "src/generated/api/model/**",
    "next-env.d.ts",
  ]),
]);
