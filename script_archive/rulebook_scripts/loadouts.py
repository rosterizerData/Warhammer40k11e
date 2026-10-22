"""Wire 11e wargear options from a per-book spec (loadout_specs/<Book>.py) into Loadout rank stats.

  python3 loadouts.py <Book> [--apply] [--prune]

Spec: SPEC = {"<unit name>": {"<holder>": {...}, "_limits": [...]}}, holder = "_unit" or a "Model§…" key.
  holder: {"static": [weapon…], "slots": {"<stat name>": [rank…]}, "keep": [stat names to leave alone]}
    rank: "A + B" (several weapons), "2x A", "-" (nothing), suffix " @tag" adds tracking {tag: 1};
          the first rank is the default. A rank can also be (label, "A + B @tag").
  _limits: [(tag, cap, "Rule name")], cap = int, "1inN" (core count1inN) or "1inN*k".
  _drop_rules / _drop_stats: names removed from the unit (old limit rules, 10e convenience stats).
Weapon names resolve to `<Kind> Weapon§<Unit>—<name>` (multi-profile parent preferred), then the faction
armoury, a generic `<Kind> Weapon§<name>`, then `Wargear§<name>`. Ranks replace a holder's weapon traits; non-weapon
traits stay. Re-running is idempotent. --prune deletes per-unit weapons of the specced units that nothing references.
"""
import importlib.util, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import waha_lib as W

RZ = Path(__file__).resolve().parents[2]
book = sys.argv[1]
APPLY, PRUNE = "--apply" in sys.argv, "--prune" in sys.argv
spec_path = Path(__file__).parent / "loadout_specs" / f"{book}.py"
sp = importlib.util.spec_from_file_location("spec", spec_path); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
SPEC = mod.SPEC

raw = W.load_books()
own = raw[book]["rulebook"]["assetCatalog"]
res = W.resolved(raw, book)

UNITCLS = ("Unit", "Character", "Vehicle", "Infantry/Mounted", "Titan")
WEP = ("Ranged Weapon", "Melee Weapon", "Weapon")
def n(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("’", "'").replace("ʼ", "'"))
def sing(s): return re.sub(r"(?<=[a-z])s$", "", s)
faction = None
errors, log = [], []

_wg = {}
def waha_wargear(unit):
    """Wargear-type abilities on the unit's Waha datasheet: {name without '(Once per battle…)': markdown text}"""
    if unit not in _wg:
        dss = [d for d in W.ds.values() if n(d["name"]) == n(unit) and W.book_of_datasheet(d) == book and d.get("virtual") != "true"]
        _wg[unit] = {re.sub(r"\s*\(.*?\)\s*$", "", a["name"]).strip(): W.md(a["description"])
                     for d in dss for a in W.abils[d["id"]] if a["type"] == "Wargear" and a["name"]}
    return _wg[unit]

KIND = {"R": ("Ranged Weapon",), "M": ("Melee Weapon",), "W": ("Weapon",)}
def resolve_weapon(unit, name):
    m = re.match(r"^([RMW]):(.*)$", name)
    kinds, name = (KIND[m.group(1)], m.group(2)) if m else (WEP, name)
    want = n(name)
    def pick(pred):
        hits = [k for k in res if pred(k)]
        parents = [k for k in hits if " – " not in k.split("§", 1)[1]]
        return (parents or hits or [None])[0]
    for cmp in (lambda a: n(a) == want, lambda a: sing(n(a)) == sing(want)):
        k = pick(lambda k: k.split("§")[0] in kinds and "—" in k and n(k.split("§", 1)[1].split("—")[0]) == n(unit) and cmp(k.split("—", 1)[1]))
        if k: return k
        k = pick(lambda k: k.split("§")[0] in kinds and "Armoury—" in k and cmp(k.split("—", 1)[1]))
        if k: return k
        k = pick(lambda k: k.split("§")[0] in kinds and "—" not in k and cmp(k.split("§", 1)[1]))
        if k: return k
        wg = waha_wargear(unit)
        hit = next((nm for nm in wg if cmp(nm)), None)
        if hit:
            k, text = f"Wargear§{hit}", wg[hit]
            k = next((x for x in res if x.startswith("Wargear§") and n(x[8:]) == n(hit)), k)
            if (res.get(k) or {}).get("text") != text:
                log.append(f"WARGEAR {k}: text from Waha" + (" (new)" if k not in res else ""))
                own.setdefault(k, {})["text"] = text
                res[k] = {**(res.get(k) or {}), "text": text}
            return k
        k = pick(lambda k: k.startswith("Wargear§") and cmp(re.sub(r"^.*—", "", k.split("§", 1)[1])))
        if k: return k
    errors.append(f"{unit}: no asset for weapon '{name}'")
    return None

def parse_rank(unit, r):
    label, body = r if isinstance(r, tuple) else (None, r)
    tags = re.findall(r"@(\w+)(?:=(\d+))?", body); body = re.sub(r"\s*@\w+(=\d+)?", "", body).strip()
    traits = []
    if body != "-":
        for part in [p.strip() for p in body.split(" + ")]:
            m = re.match(r"^(\d+)x\s+(.*)$", part)
            q, nm = (int(m.group(1)), m.group(2)) if m else (1, part)
            k = resolve_weapon(unit, nm)
            traits += [{"trait": k}] * q if k else []
    if label is None:
        label = re.sub(r"\b(\d+)x ", r"\1 ", re.sub(r"\b[RMW]:", "", body).replace(" + ", " & "))
    out = {"traits": traits} if traits else {}
    if tags:
        out["tracking"] = {t: int(q or 1) for t, q in tags}
    return label, out

