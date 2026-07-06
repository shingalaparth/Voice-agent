import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function AnalyticsPage() {
  return (
    <PlaceholderPage
      title="Analytics"
      description="Trends and performance across agents, campaigns, and time."
      planned={[
        "KPIs: total calls, answer rate, confirmation rate, AI success rate",
        "Daily-trend stacked area (answered vs. not)",
        "Campaign comparison table and agent performance breakdown",
        "Drill-down from any chart into filtered Call History",
        "Saved views and CSV/PNG export",
      ]}
    />
  );
}
