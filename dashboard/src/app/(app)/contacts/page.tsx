import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function ContactsPage() {
  return (
    <PlaceholderPage
      title="Contacts"
      description="Your audience: contacts, lists, tags, and segments."
      planned={[
        "Import CSV/Excel or paste numbers with column mapping",
        "Dedupe preview and tag-on-import",
        "Segment by tag, list, or last-call outcome",
        "Per-contact detail with full call history",
        "Bulk tag, delete, or add to campaign",
      ]}
    />
  );
}
