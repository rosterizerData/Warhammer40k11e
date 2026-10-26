"""Scenario helper for the headless runner: build a Crusade roster, run it, read back errors and stats.

  import scen
  r = scen.roster('Plague Company', size='Strike Force', play='Narrative', units=[
          scen.unit('Character§Lord of Virulence', xp=31, included=['Crusade Honour§Veil of Flies']),
      ], roster_traits=[scen.campaign('Armageddon')])
  res = scen.run('Death_Guard', r)       # dict: errors (list of (asset, msg)), tree (pruned json), raw
  scen.show(res)                          # prints assets with their errors

RZ_MJS (env) points at the bundled runner; NODE at node 24.
"""
import json, os, subprocess, tempfile
from pathlib import Path

S = os.environ.get("RZ_SCRATCH") or "/private/tmp/claude-502/-Users-kduda-websites-RosterizerData/0e523f25-d5fe-4274-b312-15bc7891bae1/scratchpad"
RZ_MJS = os.environ.get("RZ_MJS") or f"{S}/rz.mjs"
NODE = os.environ.get("NODE") or os.path.expanduser("~/.nvm/versions/node/v24.11.1/bin/node")


def unit(item, *, xp=None, included=(), traits=(), stats=None):
    u = {"item": item}
    st = dict(stats or {})
    if xp is not None:
        st["Experience"] = {"value": xp}
    if st:
        u["stats"] = st
    a = {}
    if included:
        a["included"] = [x if isinstance(x, dict) else {"item": x} for x in included]
    if traits:
        a["traits"] = [x if isinstance(x, dict) else {"item": x} for x in traits]
    if a:
        u["assets"] = a
    return u


def campaign(mission=None, *, phases=None, alliance=None):
    c = {"item": "Campaign§Campaign", "stats": {}}
    if mission:
        c["stats"]["Mission"] = {"value": mission}
    if alliance:
        c["stats"]["Alliance"] = {"value": alliance}
    if phases:
        c["assets"] = {"traits": phases}
    return c


def phase(n, records=()):
    return {"item": f"Campaign Phase§Phase {n}", "assets": {"included": list(records)}}


def record(agenda1=None, agenda2=None, **stats):
    st = {k.replace("_", " "): {"value": v} for k, v in stats.items()}
    if agenda1:
        st["Agenda 1"] = {"value": agenda1}
    if agenda2:
        st["Agenda 2"] = {"value": agenda2}
    return {"item": "Mission Record§Mission Record", "stats": st}


def oob(included=()):
    return {"item": "Order of Battle§Order of Battle", "assets": {"included": [x if isinstance(x, dict) else {"item": x} for x in included]}}


def roster(detachment, *, size="Strike Force", play="Narrative", units=(), roster_traits=(), stats=None, legends=False):
    st = {"Battle Size": {"value": size}, "Detachment": {"value": [detachment] if isinstance(detachment, str) else list(detachment)}, "Play": {"value": play}}
    if legends:
        st["Legends"] = {"value": "✓"}
    st.update(stats or {})
    r = {"item": "Roster§Roster", "stats": st, "assets": {"included": list(units)}}
    if roster_traits:
        r["assets"]["traits"] = list(roster_traits)
    return r


def run(book, ros, *, json_dump=True, timeout=120):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=S) as f:
        json.dump(ros, f, ensure_ascii=False)
        rp = f.name
    out = rp + ".out.json"
    cmd = [NODE, RZ_MJS, book, rp] + (["--json", out] if json_dump else [])
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tree = json.load(open(out)) if json_dump and os.path.exists(out) else None
    errors = []

    def walk(a, path=""):
        if not isinstance(a, dict):
            return
        nm = path + ("/" if path else "") + (a.get("designation") or a.get("item") or "?")
        for e in a.get("errors") or []:
            errors.append((nm, e))
        for t in (a.get("traits") or []) + (a.get("included") or []):
            walk(t, nm)
    if tree:
        walk(tree)
    return {"errors": errors, "tree": tree, "stdout": p.stdout, "stderr": p.stderr, "rc": p.returncode}


def find(tree, item):
    """first node whose item or designation equals/startswith item"""
    hit = []

    def walk(a):
        if hit or not isinstance(a, dict):
            return
        if (a.get("item") or "") == item or (a.get("designation") or "") == item or (a.get("item") or "").startswith(item):
            hit.append(a)
            return
        for t in (a.get("traits") or []) + (a.get("included") or []):
            walk(t)
    walk(tree)
    return hit[0] if hit else None


def stat(node, name):
    s = (node or {}).get("stats", {}).get(name)
    return None if s is None else {"value": s.get("value"), "current": s.get("current"), "max": s.get("max"), "visibility": s.get("visibility")}


def show(res, only_errors=False, depth=3):
    if res["rc"] != 0 and not res["tree"]:
        print("RUN FAILED", res["stderr"][-800:])
        return
    def walk(a, d=0):
        if not isinstance(a, dict) or d > depth:
            return
        errs = a.get("errors") or []
        if errs or not only_errors:
            print("  " * d + (a.get("designation") or a.get("item") or "?") + (("  ERRORS: " + " | ".join(errs)) if errs else ""))
        for t in (a.get("traits") or []) + (a.get("included") or []):
            walk(t, d + 1)
    walk(res["tree"])
