import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function IntegrationsPage() {
  return (
    <PlaceholderPage
      title="Integrations"
      description="Connect CRMs, messaging apps, and webhooks."
      planned={[
        "Catalog grid: Slack, HubSpot, Salesforce, Sheets, Zapier, Webhook",
        "OAuth or API-key connect flows per integration",
        "Field mapping and event selection",
        "Connected-state summary and disconnect",
      ]}
    />
  );
}
