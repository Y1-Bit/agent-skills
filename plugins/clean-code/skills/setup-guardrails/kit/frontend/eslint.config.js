// @ts-check
// Guardrails for agent-written TypeScript/React. Same philosophy as the Python kit:
// every correction you'd give an agent twice becomes a rule here.
import js from "@eslint/js";
import boundaries from "eslint-plugin-boundaries";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import sonarjs from "eslint-plugin-sonarjs";
import tseslint from "typescript-eslint";

// Layers (Feature-Sliced-Design-lite). A layer may import only from layers to its right:
// app → features → entities → shared. Slices are imported only through their index.ts.
const LAYERS = [
  { type: "app", pattern: "src/app" },
  { type: "features", pattern: "src/features/*", capture: ["slice"] },
  { type: "entities", pattern: "src/entities/*", capture: ["slice"] },
  { type: "shared", pattern: "src/shared/*", capture: ["segment"] },
];

const layer = (/** @type {string} */ type) => ({ element: { type } });
const publicApiOf = (/** @type {string[]} */ types) => ({
  element: { types, fileInternalPath: "index.ts" },
});

// Interface width: a type that offers more than 10 operations serves several consumers and must
// be split by consumer, not by size. ESLint has no width rule, so `no-restricted-syntax` flags the
// 11th sibling operation (method, or property typed as a function) of one interface, type literal
// or class body; data fields do not count.
const MAX_OPERATIONS = 10;
const operation = [
  "TSMethodSignature",
  'TSPropertySignature[typeAnnotation.typeAnnotation.type="TSFunctionType"]',
  'TSPropertySignature[typeAnnotation.typeAnnotation.types.0.type="TSFunctionType"]',
  'TSPropertySignature[typeAnnotation.typeAnnotation.types.1.type="TSFunctionType"]',
  'MethodDefinition[kind="method"][accessibility!="private"][accessibility!="protected"][key.type!="PrivateIdentifier"]',
  'PropertyDefinition[value.type="ArrowFunctionExpression"][accessibility!="private"][accessibility!="protected"][key.type!="PrivateIdentifier"]',
].join(", ");
const moreOperations = Array.from({ length: MAX_OPERATIONS + 1 }, () => `:matches(${operation})`);
const interfaceWidth = ["TSInterfaceBody", "TSTypeLiteral", "ClassBody"].map((body) => ({
  selector: `${body}:has(> ${moreOperations.join(" ~ ")})`,
  message: `More than ${String(MAX_OPERATIONS)} operations on one type: give each consumer its own narrow interface.`,
}));

export default tseslint.config(
  { ignores: ["dist", "node_modules", "examples", "coverage"] },

  {
    // No `// eslint-disable` escape hatches. Change this file in a reviewed PR instead.
    linterOptions: { noInlineConfig: true, reportUnusedDisableDirectives: "error" },
  },

  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      sonarjs,
      boundaries,
    },
    settings: {
      "boundaries/elements": LAYERS,
      "boundaries/include": ["src/**/*"],
      "import/resolver": { typescript: { project: "./tsconfig.json" } },
    },
    rules: {
      // ── size & complexity: one function = one idea ─────────────────────────
      complexity: ["error", 6],
      "sonarjs/cognitive-complexity": ["error", 8],
      "max-lines-per-function": ["error", { max: 40, skipBlankLines: true, skipComments: true }],
      "max-lines": ["error", { max: 250, skipBlankLines: true, skipComments: true }],
      "max-params": ["error", 3],
      "max-depth": ["error", 3],
      "max-nested-callbacks": ["error", 3],
      "max-statements": ["error", 15],
      "no-nested-ternary": "error",

      // ── types: no lying to the compiler ────────────────────────────────────
      "@typescript-eslint/consistent-type-assertions": ["error", { assertionStyle: "never" }],
      "@typescript-eslint/no-non-null-assertion": "error",
      "@typescript-eslint/non-nullable-type-assertion-style": "off", // would suggest `!`, which we ban
      "@typescript-eslint/ban-ts-comment": [
        "error",
        { "ts-expect-error": true, "ts-ignore": true, "ts-nocheck": true },
      ],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/strict-boolean-expressions": "error",
      "@typescript-eslint/switch-exhaustiveness-check": "error",
      "@typescript-eslint/explicit-module-boundary-types": "error",
      "@typescript-eslint/consistent-type-imports": "error",

      // ── react ──────────────────────────────────────────────────────────────
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "error",
      "no-restricted-syntax": [
        "error",
        {
          selector: "ImportSpecifier[imported.name='useEffect']",
          message:
            "useEffect is banned in product code. Derive state during render, react in event " +
            "handlers, or use a hook from shared/lib that wraps the effect once, correctly.",
        },
        {
          selector: "TryStatement",
          message:
            "No try/catch here. shared/api converts failures into Result values; " +
            "unexpected errors go to the app-level ErrorBoundary.",
        },
        ...interfaceWidth,
      ],
      "no-console": "error",

      // ── architecture ───────────────────────────────────────────────────────
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          message:
            "{{ from.element.types.[0] }} → {{ to.element.types.[0] }}: not allowed. " +
            "Layers: app → features → entities → shared; slices only via index.ts.",
          policies: [
            { allow: { dependency: { relationship: { to: "internal" } } } },
            {
              from: layer("app"),
              allow: [{ to: publicApiOf(["features", "entities"]) }, { to: layer("shared") }],
            },
            {
              from: layer("features"),
              allow: [{ to: publicApiOf(["entities"]) }, { to: layer("shared") }],
            },
            { from: layer("entities"), allow: { to: layer("shared") } },
            { from: layer("shared"), allow: { to: layer("shared") } },
          ],
        },
      ],
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            { group: ["../*"], message: "Use the @/ alias instead of parent-relative imports." },
          ],
        },
      ],
    },
  },

  // The boundary layers are the ONLY places allowed to do the things banned above.
  {
    files: ["src/shared/api/**/*.ts"],
    rules: { "no-restricted-syntax": ["error", ...interfaceWidth] },
  },
  {
    files: ["src/shared/lib/**/*.ts", "src/app/**/*.tsx"],
    rules: {
      "no-restricted-syntax": [
        "error",
        { selector: "TryStatement", message: "Handle errors via Result or the ErrorBoundary." },
        ...interfaceWidth,
      ],
    },
  },
  {
    files: ["**/*.test.ts", "**/*.test.tsx"],
    rules: { "max-lines-per-function": "off", "max-nested-callbacks": "off" },
  },
  {
    files: ["*.config.{js,ts}"],
    ...tseslint.configs.disableTypeChecked,
  },
);
