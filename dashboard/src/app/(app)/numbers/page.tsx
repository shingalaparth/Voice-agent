import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function NumbersPage() {
  return (
    <PlaceholderPage
      title="Phone Numbers"
      description="Buy, port, and assign the phone numbers your agents call from."
      planned={[
        "Search and purchase DIDs by country and feature",
        "Port an existing number through a guided multi-step flow",
        "Assign a number to an agent or campaign",
        "Release or transfer numbers",
      ]}
    />
  );
}
