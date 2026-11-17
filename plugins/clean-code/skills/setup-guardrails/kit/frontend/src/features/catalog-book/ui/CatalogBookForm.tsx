import type { ReactElement, SyntheticEvent } from "react";

import {
  useCatalogBook,
  type FieldErrors,
  type CatalogState,
} from "@/features/catalog-book/model/useCatalogBook";

const FIELDS = [
  { name: "title", label: "Title" },
  { name: "shortTitle", label: "Short title" },
  { name: "isbn", label: "ISBN" },
  { name: "countryCode", label: "Country (ISO)" },
  { name: "librarianUserId", label: "Librarian user id" },
] as const;

function Field(props: { name: string; label: string; error: string | undefined }): ReactElement {
  return (
    <label>
      {props.label}
      <input name={props.name} aria-invalid={props.error !== undefined} />
      {props.error !== undefined && <small role="alert">{props.error}</small>}
    </label>
  );
}

function StatusLine({ state }: { state: CatalogState }): ReactElement | null {
  switch (state.status) {
    case "cataloged":
      return <p>Cataloged: {state.bookId}</p>;
    case "failed":
      return <p role="alert">{state.error.message}</p>;
    case "idle":
    case "invalid":
    case "submitting":
      return null;
  }
}

export function CatalogBookForm(): ReactElement {
  const { state, submit } = useCatalogBook();
  const fieldErrors: FieldErrors = state.status === "invalid" ? state.fieldErrors : {};

  function onSubmit(event: SyntheticEvent<HTMLFormElement>): void {
    event.preventDefault();
    void submit(Object.fromEntries(new FormData(event.currentTarget)));
  }

  return (
    <form onSubmit={onSubmit}>
      {FIELDS.map((field) => (
        <Field key={field.name} {...field} error={fieldErrors[field.name]} />
      ))}
      <select name="genre" defaultValue="science">
        <option value="fiction">Fiction</option>
        <option value="science">Science</option>
        <option value="history">History</option>
      </select>
      <button type="submit" disabled={state.status === "submitting"}>
        Add to catalog
      </button>
      <StatusLine state={state} />
    </form>
  );
}
