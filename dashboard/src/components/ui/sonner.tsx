"use client";

import { useTheme } from "next-themes";
import { Toaster as SonnerToaster } from "sonner";

export function Toaster() {
  const { theme } = useTheme();
  return (
    <SonnerToaster
      theme={(theme as "light" | "dark" | "system") ?? "system"}
      position="bottom-right"
      richColors
      closeButton
      toastOptions={{
        classNames: {
          toast: "font-sans text-sm",
        },
      }}
    />
  );
}

export { toast } from "sonner";
