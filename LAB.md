# Lab: investigate with servers

An investigation agent at a support desk: tool servers, workers, a plan, and runs that outlast
a process, each built from the same loop. Everything calls the model by plain HTTP and the
tool servers by plain JSON-RPC, so the code is the wire format.

## Setup

```bash
uv sync
cp .env.example .env          # paste your Gemini key
uv run reset.py               # fresh state
```

## Where everything is

| Path | What it is |
|---|---|
| `src/agent/` | the loop, the model, the trace, the toolbox, the runs table, compaction |
| `src/mcp/` | the protocol (version 2026-07-28), a server, a client |
| `src/servers/` | the desk's servers: `orders`, `payments`, `events`, each run by its own team |
| `src/desk/` | the investigation agent: instructions, workers, the plan, tool search, durable runs |
| `servers.toml` | the servers the desk connects to, with allow lists |
| `data/desk/seed.json` | the desk's orders, charges and tickets |
| `data/state/` | refunds, runs, approvals, cut results: emptied by `reset.py` |

## Section 1 · Follow the agents

Run each when the lecture reaches it. Each main is complete. Compare it with the one before,
for example `diff main_4_workers.py main_5_plan.py`.

| Main | Command | What it adds |
|---|---|---|
| 1 | `uv run main_1_server.py` | a tool server and a client, no model |
| 2 | `uv run main_2_servers.py` | the loop as a client of every server |
| 3 | `uv run main_3_curate.py` | only some tools in each request: allow lists and a search |
| 4 | `uv run main_4_workers.py` | a lead that hands work to workers |
| 5 | `uv run main_5_plan.py` | a plan the run writes, placed last in each request |
| 6 | `uv run main_6_checkpoint.py --crash-after 2`, then `uv run resume.py <run_id>` | the run as a row, then kill and resume |
| 7 | `uv run main_7_approval.py`, then `uv run approve.py <run_id>` | a person's approval, as a row |
| 8 | `uv run main_8_compact.py --budget 3000` | cut long results, summarize old turns |

Main 6 also takes `--crash-after-effect issue_refund`: the process exits right after the
refund, before the checkpoint. Resume it and read the second `issue_refund` result.

Run `uv run reset.py` between mains to start the desk over.

## Section 2 · Serve a tool

0. **Talk to a server you did not write.** `uv run try_a_public_server.py` sends the discovery
   methods to DeepWiki's public server and one `tools/call`. Try `--repo` with a public
   repository you know. Which methods return anything, and which tools does it offer?
1. **Write a server.** Copy `src/servers/events.py` to `src/servers/shipping.py` and give it
   one tool, `get_shipment(order_id)`, that returns a carrier, a tracking number and a status
   (make them up). Add it to `servers.toml` with an allow list.
2. **Talk to it with no model.** Change `main_1_server.py` to start your server, list its
   tools, and call yours. Read the request and the reply.
3. **Use it.** Run `uv run main_4_workers.py "Where is order 88213, and was I charged twice?"`.
   Did the lead send a worker to your server? What did the worker return?
4. **Over HTTP.** Run `uv run serve_http.py` in one terminal and, in another,
   `PAYMENTS_URL=http://localhost:8765/mcp uv run main_2_servers.py`. Nothing else changes.
5. **Behind a URL.** With a Learner Lab session, `./deploy.sh` puts the payments server in a
   function behind an API and prints its URL. Run Main 2 with `PAYMENTS_URL` set to it.
   `./teardown.sh` removes both.

## Keep

The tokens of the first request in Mains 2 and 3, the lead's and the events worker's largest
requests in Main 4, and the resumed run's second `issue_refund` result.