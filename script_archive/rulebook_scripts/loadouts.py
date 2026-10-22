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
import copy, importlib.util, json, re, sys
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
base = {}   # what the dependency chain alone gives (hub assets the book overrides)
for b in W.chain(raw, book):
    for k, v in raw[b]["rulebook"]["assetCatalog"].items():
        base[k] = W.merge_entry(base[k], v) if k in base else v
targets = {}   # inherited holders being edited: key -> resolved copy, written back as an overlay at the end

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
    if name.startswith("U:"):   # unit-specific wargear (its own points), text from Waha or the shared asset
        nm = name[2:]; k = f"Wargear§{unit}—{nm}"
        text = waha_wargear(unit).get(nm) or (res.get(f"Wargear§{nm}") or {}).get("text")
        if (res.get(k) or {}).get("text") != text:
            own.setdefault(k, {})["text"] = text; res[k] = {**(res.get(k) or {}), "text": text}
            log.append(f"WARGEAR {k}: unit-specific")
        return k
    m = re.match(r"^([RMW]):(.*)$", name)
    kinds, name = (KIND[m.group(1)], m.group(2)) if m else (WEP, name)
    want = n(name)
    def pick(pred):
        hits = [k for k in res if pred(k)]
        parents = [k for k in hits if " – " not in k.split("§", 1)[1]]
        # name-equal duplicates (old 10e "Termite drill" beside 11e "Termite Drill"): the most complete profile wins
        full = lambda k: len((res[k].get("stats") or {})) + len((res[k].get("assets") or {}).get("traits") or [])
        return max(parents or hits or [None], key=lambda k: full(k) if k else 0)
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
    tags = re.findall(r"@(\w+)(?:=([\d.]+))?", body); body = re.sub(r"\s*@\w+(=[\d.]+)?", "", body).strip()
    traits = []
    if body != "-":
        for part in [p.strip() for p in body.split(" + ")]:
            m = re.match(r"^(\d+)x\s+(.*)$", part)
            q, nm = (int(m.group(1)), m.group(2)) if m else (1, part)
            k = resolve_weapon(unit, nm)
            traits += [{"trait": k}] * q if k else []
    if label is None:
        label = re.sub(r"\b(\d+)x ", r"\1 ", re.sub(r"\b[RMWU]:", "", body).replace(" + ", " & "))
    out = {"traits": traits} if traits else {}
    if tags:
        out["tracking"] = {t: (float(q) if "." in q else int(q)) if q else 1 for t, q in tags}
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
    """the asset to edit: the book's own, or (for a hub asset) a resolved copy that becomes an override"""
    if key in base:
        if key not in targets:
            targets[key] = copy.deepcopy(res[key])
        return targets[key]
    if key not in own:
        errors.append(f"{key}: not in {book} or its dependencies")
        return None
    return own[key]


def referenced(keys):
    """keys that occur anywhere (all books) besides their own catalog entry"""
    from collections import Counter
    seen = Counter(re.findall(r'"((?:[^"\\]|\\.)*)"', json.dumps(raw, ensure_ascii=False)))
    return {k for k in keys if seen[k] > 1}
LEGENDS_UNITS = {k.split("§", 1)[1] for k, v in res.items() if k.split("§")[0] in UNITCLS
                 and "Legends" in ((v.get("keywords") or {}).get("Source") or [])}
ORPHANABLE = lambda k: k.split("§")[0] in ("Wargear", "Model") or (
    k.split("§")[0] in WEP and k.split("§", 1)[1].split("—")[0] not in LEGENDS_UNITS   # Legends units keep their weapons
    and "Armoury" not in k.split("§", 1)[1].split("—")[0])   # armoury weapons stay shared even when unused
was_referenced = referenced([k for k in own if ORPHANABLE(k)])

REFPAT = re.compile(r'"((?:Ranged Weapon|Melee Weapon|Weapon|Wargear|Model)§[^"]+)"')
def dangling():
    """asset keys any book referencing this one's chain uses but nothing defines"""
    out = set()
    for b in raw:
        if b == book or book in W.chain(raw, b):
            cat = W.resolved(raw, b)
            out |= {(b, k) for k in REFPAT.findall(json.dumps(raw[b], ensure_ascii=False)) if k not in cat}
    return out
