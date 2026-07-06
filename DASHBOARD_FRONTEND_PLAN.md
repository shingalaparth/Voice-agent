# AI Calling Platform — Frontend Implementation Plan

> **Status:** Planning blueprint (no code). Awaits approval before implementation.
> **Scope:** Frontend only. No backend in this phase.
> **Reference products:** ElevenLabs, Bland AI, Retell AI, Vapi.
> **Recommended stack:** Next.js (App Router) + React + TypeScript + Tailwind CSS + shadcn/ui-style components. *(Rationale in §13.)*

---

## Phase 1 — Product Discovery

### What type of product this is
A **B2B self-serve SaaS platform** for designing, launching, and monitoring AI voice agents that make outbound phone calls (and, later, take inbound ones). The user configures *agents* (persona, voice, language, goals, tools), attaches *phone numbers* and *contact lists*, launches *campaigns*, and then watches live results and historical analytics. The core value loop is: **configure once → call at scale → measure outcome → improve**.

It is a *workspace-based multi-tenant SaaS* (one user → one or more workspaces → agents/numbers/campaigns scoped to that workspace). Think Vapi/Retell: developers and operators self-serve, no sales call required.

### Target users
- **Growth/e-commerce operators** running COD confirmation, abandoned-cart, or NPS calls at volume (this is exactly the Diorin use case, productized).
- **Customer-experience / support leads** automating outbound reminders, renewals, reactivations.
- **Founders & ops teams at SMBs** who want voice automation without building telephony.
- **Developers/integrators** who want API + webhook access to embed calling into their own stack.

### User personas
| Persona | Goal | Pains | What they need from the UI |
|---|---|---|---|
| **Ops Operator "Priya"** | Launch a 500-contact COD campaign tonight | Telephony is scary; she's non-technical | Guided campaign wizard, templates, clear status |
| **Agent Author "Rahul"** | Tune the prompt + voice so the bot sounds human | Iterating prompts is slow | Inline prompt editor, voice preview, test-call sandbox |
| **Developer "Ankit"** | Trigger calls from his own backend | Needs API keys + webhooks + docs | API key management, webhook config, copy-paste snippets |
| **Admin "Sonia"** | Control spend + team access | Bills spiral, no oversight | Billing, roles, usage caps, audit |

### Main user goals
1. Get from **signup → first successful AI call in < 10 minutes**.
2. Reuse a working agent across many campaigns without reconfiguring.
3. Know, in real time, whether a campaign is succeeding (answer rate, confirmation rate).
4. Trust the platform: predictable billing, clear errors, no silent failures.
5. Scale from 1 call to 10,000 without changing tools.

### Overall workflow (signup → first call)
```
Land on marketing site → Sign up → Verify email → Create/join Workspace →
Onboarding wizard (skippable) → Connect a Voice provider + LLM provider →
Claim/Port a phone number → Create first Agent (template) →
Upload/paste Contacts → Launch a test Campaign → Watch live call →
See result in Call History → View Analytics.
```

---

## Phase 2 — Information Architecture

The app splits into **three surface areas**, each with its own chrome:

1. **Public surface** — marketing, no auth.
2. **Auth surface** — minimal chrome, single column.
3. **App surface** — full dashboard chrome (sidebar + topbar). Everything below lives here.

### Public pages
| Page | Why it exists |
|---|---|
| `/` Landing | Communicate value, drive signups. |
| `/pricing` | Self-serve plan selection. |
| `/product`, `/use-cases`, `/about`, etc. | SEO + trust (later). |
| `/docs` (redirect to docs site) | Developer onboarding. |

### Authentication pages
| Page | Why |
|---|---|
| `/login` | Email + password, SSO (Google/GitHub). |
| `/signup` | Create account, capture workspace intent. |
| `/verify` | Email verification (OTP/link). |
| `/forgot-password`, `/reset-password` | Standard recovery. |
| `/oauth/callback` | SSO redirect target. |
| `/logout` | Clear session. |

