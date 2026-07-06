import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function ApiKeysPage() {
  return (
    <PlaceholderPage
      title="API Keys"
      description="Programmatic access to the Diorin API."
      planned={[
        "Create scoped keys (read, write, calling, billing)",
        "One-time secret reveal with copy and confirmation gate",
        "Last-used tracking and per-key revocation",
        "Copy-paste code snippets for the most common calls",
      ]}
    />
  );
}
