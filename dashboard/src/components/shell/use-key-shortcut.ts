"use client";

import { useEffect } from "react";

/**
 * Subscribe to a keyboard shortcut globally.
 * @example useKeyShortcut({ key: "k", meta: true }, () => setOpen(true))
 */
export function useKeyShortcut(
  combo: { key: string; meta?: boolean; ctrl?: boolean; shift?: boolean },
  handler: () => void
) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const metaOk = combo.meta ? e.metaKey || e.ctrlKey : true;
      const ctrlOk = combo.ctrl ? e.ctrlKey : true;
      const shiftOk = combo.shift ? e.shiftKey : true;
      if (
        e.key.toLowerCase() === combo.key.toLowerCase() &&
        metaOk &&
        ctrlOk &&
        shiftOk
      ) {
        e.preventDefault();
        handler();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [combo.key, combo.meta, combo.ctrl, combo.shift, handler]);
}
