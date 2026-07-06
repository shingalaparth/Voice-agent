import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        neutral:
          "border-border bg-surface-3 text-muted",
        brand:
          "border-transparent bg-[color-mix(in_oklab,var(--color-brand)_15%,transparent)] text-brand",
        success:
          "border-[var(--color-success-border)] bg-[var(--color-success-bg)] text-[var(--color-success)]",
        warning:
          "border-[var(--color-warning-border)] bg-[var(--color-warning-bg)] text-[var(--color-warning)]",
        danger:
          "border-[var(--color-danger-border)] bg-[var(--color-danger-bg)] text-[var(--color-danger)]",
        info:
          "border-[var(--color-info-border)] bg-[var(--color-info-bg)] text-[var(--color-info)]",
      },
    },
    defaultVariants: { variant: "neutral" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
