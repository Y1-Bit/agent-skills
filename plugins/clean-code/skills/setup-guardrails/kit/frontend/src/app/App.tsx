import type { ReactElement } from "react";

import { ErrorBoundary } from "@/app/ErrorBoundary";
import { CatalogBookForm } from "@/features/catalog-book";

function reportError(error: unknown): void {
  // Plug Sentry/OpenTelemetry here. The one sanctioned place to report crashes.
  globalThis.reportError(error);
}

export function App(): ReactElement {
  return (
    <ErrorBoundary onError={reportError}>
      <CatalogBookForm />
    </ErrorBoundary>
  );
}
