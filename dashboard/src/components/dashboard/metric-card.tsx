import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  delta?: number; // percentage change vs. previous period
  icon?: LucideIcon;
  className?: string;
}

export function MetricCard({
  label,
  value,
  delta,
  icon: Icon,
  className,
}: MetricCardProps) {
  const positive = (delta ?? 0) >= 0;
  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted">{label}</p>
        {Icon && (
          <Icon className="size-4 text-subtle" />
        )}
      </div>
      <div className="mt-2 flex items-end justify-between gap-2">
        <span className="text-2xl font-semibold tracking-tight text-fg">
          {value}
        </span>
        {delta !== undefined && (
          <span
            className={cn(
              "flex items-center gap-0.5 text-xs font-medium",
              positive ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"
            )}
          >
            {positive ? (
              <ArrowUpRight className="size-3" />
            ) : (
              <ArrowDownRight className="size-3" />
            )}
            {Math.abs(delta)}%
          </span>
        )}
      </div>
    </Card>
  );
}
