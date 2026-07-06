import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Bot,
  BookOpen,
  Phone,
  AudioLines,
  Megaphone,
  Users,
  PhoneCall,
  BarChart3,
  Plug,
  KeyRound,
  UserCog,
  CreditCard,
  Settings,
  LifeBuoy,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Group label this item belongs to in the sidebar. */
  group: "main" | "configure" | "account";
  /** Show a "New" badge or count next to the item. */
  badge?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "main" },
  { label: "AI Agents", href: "/agents", icon: Bot, group: "main" },
  { label: "Knowledge Base", href: "/knowledge", icon: BookOpen, group: "main" },
  { label: "Phone Numbers", href: "/numbers", icon: Phone, group: "main" },
  { label: "Voice Library", href: "/voices", icon: AudioLines, group: "main" },
  { label: "Call Campaigns", href: "/campaigns", icon: Megaphone, group: "main", badge: "New" },
  { label: "Contacts", href: "/contacts", icon: Users, group: "main" },
  { label: "Call History", href: "/calls", icon: PhoneCall, group: "main" },
  { label: "Analytics", href: "/analytics", icon: BarChart3, group: "main" },

  { label: "Integrations", href: "/integrations", icon: Plug, group: "configure" },
  { label: "API Keys", href: "/api-keys", icon: KeyRound, group: "configure" },
  { label: "Team", href: "/team", icon: UserCog, group: "configure" },
  { label: "Billing", href: "/billing", icon: CreditCard, group: "configure" },
  { label: "Settings", href: "/settings", icon: Settings, group: "configure" },
  { label: "Support", href: "/support", icon: LifeBuoy, group: "configure" },
];

export const NAV_GROUPS: { id: NavItem["group"]; label: string }[] = [
  { id: "main", label: "" },
  { id: "configure", label: "Configure" },
];
