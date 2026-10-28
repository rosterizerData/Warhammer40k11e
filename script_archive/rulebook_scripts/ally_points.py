"""Allied units cost what their home faction's MFM page says. The consumer faction's MFM page doesn't list them, so
mfm_points.py never touches them and they keep whatever price the hub copy had. This copies the pricing stats
(Points, model<N>Tally/Cost, unitDiscount, unitDiscountThreshold) from the home book's resolved unit onto the
consumer's resolved unit, writing an override into the consumer book. Revisions are left alone.

  WAHA_DIR=<csvs> MFM_SITE_JSON=<mfm_site.py output> python3 ally_points.py [--apply]
"""
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import waha_lib as W

APPLY = "--apply" in sys.argv
PAIRS = [("Chaos_Daemons", "Chaos_Space_Marines"), ("Chaos_Knights", "Chaos_Space_Marines"),
         ("Imperial_Knights", "Adeptus_Mechanicus"), ("Genestealer_Cults", "Tyranids"),
         ("Genestealer_Cults", "Astra_Militarum"), ("Drukhari", "Aeldari")]
SLUG = {"Chaos_Daemons": "chaos-daemons", "Chaos_Knights": "chaos-knights", "Imperial_Knights": "imperial-knights",
        "Genestealer_Cults": "genestealer-cults", "Drukhari": "drukhari", "Chaos_Space_Marines": "chaos-space-marines",
        "Adeptus_Mechanicus": "adeptus-mechanicus", "Tyranids": "tyranids", "Astra_Militarum": "astra-militarum", "Aeldari": "aeldari"}
PRICE = re.compile(r"^(Points|model\d?(st|nd|rd|th)(Tally|Cost)|unitDiscount|unitDiscountThreshold)$")
site = json.load(open(os.environ["MFM_SITE_JSON"]))
listed = {b: {W.n(u["name"]) for u in site[s]["units"]} for b, s in SLUG.items()}
books = W.load_books()
R = {}
def res(b):
    if b not in R:
        R[b] = W.resolved(books, b)
    return R[b]

def base(k):
    return re.sub(r"\s*\((SL|CK|Knights|GSC|BB)\)\s*$", "", k.split("§", 1)[1])

sys.path.insert(0, str(Path(__file__).parent / "rz_headless"))
import scen

def selectable(b, keys):
    """the keys a matched-play roster of book b can take under at least one of its detachments"""
    C = res(b)
    dets = [k.split("§")[1] for k in C if k.startswith("Detachment§") and "Legends" not in (C[k].get("keywords", {}).get("Source") or [])]
    todo, ok = list(keys), set()
    for d in dets:
        if not todo:
            break
        r = scen.run(b, scen.roster(d, play="Matched", units=[scen.unit(k) for k in todo]))
        nodes = (r["tree"] or {}).get("included", [])
        left = []
        for k, node in zip(todo, nodes):
            if any("not allowed to be included in asset Roster" in e or "isn’t in the" in e for e in node.get("errors") or []):
                left.append(k)
            else:
                ok.add(k)
        todo = left
    return ok

def candidates(cons, home):
    C = res(cons)
    return [k for k, a in C.items() if k.split("§")[0] in W.UNITCLS and "Legends" not in (a.get("keywords", {}).get("Source") or [])
            and W.n(base(k)) not in listed[cons] and W.n(base(k)) in listed[home]]

SEL = {cons: selectable(cons, sorted({k for c, h in PAIRS if c == cons for k in candidates(c, h)})) for cons in {c for c, _ in PAIRS}}
changed = set()
for cons, home in PAIRS:
    C, H = res(cons), res(home)
    for k, a in C.items():
        if k not in SEL[cons] or k not in candidates(cons, home):
            continue
        hk = W.find_unit(H, base(k), books[home]["rulebook"]["assetCatalog"])
        if not hk:
            continue
        hs = {s: v.get("value") for s, v in H[hk].get("stats", {}).items() if PRICE.match(s)}
        cs = {s: v.get("value") for s, v in a.get("stats", {}).items() if PRICE.match(s)}
        want = dict(hs)
        for s in cs:
            if s not in hs:   # a tier the home unit doesn't have
                want[s] = 0 if s.startswith("unitDiscount") else None
        diff = {s: (cs.get(s), v) for s, v in want.items() if cs.get(s) != v}
        if not diff:
            continue
        print(f"{cons:18} {k:45} <- {home}:{hk.split('§')[1]}  {diff}")
        ent = books[cons]["rulebook"]["assetCatalog"].setdefault(k, {})
        st = ent.setdefault("stats", {})
        for s, v in want.items():
            if v is None:
                if s in st:
                    st.pop(s)
                if s in a.get("stats", {}) and s not in st:
                    st[s] = {"value": 0}   # inherited tier: zero it (there is no 'remove' needed for an unused tier count)
                continue
            st[s] = {**st[s], "value": v} if isinstance(st.get(s), dict) else {"value": v}
        changed.add(cons)
        R.pop(cons, None)

if APPLY:
    for b in changed:
        p = W.RZ / f"{b}.rulebook"
        raw = p.read_text()
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(books[b], indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))
        tmp.replace(p)
    print("written:", sorted(changed))
    # verify
    books2 = W.load_books()
    for cons, home in PAIRS:
        C, H = W.resolved(books2, cons), W.resolved(books2, home)
        for k, a in C.items():
            if k.split("§")[0] in W.UNITCLS and W.n(base(k)) in listed[home] and W.n(base(k)) not in listed[cons] \
                    and "Legends" not in (a.get("keywords", {}).get("Source") or []):
                hk = W.find_unit(H, base(k), books2[home]["rulebook"]["assetCatalog"])
                if hk and a["stats"].get("Points", {}).get("value") != H[hk]["stats"].get("Points", {}).get("value"):
                    print("STILL DIFFERS", cons, k)