dangling_before = dangling()

CORE_STATS = set()
for cls in raw["Warhammer_40k_11e"]["rulebook"]["assetTaxonomy"].values():
    CORE_STATS |= set((cls.get("stats") or {}).keys())

touched_units = []
for uname, uspec in SPEC.items():
    uk = next((k for k in res if k.split("§")[0] in UNITCLS and n(k.split("§", 1)[1]) == n(uname)), None)
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
        for sn in hs.get("drop_stats", []):
            if st.pop(sn, None) is not None: log.append(f"{key}: dropped stat '{sn}'")
        for rn in hs.get("drop_rules", []):
            if (a.get("rules") or {}).pop(rn, None) is not None: log.append(f"{key}: dropped rule '{rn}'")
        for sn, labels in (hs.get("drop_ranks") or {}).items():
            for lb in labels:
                if ((st.get(sn) or {}).get("ranks") or {}).pop(lb, None) is not None: log.append(f"{key}: dropped rank '{sn}/{lb}'")
        if a.get("rules") == {}:
            del a["rules"]
        for sn, ranks in (hs.get("add_slots") or {}).items():   # an extra option beside the existing loadout
            rk = {}
            for i, r in enumerate(ranks):
                label, body = parse_rank(wunit, r)
                rk[label] = {"order": i, **body}
            st[sn] = {"dynamic": True, "group": "Loadout", "groupOrder": 2, "ranks": rk, "statType": "rank",
                      "value": next(iter(rk)), "visibility": "active"}
        if "static" not in hs and "slots" not in hs:
            continue
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
    if "_rename" in uspec:   # 11e renames: swap weapon keys (and matching rank labels) through the unit tree
        tree, todo = [], [uk]
        while todo:
            k = todo.pop()
            if k in tree or k not in res: continue
            tree.append(k)
            todo += [m for m in re.findall(r'"(Model§[^"]+)"', json.dumps(res[k], ensure_ascii=False)) if m in res]
        for old, new in uspec["_rename"].items():
            nk = resolve_weapon(wunit, new)
            if not nk: continue
            pat = re.compile(r'"((?:Ranged Weapon|Melee Weapon|Weapon|Wargear)§(?:' + re.escape(wunit) + r'—)?)([^"—]+)"')
            for k in tree:
                a = holder_asset(k)
                txt = json.dumps(a, ensure_ascii=False)
                hits = {m.group(0) for m in pat.finditer(txt) if n(m.group(2)) == n(old.split(":")[-1]) and (m.group(1).startswith(("Wargear", "Weapon")) or ":" not in old or m.group(1).startswith(KIND[old[0]][0]))}
                hits = {h for h in hits if h != f'"{nk}"' and h[1:-1] in res}
                if not hits: continue
                for h in hits:
                    txt = txt.replace(h, f'"{nk}"')
                lab = re.sub(r"^[RMWU]:", "", new)
                txt = re.sub(r'"' + re.escape(old.split(":")[-1]) + r'"(?=\s*:\s*\{)', f'"{lab}"', txt, flags=re.I)   # rank labels
                a.clear(); a.update(json.loads(txt))
                for st in (a.get("stats") or {}).values():   # a renamed rank that was the stat's default
                    if isinstance(st, dict) and st.get("ranks") and isinstance(st.get("value"), str) and st["value"] not in st["ranks"] \
                            and n(st["value"]) == n(old.split(":")[-1]):
                        st["value"] = lab
                log.append(f"{k}: {sorted(hits)} -> {nk}")
    ua = holder_asset(uk)
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

