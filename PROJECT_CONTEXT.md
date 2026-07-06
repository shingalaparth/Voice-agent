# Project Context Document

# 1. Project Overview
* **Project Name**: Diorin AI Calling Agent
* **Purpose**: An AI-driven outbound voice agent designed to confirm or retain customer cash-on-delivery (COD) orders for Diorin.
* **Current Stage**: Minimum Viable Product (MVP)
* **Primary Business Workflow**: Outbound calling to customers who placed COD orders to confirm the order, handle cancellation requests, and attempt customer retention.
* **Success Criteria**: The agent successfully initiates a call in Hindi, converses naturally, accurately categorizes the call outcome (confirmed, cancelled, retained), saves the transcript, and performs post-call analysis without crashing.

---

# 2. Business Goal
* **Problem Solved**: Automating the manual process of calling customers to verify COD orders, saving time and human resource costs.
* **Target Audience**: Customers who have placed COD orders on the Diorin platform.
* **Why AI Calling**: To provide a scalable, fast, and consistent way of verifying orders, reducing RTO (Return to Origin) rates by converting potential cancellations into successful deliveries through retention attempts.
* **Successful Call**: The agent verifies the customer's intent, updates the order status accurately based on the conversation, gracefully ends the call, and stores a complete analysis of the interaction.

---

# 3. Current MVP Scope
**In Scope:**
* Manual customer input (driven via a JSON payload).
* One outbound call at a time.
* Hindi language conversation.
* Order confirmation flow.
* Cancellation handling flow.
* Retention attempt (persuading the customer to keep the order).
* Persistence of call data to a local JSON file.
* Full transcript collection (both customer and agent).
* Post-call summary and analysis using Gemini.

**Not In Scope:**
* Web dashboards or UI.
* Relational database integration.
* User authentication or authorization.
* Multi-tenancy / SaaS capabilities.
* Campaign management or bulk dialing.

---

# 4. Technology Stack
* **LiveKit**: Core real-time voice and video infrastructure used to manage rooms and handle WebRTC audio streams.
* **Deepgram**: Used for high-quality, real-time Speech-to-Text (STT) processing to transcribe customer speech.
* **Groq**: Powers the fast, low-latency LLM inference during the live call conversation.
* **ElevenLabs**: High-fidelity Text-to-Speech (TTS) for natural, human-like agent voice generation.
* **Gemini**: Used for post-call analysis and summarization of transcripts due to its strong contextual understanding.
* **Vobiz SIP**: SIP trunk provider used to bridge LiveKit rooms to traditional PSTN phone numbers.
* **Python**: Primary backend programming language.
* **Local JSON storage**: Used as a simple, file-based database to store call results, metadata, and transcripts.

---

# 5. Repository Structure
* **`agent.py`**: The core AI agent logic. Handles the LiveKit connection, voice agent initialization, and event callbacks (like agent speech, user speech, and call disconnection).
* **`config.py`**: Centralized configuration management. Loads all environment variables and API keys (LiveKit, ElevenLabs, Groq, Gemini) required for the system.
* **`prompts.py`**: Stores the system prompts and behavioral instructions that guide the Groq LLM on how to converse with the customer.
* **`tools.py`**: Contains callable tool functions (e.g., `mark_confirmed`, `cancel_order`) that the agent LLM can trigger during the conversation to signal business intent.
* **`storage.py`**: Handles all file I/O operations. Responsible for reading initial customer data and saving the final JSON payload including transcripts and outcomes.
* **`analysis_service.py`**: A decoupled, asynchronous background service that reads saved call transcripts, sends them to Gemini for structured analysis, and updates the JSON file.
* **`logger.py`**: Configures customized, structured logging to help track the system state and debug issues across the pipeline.
* **`make_call.py`**: The entrypoint script used to dispatch an outbound SIP call using the LiveKit Cloud API.

---

# 6. Complete Call Lifecycle
1. **Customer data loaded** (from JSON)
2. **Agent dispatched** (via `make_call.py`)
3. **LiveKit room created**
4. **SIP call initiated** (via Vobiz)
5. **Customer answers**
6. **Greeting** (Agent speaks first)
7. **Conversation** (Groq + Deepgram + ElevenLabs loop)
8. **Transcript collection** (In-memory aggregation of events)
9. **Business outcome** (Tool triggered by Groq)
10. **Call ends** (Agent auto-disconnects gracefully)
11. **JSON saved** (Transcript and raw status written by `storage.py`)
12. **Gemini analysis** (Triggered via `analysis_service.py`)
13. **JSON updated** (Appends structured analysis and metadata)
14. **Worker becomes idle**

---

# 7. Folder Structure
The project uses a flat, functional folder structure tailored for a single-agent MVP. Scripts are grouped in the root directory for simplicity. 
`call_results/` holds all output JSONs, and `logs/` holds application logs. 
Larger structural refactoring (like domain-driven modules) is intentionally deferred until multiple agent types or web services are introduced.

---

# 8. Current Features
### Completed
* Outbound SIP calling via LiveKit and Vobiz.
* Full conversational loop (STT -> LLM -> TTS) in Hindi.
* Automated tool execution for order confirmation and cancellation.
* Complete transcript capture.
* Graceful call auto-disconnect.
* Post-call JSON data persistence.
* Asynchronous Gemini-powered call analysis.

### In Progress
* Hardening error boundaries (especially around API rate limits and async loop closures).

### Planned
* Dashboard integration for viewing call results.
* Bulk dialing support.

