import Link from "next/link";
import { ArrowRight, Bot, PhoneCall, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/shell/logo";

export default function MarketingPage() {
  return (
    <div className="min-h-screen bg-bg">
      {/* Nav */}
      <header className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Logo href="/" />
        <nav className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/login">Log in</Link>
          </Button>
          <Button variant="primary" size="sm" asChild>
            <Link href="/signup">
              Start free
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </nav>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-24 pt-20 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted">
          <span className="size-1.5 rounded-full bg-[var(--color-success)]" />
          Now in beta
        </div>
        <h1 className="text-balance text-5xl font-semibold tracking-tight text-fg sm:text-6xl">
          AI voice agents that{" "}
          <span className="text-gradient-brand">actually call your customers</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-balance text-lg text-muted">
          Design a voice agent in minutes. Launch thousands of calls. Confirm
          COD orders, recover carts, and reactivate customers — in Hindi,
          English, or both.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Button variant="primary" size="lg" asChild>
            <Link href="/signup">
              Start free
              <ArrowRight className="size-4" />
            </Link>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <Link href="/dashboard">View live demo</Link>
          </Button>
        </div>
      </section>

      {/* Feature cards */}
      <section className="mx-auto grid max-w-5xl gap-4 px-6 pb-24 sm:grid-cols-3">
        <Feature
          icon={Bot}
          title="No-code agent builder"
          body="Pick a template, write your prompt, choose a voice. Test it on your own phone before going live."
        />
        <Feature
          icon={PhoneCall}
          title="Real outbound calling"
          body="Powered by LiveKit + SIP trunking. Your agent dials the customer and runs the conversation end-to-end."
        />
        <Feature
          icon={BarChart3}
          title="Confirmation analytics"
          body="See answer rate, confirmation rate, and retention success in real time. Drill into any call."
        />
      </section>

      <footer className="border-t border-border py-8 text-center text-sm text-muted">
        © {new Date().getFullYear()} Diorin. Built on LiveKit, Deepgram, Groq,
        and ElevenLabs.
      </footer>
    </div>
  );
}

function Feature({
  icon: Icon,
  title,
  body,
}: {
  icon: typeof Bot;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-6 text-left">
      <div className="mb-3 flex size-10 items-center justify-center rounded-md bg-surface-3 text-brand">
        <Icon className="size-5" />
      </div>
      <h3 className="mb-1 font-semibold text-fg">{title}</h3>
      <p className="text-sm text-muted">{body}</p>
    </div>
  );
}
