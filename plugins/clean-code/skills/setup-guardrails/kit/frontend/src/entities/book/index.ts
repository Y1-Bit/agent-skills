// Public API of the slice. Other layers import ONLY from here (enforced by boundaries/entry-point).
export { getBook, catalogBook } from "@/entities/book/api/bookApi";
export {
  genreSchema,
  catalogBookInputSchema,
  type CountryCode,
  type Genre,
  type Book,
  type BookId,
  type CatalogBookInput,
} from "@/entities/book/model/book";