### Dashboard (app) pages — grouped by object
| Group | Pages | Why |
|---|---|---|
| **Home** | `/dashboard` | At-a-glance: today's calls, active campaigns, alerts. |
| **Agents** | `/agents`, `/agents/new`, `/agents/[id]`, `/agents/[id]/test` | The core authoring surface. |
| **Knowledge Base** | `/knowledge`, `/knowledge/[id]` | Documents the agent can reference (RAG). |
| **Phone Numbers** | `/numbers`, `/numbers/buy`, `/numbers/port` | Provision + assign DIDs. |
| **Voice Library** | `/voices` | Browse/preview voices across providers. |
| **Campaigns** | `/campaigns`, `/campaigns/new`, `/campaigns/[id]` | Batch outbound runs. |
| **Contacts** | `/contacts`, `/contacts/import`, `/contacts/[id]` | Audience management. |
| **Call History** | `/calls`, `/calls/[id]` | Per-call detail incl. transcript + recording. |
| **Analytics** | `/analytics` | Trends + performance. |
| **Integrations** | `/integrations` | CRM, Slack, webhook targets. |
| **API Keys** | `/api-keys` | Programmatic access. |
| **Team** | `/team`, `/team/invite` | Members + roles. |
| **Billing** | `/billing`, `/billing/plans`, `/billing/invoices` | Plans, usage, payment. |
| **Settings** | `/settings/*` | Workspace, profile, security, notifications, appearance. |
| **Support** | `/support` | Help widget + ticket entry. |

### Settings pages (sub-navigation)
Workspace · Profile · Team · Notifications · AI Defaults · Calling Preferences · Integrations · API Keys · Billing · Security · Appearance.

---

## Phase 3 — Sidebar Navigation

The sidebar is the spine of the app surface. Structure (top → bottom):

```
[Workspace switcher ▾]        ← multi-workspace (Phase 15)
─────────────────
Dashboard                     ← /dashboard
AI Agents                     ← /agents
Knowledge Base                ← /knowledge
Phone Numbers                 ← /numbers
Voice Library                 ← /voices
Call Campaigns                ← /campaigns
Contacts                      ← /contacts
Call History                  ← /calls
Analytics                     ← /analytics
─────────────────             ← divider: "Configure"
Integrations                  ← /integrations
API Keys                      ← /api-keys
Team                          ← /team
Billing                       ← /billing
Settings                      ← /settings
Support                       ← /support
─────────────────
[User menu: avatar, profile, log out]
```

### Per-menu justification

| Menu | Purpose | User workflow | Required screens |
|---|---|---|---|
| **Dashboard** | Daily cockpit. | "What needs my attention right now?" | Overview with KPIs + recent activity. |
| **AI Agents** | Create/tune agents. | List → open → edit prompt/voice/tools → test. | List, create wizard, detail editor, test sandbox. |
| **Knowledge Base** | Give the agent facts. | Upload docs → attach to agent. | List, upload, detail. |
| **Phone Numbers** | Provision DIDs. | Buy/port → assign to agent/campaign. | List, buy, port, assign modal. |
| **Voice Library** | Pick voices. | Filter by provider/language/gender → preview → favorite. | Gallery with audio previews. |
| **Call Campaigns** | Batch calling. | New campaign → pick agent + contacts → schedule → launch → monitor. | List, wizard, live monitor, results. |
| **Contacts** | Manage audience. | Import CSV → tag → segment. | List, import, detail, segments. |
| **Call History** | Audit every call. | Filter by status/agent/date → open detail (transcript, recording, outcome). | List with filters, detail drawer/page. |
| **Analytics** | Trends. | Pick range → read charts → drill into agent/campaign. | Dashboard with filters. |
| **Integrations** | Connect external systems. | Browse catalog → connect → map fields. | Catalog grid, configure modal. |
| **API Keys** | Programmatic access. | Create key → copy once → scope → revoke. | List + create modal. |
| **Team** | Members & roles. | Invite → assign role → remove. | Members list, invite modal, roles. |
| **Billing** | Money. | See plan/usage → upgrade → download invoice. | Overview, plans, payment method, invoices. |
| **Settings** | Everything else. | Adjust defaults, security, appearance. | Tabbed settings. |
| **Support** | Help. | Search docs → raise ticket. | Widget + page. |

**Behavior:** collapsible (icon-only on small screens), pinned section labels, "⌘K" command palette reachable everywhere, contextual "New" button in the topbar that creates the right thing for the current section.

