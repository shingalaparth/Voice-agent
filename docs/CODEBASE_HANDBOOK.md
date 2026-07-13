# Diorin AI Voice Agent: Complete Codebase Handbook

This document is a complete, file-by-file breakdown of the entire Voice Agent project. It is designed to be easily readable by **non-technical team members** (to understand *why* a file exists) and highly detailed for **developers** (to understand *how* the code works and what to edit in the future).

---

## 🧠 1. The Core AI Engine

### `agent.py`
* **For Normal People:** This is the actual "brain" of the AI caller. When a call is triggered, this file picks up the phone, listens to the customer, thinks about what to say, and speaks back. It also makes sure the final result is saved when the call hangs up.
* **For Developers:** The LiveKit worker entrypoint. It initializes the `AgentSession` linking Deepgram (STT), Groq (LLM), and ElevenLabs (TTS). It handles the SIP dial-out (`create_sip_participant`), manages silence/re-prompting, and registers a shutdown callback to guarantee that transcripts and webhook deliveries happen even if the customer unexpectedly hangs up.
* **Why it exists:** Without this, there is no AI. This file orchestrates the real-time audio streams.

### `prompts.py`
* **For Normal People:** This is the script the AI follows. It contains the exact words the AI will use to greet the customer, and the rules it must follow (like "be polite," "speak in Hindi," and "try to save the order if they cancel").
* **For Developers:** Contains Python functions (`build_system_prompt`, `build_greeting`) that dynamically inject customer data (like `{{name}}` and `{{amount}}`) into the Groq LLM system instructions. 
* **Why it exists:** To separate the AI's "personality" and conversation rules from the complex networking code in `agent.py`. If you want to change how the AI talks, you only edit this file.

### `tools.py`
* **For Normal People:** These are the "buttons" the AI can press during a call. If the customer says "Yes, I want the order," the AI presses the `Confirm` button. If they say "No," the AI presses the `Cancel` button and asks why. 
* **For Developers:** Defines the `OrderTools` class using LiveKit's `@ai.tool` decorators. It exposes callable functions to the LLM (`confirm_order`, `cancel_order`, `record_retention_successful`). It tracks the call state in memory and handles the final trigger to persist data to disk.
* **Why it exists:** LLMs can only talk. Tools allow the LLM to take *actions* that affect your business logic. 

### `analysis_service.py`
* **For Normal People:** The "Quality Assurance" reviewer. After the call ends, this file reads the entire conversation text and uses a smarter AI (Gemini) to write a summary, judge the customer's mood, and grade how well the AI did.
* **For Developers:** An asynchronous background service that reads the saved JSON transcript, sends it to Google's Gemini LLM with a strict JSON-schema prompt, and appends the structured analysis (sentiment, summary, retention success) back into the file.
* **Why it exists:** Real-time AI (Groq) is fast but sometimes misses the big picture. Gemini is slower but smarter, so we run it *after* the call so the customer doesn't have to wait on the phone.

---

## 🌐 2. The API & Web Server (How to trigger calls)

### `main.py`
* **For Normal People:** The front door of the system for other software. If your website or Shopify store wants to tell the AI to make a call, it sends a message here.
* **For Developers:** A FastAPI application. It exposes `POST /v1/calls` to accept incoming JSON requests, validates them, and triggers the LiveKit room creation. It also exposes `GET /health` for server monitoring.
* **Why it exists:** To allow the voice agent to be integrated into external platforms automatically, rather than requiring a human to type commands in a terminal.

### `dispatch.py`
* **For Normal People:** The dispatcher. Once a call request is received, this file creates a secure "room" and tells an available AI worker (`agent.py`) to enter the room and dial the number.
* **For Developers:** Contains the `dispatch_call()` function. It handles the LiveKit Server API logic to create a `CreateAgentDispatchRequest`, passing the customer data as secure metadata so the worker can read it.
* **Why it exists:** To share the dispatching logic so both the HTTP API (`main.py`) and the manual terminal command (`make_call.py`) use the exact same code to start a call.

