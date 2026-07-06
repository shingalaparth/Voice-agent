import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function CallsPage() {
  return (
    <PlaceholderPage
      title="Call History"
      description="Every call your agents have made, with transcripts and recordings."
      planned={[
        "Virtualized table for 100k+ rows: time, contact, agent, outcome, duration",
        "Filters: date range, agent, campaign, outcome, duration",
        "Full-text search across transcripts",
        "Detail drawer: transcript timeline synced to audio waveform",
        "Tool-call markers, sentiment, cost, and retry",
      ]}
    />
  );
}
