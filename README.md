# Diorin AI Calling Agent (MVP)

A focused voice agent that calls **one customer at a time** to verify a Cash on
Delivery (COD) order, conducts the conversation in **Hindi** (with English +
Hinglish support), captures the final outcome, and saves it locally as JSON.

Built on the existing LiveKit + Deepgram + Groq + ElevenLabs + Vobiz SIP stack.
No database, dashboard, auth, or webhook — pure proof that the end-to-end voice
workflow works for one manually-entered customer.

---

## 1. Repository architecture

```
LIvekitAIVoice/
├── agent.py              # LiveKit worker: build session, dial, run, save
├── make_call.py          # CLI: load customer.json → dispatch the agent
├── customer.json         # INPUT — the one customer to call (you edit this)
├── customer.example.json # blank template to copy from
├── config.py             # env vars, model + path settings, validate_env()
├── prompts.py            # Diorin system prompt + greeting (variable injection)
├── tools.py              # OrderTools: confirm/cancel/retention/save function tools
├── storage.py            # load_customer() + save_result() JSON helpers
├── logger.py             # shared logger (console + logs/agent.log)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── create_trunk.py       # one-off: create Vobiz SIP trunk
├── setup_trunk.py        # one-off: update trunk credentials
├── list_trunks.py        # one-off: list existing trunks
├── call_results/         # OUTPUT — <timestamp>_<order_id>.json (auto-created)
└── logs/                 # agent.log + rotated files (auto-created)
```

**What each file does and why it exists** (only changed files noted in §5):

| File | Role |
|------|------|
| `agent.py` | LiveKit worker entrypoint. Reads customer from job metadata, builds the STT/LLM/TTS session, dials the customer via SIP, drives the conversation, and guarantees a result save via a shutdown callback. |
| `make_call.py` | Loads + validates `customer.json`, creates a unique room, dispatches the `outbound-caller` agent with the full customer record as metadata. |
| `config.py` | All env vars, model choices, paths. `validate_env()` fails fast on missing credentials. |
| `prompts.py` | All conversation prompts live here — Hindi/English/multi language-aware, with `{name}`, `{product}`, etc. injected from the customer record. |
| `tools.py` | `OrderTools` — `confirm_order`, `cancel_order(reason)`, `record_retention_successful`, `save_call_result`. Tracks outcome state and persists to `call_results/`. |
| `storage.py` | `load_customer()` validates `customer.json`; `save_result()` writes the final JSON. |
| `logger.py` | One configured logger used across the project (console + rotating file). |
| `create_trunk.py` / `setup_trunk.py` / `list_trunks.py` | Unchanged SIP-trunk utilities. Run once when configuring Vobiz. |

---

## 2. The MVP workflow

```
 You edit customer.json
        │
        ▼
 python make_call.py  ──►  LiveKit creates a room + dispatches agent
        │
        ▼
 agent.py entrypoint  ──►  reads customer from metadata
        │
        ▼
 Deepgram(STT) + Groq(LLM) + ElevenLabs(TTS) session starts
        │
        ▼
 SIP dial-out via Vobiz trunk  ──►  customer's phone rings
        │
        ▼
 Customer answers  ──►  greeting (Hindi, names product + amount, COD)
        │
        ▼
 Conversation (Hindi / Hinglish / English)
        │
        ├── confirms  ──► confirm_order()  ──► CONFIRMED
        │
        └── cancels   ──► cancel_order(reason)
                              │
                              ▼
                       ONE retention attempt
                              │
                              ├── reconsiders ──► record_retention_successful()
                              │                     └─► CONFIRMED
                              └── still cancels  ──► CANCELLED
        │
        ▼
 save_call_result()  ──►  call_results/<timestamp>_<order_id>.json
        │
        ▼
 Polite Hindi goodbye ("Namaste")  ──►  call ends
```

### Conversation flow

1. **Greeting** — Introduce Diorin, the customer's name, the product, the order
   amount, and that this is a COD verification call.
2. **Confirmation** — Ask whether the customer wants to keep the order.
3. **Cancellation flow** *(only if they cancel)* — Ask the reason politely,
   record it via `cancel_order(reason)`, then make **exactly one** polite
   retention attempt (delivery / product quality / brand reassurance). Never
   pressure the customer. If they still cancel, respect the decision.
4. **Final outcome** — `CONFIRMED` or `CANCELLED` (+ reason, retention outcome).
5. **Save + end** — `save_call_result()` writes the JSON; the agent ends politely.

---

## 3. Setup & running

### Prerequisites
- Python 3.10+
- A LiveKit Cloud project, Deepgram key, Groq key, ElevenLabs key
- A Vobiz SIP trunk registered in LiveKit (`VOBIZ_SIP_TRUNK_ID`)

### Install
```bash
cd LIvekitAIVoice
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

### Configure `.env`
Make sure these are set (the existing `.env` already has them):
```
LIVEKIT_URL=wss://....livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...

