import * as React from "react";
import type { LucideIcon } from "lucide-react";
import { AlertTriangle, Inbox, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface StateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

function State({
  icon: Icon,
  title,
  description,
  action,
  className,
}: StateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border bg-surface-2 px-6 py-16 text-center",
        className
      )}
    >
      {Icon && (
        <div className="flex size-12 items-center justify-center rounded-full bg-surface-3 text-muted">
          <Icon className="size-6" />
        </div>
      )}
      <div className="space-y-1">
        <p className="text-base font-semibold text-fg">{title}</p>
        {description && (
          <p className="mx-auto max-w-sm text-sm text-muted">{description}</p>
        )}
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

export function EmptyState(props: StateProps) {
  return <State icon={props.icon ?? Inbox} {...props} />;
}

export function ErrorState({
  description = "Something went wrong. Please try again.",
  ...props
}: Omit<StateProps, "icon">) {
  return <State icon={AlertTriangle} description={description} {...props} />;
}

export function LoadingState({
  label = "Loading…",
  className,
}: {
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex items-center justify-center gap-2 rounded-lg border border-border bg-surface-2 px-6 py-16 text-sm text-muted",
        className
      )}
    >
      <Loader2 className="size-4 animate-spin" />
      {label}
    </div>
  );
}
