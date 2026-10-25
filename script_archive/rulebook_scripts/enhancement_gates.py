"""Enhancement keyword gates ("X model only.") whose evals the importer split word by word: the engine matches keyword
list elements exactly, so 'Troupe' never matches 'Troupe Master'. Rebuilds each broken gate from the rule's own name:
each '/'-separated phrase becomes one eval — a `contains` on the real keyword (matched ignoring case, apostrophes,
hyphens and diacritics) or, when the phrase is a unit name rather than a keyword, an equality on the parent's
designation — evaluated OR. Dry-run unless --apply. Needs WAHA_DIR (waha_lib)."""
import json, os, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
APPLY = "--apply" in sys.argv
def norm(s):
    s = unicodedata.normalize("NFKD", s); s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())
books = W.load_books(); RZ = W.RZ
UNITCLS = ("Character", "Unit", "Infantry/Mounted", "Vehicle")
GATE = re.compile(r"^(.*?)\s+(?:model|models|unit|units)\s+only", re.I)
changed = {}; unresolved = []
for b in sorted(books):
    try: res = W.resolved(books, b)
    except Exception: continue
    units = {k: v for k, v in res.items() if k.split("§")[0] in UNITCLS}
    kwnorm = {}; facnorm = {}
    for v in units.values():
        for kw in (v.get("keywords") or {}).get("Keywords") or []: kwnorm.setdefault(norm(kw), kw)
        for kw in (v.get("keywords") or {}).get("Faction") or []: facnorm.setdefault(norm(kw), kw)
    names = {}
    for k in units: n = k.split("§", 1)[1]; names.setdefault(norm(n), n); names.setdefault(norm(n).rstrip("s"), n)
    for k, v in res.items():
        if not k.startswith("Enhancement§"): continue
        for rk, rv in list((v.get("rules") or {}).items()):
            if rv.get("failState") != "error": continue
            gates = [e for e in rv.get("evals", []) if e.get("paths") and e["paths"][0][:3] == ["{parent}", "keywords", "Keywords"] and e.get("contains") and not e.get("not")]
            if not gates or len(gates) != len(rv.get("evals", [])): continue   # only pure keyword gates
            if all(e.get("value") in kwnorm.values() for e in gates): continue   # already exact
            m = GATE.match(rk)
            if not m: unresolved.append((b, k, rk, "no phrase in rule name")); continue
            evals = []; and_all = False
            for phrase in [p.strip() for p in re.split(r"\s*/\s*", m.group(1)) if p.strip()]:
                n = norm(phrase)
                if n in kwnorm: evals.append({"actionable": True, "contains": True, "not": False, "operator": "AND", "paths": [["{parent}", "keywords", "Keywords"]], "value": kwnorm[n]})
                elif n in facnorm: evals.append({"actionable": True, "contains": True, "not": False, "operator": "AND", "paths": [["{parent}", "keywords", "Faction"]], "value": facnorm[n]})
                elif n in names or n.rstrip("s") in names: evals.append({"actionable": True, "not": False, "operator": "AND", "paths": [["{parent}", "designation"]], "value": names.get(n) or names[n.rstrip("s")]})
                else:
                    # two keywords side by side ("GRAV-ASSAULT TRANSPORT"): every word-group must be a real keyword
                    parts = [w for w in re.split(r"\s+", phrase) if w]; found = [kwnorm.get(norm(w)) for w in parts]
                    if len(parts) > 1 and all(found) and len(alts_all := [p.strip() for p in re.split(r"\s*/\s*", m.group(1)) if p.strip()]) == 1:
                        evals = [{"actionable": True, "contains": True, "not": False, "operator": "AND", "paths": [["{parent}", "keywords", "Keywords"]], "value": f} for f in found]; and_all = True; break
                    evals = None; break
            if not evals: unresolved.append((b, k, rk, m.group(1))); continue
            new = {**rv, "evals": evals, "evaluate": "AND" if and_all or len(evals) == 1 else "OR"}
            # write into the book that defines this rule (own book first, then up the chain)
            for bk in [b] + W.chain(books, b)[::-1]:
                e = books[bk]["rulebook"]["assetCatalog"].get(k)
                if e and rk in (e.get("rules") or {}):
                    e["rules"][rk] = new; changed.setdefault(bk, []).append(f"{k} | {rk} -> {[x['value'] for x in evals]}"); break
for bk, lines in changed.items():
    print(f"== {bk}"); print("\n".join("   " + l for l in lines))
print(len(unresolved), "unresolved:"); [print("   ", u) for u in unresolved]
if APPLY:
    for bk in changed:
        d = books[bk]; a, m_, c = d["revision"].split("."); d["revision"] = f"{a}.{m_}.{int(c)+1}"
        open(RZ / f"{bk}.rulebook", "w").write(json.dumps(d, indent=2, ensure_ascii=False)); print("wrote", bk, d["revision"])