---

## Phase 4 — Complete User Flow

### First-time user journey (happy path)
```
1. Visitor lands on marketing site
2. Clicks "Start free"  →  /signup
3. Enters email + password (or Google SSO)
4. Email verification     →  /verify  (OTP)
5. Onboarding wizard      →  /onboarding
   a. Create Workspace     ("Acme Pvt Ltd")
   b. Connect Providers    (Voice: ElevenLabs · LLM: Groq)
   c. Get a Phone Number   (buy a +91 DID, or skip)
   d. Create first Agent   (start from "COD Confirmation" template)
   e. (Optional) Test call → /agents/[id]/test
6. Import Contacts         →  /contacts/import
7. New Campaign            →  /campaigns/new
   a. Pick agent
   b. Pick contacts / segment
   c. Schedule (now / later)
   d. Review & Launch
8. Live Monitor            →  /campaigns/[id]  (calls rolling in)
9. Open a Call             →  /calls/[id]      (transcript + outcome)
10. View Analytics         →  /analytics       (confirmation rate ↑)
```
Every step is **skippable and resumable**; the wizard stores progress so a user can leave and return. Returning users land on `/dashboard` and bypass the wizard.

### Returning user flow
Login → Dashboard → (open active campaign / launch new one / tune an agent) → done.

### Secondary flows
- **Billing recovery:** usage alert toast → Billing → upgrade → confirm.
- **Error recovery:** failed call in Call History → open detail → see reason → retry / blacklist contact.
- **Invite teammate:** Team → invite by email → assign "Operator" role.

---

## Phase 5 — Screen-by-Screen Planning

For every page below, the same template applies:

> **Purpose · Main sections · Components · Tables/Forms · Filters/Search · Empty state · Loading state · Error state · Mobile behavior · User actions**

I'll fully detail the most important screens and apply a consistent shorthand for the rest.

