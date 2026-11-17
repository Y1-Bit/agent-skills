import { describe, expect, it } from "vitest";

import { countryCodeSchema, catalogBookInputSchema } from "@/entities/book/model/book";

describe("countryCodeSchema", () => {
  it("normalises case and whitespace", () => {
    expect(countryCodeSchema.parse(" de ")).toBe("DE");
  });

  it.each(["DEU", "D1", ""])("rejects %j", (raw) => {
    expect(countryCodeSchema.safeParse(raw).success).toBe(false);
  });
});

describe("catalogBookInputSchema", () => {
  const valid = {
    title: "Dune",
    shortTitle: "Dune",
    isbn: "9780441013593",
    countryCode: "de",
    genre: "science",
    librarianUserId: "7",
  };

  it("parses form-like input into domain values", () => {
    const parsed = catalogBookInputSchema.parse(valid);
    expect(parsed.librarianUserId).toBe(7);
    expect(parsed.countryCode).toBe("DE");
  });

  it.each(["0441013597", "9770441013593", "978044101359X"])("rejects the ISBN %j", (isbn) => {
    const result = catalogBookInputSchema.safeParse({ ...valid, isbn });
    expect(result.error?.issues[0]?.message).toBe("must be a 13-digit ISBN");
  });

  it("reports the failing field", () => {
    const result = catalogBookInputSchema.safeParse({ ...valid, title: "   " });
    expect(result.error?.issues[0]?.path).toEqual(["title"]);
  });
});
