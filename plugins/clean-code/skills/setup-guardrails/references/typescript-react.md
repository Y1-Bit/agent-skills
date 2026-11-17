# TypeScript/React guardrails

Working reference: `kit/frontend/` (`npm run check`, `scripts/demo-violations.sh`).

1. **tsconfig**: strict + `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`,
   `noPropertyAccessFromIndexSignature`, `verbatimModuleSyntax`.
2. **ESLint flat config**: `strictTypeChecked` + `stylisticTypeChecked`;
   `linterOptions.noInlineConfig: true`; run with `--max-warnings 0`.
   - Size: complexity 6, sonarjs cognitive 8, max-lines-per-function 40, max-statements 15,
     max-params 3, max-depth 3, max-lines 250, no-nested-ternary.
   - Types: `consistent-type-assertions: never`, `no-non-null-assertion`, ban all ts-comments,
     `strict-boolean-expressions`, `switch-exhaustiveness-check`. Turn
     `non-nullable-type-assertion-style` off.
   - `no-restricted-syntax`: ban `useEffect` imports and `TryStatement` (override for
     `shared/api`), plus the **interface-width selector**: more than 10 operations (methods or
     function-typed properties; data fields do not count) on one interface, type literal or
     class body is an error. The selector is in `kit/frontend/eslint.config.js`. An override
     that sets `no-restricted-syntax` replaces the whole list, so spread the width selectors
     into every override.
   - Coupling: `import-x/max-dependencies` (12 imports per module, 20 in tests) from
     `eslint-plugin-import-x`; not in the kit, add it when a project has the plugin.
3. **eslint-plugin-boundaries** v7 with `boundaries/dependencies` policies:
   - internal relationships allowed;
   - `app → features|entities (fileInternalPath: index.ts) | shared`;
   - `features → entities (index.ts) | shared`;
   - `entities → shared`.

   For feature slices (`features/<feature>/{model,ui,adapters}` with `index.ts` as the only
   entry), see `references/design-rules.md`.
4. **Patterns**:
   - zod schemas with `.brand()` instead of casts;
   - `Result<T, AppError>` from one `request()` in `shared/api`;
   - discriminated-union UI state;
   - one ErrorBoundary.
5. **Tests**: vitest; mutation testing with Stryker (break below 80%).
6. **Existing codebase**: ESLint ≥ 9.24 `--suppress-rule <rule>` records today's violations of
   one rule in `eslint-suppressions.json`. Fixing a file removes its entries
   (`--prune-suppressions`). Never `--suppress-all` again to hide new violations.
