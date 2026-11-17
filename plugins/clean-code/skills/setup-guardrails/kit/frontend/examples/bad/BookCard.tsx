// TYPICAL AGENT OUTPUT — negative example.
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState, type ReactElement } from "react";

import { getBook } from "@/entities/book/api/bookApi";
import type { Book } from "@/entities/book";

export function BookCard(props: {
  id: string;
  showStatus: boolean;
  compact: boolean;
  onLoad: () => void;
}): ReactElement {
  const [book, setBook] = useState<Book | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  useEffect(() => {
    async function load(): Promise<void> {
      try {
        // @ts-ignore
        const res = await getBook(props.id);
        if (res.ok) {
          setBook(res.value);
          props.onLoad();
        } else {
          console.log("failed", res.error);
          setIsError(true);
        }
      } catch (e) {
        setIsError(true);
      } finally {
        setIsLoading(false);
      }
    }
    void load();
  }, [props.id]);
  const data = book as Book;
  if (isLoading) return <p>Loading</p>;
  if (isError) return <p>Error</p>;
  return (
    <div>
      {props.compact
        ? data.id
        : props.showStatus
          ? `${data.short_title} (${data.status})`
          : data.short_title}
    </div>
  );
}
