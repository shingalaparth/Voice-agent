import Link from "next/link";
import {
  ArrowRight,
  Megaphone,
  PhoneCall,
  CheckCircle2,
  Activity,
  Plus,
} from "lucide-react";
import { PageHeader } from "@/components/shell/page-header";
import { MetricCard } from "@/components/dashboard/metric-card";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/states";

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Dashboard"
        description="What's happening across your workspace today."
        actions={
          <Button variant="primary" size="sm" asChild>
            <Link href="/campaigns/new">
              <Plus className="size-4" />
              New campaign
            </Link>
          </Button>
        }
      />

      {/* KPI row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Calls today" value="0" delta={0} icon={PhoneCall} />
        <MetricCard label="Answer rate" value="—" icon={Activity} />
        <MetricCard label="Confirmation rate" value="—" icon={CheckCircle2} />
        <MetricCard label="Active campaigns" value="0" icon={Megaphone} />
      </div>

      {/* Active campaigns */}
      <section className="mt-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-medium text-muted">Active campaigns</h2>
          <Link
            href="/campaigns"
            className="flex items-center gap-1 text-xs text-brand hover:underline"
          >
            View all <ArrowRight className="size-3" />
          </Link>
        </div>
        <EmptyState
          title="No active campaigns yet"
          description="Launch your first campaign to start confirming COD orders, recovering carts, or reactivating customers."
          action={
            <Button variant="primary" size="sm" asChild>
              <Link href="/campaigns/new">
                <Plus className="size-4" />
                Launch campaign
              </Link>
            </Button>
          }
        />
      </section>

      {/* Recent calls */}
      <section className="mt-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-medium text-muted">Recent calls</h2>
          <Link
            href="/calls"
            className="flex items-center gap-1 text-xs text-brand hover:underline"
          >
            View all <ArrowRight className="size-3" />
          </Link>
        </div>
        <Card className="p-4">
          <EmptyState
            title="No calls yet"
            description="Once you launch a campaign, individual calls will appear here with their transcripts, recordings, and outcomes."
          />
        </Card>
      </section>

      {/* Getting started */}
      <section className="mt-8">
        <h2 className="mb-3 text-sm font-medium text-muted">Getting started</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <GettingStartedStep
            step={1}
            title="Create your first agent"
            body="Start from the COD Confirmation template, then tune the prompt and voice."
            href="/agents/new"
            cta="Create agent"
            done={false}
          />
          <GettingStartedStep
            step={2}
            title="Import contacts"
            body="Upload a CSV or paste phone numbers to build your audience."
            href="/contacts"
            cta="Import contacts"
            done={false}
          />
          <GettingStartedStep
            step={3}
            title="Launch a campaign"
            body="Pick your agent, pick your contacts, and start the dialer."
            href="/campaigns/new"
            cta="Launch"
            done={false}
          />
        </div>
      </section>
    </>
  );
}

function GettingStartedStep({
  step,
  title,
  body,
  href,
  cta,
  done,
}: {
  step: number;
  title: string;
  body: string;
  href: string;
  cta: string;
  done: boolean;
}) {
  return (
    <Card className="flex flex-col gap-3 p-5">
      <div className="flex items-center gap-2">
        <span
          className={`flex size-6 items-center justify-center rounded-full text-xs font-semibold ${
            done
              ? "bg-[var(--color-success-bg)] text-[var(--color-success)]"
              : "bg-surface-3 text-muted"
          }`}
        >
          {done ? <CheckCircle2 className="size-3.5" /> : step}
        </span>
        <h3 className="text-sm font-semibold text-fg">{title}</h3>
      </div>
      <p className="flex-1 text-sm text-muted">{body}</p>
      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm" asChild>
          <Link href={href}>{cta}</Link>
        </Button>
        {done && <Badge variant="success">Done</Badge>}
      </div>
    </Card>
  );
}
