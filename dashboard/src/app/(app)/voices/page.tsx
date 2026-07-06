import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function VoicesPage() {
  return (
    <PlaceholderPage
      title="Voice Library"
      description="Browse, preview, and favorite voices across providers."
      planned={[
        "Card grid with name, provider, language flags, gender, and tags",
        "One-click preview using a fixed sample line",
        "Per-agent preview using that agent's actual greeting",
        "Favorites and a default voice for the workspace",
        "Filter by provider, language, gender, and tag",
      ]}
    />
  );
}
