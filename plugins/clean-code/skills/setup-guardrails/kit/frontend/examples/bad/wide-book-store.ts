// Typical agent output: one "service" type that every screen reads a different slice of.
export interface BookStore {
  load(): Promise<void>;
  reload(): Promise<void>;
  findById(id: string): string | undefined;
  search(query: string): readonly string[];
  catalog(title: string): Promise<void>;
  withdraw(id: string): Promise<void>;
  rename(id: string, title: string): Promise<void>;
  exportCsv(): string;
  subscribe(listener: () => void): () => void;
  reset(): void;
  formatForList(id: string): string;
}
