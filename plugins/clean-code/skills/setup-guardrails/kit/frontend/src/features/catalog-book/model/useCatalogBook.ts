// State is a discriminated union, not a bag of booleans (isLoading + isError + data
// can't contradict each other). Work happens in the event handler, not in useEffect.
import { useState } from "react";

import { catalogBook, catalogBookInputSchema, type BookId } from "@/entities/book";
import type { AppError } from "@/shared/api";

export type FieldErrors = Partial<Record<string, string>>;

export type CatalogState =
  | { readonly status: "idle" }
  | { readonly status: "invalid"; readonly fieldErrors: FieldErrors }
  | { readonly status: "submitting" }
  | { readonly status: "failed"; readonly error: AppError }
  | { readonly status: "cataloged"; readonly bookId: BookId };

function collectFieldErrors(
  issues: readonly { path: PropertyKey[]; message: string }[],
): FieldErrors {
  return Object.fromEntries(issues.map((issue) => [String(issue.path[0]), issue.message]));
}

export function useCatalogBook(): {
  state: CatalogState;
  submit: (raw: Record<string, unknown>) => Promise<void>;
} {
  const [state, setState] = useState<CatalogState>({ status: "idle" });

  async function submit(raw: Record<string, unknown>): Promise<void> {
    const parsed = catalogBookInputSchema.safeParse(raw);
    if (!parsed.success) {
      setState({ status: "invalid", fieldErrors: collectFieldErrors(parsed.error.issues) });
      return;
    }
    setState({ status: "submitting" });
    const result = await catalogBook(parsed.data);
    setState(
      result.ok
        ? { status: "cataloged", bookId: result.value }
        : { status: "failed", error: result.error },
    );
  }

  return { state, submit };
}
