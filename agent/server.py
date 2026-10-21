import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from langchain_core.messages import AIMessage, HumanMessage

from .executor import build_executor
from .tracing import configure_tracing

HOST = os.environ.get("AGENT_HOST", "0.0.0.0")
PORT = int(os.environ.get("AGENT_PORT", os.environ.get("PORT", "8080")))

configure_tracing()
EXECUTOR = build_executor()


def _turn(payload: dict) -> tuple[list, str]:
    history = []
    for message in payload.get("messages") or []:
        content = str(message.get("content") or "")
        if message.get("role") == "user":
            history.append(HumanMessage(content=content))
        elif message.get("role") == "assistant":
            history.append(AIMessage(content=content))
    new_message = str(payload.get("new_message") or "").strip()
    if not new_message and history and isinstance(history[-1], HumanMessage):
        new_message = history.pop().content
    elif history and isinstance(history[-1], HumanMessage) and history[-1].content == new_message:
        history.pop()
    return history, new_message


def respond(payload: dict) -> dict:
    history, new_message = _turn(payload)
    result = EXECUTOR.invoke({"input": new_message, "chat_history": history})
    tool_calls, tool_responses = [], []
    for position, (action, observation) in enumerate(result.get("intermediate_steps", [])):
        call_id = getattr(action, "tool_call_id", None) or f"call_{position}"
        tool_calls.append({"id": call_id, "name": action.tool, "arguments": action.tool_input})
        tool_responses.append({"id": call_id, "name": action.tool, "content": observation})
    return {
        "content": str(result.get("output") or ""),
        "tool_calls": tool_calls,
        "tool_responses": tool_responses,
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body):
        encoded = json.dumps(body, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            self._send(200, {"status": "ok"})
            return
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/chat":
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "request body must be JSON"})
            return
        if not isinstance(payload, dict):
            self._send(400, {"error": "request body must be a JSON object"})
            return
        self._send(200, respond(payload))

    def log_message(self, fmt, *args):
        return


def main():
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
