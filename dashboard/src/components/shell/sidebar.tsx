"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_GROUPS, NAV_ITEMS, type NavItem } from "@/lib/navigation";
import { Logo } from "./logo";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-surface md:flex">
      {/* Workspace switcher */}
      <div className="flex h-16 items-center gap-2 border-b border-border px-4">
        <Logo href="/dashboard" showText={false} />
        <button className="flex flex-1 items-center justify-between rounded-md px-2 py-1.5 text-left transition-colors hover:bg-surface-3">
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-fg">
              Diorin HQ
            </p>
            <p className="truncate text-xs text-muted">Free plan</p>
          </div>
          <ChevronsUpDown className="size-4 shrink-0 text-muted" />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4">
        {NAV_GROUPS.map((group) => {
          const items = NAV_ITEMS.filter((i) => i.group === group.id);
          if (!items.length) return null;
          return (
            <div key={group.id} className="space-y-1">
              {group.label && (
                <p className="px-3 pb-1 text-xs font-medium uppercase tracking-wider text-subtle">
                  {group.label}
                </p>
              )}
              {items.map((item) => (
                <SidebarLink key={item.href} item={item} active={isActive(pathname, item.href)} />
              ))}
            </div>
          );
        })}
      </nav>

      {/* User card */}
      <div className="border-t border-border p-3">
        <button className="flex w-full items-center gap-3 rounded-md p-2 text-left transition-colors hover:bg-surface-3">
          <span className="flex size-8 items-center justify-center rounded-full bg-surface-3 text-xs font-semibold text-muted">
            PS
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-fg">Parth</p>
            <p className="truncate text-xs text-muted">parth@diorin.ai</p>
          </div>
          <ChevronDown className="size-4 text-muted" />
        </button>
      </div>
    </aside>
  );
}

function SidebarLink({ item, active }: { item: NavItem; active: boolean }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      className={cn(
        "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-surface-3 text-fg"
          : "text-muted hover:bg-surface-2 hover:text-fg"
      )}
    >
      <Icon
        className={cn(
          "size-4 shrink-0",
          active ? "text-brand" : "text-subtle group-hover:text-muted"
        )}
      />
      <span className="flex-1 truncate">{item.label}</span>
      {item.badge && (
        <span className="rounded-full bg-brand px-1.5 py-0.5 text-[10px] font-semibold text-white">
          {item.badge}
        </span>
      )}
    </Link>
  );
}

function isActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(`${href}/`);
}
