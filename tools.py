"""Function tools the Diorin agent can call during a call.

Replaces the demo `lookup_user` / `transfer_call` tools. Each call gets one
`OrderTools` instance that tracks the outcome (status, reason, retention) and
persists it to call_results/*.json via storage.save_result().

The LLM-facing tools are:
    confirm_order()               -> customer confirmed
    cancel_order(reason)          -> customer cancelled, capture the reason
    record_retention_successful() -> a retention attempt changed their mind
    save_callback_time(date, time) -> customer requested a callback at specific IST time
    mark_do_not_call()            -> customer opted out, don't call again
    mark_wrong_number()           -> wrong number reported
    mark_escalation_requested(r)   -> customer wants human agent
    save_call_result()            -> persist the final result (call before ending)

Possible final_status values:
    CONFIRMED | CANCELLED | CALLBACK_SCHEDULED | FAILED | UNKNOWN
    SILENT_NO_RESPONSE | CUSTOMER_HUNG_UP | WRONG_NUMBER | DO_NOT_CALL | ESCALATION_REQUESTED
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from livekit import agents
from livekit.agents import llm

from logger import logger
from storage import save_result
import config


class OrderTools:
    """Per-call business tools. Holds in-memory state + writes results to disk."""

    def __init__(self, customer: dict[str, Any], ctx: agents.JobContext) -> None:
        self.customer = customer
        self.ctx = ctx
        self.start_time: datetime = datetime.now(timezone.utc)

        # Outcome state — updated by the tools below.
        self.status: str = "UNKNOWN"           # CONFIRMED | CANCELLED | CALLBACK_SCHEDULED | UNKNOWN
        self.cancel_reason: str | None = None
        self.retention_attempted: bool = False
        self.retention_successful: bool = False
        self._saved: bool = False

        # Callback time (when customer asks to call back later)
        self.callback_date: str | None = None   # DD/MM/YYYY (IST)
        self.callback_time: str | None = None   # 12-hour AM/PM (IST)

        # Transcript tracking
        self.schema_version: int = 1
        self.transcript: list[dict[str, str]] = []

    # ------------------------------------------------------------------ helpers
    def _result_dict(self) -> dict[str, Any]:
        result = {
            "order_id": self.customer.get("order_id"),
            "customer_name": self.customer.get("name"),
            "phone_number": self.customer.get("phone"),
            "product_name": self.customer.get("product"),
            "order_amount": self.customer.get("amount"),
            "language": self.customer.get("language", "hi"),
            "final_status": self.status,
            "cancellation_reason": self.cancel_reason,
            "retention_attempted": self.retention_attempted,
            "retention_successful": self.retention_successful,
            "call_start_time": self.start_time.isoformat(),
            "call_end_time": datetime.now(timezone.utc).isoformat()
            if self._saved
            else None,
            "schema_version": self.schema_version,
            "transcript": self.transcript,
        }
        # Include callback time if the customer requested one
        if self.callback_date and self.callback_time:
            result["preferred_callback"] = {
                "date": self.callback_date,      # DD/MM/YYYY IST
                "time": self.callback_time,      # 12-hour AM/PM IST
                "timezone": "IST",
            }
        return result

    def persist(self) -> str | None:
        """Flush the current state to a result file. Idempotent per call.

        Public so agent.py's shutdown callback can guarantee a save even if the
        LLM never calls save_call_result() (e.g. customer hangs up mid-flow).
        
        Returns the absolute filepath of the saved JSON, or None if failed.
        """
        if config.ENABLE_TRANSCRIPTION and hasattr(self, "agent") and getattr(self.agent, "chat_ctx", None):
            self.transcript = []
            for m in self.agent.chat_ctx.messages():
                role = getattr(m, "role", "")
                if role not in ("user", "assistant"): continue
                
                content = getattr(m, "content", "")
                if isinstance(content, str): text = content
                elif isinstance(content, list):
                    text = "".join(getattr(c, "text", "") or str(c) for c in content)
                else: text = ""
                
                if text.strip():
                    created_at = getattr(m, "created_at", None)
                    if isinstance(created_at, (int, float)):
                        ts = datetime.fromtimestamp(created_at, timezone.utc).isoformat()
                    elif created_at:
                        ts = str(created_at)
                    else:
                        ts = datetime.now(timezone.utc).isoformat()
                        
                    self.transcript.append({
                        "speaker": "customer" if role == "user" else "agent",
                        "timestamp": ts,
                        "text": text.strip()
                    })

        try:
            out_path = save_result(self._result_dict())
            self._saved = True
            logger.info(
                "Result persisted to %s: status=%s reason=%s retention=%s/%s",
                out_path.name,
                self.status,
                self.cancel_reason,
                self.retention_successful,
                self.retention_attempted,
            )
            return str(out_path)
        except Exception as exc:  # never crash the call because of a write error
            logger.error("Failed to persist call result: %s", exc, exc_info=True)
            return None

    # ---------------------------------------------------------------- LLM tools
    @llm.function_tool(description="Call this the moment the customer confirms they want to keep the order.")
    async def confirm_order(self) -> str:
        self.status = "CONFIRMED"
        logger.info("Customer CONFIRMED the order (%s).", self.customer.get("order_id"))
        return "[ACTION_SUCCESS: MUST_CALL_SAVE_CALL_RESULT_NOW]"

    @llm.function_tool(description="Call this when the customer wants to cancel. Pass a short reason.")
    async def cancel_order(self, reason: str) -> str:
        self.status = "CANCELLED"
        self.cancel_reason = (reason or "").strip()[:500] or None
        self.retention_attempted = True
        logger.info(
            "Customer CANCELLED (%s). Reason: %s. Make exactly one polite retention attempt.",
            self.customer.get("order_id"),
            self.cancel_reason,
        )
        return "[ACTION_SUCCESS: EXECUTE_RETENTION_ATTEMPT_NOW]"

    @llm.function_tool(description="Call this ONLY if a retention attempt successfully changed the customer's mind back to keeping the order.")
    async def record_retention_successful(self) -> str:
        self.retention_successful = True
        self.status = "CONFIRMED"
        logger.info("Retention succeeded — order back to CONFIRMED (%s).", self.customer.get("order_id"))
        return "[ACTION_SUCCESS: MUST_CALL_SAVE_CALL_RESULT_NOW]"

    @llm.function_tool(description="Call this when the customer asks you to call back at a specific time. Pass date in DD/MM/YYYY format (IST) and time in 12-hour AM/PM format (IST).")
    async def save_callback_time(self, date: str, time: str) -> str:
        self.callback_date = (date or "").strip()
        self.callback_time = (time or "").strip()
        self.status = "CALLBACK_SCHEDULED"
        logger.info(
            "Customer requested callback on %s at %s IST (%s).",
            self.callback_date,
            self.callback_time,
            self.customer.get("order_id"),
        )
        return "[ACTION_SUCCESS: MUST_CALL_SAVE_CALL_RESULT_NOW]"

    @llm.function_tool(description="Call ONLY when the customer explicitly says 'don't call again', 'call mat karo', or 'remove my number'. Do NOT call for normal cancellations.")
    async def mark_do_not_call(self) -> str:
        self.status = "DO_NOT_CALL"
        logger.info("Customer opted out — DO_NOT_CALL (%s).", self.customer.get("order_id"))
        return "[ACTION_SUCCESS: END_CONVERSATION_NOW]"

    @llm.function_tool(description="Call ONLY when the customer says this is the wrong number.")
    async def mark_wrong_number(self) -> str:
        self.status = "WRONG_NUMBER"
        logger.info("Wrong number reported (%s).", self.customer.get("order_id"))
        return "[ACTION_SUCCESS: END_CONVERSATION_NOW]"

    @llm.function_tool(description="Call ONLY when the customer asks to speak to a human or manager. Do NOT call for normal order issues.")
    async def mark_escalation_requested(self, reason: str = "") -> str:
        self.status = "ESCALATION_REQUESTED"
        self.cancel_reason = (reason or "").strip()[:200] or "Customer requested human agent"
        logger.info("Escalation requested: %s (%s).", self.cancel_reason, self.customer.get("order_id"))
        return "[ACTION_SUCCESS: END_CONVERSATION_NOW]"

    @llm.function_tool(description="Call this right before ending the call to save the final result.")
    async def save_call_result(self) -> str:
        self.persist()
        return "[ACTION_SUCCESS: END_CONVERSATION_NOW]"
