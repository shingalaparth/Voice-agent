"use client";

import { useState } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";
import { CommandPalette } from "./command-palette";
import { useKeyShortcut } from "./use-key-shortcut";

/**
 * Authenticated app chrome: persistent sidebar + sticky topbar + content area.
 * The command palette is owned here so both the ⌘K shortcut and the topbar
 * search button drive a single source of truth.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  const [paletteOpen, setPaletteOpen] = useState(false);
  useKeyShortcut({ key: "k", meta: true }, () => setPaletteOpen((v) => !v));

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onOpenSearch={() => setPaletteOpen(true)} />
        <main className="flex-1 px-4 py-6 md:px-6 lg:px-8">{children}</main>
      </div>
      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
    </div>
  );
}
