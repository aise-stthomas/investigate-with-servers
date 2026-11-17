"""Talk to a public MCP server you did not write. No model, no key, no SDK.

  uv run try_a_public_server.py                       DeepWiki's public server
  uv run try_a_public_server.py --repo owner/name     ask about another public GitHub repository
  uv run try_a_public_server.py --url <server URL>    any server that speaks 2026-07-28

It sends the discovery methods one at a time (server/discover, tools/list, prompts/list,
resources/list) and then one tools/call, printing what comes back. Every request carries its
protocol version and capabilities in _meta, and over HTTP the method also goes in a header.
"""
import argparse, itertools, json, urllib.error, urllib.request

VERSION = "2026-07-28"
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="https://mcp.deepwiki.com/mcp")
ap.add_argument("--repo", default="modelcontextprotocol/modelcontextprotocol")
args = ap.parse_args()
ids = itertools.count(1)


def send(method, params=None):
    message = {"jsonrpc": "2.0", "id": next(ids), "method": method, "params": {
        **(params or {}),
        "_meta": {"io.modelcontextprotocol/protocolVersion": VERSION,
                  "io.modelcontextprotocol/clientCapabilities": {},
                  "io.modelcontextprotocol/clientInfo": {"name": "investigate-with-servers", "version": "0.1.0"}}}}
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
               "MCP-Protocol-Version": VERSION, "Mcp-Method": method}
    if method == "tools/call":
        headers["Mcp-Name"] = params["name"]
    req = urllib.request.Request(args.url, json.dumps(message).encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode()
    # A reply is either one JSON object or a short event stream whose data line holds it.
    for line in body.splitlines():
        if line.startswith("data:"):
            body = line[5:].strip()
    return json.loads(body)


def show(title, reply, keep=600):
    print(f"\n== {title}")
    print("  " + json.dumps(reply)[:keep])


reply = send("server/discover")
show("server/discover: which versions, which capabilities", reply)

reply = send("tools/list")
tools = reply.get("result", {}).get("tools", [])
print(f"\n== tools/list: {len(tools)} tools")
for t in tools:
    print(f"  {t['name']:<24} {t['description'][:80]}")
    print(f"  {'':<24} arguments: {json.dumps(t['inputSchema'].get('properties', {}))[:80]}")

show("prompts/list", send("prompts/list"), 300)
show("resources/list", send("resources/list"), 300)

# One call: the first tool whose only required argument names a repository.
tool = next((t for t in tools if t["name"] == "read_wiki_structure"), None)
if tool:
    arg = tool["inputSchema"]["required"][0]
    reply = send("tools/call", {"name": tool["name"], "arguments": {arg: args.repo}})
    result = reply.get("result", {})
    text = "".join(c.get("text", "") for c in result.get("content", []))
    print(f"\n== tools/call {tool['name']}({arg}={args.repo!r})   isError: {result.get('isError', False)}")
    print("  " + text[:700].replace("\n", "\n  "))
