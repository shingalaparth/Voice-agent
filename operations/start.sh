#!/bin/bash
# Single-container entrypoint: runs the LiveKit agent worker (executes calls)
# and the FastAPI server (accepts call requests) side by side. If either
# process dies, this script exits and lets `restart: unless-stopped` in
# docker-compose.yml bring the whole container back up.
set -e

# src/ must be on the path so `communication.*` imports resolve.
export PYTHONPATH="${PYTHONPATH:-/app/src}"

python -m communication.calling.agent start &
AGENT_PID=$!

uvicorn communication.api.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8080}" &
API_PID=$!

wait -n "$AGENT_PID" "$API_PID"
EXIT_CODE=$?
kill "$AGENT_PID" "$API_PID" 2>/dev/null || true
exit $EXIT_CODE
