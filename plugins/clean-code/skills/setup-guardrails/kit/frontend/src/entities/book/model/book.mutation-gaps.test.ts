// Written because `npm run mutate` showed survivors despite green tests.
import { describe, expect, it } from "vitest";

import {
  countryCodeSchema,
  genreSchema,
  bookIdSchema,
  bookSchema,
  bookStatusSchema,
  catalogBookInputSchema,
} from "@/entities/book/model/book";

const firstMessage = (result: { error?: { issues: { message: string }[] } }): string | undefined =>
  result.error?.issues[0]?.message;

describe("bookIdSchema", () => {
  it.each(["bk_abcd1234", "bk_0123456789abcdef"])("accepts %s", (raw) => {
    expect(bookIdSchema.safeParse(raw).success).toBe(true);
  });

  it.each(["xbk_abcd1234", "bk_abcd1234!", "bk_abc", "bk_ABCD1234", "usr_abcd1234"])(
    "rejects %s",
    (raw) => {
      const result = bookIdSchema.safeParse(raw);
      expect(result.success).toBe(false);
      expect(firstMessage(result)).toBe("must look like bk_<id>");
    },
  );
});

it("country code error message is user-facing", () => {
  expect(firstMessage(countryCodeSchema.safeParse("D1"))).toBe(
    "must be a 2-letter ISO code, e.g. DE",
  );
});

it("blank text has a readable message", () => {
  const result = catalogBookInputSchema.shape.title.safeParse("  ");
  expect(firstMessage(result)).toBe("must not be blank");
});

it("enums list exactly the backend values", () => {
  expect(genreSchema.options).toEqual(["fiction", "science", "history"]);
  expect(bookStatusSchema.options).toEqual(["active", "withdrawn"]);
});

it("parses a backend book payload", () => {
  const payload = { id: "bk_abcd1234", short_title: "Dune", country_code: "de", status: "active" };
  expect(bookSchema.parse(payload)).toEqual({ ...payload, country_code: "DE" });
});
