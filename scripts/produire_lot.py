"""Produit un lot de panneaux dans Blender via le service MCP.
Usage : BLENDER_MCP_URL=... BLENDER_MCP_KEY=... python produire_lot.py items.json
items.json : [{"code","svg","path","width_m","height_m","meta":{...}}, ...]
"""
import os, sys, json, ast, time, requests
U = os.environ["BLENDER_MCP_URL"]; K = os.environ["BLENDER_MCP_KEY"]
H = {"Authorization": "Bearer " + K, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
def rpc(body, sid=None):
    h = dict(H)
    if sid: h["Mcp-Session-Id"] = sid
    r = requests.post(U, headers=h, data=json.dumps(body), timeout=290)
    t = r.text
    if "data:" in t: t = "".join(l[5:] for l in t.splitlines() if l.startswith("data:"))
    return r.headers.get("Mcp-Session-Id"), t
def init():
    sid, _ = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "lot", "version": "1"}}})
    rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    return sid
items = json.load(open(sys.argv[1])); sid = init(); out = []; N = 3
for i in range(0, len(items), N):
    chunk = items[i:i + N]
    code = "exec(open('/projects/catalogue_panneaux/gen_svg.py').read())\nresult=run_batch(%r)" % (chunk,)
    for attempt in range(6):
        try:
            _, t = rpc({"jsonrpc": "2.0", "id": 100 + i, "method": "tools/call", "params": {"name": "execute_python", "arguments": {"code": code}}}, sid)
            txt = json.loads(t)["result"]["content"][0]["text"]
            out += ast.literal_eval(txt.split("Result: ", 1)[1].split("\n\n_context")[0]); break
        except Exception:
            time.sleep(20); sid = init()
json.dump(out, open("resultats.json", "w"), indent=1)