### 5.1 Dashboard (`/dashboard`)
- **Purpose:** "What's happening today?"
- **Sections:** KPI row (Calls today, Answer rate, Confirmation rate, Active campaigns) · Live campaign strip · Recent calls table · Agent health · Usage/burn-rate card.
- **Components:** MetricCard × 4, ActivityFeed, MiniLineChart, CampaignProgressCard.
- **Empty state:** "No calls yet — launch your first campaign" CTA.
- **Loading:** skeleton KPI cards + shimmer table.
- **Error:** inline retry on each card (one card failing shouldn't blank the page).
- **Mobile:** KPIs collapse to 2×2; tables become cards; sidebar becomes a drawer.

### 5.2 Agents list (`/agents`)
- **Purpose:** Manage all agents.
- **Sections:** Header (search, "New Agent"), filter chips (status, language, voice), grid/list toggle.
- **Components:** AgentCard (name, status badge, voice chip, last-used, ⋯ menu), EmptyState with template gallery.
- **Filters/Search:** text search on name; filter by provider/voice/language; sort by recent.
- **Actions:** Duplicate, Edit, Test, Archive, Delete (with confirm).
- **Mobile:** single-column card list.

### 5.3 Agent detail / editor (`/agents/[id]`) — *the heart of the product, see Phase 6.*
Multi-section editor with sticky section nav, live preview pane, and "Save draft / Publish" semantics.

### 5.4 Phone Numbers (`/numbers`)
- Table: number, country, type (local/toll-free), assigned agent/campaign, status, purchased date.
- Actions: Buy (modal with country/feature search), Port (multi-step), Assign, Release.
- Empty: "You have no numbers" + Buy CTA.

### 5.5 Voice Library (`/voices`) — see Phase 7.

### 5.6 Campaigns (`/campaigns`, `/campaigns/new`, `/campaigns/[id]`) — see Phase 8.

### 5.7 Contacts (`/contacts`)
- Table: name, phone (E.164), tags, lists, last-called, status.
- Import: CSV/Excel drag-drop + paste; column-mapping step; dedupe preview; tag-on-import.
- Filters: by list/tag/last-call-outcome; bulk tag/delete/add-to-campaign.

### 5.8 Call History (`/calls`, `/calls/[id]`)
- Table: time, contact, phone, agent, campaign, duration, outcome (Confirmed/Cancelled/No-answer), recording play button.
- Filters: date range, agent, campaign, outcome, duration; full-text search across transcripts.
- Detail: transcript timeline synced with audio waveform, tool-call markers, sentiment, cost.

### 5.9 Analytics (`/analytics`) — see Phase 9.

### 5.10 Settings (`/settings/*`) — see Phase 10.

### 5.11 Integrations (`/integrations`)
- Catalog grid (Slack, HubSpot, Salesforce, Sheets, Webhook, Zapier…); each tile → connect modal (OAuth or API key) → configuration.

### 5.12 API Keys (`/api-keys`)
- Table: label, prefix, scopes, created, last-used, revoke.
- Create modal: label + scopes; **secret shown once** with copy + "I've saved it" gate.

### 5.13 Team (`/team`)
- Members table: name, email, role, status, last-active. Invite modal (email + role). Role definitions inline.

### 5.14 Billing (`/billing`)
- Current plan, this-period usage vs. quota, payment method, invoices table, "Manage plan" → pricing modal.

### Generic states (apply everywhere)
- **Empty:** illustration + 1-line reason + primary CTA.
- **Loading:** skeleton matching final layout (never a spinner for lists).
- **Error:** friendly message + retry + error code for support.
- **Mobile:** drawer nav, stacked cards instead of tables, sticky action bars.

---

## Phase 6 — AI Agent Builder

A guided, opinionated editor. Layout: **left section nav · main form · right live preview**, with **Save draft** and **Publish** in the sticky header.

| Section | UX |
|---|---|
| **Basics** | Name, description, avatar/emoji. Inline validation. |
| **Template start** | Gallery (COD Confirmation, Appointment Reminder, NPS Survey, Win-back…) — picking one prefills the rest. |
| **System prompt** | Monospace editor with variable tokens (`{{customer_name}}`, `{{order_id}}`), token chip inserter, char count, "Improve" assistant button (later). |
| **Language** | Default language selector (`hi`, `en`, `multi`) + allowed-mixing toggle. Drives STT language. |
| **Voice** | Provider picker → voice picker (preview play buttons) → speed/pitch sliders. |
| **Greeting** | First-message editor + live "what the customer hears" preview (TTS preview button). |
| **Conversation goals** | Define success/terminate intents + which tool maps to each (e.g., "confirm" → `confirm_order`). |
| **Tools / Functions** | List of tools (name, description, params schema). Enable/disable per agent. Maps to function-calling. |
| **Knowledge base** | Attach docs/knowledge sets for RAG. |
| **Advanced** | Temperature, max turns, interruption sensitivity, silence timeout, retry-on-failure, transfer-to-human number. |
| **Test interface** | Sandbox: type or speak → see transcript, tool calls, latency, cost. "Call me" button for a real test call to your phone. |

**UX principles:** autosave drafts; never lose work; "Publish" creates an immutable version; diff between draft and published shown clearly.

---

## Phase 7 — Voice Management

A browsable library — the UX is closer to a music app than a settings form.

| Element | Design |
|---|---|
| **Voice library** | Card grid: name, provider badge, language flags, gender, sample waveform, play button. |
| **Provider selection** | Filter chips (ElevenLabs, Cartesia, Sarvam, Deepgram, OpenAI…). Multiple providers coexist. |
| **Voice preview** | One-click preview using a fixed sample line; per-voice preview using the agent's greeting when launched from the builder. |
| **Default voice** | Workspace-level default + per-agent override. |
| **Voice tags** | "Warm", "Professional", "Energetic", "Indian-accent" — filterable. |
| **Favorites** | Heart icon; "Favorites" filter. |
| **Search & filters** | Free text + multi-select filters (provider, language, gender, tag). |

Mobile: single column, large tap targets on play buttons.

---

## Phase 8 — Campaign Management

### List (`/campaigns`)
Table: name, agent, status (Draft/Scheduled/Running/Paused/Completed/Failed), progress bar (called/total), answer rate, confirmation rate, started, scheduled-time. Bulk actions: pause, resume, duplicate, archive.

### New campaign wizard (`/campaigns/new`) — 4 steps
1. **Agent & Goal** — pick agent + success metric.
2. **Audience** — pick contacts/list/segment or paste numbers; dedupe preview; excludes (DNC, previously cancelled).
3. **Schedule & Limits** — start now/later; concurrency; daily caps; quiet hours (per timezone); retry policy.
4. **Review & Launch** — summary, cost estimate, compliance checkbox → Launch (or Save as Draft).

### Detail / live monitor (`/campaigns/[id]`)
- **Header:** status, controls (Pause/Resume/Stop), progress.
- **Live tiles:** calls/min, live queue, current outcomes (donut).
- **Live feed:** streaming rows as calls happen.
- **Results tab:** full table with same filters as Call History, exportable.
- **Charts tab:** funnel (Dialed → Answered → Confirmed).

States: live polling + WebSocket for streaming; full-page error with retry; safe pause that drains gracefully.

---

## Phase 9 — Analytics

Single page with a **filter rail** (date range, agent, campaign, outcome, country) and **drill-down** everywhere.

| Metric | Presentation |
|---|---|
| Total Calls | Big number + sparkline + %Δ vs. previous period. |
| Answer Rate | Big number + donut (answered / no-answer / busy / failed). |
| Confirmation Rate | Big number + trend line (the *business* KPI). |
| Average Duration | Number + distribution histogram. |
| AI Success Rate | Number (calls that reached a terminal tool) + breakdown by failure mode. |
| Campaign Performance | Comparison bar/table across campaigns. |
| Daily Trends | Stacked area (answered vs. not) over the range. |
| Agent Performance | Table: agent × (calls, answer rate, confirm rate, avg duration, cost). |

**UX:** every chart is a clickable drill-down (chart → filtered Call History). Export PNG/CSV. "Saved views" for repeat analyses. Skeleton loaders per tile; graceful degradation if a single metric fails.

---

## Phase 10 — Settings

Tabbed (or sub-routed) settings with a left sub-nav:

| Page | Contents |
|---|---|
| **Workspace** | Name, logo, default timezone/currency, delete workspace. |
| **Profile** | Name, email, avatar, timezone, preferred language. |
| **Team** | Members + roles (covered in `/team`). |
| **Notifications** | Email/in-app toggles per event (campaign complete, error spikes, billing). |
| **AI Defaults** | Default LLM, default voice, default language, default temperature. |
| **Calling Preferences** | Default caller ID, quiet hours, retry policy, DNC handling. |
| **Integrations** | Shortcut to `/integrations` with connected-state summary. |
| **API Keys** | Shortcut to `/api-keys`. |
| **Billing** | Shortcut to `/billing`. |
| **Security** | 2FA, password, active sessions, audit log. |
| **Appearance** | Light/dark/system, density (comfortable/compact). |

---

## Phase 11 — Design System

Goal: premium, enterprise-grade, calm. Density-friendly for power users, but never clinical.

### Typography
- **Sans (UI):** Inter (or Geist). Weights 400/500/600/700.
- **Mono:** JetBrains Mono / Geist Mono (prompt + code + API).
- Scale: 12 / 13 / 14 (base) / 16 / 18 / 20 / 24 / 30 / 36. Line-height tight on headings, relaxed on body.

### Color palette
- **Neutral:** zinc/slate ramp (0 → 950). Backgrounds: white (light) / `#0a0a0a` (dark).
- **Brand:** a single confident accent (e.g., indigo→violet gradient for CTAs). Kept sparing.
- **Semantic:** success (emerald), warning (amber), danger (rose), info (sky). Each with subtle bg/border tints for badges.
- **Data-viz:** a fixed 8-color categorical palette + sequential ramps for heatmaps. Color-blind safe.

### Spacing & grid
- 4px base scale (4/8/12/16/20/24/32/40/48/64).
- 12-column grid at ≥1280px; comfortable max content width ~1440.
- Consistent card padding (24 desktop / 16 mobile).

### Components language
- **Cards:** 1px border, soft shadow on hover, 12–16px radius.
- **Tables:** dense, sticky headers, hover row, inline row actions on hover.
- **Buttons:** 3 variants (primary, secondary, ghost) × 3 sizes; destructive has confirm.
- **Forms:** labels above inputs, helper text below, inline error with icon; left-aligned submit.
- **Modals:** centered, max 560px, ESC + backdrop close (disabled for destructive confirms).
- **Drawers:** right-side for detail/edit without losing list context.
- **Tooltips:** 250ms delay, dark bubble.
- **Icons:** Lucide (consistent stroke, tree-shakeable).
- **Charts:** Recharts/Visx; consistent tooltip, legend, empty state.
- **Empty states:** illustration + line + CTA. **Skeletons:** match final layout. **Toasts:** bottom-right, auto-dismiss, action optional.

Dark mode is **first-class** — every color is token-based, never hardcoded.

---

## Phase 12 — Component Library

| Component | Used in |
|---|---|
| Button, IconButton | Everywhere. |
| Card, StatCard | Dashboard, lists, settings. |
| Table, DataGrid | Calls, Contacts, Campaigns, Numbers, API keys, Invoices, Team. |
| Sidebar, Topbar, Breadcrumbs, PageHeader | App shell. |
| CommandPalette (⌘K) | Global nav + actions. |
| SearchBar | Lists, voice library, docs. |
| Pagination, InfiniteScroll | Long lists. |
| FilterPanel, FilterChips, DatePicker, DateRangePicker | Calls, Contacts, Analytics. |
| Tabs, SegmentedControl | Agent editor, settings, call detail. |
| StatusBadge, Pill, Tag | Status, outcome, language tags. |
| Modal, Dialog, Drawer, Popover | Confirms, detail views, editors. |
| Form: Input, Textarea, Select, Combobox, Checkbox, Switch, Slider, FileUpload, CodeEditor | All forms. |
| Toast, Alert, Tooltip | Feedback. |
| Skeleton, EmptyState, ErrorState, InlineError | Async states. |
| LineChart, BarChart, DonutChart, AreaChart, Sparkline, Funnel | Analytics, dashboard, campaign monitor. |
| VoicePlayer (waveform + play) | Voice library, call recording. |
| AgentCard, CampaignCard, MetricCard | Domain lists. |
| CallTimeline (transcript + audio sync) | Call detail. |
| ActivityFeed | Dashboard, campaign monitor. |
| Avatar, WorkspaceSwitcher, UserMenu | Shell. |
| DataTable toolbar (column toggle, export) | DataGrid. |

Each component is **accessible (WCAG AA)**, keyboard-navigable, and has a storybook entry (Milestone 1).

---

## Phase 13 — Frontend Architecture

### Recommended stack & why
- **Next.js (App Router) + React + TypeScript** — SSR/ISR for marketing, route-level code splitting, server components for data-heavy pages, API routes for BFF later. Consistent with the (now-removed) original dashboard (Next 16 + React 19), so the team already knows it. Industry standard for this category (Vapi, Retell).
- **Tailwind CSS** + **shadcn/ui-style** primitives — token-driven theming, dark mode, fast iteration, no heavy UI-lib lock-in.
- **TanStack Query** for server state (caching, polling campaigns, mutations).
- **Zustand** (or React Context) for *small* UI-only state; avoid a global store.
- **TanStack Table** for data grids.
- **Recharts** for charts (upgrade to Visx only if needed).
- **react-hook-form + zod** for forms + validation (type-safe schemas shared with the future API).
- **Lucide** icons, **sonner** toasts, **cmdk** for the command palette.
- **Vitest + Testing Library + Playwright** for unit/component/E2E.
- **Storybook** for the component library.

### Folder structure (feature-sliced)
```
src/
├── app/                     # Next.js App Router (routes only)
│   ├── (marketing)/         # public site group
│   ├── (auth)/              # login/signup/etc.
│   ├── (app)/               # authenticated dashboard group (shell layout)
│   │   ├── dashboard/
│   │   ├── agents/...
│   │   └── layout.tsx       # sidebar + topbar shell
│   └── layout.tsx
├── features/                # vertical feature modules
│   ├── agents/              # ui/, api/, hooks/, types/, schema.ts
│   ├── campaigns/
│   ├── calls/
│   ├── contacts/
│   ├── analytics/
│   ├── billing/
│   └── auth/
├── components/              # shared design-system primitives
│   ├── ui/                  # Button, Card, Modal, Table…
│   ├── charts/
│   └── layouts/
├── lib/                     # cross-cutting
│   ├── api/                 # client, types, endpoints
│   ├── auth/                # session, RBAC helpers
│   ├── utils/               # format, dates, phone, csv
│   └── constants/
├── hooks/                   # generic hooks (useDebounce, useMediaQuery)
├── styles/                  # tokens, globals.css
└── types/                   # shared domain types
```

**Reasoning:** feature modules keep each domain's UI, data, and validation colocated (easy to find, easy to delete). The `app/` directory stays thin — only routing + layout. Shared primitives live in `components/ui` so the design system has one home. This scales: a new feature = a new folder, no refactor.

### Routing
- File-based (App Router). Route groups `(marketing)`, `(auth)`, `(app)` for distinct shells without URL noise.
- Nested layouts: `(app)/layout.tsx` renders the sidebar+topbar shell once for every dashboard page.
- Middleware for auth + workspace resolution + redirects (onboarding completion guard).

### State management
- **Server state:** TanStack Query (calls, agents, campaigns). Caches by query key; invalidation on mutations.
- **URL state:** filters/sort/pagination in search params (shareable, back-button friendly) via `nuqs`.
- **Client UI state:** Zustand slices only for genuinely global UI (sidebar collapse, theme, command-palette open).
- **Form state:** react-hook-form local to each form.

### API layer
- Single typed client (`lib/api/client.ts`) wrapping fetch with auth, base URL, error normalization.
- Endpoints grouped per feature (`features/agents/api.ts`) returning typed results.
- **MSW** mocks during the frontend-only phase so the UI is fully buildable today; swap to real endpoints later with no component changes.
- All schemas in zod, derived TS types via `z.infer` — same schemas will validate server responses and (later) backend requests.

### Hooks
- Generic: `useDebounce`, `useMediaQuery`, `useCopyToClipboard`, `useLocalStorage`, `usePolling`.
- Feature: `useAgents`, `useAgent(id)`, `useCampaigns`, `useCall(id)`, `useAnalytics(filters)`.

### Utilities
`formatPhone`, `formatCurrency`, `formatDuration`, `formatRelativeTime`, `downloadCsv`, `cn` (classnames), `parseCsv`, RBAC `can(user, action)`.

---

## Phase 14 — Implementation Roadmap

Each milestone is independently shippable.

### M0 — Foundation (week 1)
- **Goal:** runnable shell + design system.
- **Pages:** `(marketing)` landing stub, `(auth)` login/signup, `(app)` empty dashboard.
- **Components:** full design-system primitives (Button, Card, Input, Table, Modal, Badge, Toast, Skeleton, EmptyState, ErrorState), dark mode, Storybook.
- **Dependencies:** none.
- **Deliverable:** themed app shell with sidebar + topbar + ⌘K palette, MSW mock API, CI.

### M1 — Agents (week 2)
- **Goal:** the core authoring loop.
- **Pages:** Agents list, create wizard, agent editor (all sections from Phase 6), test sandbox.
- **Components:** AgentCard, CodeEditor, VoicePicker, Tabs, Drawer.
- **Dependencies:** M0.
- **Deliverable:** user can create, save, publish, and test-call an agent end-to-end (mocked).

### M2 — Voice + Numbers + Contacts (week 3)
- **Goal:** configure inputs to a campaign.
- **Pages:** Voice Library, Phone Numbers (buy/port/assign), Contacts (import/map/tag).
- **Components:** VoicePlayer, FileUpload, DataGrid, FilterPanel.
- **Dependencies:** M0, M1.
- **Deliverable:** voice selection, number assignment, contact import all working against mocks.

### M3 — Campaigns + Call History (week 4)
- **Goal:** launch + observe.
- **Pages:** Campaign list, wizard, live monitor; Call History list + detail.
- **Components:** CampaignCard, CallTimeline, ProgressChart, DonutChart, WebSocket-driven ActivityFeed.
- **Dependencies:** M1, M2.
- **Deliverable:** launch a (mocked) campaign, watch it stream, open any call's transcript.

### M4 — Analytics + Dashboard (week 5)
- **Goal:** measure.
- **Pages:** Analytics, real Dashboard.
- **Components:** full chart suite, MetricCard, DatePicker range, saved views.
- **Dependencies:** M3.
- **Deliverable:** filterable analytics with drill-down into Call History.

### M5 — Settings, Team, Billing, Integrations, API Keys (week 6)
- **Goal:** operational completeness.
- **Pages:** all settings tabs, Team, Billing, Integrations catalog, API Keys.
- **Components:** SettingsShell, RoleBadge, PlanCard, InvoiceTable, IntegrationTile.
- **Dependencies:** M0.
- **Deliverable:** everything an admin needs; ready to plug a real backend into.

### M6 — Polish & a11y (week 7)
- **Goal:** enterprise bar.
- **Focus:** WCAG AA pass, keyboard flows, empty/loading/error audit, performance budgets, E2E suite, onboarding-wizard polish, mobile pass.
- **Deliverable:** production-grade frontend.

---

## Phase 15 — Future Expansion (designed-for, not built)

The architecture above is shaped so the following require **new code, not rewrites**:

- **Multiple workspaces** — WorkspaceSwitcher + `[workspaceSlug]` segment + RBAC already in the model.
- **Teams & roles** — `can(user, action)` gate already referenced; add role screens.
- **Multiple providers** (Voice/LLM/Telephony) — provider is already a *selector*, not a hardcode; each has a config schema.
- **Knowledge bases (RAG)** — `/knowledge` route reserved; agent editor already has an attach step.
- **Phone number management** — buy/port/assign flows already planned.
- **Billing & subscriptions** — Stripe-based; pages + webhooks (later).
- **API access + Webhooks** — `/api-keys` + an integrations/webhook UI reserved.
- **Marketplace** (templates, voices, agents) — AgentCard/VoiceCard already share a tile pattern; a marketplace is a new list source.
- **Enterprise** (SSO/SAML, audit log, data residency) — auth layer abstracted; settings/Security page reserved.

The rule: **every list is data-driven, every provider is pluggable, every page is feature-foldered** — so growth is additive.

---

## Deliverables Summary

1. **Product architecture** — §1: B2B self-serve, workspace-scoped, agent→campaign→calls loop.
2. **Information architecture** — §2: public / auth / app surfaces, full page inventory.
3. **User journey** — §4: signup → first call in <10 min, skippable/resumable.
4. **Sitemap** — §2 table + §3 sidebar.
5. **Navigation structure** — §3 sidebar with per-item justification.
6. **Screen inventory** — §5 (12 page groups, every state defined).
7. **Component inventory** — §12 (~40 primitives + domain components).
8. **Design system spec** — §11 (type, color, spacing, components, dark mode).
9. **Frontend architecture** — §13 (Next.js + feature-sliced folders, state, API, mocks).
10. **Implementation roadmap** — §14 (M0–M6, foundation → polish).
11. **Risks & UX considerations** — below.
12. **Scalability recommendations** — §15.

### Risks & UX considerations
- **Telephony complexity leakage** — shield non-technical operators behind templates + wizards; never expose SIP/trunks in the primary flow.
- **Realtime reliability** — live campaign monitor must degrade gracefully (polling fallback when WebSocket drops).
- **Cost anxiety** — always show estimated cost *before* launch and burn-rate *during*.
- **Compliance** — DNC/quiet hours must be first-class in the campaign wizard, not buried.
- **Secrets** — API key shown once; sessions/audit visible in Security.
- **Performance** — Call History and Contacts can reach 100k+ rows; design virtualized DataGrid from day one.
- **Accessibility** — audio content (recordings) needs transcripts; charts need text alternatives.

### Scalability recommendations
- Token-based theming + dark mode from M0.
- Feature-foldered code + typed API contract (zod) so backend swap is mechanical.
- MSW mocks now → real API later, zero component churn.
- Virtualized lists, paginated APIs, query caching by default.
- RBAC (`can()`) plumbed even if only one role exists today.
- Every provider behind an interface, never inlined.

---

*End of plan. No code has been written. Ready for review and approval before any implementation begins.*