def limit_rule(tag, cap):
    if isinstance(cap, int):
        mx = cap
    else:
        m = re.match(r"^1in(\d+)(?:\*(\d+))?$", cap)
        mx = ["{self}", "rules", f"count1in{m.group(1)}", "evals", "0", "result", "integer"]
        if m.group(2):   # k per N: no core rule multiplies, so give an own count rule
            return None
    return {"evals": [{"actionable": True, "max": mx, "not": False, "operator": "AND", "paths": [["{self}", "tracked", tag]]}],
            "evaluate": "AND", "failState": "error"}

def is_wep_trait(t):
    k = t if isinstance(t, str) else t.get("item")
    return isinstance(k, str) and k.split("§")[0] in WEP

def holder_asset(key):
    if key not in own:
        errors.append(f"{key}: not defined in {book} (hub override not supported yet)")
        return None
    return own[key]

def referenced(keys):
    everything = json.dumps(raw, ensure_ascii=False)
    return {k for k in keys if everything.count(f'"{k}"') > 1}
ORPHANABLE = lambda k: k.split("§")[0] in ("Wargear", "Model") or k.split("§")[0] in WEP
was_referenced = referenced([k for k in own if ORPHANABLE(k)])

touched_units = []
for uname, uspec in SPEC.items():
    uk = next((k for k in own if k.split("§")[0] in UNITCLS and n(k.split("§", 1)[1]) == n(uname)), None)
    if not uk:
        errors.append(f"unit '{uname}' not in {book}"); continue
    touched_units.append(uk)
    wunit = uspec.get("_weapons_of", uname)
    for hk, hs in uspec.items():
        if hk.startswith("_") and hk != "_unit":
            continue
        key = uk if hk == "_unit" else hk
        a = holder_asset(key)
        if a is None: continue
        st = a.setdefault("stats", {})
        keep = set(hs.get("keep", []))
        for sn in [s for s, v in st.items() if isinstance(v, dict) and v.get("group") == "Loadout" and v.get("statType") == "rank" and s not in keep]:
            del st[sn]
        tr = (a.setdefault("assets", {})).setdefault("traits", [])
        a["assets"]["traits"] = [t for t in tr if not is_wep_trait(t)]
        for w in hs.get("static", []):
            m = re.match(r"^(\d+)x\s+(.*)$", w)
            q, nm = (int(m.group(1)), m.group(2)) if m else (1, w)
            k = resolve_weapon(wunit, nm)
            if k: a["assets"]["traits"] += [k] * q
        for sn, ranks in (hs.get("slots") or {}).items():
            rk = {}
            for i, r in enumerate(ranks):
                label, body = parse_rank(wunit, r)
                rk[label] = {"order": i, **body}
            st[sn] = {"dynamic": True, "group": "Loadout", "groupOrder": 2, "ranks": rk, "statType": "rank",
                      "value": next(iter(rk)), "visibility": "active"}
        if not a["assets"]["traits"]:
            del a["assets"]["traits"]
        if not a["assets"]:
            del a["assets"]
        log.append(f"{key}: static {hs.get('static', [])} slots {list((hs.get('slots') or {}).keys())}")
    ua = own[uk]
    rules = ua.setdefault("rules", {})
    for rn in uspec.get("_drop_rules", []):
        if rules.pop(rn, None) is not None: log.append(f"{uk}: dropped rule '{rn}'")
    for sn in uspec.get("_drop_stats", []):
        if (ua.get("stats") or {}).pop(sn, None) is not None: log.append(f"{uk}: dropped stat '{sn}'")
    for tag, cap, rn in uspec.get("_limits", []):
        r = limit_rule(tag, cap)
        if r: rules[rn] = r
    rules.update(uspec.get("_rules", {}))
    if "_warning" in uspec:   # a reading of the option text that needs a human check
        w = f"WARNING: loadout — {uspec['_warning']}"
        body = re.sub(r"^WARNING: loadout — [^\n]*(\n\n)?", "", ua.get("text") or "")
        ua["text"] = w + ("\n\n" + body if body else "")
    if "_patch" in uspec:
        log.append(f"{uk}: patch — " + uspec["_patch"](ua, own, res))
    if not rules:
        del ua["rules"]

# stale per-unit weapons: nothing in the book references them any more
blob = json.dumps({k: v for k, v in own.items()}, ensure_ascii=False)
others = json.dumps({b: d for b, d in raw.items() if b != book}, ensure_ascii=False)
for uk in touched_units:
    if "Legends" in ((res[uk].get("keywords") or {}).get("Source") or []):
        continue   # Legends units keep their old weapons
    uname = uk.split("§", 1)[1]
    for k in [k for k in own if k.split("§")[0] in WEP and k.split("§", 1)[1].split("—")[0] == uname and "—" in k]:
        refs = blob.count(f'"{k}"') - 1
        if refs == 0:
            parent_ref = any(f'"{k}"' in json.dumps(v, ensure_ascii=False) for kk, v in own.items() if kk != k)
            if not parent_ref and f'"{k}"' not in others:
                log.append(f"STALE {k}" + (" (pruned)" if PRUNE else ""))
                if PRUNE: del own[k]

# assets this run left unreferenced (dropped wargear options, removed models and their weapons)
while PRUNE:
    gone = [k for k in was_referenced if k in own and k not in referenced([k])]
    if not gone:
        break
    for k in gone:
        log.append(f"ORPHANED {k} (pruned)"); del own[k]

print("\n".join(log))
print("\n".join("ERROR " + e for e in errors) or "no errors")
if APPLY and not errors:
    p = RZ / f"{book}.rulebook"
    open(p, "w").write(json.dumps(raw[book], indent=2, ensure_ascii=False))
    print("written", p.name)
