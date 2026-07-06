"use client";

import { Bell, Menu, Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";

export function Topbar({ onOpenSearch }: { onOpenSearch: () => void }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-surface/80 px-4 backdrop-blur-md md:px-6">
      {/* Mobile menu (sidebar is hidden on md-) */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        aria-label="Open menu"
      >
        <Menu className="size-4" />
      </Button>

      {/* Search trigger */}
      <button
        onClick={onOpenSearch}
        className="group flex h-9 w-full max-w-md items-center gap-2 rounded-md border border-border bg-surface-2 px-3 text-sm text-subtle transition-colors hover:border-[var(--color-brand)] hover:text-muted"
      >
        <Search className="size-4" />
        <span className="flex-1 text-left">Search or jump to…</span>
        <kbd className="hidden rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-muted sm:inline-block">
          ⌘K
        </kbd>
      </button>

      <div className="ml-auto flex items-center gap-1">
        <Button variant="primary" size="sm" className="hidden sm:inline-flex">
          <Plus className="size-4" />
          New Agent
        </Button>
        <ThemeToggle />
        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="size-4" />
        </Button>
      </div>
    </header>
  );
}
