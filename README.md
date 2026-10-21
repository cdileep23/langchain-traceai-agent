# Harbor Hotels booking agent (LangChain, traceAI)

A chat booking assistant for Harbor Hotels, a fictional hotel chain. It is a LangChain
tool-calling agent (`create_tool_calling_agent` + `AgentExecutor`) on an Anthropic Claude chat model (`langchain-anthropic`) with
three tools, traced with Future AGI's traceAI (`fi_instrumentation` + `traceai_langchain`).

## HTTP interface

| Method | Path      | Purpose                                   |
|--------|-----------|-------------------------------------------|
| POST   | `/chat`   | One conversation turn.                    |
| GET    | `/health` | Readiness probe. Returns `{"status":"ok"}`. |

Listens on port `8080`, overridable with `AGENT_PORT`.

Request (the FutureAGI agent callback envelope; only `messages` and `new_message` are read):

```json
{"turn_index": 0, "messages": [{"role": "user", "content": "check HB-5001"}], "new_message": "check HB-5001"}
```

Response:

```json
{
  "content": "Booking HB-5001 for Ana Silva at Harbor Lisbon Riverside is confirmed from 2026-11-02 for 3 nights.",
  "tool_calls": [{"id": "call_1", "name": "get_booking", "arguments": {"booking_id": "HB-5001"}}],
  "tool_responses": [{"id": "call_1", "name": "get_booking", "content": {"found": true}}]
}
```

## Tools

| Tool             | Arguments                    | Behaviour                                                |
|------------------|------------------------------|----------------------------------------------------------|
| `find_hotels`    | `city`, `max_nightly_rate`   | Hotels in a city, optionally under a nightly rate.       |
| `get_booking`    | `booking_id`                 | Guest, hotel, dates and status of a booking.             |
| `cancel_booking` | `booking_id`                 | Cancels only a confirmed booking.                        |

Fixture bookings: `HB-5001` confirmed (cancellable), `HB-5002` checked in, `HB-5003` cancelled.
Any other id is not found. Hotels exist in Lisbon, Berlin and Tokyo. Data is in memory and
resets on restart.

## Configuration

| Variable                          | Purpose                                                  |
|-----------------------------------|----------------------------------------------------------|
| `ANTHROPIC_API_KEY`                   | Required. The Anthropic API key. |
| `ANTHROPIC_MODEL`                     | Optional, default `claude-haiku-5-5`. |
| `FI_API_KEY`, `FI_SECRET_KEY`     | Optional. When both are set, traceAI sends traces.       |
| `FI_PROJECT_NAME`                 | Optional, default `harbor-hotels-langchain-agent`.       |

## Running it

```
pip install -r requirements.txt
ANTHROPIC_API_KEY=... python -m agent.server
curl -s localhost:8080/chat -H 'content-type: application/json' -d '{"new_message":"hotels in Lisbon under 150","messages":[]}'
```
