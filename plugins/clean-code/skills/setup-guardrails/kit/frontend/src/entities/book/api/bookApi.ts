import { z } from "zod";

import {
  bookIdSchema,
  bookSchema,
  type Book,
  type BookId,
  type CatalogBookInput,
} from "@/entities/book/model/book";
import { request, type AppError } from "@/shared/api";
import type { Result } from "@/shared/lib/result";

const JSON_HEADERS = { "Content-Type": "application/json" };

export function catalogBook(input: CatalogBookInput): Promise<Result<BookId, AppError>> {
  const body = JSON.stringify({
    title: input.title,
    short_title: input.shortTitle,
    isbn: input.isbn,
    country_code: input.countryCode,
    genre: input.genre,
    librarian_user_id: input.librarianUserId,
  });
  const schema = z.object({ id: bookIdSchema }).transform((data) => data.id);
  return request("/books", { method: "POST", headers: JSON_HEADERS, body }, schema);
}

export function getBook(id: BookId): Promise<Result<Book, AppError>> {
  return request(`/books/${id}`, { method: "GET" }, bookSchema);
}