# inherited holders → overrides in this book, verified with the merge simulator
from rzmerge import make_overlay, canon_unordered_traits as canon
def avoid_readd(k, t):
    """The app loses a stat an override both removes and re-adds (seen 2026-10-22: Stormraven Loadout 1/2,
    BT Impulsor). Ranks that only grow merge without a removal; otherwise the new stat gets its own key, shown
    under the old name via `label`."""
    bst = base[k].get("stats") or {}
    for sn in list((t.get("stats") or {}).keys()):
        new, old = t["stats"][sn], bst.get(sn)
        if not (isinstance(new, dict) and new.get("ranks") and isinstance(old, dict) and old.get("ranks")) or new == old:
            continue
        if set(old["ranks"]) <= set(new["ranks"]):
            continue   # make_overlay's rank diff merges cleanly
        key = f"{sn} (11e)"
        t["stats"][key] = {**new, "label": new.get("label") or sn}
        del t["stats"][sn]
        txt = json.dumps(t.get("rules") or {}, ensure_ascii=False)
        if f'"stats", "{sn}"' in txt:
            t["rules"] = json.loads(txt.replace(f'"stats", "{sn}"', f'"stats", "{key}"'))
        log.append(f"{k}: stat '{sn}' re-keyed '{key}' (override can't remove and re-add one name)")

for k, t in targets.items():
    avoid_readd(k, t)
    ov = make_overlay(base[k], t)
    rem = (ov.get("removed") or {}).get("stats") or {}
    for sn in [x for x in rem if x in (ov.get("stats") or {})]:   # rank-growing stats: plain merge, no removal
        del rem[sn]
        ov["stats"][sn] = {kk: vv for kk, vv in t["stats"][sn].items() if (base[k]["stats"].get(sn) or {}).get(kk) != vv}
    if "removed" in ov and "stats" in ov["removed"] and not ov["removed"]["stats"]:
        del ov["removed"]["stats"]
    if ov.get("removed") == {}:
        del ov["removed"]
    if canon(W.merge_entry(base[k], ov)) != canon(t):
        got, want = canon(W.merge_entry(base[k], ov)), canon(t)
        diff = {f: (got.get(f), want.get(f)) for f in set(got) | set(want) if got.get(f) != want.get(f)}
        errors.append(f"{k}: override does not reproduce the edited asset: {json.dumps(diff, ensure_ascii=False)[:800]}"); continue
    if ov: own[k] = ov
    elif k in own: del own[k]
    log.append(f"OVERRIDE {k}: {sorted(ov)}")

# stale per-unit weapons: nothing in any book references them any more (repeat: a pruned parent frees its profiles)
from collections import Counter
while True:
    seen = Counter(re.findall(r'"((?:[^"\\]|\\.)*)"', json.dumps(raw, ensure_ascii=False)))
    stale = [k for uk in touched_units if "Legends" not in ((res[uk].get("keywords") or {}).get("Source") or [])
             for k in own if k.split("§")[0] in WEP and "—" in k and k.split("§", 1)[1].split("—")[0] == uk.split("§", 1)[1]
             and seen[k] <= 1]
    for k in stale:
        log.append(f"STALE {k}" + (" (pruned)" if PRUNE else ""))
        if PRUNE: del own[k]
    if not (PRUNE and stale):
        break

# assets this run left unreferenced (dropped wargear options, removed models and their weapons)
while PRUNE:
    alive = referenced([k for k in was_referenced if k in own])
    gone = [k for k in was_referenced if k in own and k not in alive]
    if not gone:
        break
    for k in gone:
        log.append(f"ORPHANED {k} (pruned)"); del own[k]

# rules in touched units must not read stats that are gone
for uk in touched_units:
    for k in [uk] + [m for m in re.findall(r'"(Model§[^"]+)"', json.dumps(own.get(uk) or res[uk], ensure_ascii=False))]:
        a = own.get(k) if k not in base else W.merge_entry(base[k], own.get(k) or {})
        a = a or res.get(k) or {}
        for rn, r in (a.get("rules") or {}).items():
            for sn in set(re.findall(r'\["\{self\}", "stats", "([^"]+)"', json.dumps(r, ensure_ascii=False))):
                if sn not in (a.get("stats") or {}) and sn not in CORE_STATS:
                    errors.append(f"{k}: rule '{rn}' reads missing stat '{sn}'")

for b, k in sorted(dangling() - dangling_before):
    errors.append(f"{b}: now references missing {k}")

print("\n".join(log))
print("\n".join("ERROR " + e for e in errors) or "no errors")
if APPLY and not errors:
    p = RZ / f"{book}.rulebook"
    open(p, "w").write(json.dumps(raw[book], indent=2, ensure_ascii=False))
    print("written", p.name)
