import * as React from "react";
import { cn } from "@/lib/utils";

export const Label = React.forwardRef<
  HTMLLabelElement,
  React.LabelHTMLAttributes<HTMLLabelElement>
>(({ className, ...props }, ref) => (
  <label
    ref={ref}
    className={cn(
      "text-sm font-medium leading-none text-fg peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
      className
    )}
    {...props}
  />
));
Label.displayName = "Label";

export function FieldHint({ children }: { children: React.ReactNode }) {
  return <p className="text-xs text-muted">{children}</p>;
}

export function FieldError({ children }: { children: React.ReactNode }) {
  return (
    <p className="flex items-center gap-1 text-xs text-[var(--color-danger)]">
      {children}
    </p>
  );
}
