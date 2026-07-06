"use client";

import { Command as CommandPrimitive } from "cmdk";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { NAV_ITEMS } from "@/lib/navigation";
import { cn } from "@/lib/utils";

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const router = useRouter();

  const go = (href: string) => {
    onOpenChange(false);
    router.push(href);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <CommandPrimitive
        loop
        label="Command Menu"
        className={cn(
          "relative z-10 w-full max-w-xl overflow-hidden rounded-xl border border-border bg-surface shadow-2xl",
          "[&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wide [&_[cmdk-group-heading]]:text-subtle",
          "[&_[cmdk-group]]:px-2 [&_[cmdk-group]]:pb-2",
          "[&_[cmdk-item]]:flex [&_[cmdk-item]]:cursor-pointer [&_[cmdk-item]]:items-center [&_[cmdk-item]]:gap-3 [&_[cmdk-item]]:rounded-md [&_[cmdk-item]]:px-3 [&_[cmdk-item]]:py-2 [&_[cmdk-item]]:text-sm [&_[cmdk-item]]:text-muted",
          "[&_[cmdk-item][data-selected=true]]:bg-surface-3 [&_[cmdk-item][data-selected=true]]:text-fg"
        )}
      >
        <div className="flex items-center gap-2 border-b border-border px-3">
          <Search className="size-4 text-subtle" />
          <CommandPrimitive.Input
            autoFocus
            placeholder="Search pages, agents, contacts…"
            className="h-12 flex-1 bg-transparent text-sm text-fg outline-none placeholder:text-subtle"
          />
        </div>
        <CommandPrimitive.List className="max-h-[60vh] overflow-y-auto p-2">
          <CommandPrimitive.Empty className="px-3 py-8 text-center text-sm text-muted">
            No results found.
          </CommandPrimitive.Empty>
          <CommandPrimitive.Group heading="Navigation">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <CommandPrimitive.Item
                  key={item.href}
                  value={`${item.label} ${item.href}`}
                  onSelect={() => go(item.href)}
                >
                  <Icon className="size-4 text-subtle" />
                  <span className="flex-1">{item.label}</span>
                  <span className="text-xs text-subtle">{item.href}</span>
                </CommandPrimitive.Item>
              );
            })}
          </CommandPrimitive.Group>
          <CommandPrimitive.Group heading="Actions">
            <CommandPrimitive.Item
              value="create new agent"
              onSelect={() => go("/agents/new")}
            >
              <span className="flex-1">Create new agent</span>
            </CommandPrimitive.Item>
            <CommandPrimitive.Item
              value="launch campaign"
              onSelect={() => go("/campaigns/new")}
            >
              <span className="flex-1">Launch a campaign</span>
            </CommandPrimitive.Item>
          </CommandPrimitive.Group>
        </CommandPrimitive.List>
      </CommandPrimitive>
    </div>
  );
}
