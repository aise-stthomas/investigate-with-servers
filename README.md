# investigate-with-servers

AI Systems Engineering lab. An agent at a support desk that reads other teams' systems
through tool servers, splits its work across workers, writes its run down after every step,
and waits for a person when it must.

- No SDK for the model (plain HTTP to the Gemini API) and none for the tool protocol (plain
  JSON-RPC, Model Context Protocol version 2026-07-28), so the code is the wire format.
- The instructions are in [LAB.md](LAB.md).

```bash
uv sync
cp .env.example .env            # your Gemini key
uv run reset.py
uv run main_1_server.py         # no key needed: our payments server
```

`measure.py` counts what each tool's declaration costs in tokens. Set `WIRE_DIR=<folder>` on
any run to record every model request and every protocol message there.
