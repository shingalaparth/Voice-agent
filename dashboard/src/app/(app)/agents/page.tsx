import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function AgentsPage() {
  return (
    <PlaceholderPage
      title="AI Agents"
      description="Design and manage the voice agents that call your customers."
      planned={[
        "Agent gallery with status, voice, and last-used",
        "Create-from-template wizard (COD Confirmation, Reminder, NPS, Win-back)",
        "Inline system-prompt editor with variable tokens",
        "Voice picker with preview, language selector, and tools configuration",
        "Test sandbox: type or speak → see transcript and tool calls",
      ]}
    />
  );
}
