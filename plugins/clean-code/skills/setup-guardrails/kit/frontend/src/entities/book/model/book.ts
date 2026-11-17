// Value objects as zod schemas with brands: once a value has the branded type,
// it has been validated. No `as` casts anywhere — the brand comes from parsing.
import { z } from "zod";

export const bookIdSchema = z
  .string()
  .regex(/^bk_[a-z0-9]{8,}$/, "must look like bk_<id>")
  .brand<"BookId">();

export const countryCodeSchema = z
  .string()
  .trim()
  .toUpperCase()
  .regex(/^[A-Z]{2}$/, "must be a 2-letter ISO code, e.g. DE")
  .brand<"CountryCode">();

const boundedText = (max: number) => z.string().trim().min(1, "must not be blank").max(max);

export const genreSchema = z.enum(["fiction", "science", "history"]);

export const bookStatusSchema = z.enum(["active", "withdrawn"]);

export const bookSchema = z.object({
  id: bookIdSchema,
  short_title: z.string(),
  country_code: countryCodeSchema,
  status: bookStatusSchema,
});

export const catalogBookInputSchema = z.object({
  title: boundedText(200),
  shortTitle: boundedText(80),
  isbn: z
    .string()
    .trim()
    .regex(/^97[89]\d{10}$/, "must be a 13-digit ISBN"),
  countryCode: countryCodeSchema,
  genre: genreSchema,
  librarianUserId: z.coerce.number().int().positive(),
});

export type BookId = z.infer<typeof bookIdSchema>;
export type CountryCode = z.infer<typeof countryCodeSchema>;
export type Genre = z.infer<typeof genreSchema>;
export type Book = z.infer<typeof bookSchema>;
export type CatalogBookInput = z.infer<typeof catalogBookInputSchema>;
