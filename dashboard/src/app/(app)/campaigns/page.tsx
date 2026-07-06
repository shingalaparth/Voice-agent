import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function CampaignsPage() {
  return (
    <PlaceholderPage
      title="Call Campaigns"
      description="Launch and monitor batch outbound calling."
      planned={[
        "Campaign list with status, progress, answer rate, and confirmation rate",
        "Four-step launch wizard: agent → audience → schedule → review",
        "Live monitor with streaming feed, queue depth, and outcome donut",
        "Pause, resume, stop, duplicate, and archive",
        "Funnel view: dialed → answered → confirmed",
      ]}
    />
  );
}
