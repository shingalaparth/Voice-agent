import { Construction } from "lucide-react";
import { PageHeader } from "./page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PlaceholderPageProps {
  title: string;
  description: string;
  /** What this page will contain once implemented. */
  planned: string[];
}

/**
 * M0 stand-in for every sidebar destination other than /dashboard.
 * Replaced with real implementations in milestones M1–M5.
 */
export function PlaceholderPage({
  title,
  description,
  planned,
}: PlaceholderPageProps) {
  return (
    <>
      <PageHeader
        title={title}
        description={description}
        actions={<Badge variant="brand">M0 · Coming soon</Badge>}
      />
      <Card className="p-8">
        <div className="mb-4 flex size-12 items-center justify-center rounded-full bg-surface-3 text-brand">
          <Construction className="size-6" />
        </div>
        <h2 className="text-lg font-semibold text-fg">
          This page is part of the next milestone
        </h2>
        <p className="mt-1 max-w-xl text-sm text-muted">
          The foundation shell is in place. This screen gets its real content in
          an upcoming milestone of the implementation roadmap.
        </p>
        <div className="mt-6">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-subtle">
            Planned
          </p>
          <ul className="space-y-1.5">
            {planned.map((item) => (
              <li key={item} className="flex items-start gap-2 text-sm text-muted">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-brand" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </Card>
    </>
  );
}