---

# 9. Conversation Flow
1. **Greeting**: Agent identifies itself as Diorin and references the specific COD order.
2. **Identity Verification**: Confirming the customer is the correct person.
3. **Order Confirmation**: Asking if they still want the order.
4. **Cancellation**: If requested, gracefully acknowledging the request.
5. **Retention**: If cancelling, attempting to persuade the customer by highlighting delivery speed or product popularity.
6. **Goodbye**: Thanking the customer appropriately based on the outcome.
7. **Automatic disconnect**: Terminating the SIP session once the business logic is complete.

---

# 10. Transcript System
* **Collection**: Collected in memory during the LiveKit room session by listening to agent transcription and user transcription events.
* **Format**: A sequential array of objects, containing `speaker` ("agent" or "customer"), `timestamp`, and the `text` spoken.
* **Storage**: Saved directly into the output JSON document when the call ends.
* **Purpose**: Capturing both sides ensures the post-call Gemini analysis has full context to determine sentiment, actual intent, and agent performance.

---

# 11. Gemini Analysis
* **When it runs**: Immediately after the call concludes and the initial JSON is saved to disk.
* **Why decoupled**: Running after the call prevents blocking the real-time voice pipeline and ensures the customer isn't waiting on a slow LLM response before the call ends.
* **Output**: A highly structured JSON object including summary, outcome, sentiment, customer questions, key points, and AI performance notes.
* **Error Handling**: Wraps the LLM call in a `try/except` block; if it fails, the original transcript JSON remains intact, preventing data loss.

---

# 12. JSON Structure
The output JSON (`call_results/<timestamp>_<order_id>.json`) contains:
* `order_id`: (String) Unique identifier for the order.
* `customer_name`: (String) Name of the customer.
* `phone_number`: (String) The dialed number.
* `product_name`: (String) The product in question.
* `order_amount`: (String) The value of the order.
* `language`: (String) Language of the call (e.g., "hi").
* `final_status`: (String) End state (e.g., "CONFIRMED", "CANCELLED").
* `cancellation_reason`: (String) Extracted reason if cancelled.
* `retention_attempted`: (Boolean) Did the agent try to save the sale?
* `retention_successful`: (Boolean) Did the customer change their mind?
* `call_start_time` / `call_end_time`: (String) Timestamps.
* `schema_version`: (Int) Used for tracking structural changes to the JSON.
* `transcript`: (Array) List of timestamped conversational turns.
* `call_duration_seconds`: (Float) Total length of the call.
* `conversation_analysis`: (Object) Gemini-generated summary, sentiment, outcome, and points.
* `metadata`: (Object) Processing metadata like `analysis_duration_ms` and the Gemini model used.

---

# 13. Error Handling
* **Global exception handling**: Top-level loops catch and log unhandled exceptions to prevent hard crashes.
* **Shutdown callbacks**: LiveKit room disconnection events are wired to ensure all resources are freed.
* **Gemini failures**: The background task catches network/API errors from Gemini and safely ignores them, ensuring core call data is still saved.
* **LiveKit failures**: Connection drops are treated as a call-end, triggering the standard save and teardown flow.

---

# 14. Logging
* **What is logged**: Application lifecycle events, LLM prompt generation, tool triggers, connection state changes, and caught exceptions.
* **Why**: To provide an audit trail for failed calls or unexpected AI behaviors.
* **Format**: Structured text, typically including timestamps and log levels (INFO, WARNING, ERROR).

---

# 15. Known Bugs & Lessons Learned
* **Agent exiting before speaking**: Resolved by ensuring the LiveKit room remains open until the TTS buffer is fully flushed and a "goodbye" message completes.
* **Unhandled async exceptions**: Async tasks (like transcript saves) occasionally failed during teardown; resolved by properly awaiting background tasks or running them in detached, safe loops.
* **Missing auto-disconnect**: Early versions left SIP trunks hanging; resolved by implementing explicit room disconnect calls after final tool execution.

---

# 16. Coding Guidelines
* **Reuse existing architecture**: Do not rewrite working pipelines.
* **Don't over-engineer**: Keep the MVP simple. Avoid introducing abstract classes, interfaces, or complex design patterns for a single script.
* **Preserve real-time isolation**: Never add blocking operations (like database writes or heavy LLM processing) to the live conversation loop.
* **Backward compatibility**: If modifying the output JSON, increment `schema_version` and ensure old fields are not deleted without reason.
* **Focus on stability**: The voice pipeline is fragile. Do not introduce changes that could affect latency or audio stream processing.

---

# 17. Roadmap
*(These are future goals, not current implementation targets)*
* Web Dashboard for monitoring calls and results.
* Multiple AI agent personas.
* Multi-user SaaS model.
* Relational database integration (PostgreSQL).
* Call analytics and campaign management.

---

# 18. How to Work on This Project
* **Always analyze the repository before making changes.** Start by reading this document and exploring `agent.py`.
* **Understand the current architecture first.** Recognize the split between real-time processing and post-call processing.
* **Explain the implementation plan before coding.** Present your solution to the user before editing files.
* **Avoid unrelated refactoring.** Do not format or refactor files unless explicitly asked to do so.
* **Keep changes focused.** Only touch the files necessary to complete the requested feature.
* **Verify non-breaking changes.** Ensure that new features (like dashboards) do not break the existing LiveKit voice pipeline.
* **Preserve the stability of the voice pipeline.**
