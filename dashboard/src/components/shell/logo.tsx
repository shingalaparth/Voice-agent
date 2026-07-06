import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({
  className,
  href = "/dashboard",
  showText = true,
}: {
  className?: string;
  href?: string;
  showText?: boolean;
}) {
  return (
    <Link
      href={href}
      className={cn("flex items-center gap-2 font-semibold", className)}
    >
      <span className="flex size-7 items-center justify-center rounded-md gradient-brand text-white">
        <span className="text-sm font-bold">D</span>
      </span>
      {showText && (
        <span className="text-base tracking-tight text-fg">
          Diorin
          <span className="text-gradient-brand"> Voice</span>
        </span>
      )}
    </Link>
  );
}
