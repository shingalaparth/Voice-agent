import Link from "next/link";
import { Logo } from "@/components/shell/logo";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Left: form */}
      <div className="flex flex-col justify-between p-8">
        <Logo href="/" />
        <div className="mx-auto w-full max-w-sm">{children}</div>
        <p className="text-center text-xs text-subtle">
          © {new Date().getFullYear()} Diorin
        </p>
      </div>

      {/* Right: brand panel */}
      <div className="relative hidden overflow-hidden bg-surface-2 lg:block">
        <div className="absolute inset-0 gradient-brand opacity-10" />
        <div className="absolute -left-20 top-1/4 size-96 rounded-full bg-brand opacity-20 blur-3xl" />
        <div className="absolute bottom-0 right-0 size-96 rounded-full bg-purple-500 opacity-20 blur-3xl" />
        <div className="relative flex h-full flex-col justify-center p-12">
          <blockquote className="max-w-md space-y-4">
            <p className="text-2xl font-medium leading-relaxed text-fg">
              “We confirmed 1,200 COD orders in a single afternoon — without
              hiring a single caller. The Hindi sounded completely natural.”
            </p>
            <footer className="text-sm text-muted">
              — E-commerce lead, Diorin pilot program
            </footer>
          </blockquote>
        </div>
      </div>
    </div>
  );
}