### `schemas.py`
* **For Normal People:** The rulebook for data. It ensures that when someone asks the system to make a call, they don't forget important details like the phone number or the order amount.
* **For Developers:** Defines Pydantic models (`CallRequest`, `CallAcceptedResponse`). These provide automatic validation and generate the OpenAPI/Swagger documentation.
* **Why it exists:** To prevent bad data (like missing phone numbers) from crashing the AI during a live call.

### `auth.py`
* **For Normal People:** The security guard. It checks the secret password (API Key) before allowing an external system to trigger a call.
* **For Developers:** A FastAPI dependency that reads the `Authorization: Bearer <token>` header and compares it against the `API_KEY` environment variable.
* **Why it exists:** To prevent hackers from finding your server and making thousands of expensive AI calls on your dime.

### `webhook.py`
* **For Normal People:** The messenger. Once a call is totally finished, this file packages up the final result (confirmed/cancelled) and sends it back to your website or database so your system knows what happened.
* **For Developers:** Handles outbound HTTP POST requests using `httpx`. It signs the payload with HMAC-SHA256 (using `WEBHOOK_SECRET`) so the receiving server can verify the data is authentic, and uses `tenacity` to retry if the receiver is down.
* **Why it exists:** Because the API is stateless. You trigger a call and disconnect. The webhook is the only way your backend finds out the result of the call later.

---

## 🛠️ 3. Setup, Config, & Manual Tools

### `config.py`
* **For Normal People:** The settings menu. It holds all the secret passwords for the AI providers (Deepgram, ElevenLabs, etc.) and settings like default language or AI voice choices. 
* **For Developers:** Uses Python `os.getenv` to load `.env` variables. It provides a `validate_env()` function that runs on startup to crash the app *early* if a required API key is missing, rather than failing mid-call.
* **Why it exists:** Centralizes all configuration so you don't have API keys or settings scattered across 10 different files.

### `make_call.py` & `customer.json`
* **For Normal People:** The manual testing tools. You type a customer's name and number into `customer.json`, then run `make_call.py` on your computer to force the AI to call them immediately.
* **For Developers:** A CLI script that reads `customer.json`, validates the fields, and calls `dispatch.py`. 
* **Why it exists:** For local testing and debugging without needing to send complex HTTP requests via Postman.

### `storage.py` & `logger.py`
* **For Normal People:** The filing cabinets. `storage.py` saves the final call transcripts to your hard drive. `logger.py` writes down everything the system is doing (like "Call started," "Error happened") into log files so you can investigate if something breaks.
* **For Developers:** `storage.py` handles atomic JSON file writing to `call_results/`. `logger.py` configures Python's standard `logging` module to output to both the console and rotating files in `logs/`.
* **Why it exists:** To ensure you never lose data and can always debug historical issues.

### `create_trunk.py` & `list_trunks.py`
* **For Normal People:** Telephone wires. These are setup scripts run once to connect the LiveKit system to Vobiz (the telecom provider that actually dials real phone numbers).
* **For Developers:** Utility scripts that interact with the LiveKit SIP API to configure inbound/outbound SIP trunks.
* **Why it exists:** To configure the telephony bridge programmatically instead of clicking through a UI.

---

## 🐳 4. Deployment (Docker)

### `Dockerfile`, `docker-compose.yml`, & `start.sh`
* **For Normal People:** The shipping container. These files bundle the entire project into a neat package so it can be uploaded to an AWS or Google Cloud server and run perfectly with one command.
* **For Developers:** The `Dockerfile` packages the Python environment. `docker-compose.yml` configures network modes and environment variables. `start.sh` is the entrypoint that runs *both* `agent.py` (the worker) and `main.py` (the API server) side-by-side in the same container.
* **Why it exists:** To ensure the code runs identically on the developer's laptop and the production server.
