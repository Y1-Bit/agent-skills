#!/usr/bin/env bash
# Copies the negative examples into src/, lints them, then removes them again.
set -uo pipefail
cd "$(dirname "$0")/.."
mkdir -p src/features/book-card/ui
cp examples/bad/BookCard.tsx src/features/book-card/ui/BookCard.tsx
cp examples/bad/entities-book-model-leak.ts src/entities/book/model/leak.ts
cp examples/bad/wide-book-store.ts src/entities/book/model/wide.ts
trap 'rm -rf src/features/book-card src/entities/book/model/leak.ts src/entities/book/model/wide.ts' EXIT
npx eslint src/features/book-card src/entities/book/model/leak.ts src/entities/book/model/wide.ts --max-warnings 0
exit 0
