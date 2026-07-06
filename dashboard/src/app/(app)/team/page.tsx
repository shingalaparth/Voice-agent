import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function TeamPage() {
  return (
    <PlaceholderPage
      title="Team"
      description="Invite teammates and manage roles."
      planned={[
        "Members table with role, status, and last-active",
        "Invite by email with a role picker (Admin, Operator, Author, Viewer)",
        "Role definitions and permissions matrix",
        "Remove or suspend members",
      ]}
    />
  );
}