DEEPGRAM_API_KEY=...
GROQ_API_KEY=...
ELEVEN_API_KEY=...            # or ELEVENLABS_API_KEY
ELEVENLABS_VOICE_ID=tA6LGZpsqStKtSaGiXND

VOBIZ_SIP_TRUNK_ID=ST_...
VOBIZ_SIP_DOMAIN=e00836eb.sip.vobiz.ai
```
Optional overrides (defaults shown):
```
STT_MODEL=nova-3
STT_LANGUAGE=hi
ELEVEN_MODEL=eleven_turbo_v2_5
GROQ_MODEL=llama-3.3-70b-versatile
DEFAULT_LANGUAGE=hi
```

### First-time SIP setup (only if the trunk isn't already in LiveKit)
```bash
python create_trunk.py    # creates the trunk, prints the Trunk ID
# put that ID in .env as VOBIZ_SIP_TRUNK_ID, then:
python setup_trunk.py     # syncs credentials
python list_trunks.py     # verify
```

### Make a call
1. Edit `customer.json` with the customer's details (see §4).
2. Start the worker:
   ```bash
   python agent.py start
   ```
3. In a second terminal, dispatch the call:
   ```bash
   python make_call.py
   ```
4. Watch the worker logs for the conversation; read the outcome in
   `call_results/<timestamp>_<order_id>.json`.

---

## 4. How to update customer details

Open `customer.json` and edit the fields. **All fields are required** except
`language`.

```json
{
  "name": "Rahul Sharma",
  "phone": "+919876543210",
  "order_id": "DRN-100245",
  "product": "Dior Sauvage EDP 100ml",
  "amount": "₹8,500",
  "language": "hi"
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | Customer's name (used in the greeting) |
| `phone` | yes | E.164 format, e.g. `+919876543210` |
| `order_id` | yes | Order reference |
| `product` | yes | Product name |
| `amount` | yes | Order total (COD) |
| `language` | no | `hi` (default), `en`, or `multi`. Drives STT language + prompt. |

To call a different customer, just overwrite `customer.json` and run
`python make_call.py` again.

---

## 5. What changed from the original project (and why)

| File | Change | Why |
|------|--------|-----|
| `agent.py` | Rewritten | Replace "School Receptionist" persona with Diorin COD verifier; receive the full customer record (not just `phone`); use `OrderTools`; add shutdown-callback safety save; robust error handling around session/SIP/reply. |
| `config.py` | Rewritten | Strip persona prompt + unused Sarvam/Cartesia/OpenAI blocks; add `validate_env()`; add paths + language settings; normalize `ELEVEN_API_KEY`. |
| `make_call.py` | Rewritten | Read + validate `customer.json`; pass full customer in metadata (was phone-only). |
| `prompts.py` | **New** | Centralize all prompts (was embedded in `config.py`); variable injection for name/product/etc.; language-aware. |
| `tools.py` | **New** | Business tools (`confirm_order`, `cancel_order`, `record_retention_successful`, `save_call_result`) replace demo `lookup_user`/`transfer_call`. |
| `storage.py` | **New** | Local JSON load/save (no DB/ORM). |
| `logger.py` | **New** | One shared rotating logger across the project. |
| `customer.json` / `customer.example.json` | **New** | Manual per-call input. |
| `requirements.txt` | Trimmed | Removed unused `livekit-plugins-cartesia` + `livekit-plugins-sarvam`. |
| `README.md` | Rewritten | Full Diorin MVP documentation. |
| `.gitignore` | Updated | Ignore `customer.json`, `call_results/`, `logs/`. |
| `dashboard/` | **Deleted** | Separate bulk-call Next.js app branded "Rapid X AI"; its `/api/dispatch` never dispatched the agent (broken vs. `make_call.py`), and bulk/UI is out of scope for this MVP. |
| `KMS/`, `package-lock.json`, `transfer_call.md` | **Deleted** | Empty / stray / documents the removed transfer feature. |
| `Dockerfile`, `docker-compose.yml`, `create_trunk.py`, `setup_trunk.py`, `list_trunks.py` | **Unchanged** | Still valid for the MVP. |

### Models used
- **STT**: Deepgram `nova-3`, language `hi` (better Hindi/Hinglish than the original `nova-2`).
- **LLM**: Groq `llama-3.3-70b-versatile` (unchanged, via OpenAI-compatible client).
- **TTS**: ElevenLabs `eleven_turbo_v2_5` (multilingual), voice `tA6LGZpsqStKtSaGiXND`.

---

## 6. Error handling strategy

- **Startup** — `config.validate_env()` aborts before the worker accepts jobs if any required credential is missing.
- **Input** — `load_customer()` rejects missing fields, bad JSON, and malformed phone numbers with clear messages; `make_call.py` prints them and exits non-zero.
- **Session init / start** — Wrapped in try/except; on failure the partial result is saved and the job shuts down cleanly.
- **SIP dial** — Failure (no answer, busy, bad trunk) is logged with the phone + trunk and the job shuts down after saving.
- **Tool execution** — Each tool updates state in-memory; persistence failures are logged but never crash the call.
- **Hangup / disconnect** — `RoomInputOptions(close_on_disconnect=True)` plus `ctx.add_shutdown_callback(order_tools.persist)` guarantee the result is flushed even if the customer hangs up before `save_call_result()` runs.
- **`generate_reply`** — Wrapped so a TTS/LLM hiccup during the greeting doesn't tear down the session.

---

## 7. Logging strategy

All logs go to the console **and** `logs/agent.log` (rotating, ~2 MB × 3).

Lifecycle events logged:
`agent job started` → `customer loaded` → `session/STT/LLM/TTS initialized` →
`outbound SIP call initiated` → `call answered` → `customer CONFIRMED/CANCELLED` →
`retention attempted/succeeded` → `result persisted` → `call completed`,
plus every error with `exc_info=True`.

---

## 8. Environment variable reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `LIVEKIT_URL` | yes | — | LiveKit Cloud WebSocket URL |
| `LIVEKIT_API_KEY` | yes | — | LiveKit API key |
| `LIVEKIT_API_SECRET` | yes | — | LiveKit API secret |
| `DEEPGRAM_API_KEY` | yes | — | Deepgram STT key |
| `GROQ_API_KEY` | yes | — | Groq LLM key |
| `ELEVEN_API_KEY` *(or `ELEVENLABS_API_KEY`)* | yes | — | ElevenLabs key |
| `ELEVENLABS_VOICE_ID` | yes | `tA6LGZpsqStKtSaGiXND` | Voice ID |
| `VOBIZ_SIP_TRUNK_ID` | yes | — | LiveKit SIP trunk ID |
| `VOBIZ_SIP_DOMAIN` | optional | — | Used by trunk setup scripts |
| `STT_MODEL` | no | `nova-3` | Deepgram model |
| `STT_LANGUAGE` | no | `hi` | Default STT language |
| `ELEVEN_MODEL` | no | `eleven_turbo_v2_5` | ElevenLabs model |
| `GROQ_MODEL` | no | `llama-3.3-70b-versatile` | Groq model |
| `GROQ_TEMPERATURE` | no | `0.7` | LLM temperature |
| `DEFAULT_LANGUAGE` | no | `hi` | Fallback if customer.json omits `language` |

---

## 9. Expected call sequence (start to finish)

1. `python agent.py start` — worker connects to LiveKit, validates env, waits.
2. `python make_call.py` — reads `customer.json`, creates room `call-<phone>-<rand>`, dispatches agent.
3. Worker accepts the job, parses customer from metadata, logs it.
4. Session initialized (Deepgram `hi` + Groq + ElevenLabs).
5. `create_sip_participant(wait_until_answered=True)` — phone rings.
6. Customer answers → agent speaks the Hindi greeting.
7. Customer confirms/cancels → corresponding tool fires → state updated.
8. *(If cancelled)* reason captured → one retention attempt → outcome finalized.
9. `save_call_result()` writes `call_results/<timestamp>_<order_id>.json`.
10. Agent says goodbye, call ends, room closes.

---

## 10. Limitations of this MVP

- **One customer at a time** — `customer.json` is overwritten per call; no queue.
- **No persistence backend** — results are flat JSON files, not queryable.
- **No retry / scheduling** — a failed/no-answer call is logged and ends.
- **No live transcript UI** — read logs / result JSON to see what happened.
- **Hindi-first** — English/Hinglish handled, but other languages need new entries in `prompts.LANGUAGE_INSTRUCTIONS` and possibly a different STT language.
- **No auth** on any endpoint (none exposed — agent is driven by the LiveKit worker only).

---

## 11. Recommendations for the next (production) version

- **Multi-customer pipeline**: replace `customer.json` with a queue (CSV upload, Redis/BullMQ, or a small DB), and have `make_call.py` enqueue rather than dial directly.
- **Webhook + dashboard**: bring back a dashboard, but drive it through proper `agent_dispatch` (the original `dashboard/` bug). Show live transcript, status, and replay audio.
- **Database**: move `call_results/` into Postgres/SQLite with an ORM for queryable history and reporting.
- **Languages at scale**: add a language-detection step (or Deepgram `multi`) and extend `prompts.LANGUAGE_INSTRUCTIONS`. Consider Sarvam/Murph for higher-quality regional Indian TTS.
- **Reliability**: add SIP answer/no-answer detection beyond `wait_until_answered`, retry policies, per-call timeout, and dead-letter handling.
- **Observability**: ship logs to a log aggregator; add per-call trace IDs and success/funnel metrics (confirmation rate, retention success rate).
- **Security**: never commit `.env`; rotate the keys currently checked into the repo; add LiveKit token signing boundaries if exposing any HTTP API.
- **Testing**: add unit tests for `storage.py` validation + `prompts.py` rendering, and a mock-SIP integration test for `agent.py`.

---

## ⚠️ Security note

The current `.env` (and `personal.md`) contain live API keys checked into the
working tree. Before this repo goes anywhere shared, **rotate every key** and
make sure `.env` is git-ignored (it already is in `.gitignore`).
