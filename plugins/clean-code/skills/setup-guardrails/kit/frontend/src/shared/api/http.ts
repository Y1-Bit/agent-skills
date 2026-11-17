// The ONLY place that turns network failures and error responses into values.
// Everything above this layer receives Result<T, AppError> and never needs try/catch.
import { z } from "zod";

import { err, ok, type Result } from "@/shared/lib/result";

export type AppErrorKind =
  "invalid_value" | "not_found" | "conflict" | "rule_violation" | "network" | "unexpected";

export interface AppError {
  readonly kind: AppErrorKind;
  readonly message: string;
}

const errorBodySchema = z.object({
  error: z.object({
    code: z.enum(["invalid_value", "not_found", "conflict", "rule_violation"]),
    message: z.string(),
  }),
});

const unexpected = (message: string): AppError => ({ kind: "unexpected", message });

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  return text === "" ? null : JSON.parse(text);
}

function toAppError(body: unknown, status: number): AppError {
  const parsed = errorBodySchema.safeParse(body);
  return parsed.success
    ? { kind: parsed.data.error.code, message: parsed.data.error.message }
    : unexpected(`HTTP ${String(status)}`);
}

export async function request<T>(
  path: string,
  init: RequestInit,
  schema: z.ZodType<T>,
): Promise<Result<T, AppError>> {
  try {
    const response = await fetch(path, init);
    const body = await readJson(response);
    if (!response.ok) return err(toAppError(body, response.status));
    const parsed = schema.safeParse(body);
    return parsed.success ? ok(parsed.data) : err(unexpected("response did not match schema"));
  } catch {
    return err({ kind: "network", message: "network request failed" });
  }
}
