import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function KnowledgePage() {
  return (
    <PlaceholderPage
      title="Knowledge Base"
      description="Documents your agents can reference during a call (RAG)."
      planned={[
        "Upload PDFs, docs, or paste text into knowledge sets",
        "Attach a knowledge set to one or more agents",
        "Per-chunk search preview so you can verify what the agent sees",
        "Version history and re-index on edit",
      ]}
    />
  );
}
