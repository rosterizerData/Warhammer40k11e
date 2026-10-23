"""Read-only audit: BSData 11e catalogues (github.com/BSData/wh40k-11e, JSON) vs the Rz 40k 11e books, with the MFM.

  BSDATA_DIR=<clone> MFM_DIR=<wh40k-11e-mfm> WAHA_DIR=<csvs> PYTHONPATH=<pyyaml> python3 bsdata_audit.py <out.json> <out.md>

Per Rz book (BSData faction catalogues mapped onto it; libraries resolved through entry links):
  units        — in BSData not Rz / current in Rz not BSData / Legends status vs BSData "[Legends]" and the MFM
  points       — BSData smallest-size cost vs MFM vs Rz
  statline     — M T Sv W Ld OC and invulnerable save per model
  composition  — unit model count min/max
  weapons      — weapon profiles (Range A BS/WS S AP D) and weapon keywords
  options      — weapons BSData lets a unit select vs what Rz offers (static + Loadout ranks + rule-added), and defaults
Nothing is written to the books.
"""
import json, os, re, sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import waha_lib as W
import yaml

BS = Path(os.environ["BSDATA_DIR"])
MFM = Path(os.environ["MFM_DIR"]) / "data"
OUT_JSON, OUT_MD = sys.argv[1], sys.argv[2]

# ------------------------------------------------------------------ names
def n(s):
    s = (s or "").lower().replace("’", "'").replace("‘", "'").replace("ʼ", "'")
    s = re.sub(r"\s*\[legends\]\s*", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)

def base(s):
    """weapon base name: drop a profile suffix ("Bolt Rifle - Focused Fire", "Kannon – frag")"""
    return re.sub(r"^the", "", n(re.split(r"\s+[–-]\s+", re.sub(r"^\W+", "", s or ""))[0]))

def sing(s):
    return re.sub(r"(?<=[a-z])s$", "", s)

def same(a, b):
    return a == b or sing(a) == sing(b)

# ------------------------------------------------------------------ BSData index
CATS = {}
for f in BS.glob("*.json"):
    d = json.load(open(f))
    CATS[f.stem] = d.get("catalogue") or d.get("gameSystem")
IDX = {}
def index(o):
    if isinstance(o, dict):
        if "id" in o and ("name" in o or "type" in o):
            IDX.setdefault(o["id"], o)
        for v in o.values():
            index(v)
    elif isinstance(o, list):
        for v in o:
            index(v)
for c in CATS.values():
    for k in ("sharedSelectionEntries", "sharedSelectionEntryGroups", "sharedProfiles"):
        index(c.get(k) or [])
for c in CATS.values():
    index(c)

SKIP = re.compile(r"crusade|weapon modification|enhancement|warlord|terminator honours|battle honour|relic|honour|marked for greatness|"
                  r"legendary veterans|scars|tactical|detachment", re.I)

def cons(o):
    lo = hi = None
    for c in o.get("constraints") or []:
        if c.get("field") == "selections" and c.get("scope") in ("parent", None):
            if c["type"] == "min": lo = c["value"]
            if c["type"] == "max": hi = c["value"]
    return lo, hi

def resolve(o):
    """an entryLink resolved to its target, the link's own constraints/name winning"""
    if "targetId" in o and o.get("type") in ("selectionEntry", "selectionEntryGroup"):
        t = IDX.get(o["targetId"])
        if not t:
            return None
        r = dict(t)
        if o.get("constraints"):
            r["constraints"] = o["constraints"]
        if o.get("hidden"):
            r["hidden"] = True
        if o.get("entryLinks") and not t.get("entryLinks"):
            r["entryLinks"] = o["entryLinks"]
        r["_link"] = o
        return r
    return o

def children(o):
    for k in ("selectionEntries", "selectionEntryGroups", "entryLinks"):
        for c in o.get(k) or []:
            r = resolve(c)
            if r is not None and not r.get("hidden"):
                yield r

def profiles(o, kind):
    out = list(p for p in o.get("profiles") or [] if p.get("typeName") == kind)
    for l in o.get("infoLinks") or []:
        if l.get("type") == "profile":
            p = IDX.get(l["targetId"])
            if p and p.get("typeName") == kind:
                out.append(p)
    return out

def chars(p):
    return {c["name"]: (c.get("$text") or "").strip() for c in p.get("characteristics") or []}

WKINDS = ("Ranged Weapons", "Melee Weapons")

def weapon_profiles(o, depth=0):
    ps = [p for k in WKINDS for p in profiles(o, k)]
    if depth < 2:
        for c in children(o):
            if c.get("type") == "upgrade" or "selectionEntries" in c:
                if not c.get("type") in ("model", "unit"):
                    ps += weapon_profiles(c, depth + 1) if c.get("type") != "upgrade" else []
    return ps

def is_weapon(o):
    return o.get("type") == "upgrade" and any(profiles(o, k) for k in WKINDS)

def bs_model_gear(model):
    """weapons of one model: {base name: {'default': bool, 'option': bool}} + {base: [profiles]}"""
    gear, profs = {}, defaultdict(list)
    def visit(o, in_group=None, group_default=None, optional=False):
        for c in children(o):
            if c.get("type") in ("model", "unit") or SKIP.search(c.get("name") or ""):
                continue
            if "selectionEntries" in c or ("type" not in c and ("entryLinks" in c or "selectionEntryGroups" in c)):
                # a selectionEntryGroup
                lo, hi = cons(c)
                dflt = c.get("defaultSelectionEntryId")
                visit(c, in_group=c, group_default=dflt, optional=optional or not lo)
                continue
            if c.get("type") != "upgrade":
                continue
            if is_weapon(c):
                b = base(c["name"])
                lo, hi = cons(c)
                link_id = (c.get("_link") or {}).get("id")
                is_default = False
                if in_group is not None and group_default and group_default in (c.get("id"), link_id):
                    is_default = not optional
                elif in_group is None and lo and lo >= 1:
                    is_default = not optional
                g = gear.setdefault(b, {"default": False, "option": False, "name": c["name"], "aka": set()})
                g["aka"] |= {base(p["name"]) for k in WKINDS for p in profiles(c, k)}
                if is_default:
                    g["default"] = True
                else:
                    g["option"] = True
                for k in WKINDS:
                    for p in profiles(c, k):
                        profs[b].append((k, p["name"], chars(p)))
            # nested upgrades (combi entries holding weapons)
            visit(c, in_group, group_default, optional)
    visit(model)
    for k in WKINDS:   # profiles carried by the model entry itself = fixed gear
        for p in profiles(model, k):
            b = base(p["name"].replace("➤", ""))
            gear.setdefault(b, {"default": True, "option": False, "name": p["name"].replace("➤", "").strip(), "aka": set()})
            profs[b].append((k, p["name"], chars(p)))
    return gear, profs

def bs_units(cat_name):
    c = CATS[cat_name]
    out = {}
    for l in c.get("entryLinks") or []:
        e = resolve(l)
        if not e or e.get("type") not in ("unit", "model") or e.get("hidden"):
            continue
        out[e["name"]] = e
    for e in c.get("selectionEntries") or []:
        if e.get("type") in ("unit", "model") and not e.get("hidden"):
            out[e["name"]] = e
    return out

def bs_models(unit):
    """[(model entry, min, max)] — the unit itself when it's a single-model entry"""
    if unit.get("type") == "model":
        return [(unit, 1, 1)]
    out = []
    def visit(o, gmin=None, gmax=None):
        for c in children(o):
            if c.get("type") == "model":
                lo, hi = cons(c)
                out.append((c, lo if lo is not None else 0, hi if hi is not None else (gmax or 1)))
            elif "selectionEntries" in c or "selectionEntryGroups" in c or ("type" not in c):
                lo, hi = cons(c)
                if c.get("type") not in ("upgrade",):
                    visit(c, lo, hi)
    visit(unit)
    return out

def bs_size(unit):
    """unit model count (min, max): a model group's own selection limits, else its models' limits; free models add theirs"""
    if unit.get("type") == "model":
        return 1, 1
    lo = hi = 0
    def visit(o):
        nonlocal lo, hi
        for c in children(o):
            if c.get("type") == "model":
                a, b = cons(c)
                lo += a or 0; hi += b if b is not None else (a or 0)
            elif c.get("type") not in ("upgrade",) and ("selectionEntries" in c or "entryLinks" in c or "selectionEntryGroups" in c):
                ms = [m for m in children(c) if m.get("type") == "model"]
                if ms:
                    a, b = cons(c)
                    ml = sum((cons(m)[0] or 0) for m in ms)
                    mh = sum((cons(m)[1] if cons(m)[1] is not None else (cons(m)[0] or 0)) for m in ms)
                    lo += a if a is not None else ml
                    hi += b if b is not None else mh
                else:
                    visit(c)
    visit(unit)
    return lo, hi

def bs_pts(unit):
    pts = next((x["value"] for x in unit.get("costs") or [] if x.get("name") == "pts"), None)
    return pts

# ------------------------------------------------------------------ catalogue → book
CAT_BOOK = {
    "Aeldari - Craftworlds": "Aeldari", "Aeldari - Drukhari": "Drukhari", "Chaos - Chaos Daemons": "Chaos_Daemons",
    "Chaos - Chaos Knights": "Chaos_Knights", "Chaos - Chaos Space Marines": "Chaos_Space_Marines", "Chaos - Death Guard": "Death_Guard",
    "Chaos - Emperor's Children": "Emperor's_Children", "Chaos - Thousand Sons": "Thousand_Sons", "Chaos - Titanicus Traitoris": "Titanicus_Traitoris",
    "Chaos - World Eaters": "World_Eaters", "Genestealer Cults": "Genestealer_Cults", "Imperium - Adepta Sororitas": "Adepta_Sororitas",
    "Imperium - Adeptus Custodes": "Adeptus_Custodes", "Imperium - Adeptus Mechanicus": "Adeptus_Mechanicus",
    "Imperium - Adeptus Titanicus": "Adeptus_Titanicus", "Imperium - Agents of the Imperium": "Imperial_Agents",
    "Imperium - Astra Militarum": "Astra_Militarum", "Imperium - Black Templars": "SM_Black_Templars", "Imperium - Blood Angels": "SM_Blood_Angels",
    "Imperium - Dark Angels": "SM_Dark_Angels", "Imperium - Deathwatch": "SM_Deathwatch", "Imperium - Grey Knights": "Grey_Knights",
    "Imperium - Imperial Knights": "Imperial_Knights", "Imperium - Space Marines": "Space_Marines", "Imperium - Space Wolves": "SM_Space_Wolves",
    "Imperium - Imperial Fists": "Space_Marines", "Imperium - Iron Hands": "Space_Marines", "Imperium - Raven Guard": "Space_Marines",
    "Imperium - Salamanders": "Space_Marines", "Imperium - Ultramarines": "Space_Marines", "Imperium - White Scars": "Space_Marines",
    "Leagues of Votann": "Leagues_of_Votann", "Necrons": "Necrons", "Orks": "Orks", "T'au Empire": "T'au_Empire", "Tyranids": "Tyranids",
}
# library catalogues whose root units belong to a book (imported via catalogueLinks)
CAT_LIB = {"Imperial_Knights": ["Imperium - Imperial Knights - Library"], "Chaos_Knights": ["Chaos - Chaos Knights Library"],
           "Chaos_Daemons": ["Chaos - Chaos Daemons Library"], "Astra_Militarum": ["Imperium - Astra Militarum - Library"],
           "Tyranids": ["Library - Tyranids"], "Aeldari": ["Aeldari - Aeldari Library"], "Drukhari": ["Aeldari - Aeldari Library"],
           "Adeptus_Titanicus": ["Library - Titans"], "Titanicus_Traitoris": ["Library - Titans"]}
# units a faction catalogue only imports for allies (another catalogue owns them)
SM_CHAPTER = {"SM_Black_Templars", "SM_Blood_Angels", "SM_Dark_Angels", "SM_Deathwatch", "SM_Space_Wolves"}

# ------------------------------------------------------------------ MFM
src = open(Path(__file__).parent / "mfm_points.py").read()
SLUG = eval(re.search(r"SLUG_TO_FILE = (\{.*?\})\n", src, re.S).group(1))
ALIASES = eval(re.search(r"ALIASES = (\{.*?\})\n", src, re.S).group(1))
MFM_UNITS = defaultdict(dict)   # book -> norm name -> smallest-size points (current units only)
MFM_LEG = defaultdict(dict)     # book -> norm name -> points, for entries the MFM flags `legends: true`
MFM_ANY = {}
for slug, b in SLUG.items():
    y = MFM / f"{slug}.yaml"
    if not y.exists():
        continue
    units = yaml.safe_load(open(y)).get("units") or []
    byname = defaultdict(list)
    for u in units:
        byname[u["name"]].append(u)
    chosen = []
    for nm_, es in byname.items():   # as mfm_points: the faction's own (ungrouped) entry; skip true conflicts
        own_es = [e for e in es if not e.get("groupTitle")] or es
        if len({json.dumps(e["pricing"], sort_keys=True) for e in own_es}) == 1:
            chosen.append(own_es[0])
    for u in chosen:
        tiers = [sorted((c["models"], c["points"]) for c in t["costs"] if not c.get("addon")) for t in u["pricing"]]
        p = tiers   # [[(models, points), …] per unit-count tier]; cheapest tier first
        for nm in {u["name"], ALIASES.get(u["name"], u["name"])}:
            if u.get("legends"):
                MFM_LEG[b][n(nm)] = p
                continue
            MFM_UNITS[b][n(nm)] = p
            MFM_ANY.setdefault(n(nm), p)

# ------------------------------------------------------------------ Rz side
raw = W.load_books()
RES = {}
def res(b):
    if b not in RES:
        RES[b] = W.resolved(raw, b)
    return RES[b]
UNITCLS = ("Unit", "Character", "Vehicle", "Infantry/Mounted", "Titan")
WEP = ("Ranged Weapon", "Melee Weapon", "Weapon")

def tk(t):
    if isinstance(t, str): return t
    v = t.get("item") if "item" in t else t.get("trait")
    return v if isinstance(v, str) else (v or {}).get("item")

def rz_find(b, name):
    cat = res(b)
    want = n(name)
    hits = [k for k in cat if k.split("§")[0] in UNITCLS and n(re.sub(r"\s*\(.*?\)\s*$", "", k.split("§", 1)[1])) == want]
    own = raw[b]["rulebook"]["assetCatalog"]
    hits.sort(key=lambda k: (k not in own, "(" in k))
    return hits[0] if hits else None

def wname(k):
    return k.split("—", 1)[1] if "—" in k else k.split("§", 1)[1]

def rz_tree(b, uk):
    """unit + model assets (statful holders) and weapons: static, options, defaults, rule-added"""
    cat = res(b)
    static, options, defaults, holders, ruled = set(), set(), set(), {}, set()
    def walk(k, seen):
        a = cat.get(k) or {}
        holders[k] = a
        for t in (a.get("assets") or {}).get("traits") or []:
            x = tk(t)
            if not x: continue
            if x.startswith("Model§") and x not in seen:
                walk(x, seen | {x})
            elif x.split("§")[0] in WEP:
                static.add(base(wname(x))); defaults.add(base(wname(x)))
        for t in (a.get("assets") or {}).get("included") or []:
            x = tk(t)
            if x and x.startswith("Model§") and x not in seen:
                walk(x, seen | {x})
        for s in (a.get("stats") or {}).values():
            if isinstance(s, dict) and s.get("ranks"):
                for rn, r in s["ranks"].items():
                    for tr in r.get("traits") or []:
                        x = tk(tr)
                        if not x: continue
                        if x.startswith("Model§") and x not in seen:
                            walk(x, seen | {x})
                        elif x.split("§")[0] in WEP:
                            options.add(base(wname(x)))
                            if rn == s.get("value"):
                                defaults.add(base(wname(x)))
        for x in re.findall(r'"((?:Ranged Weapon|Melee Weapon|Weapon)§[^"]+)"', json.dumps(a.get("rules") or {}, ensure_ascii=False)):
            options.add(base(wname(x))); ruled.add(base(wname(x)))
        for x in re.findall(r'"(Model§[^"]+)"', json.dumps(a.get("rules") or {}, ensure_ascii=False)):
            if x not in seen and x in cat:
                walk(x, seen | {x})
    walk(uk, {uk})
    rz_tree.ruled = ruled
    return static, options, defaults, holders

def rz_weapon_assets(b, uk, holders):
    cat = res(b)
    out = defaultdict(list)
    keys = set()
    for k, a in holders.items():
        keys |= set(re.findall(r'"((?:Ranged Weapon|Melee Weapon|Weapon)§[^"]+)"', json.dumps(a, ensure_ascii=False)))
    more = set()
    for k in keys:
        more |= set(re.findall(r'"((?:Ranged Weapon|Melee Weapon)§[^"]+)"', json.dumps(cat.get(k) or {}, ensure_ascii=False)))
    for k in keys | more:
        if k in cat and (cat[k].get("stats") or {}).get("A") is not None:
            out[n(wname(k))].append(k)
            lab = (cat[k].get("aspects") or {}).get("Label")
            parent = re.split(r"\s+[–-]\s+", wname(k))[0]
            if lab and " – " in wname(k):
                out[n(parent + " " + lab)].append(k)
    return out

def sval(a, s):
    st = (a.get("stats") or {}).get(s)
    if not isinstance(st, dict): return None
    return st

def fmt(st):
    if st is None: return None
    v, f = st.get("value"), st.get("format")
    if st.get("statType") == "term": return str(v)
    if f:
        return f + (f"+{v}" if v not in (0, None, "0", "") else "")
    return str(v)

def bsnum(s):
    s = (s or "").replace('"', "").replace("″", "").replace("+", "+").strip()
    return s

def norm_stat(x):
    x = (x or "").replace('"', "").replace("″", "").replace(" ", "").lower()
    x = re.sub(r"\+$", "", x) if re.fullmatch(r"\d+\+", x) else x
    return x

def inv_rz(a):
    for t in (a.get("assets") or {}).get("traits") or []:
        if isinstance(t, dict) and t.get("item") == "Ability§Invulnerable":
            return str(((t.get("stats") or {}).get("x") or {}).get("value") or "").replace("+", "")
    return None

def rz_kw(a):
    out = set()
    for t in (a.get("assets") or {}).get("traits") or []:
        x = tk(t)
        if x and x.startswith("Ability§"):
            out.add(n(x.split("§", 1)[1]).replace("anti", "anti"))
    return out

def bs_kw(text):
    out = set()
    for part in re.split(r",\s*", text or ""):
        part = part.strip()
        if not part or part == "-": continue
        part = re.sub(r"\s+(\d+\+?|D\d+)$", "", part)       # Rapid Fire 1, Sustained Hits 1
        if part.lower().startswith("anti-"): part = "Anti-"
        out.add(n(part))
    return out

# ------------------------------------------------------------------ Waha (rules content, for a third opinion)
WGEAR = defaultdict(list)
for g in W.rd("Datasheets_wargear"):
    WGEAR[g["datasheet_id"]].append(g)
def waha_profile(b, unit, pname, kind):
    ids = [d["id"] for d in W.datasheets_for(b) if n(d["name"]) == n(unit)]
    t = "Ranged" if kind == "Ranged Weapons" else "Melee"
    for i in ids:
        for g in WGEAR[i]:
            if g["type"] == t and n(g["name"]) == n(pname.replace("➤", "")):
                return {"Range": g["range"], "A": g["A"], "BS": g["BS_WS"], "WS": g["BS_WS"], "S": g["S"], "AP": g["AP"], "D": g["D"],
                        "Keywords": W.html(g["description"])}
    return None

WMODELS = defaultdict(list)
for r in W.rd("Datasheets_models"):
    WMODELS[r["datasheet_id"]].append(r)
def waha_model(b, unit, model):
    for d in W.datasheets_for(b):
        if n(d["name"]) == n(unit):
            rows = WMODELS[d["id"]]
            hit = next((r for r in rows if n(r["name"]) == n(model)), None) or (rows[0] if len(rows) == 1 else None)
            if hit:
                return {"M": hit["M"], "T": hit["T"], "Sv": hit["Sv"], "W": hit["W"], "LD": hit["Ld"], "OC": hit["OC"], "InSv": hit["inv_sv"]}
    return None

# ------------------------------------------------------------------ audit
R = defaultdict(lambda: defaultdict(list))
def add(b, cat, unit, item, bs=None, rz=None, mfm=None, note=None):
    rec = {k: v for k, v in dict(unit=unit, item=item, bsdata=bs, rz=rz, mfm=mfm, note=note).items() if v is not None}
    if rec in R[b][cat]:
        return
    R[b][cat].append({k: v for k, v in dict(unit=unit, item=item, bsdata=bs, rz=rz, mfm=mfm, note=note).items() if v is not None})

seen_bs = defaultdict(set)
JOBS = [(c, b, False) for c, b in CAT_BOOK.items()] + [(c, b, True) for b, cs in CAT_LIB.items() for c in cs]
for cat_name, b, from_lib in JOBS:
    if cat_name not in CATS or b not in raw:
        continue
    units = bs_units(cat_name)
    book0 = b
    for uname, ue in sorted(units.items()):
        b = book0
        if re.search(r"\[(?!legends)[^\]]+\]", uname, re.I):
            continue   # [Crucible] narrative characters etc.
        bs_leg = "[legends]" in uname.lower()
        clean = re.sub(r"\s*\[Legends\]\s*", "", uname).strip()
        seen_bs[b].add(n(clean))
        uk = rz_find(b, clean)
        SMF = [o for o in raw if o.startswith("SM_") or o == "Space_Marines"]
        if uk and b in SMF and (uk not in raw[b]["rulebook"]["assetCatalog"] or "(" in uk):
            for o in SMF:   # BSData keeps e.g. the Deathwatch kill teams in the SM catalogue; the Rz in a chapter book
                k2 = rz_find(o, clean)
                if k2 and k2 in raw[o]["rulebook"]["assetCatalog"] and "(" not in k2:
                    b, uk = o, k2
                    break
        in_mfm = n(clean) in MFM_UNITS.get(b, {})
        mfm_leg = n(clean) in MFM_LEG.get(b, {})
        mfm_txt = "current" if in_mfm else "Legends" if mfm_leg else "not listed"
        if not uk:
            if from_lib or "(" in clean:
                continue   # shared library units of other factions; spawned sub-units ("Spore Mines (Biovore)")
            if any(rz_find(o, clean) for o in raw if o != b and (o.startswith("SM_") or o in ("Space_Marines", "Imperial_Agents"))
                   and (b.startswith("SM_") or b == "Space_Marines")):
                continue   # an SM-family unit the Rz keeps in another chapter book
            if in_mfm:
                add(b, "units", clean, "current in the MFM, missing in Rz", bs="Legends" if bs_leg else "current", mfm=mfm_txt)
            elif not bs_leg:
                add(b, "units", clean, "current in BSData, missing in Rz", bs="current", mfm=mfm_txt)
            continue
        a = res(b)[uk]
        rz_leg = "Legends" in ((a.get("keywords") or {}).get("Source") or [])
        own_unit = uk in raw[b]["rulebook"]["assetCatalog"]
        if not rz_leg and not in_mfm and n(clean) not in MFM_ANY:
            add(b, "units", clean, "current in Rz but the MFM doesn't list it as current (Legends by rule)",
                bs="Legends" if bs_leg else "current", rz="current", mfm=mfm_txt)
        elif rz_leg and in_mfm:
            add(b, "units", clean, "Legends in Rz but current in the MFM", bs="Legends" if bs_leg else "current", rz="Legends", mfm=mfm_txt)
        elif bs_leg != (not in_mfm) and own_unit and n(clean) not in MFM_ANY:
            add(b, "units", clean, "BSData Legends status differs from the MFM", bs="Legends" if bs_leg else "current", rz="Legends" if rz_leg else "current", mfm=mfm_txt)
        # points — at the unit's smallest size; MFM tiers: [1st..Nth units, (N+1)th+ units]
        bp = bs_pts(ue)
        tiers = MFM_UNITS.get(b, {}).get(n(clean))
        rp = (sval(a, "Points") or {}).get("value")
        disc = (sval(a, "unitDiscount") or {}).get("value") or 0
        if tiers and all(tiers):
            lo_cheap, lo_full = tiers[0][0], tiers[-1][0]
            mfm_txt_p = f"{lo_cheap[1]}" + (f" / {lo_full[1]} later units" if len(tiers) > 1 else "") + f" ({lo_cheap[0]} models)"
            if bp and not bs_leg and bp not in (lo_cheap[1], lo_full[1]):
                add(b, "points", clean, "BSData cost differs from the MFM", bs=bp, rz=rp, mfm=mfm_txt_p)
            if rp is not None and own_unit and not rz_leg:
                want_full, want_cheap = lo_full[1], lo_cheap[1]
                got_cheap = rp - disc if disc else rp
                if rp != want_full or (len(tiers) > 1 and got_cheap != want_cheap):
                    add(b, "points", clean, "Rz cost differs from the MFM", bs=bp,
                        rz=f"{got_cheap} / {rp} later units" if disc else rp, mfm=mfm_txt_p)
        # models / statlines / composition
        static, options, defaults, holders = rz_tree(b, uk)
        statful = {k: h for k, h in holders.items() if sval(h, "T") is not None}
        models = bs_models(ue)
        tot_lo, tot_hi = bs_size(ue)
        ms = sval(a, "Models")
        if ms and models and not bs_leg:
            if ms.get("ranks"):
                nums = sorted(r.get("number") for r in ms["ranks"].values() if r.get("number"))
                rlo, rhi = (nums[0], nums[-1]) if nums else (None, None)
            else:
                rlo, rhi = ms.get("min"), ms.get("max")
            if rlo and rhi and tot_lo and tot_hi and (rlo, rhi) != (tot_lo, tot_hi) and tot_hi >= tot_lo:
                add(b, "composition", clean, "model count", bs=f"{tot_lo}-{tot_hi}", rz=f"{rlo}-{rhi}")
        for me, lo, hi in models:
            for p in profiles(me, "Unit"):
                c = chars(p)
                pn = n(p["name"])
                hk = next((k for k in statful if n(k.split("§", 1)[1]) == pn or n(((statful[k].get("aspects") or {}).get("Label"))) == pn), None)
                if not hk:
                    hk = next((k for k in statful if pn in n(k.split("§", 1)[1]) or n(k.split("§", 1)[1]) in pn), None)
                if not hk and len(statful) == 1 and len(models) == 1:
                    hk = next(iter(statful))
                if not hk:
                    continue
                h = statful[hk]
                wm = waha_model(b, clean, p["name"])
                diffs, rz_wrong = [], False
                for s_bs, s_rz in (("M", "M"), ("T", "T"), ("Sv", "Sv"), ("W", "W"), ("LD", "Ld"), ("OC", "OC")):
                    bv, rv = norm_stat(c.get(s_bs)), norm_stat(fmt(sval(h, s_rz)))
                    if bv in ("", "-", "*") or rv in (None, "none"):
                        continue
                    if bv != rv and not (bv == "0" and rv in ("-", "")):
                        wv = norm_stat(wm.get(s_bs)) if wm else None
                        rz_wrong |= bool(wv) and wv != rv
                        diffs.append(f"{s_rz} Rz {rv} / BSData {bv}" + (f" / Waha {wv}" if wv else ""))
                biv = norm_stat(c.get("InSv"))
                riv = inv_rz(h) or inv_rz(a)
                bnums = set(re.findall(r"\d", biv or ""))
                if bnums and (riv or "").replace("*", "") not in bnums:
                    wv = norm_stat(wm.get("InSv")) if wm else None
                    rz_wrong |= bool(wv) and wv not in ("-", "") and wv != (riv or "")
                    diffs.append(f"invuln Rz {riv or '-'} / BSData {biv}" + (f" / Waha {wv}" if wv else ""))
                if diffs:
                    add(b, "statline", clean, p["name"], bs=", ".join(diffs),
                        note=("Rz differs from Waha too" if rz_wrong else "Rz matches Waha — BSData differs" if wm else "no Waha profile") + f"; {hk}")
        # weapons + options
        bs_gear, bs_prof = {}, defaultdict(list)
        for me, lo, hi in models:
            g, pr = bs_model_gear(me)
            variant = not lo and len(models) > 1   # an optional model variant: its gear is an option for the unit
            for k, v in g.items():
                e = bs_gear.setdefault(k, {"default": False, "option": False, "name": v["name"], "aka": set()})
                e["aka"] |= v.get("aka", set())
                e["default"] |= v["default"] and not variant; e["option"] |= v["option"] or (v["default"] and variant)
            for k, v in pr.items():
                bs_prof[k] += v
        if ue.get("type") == "unit":
            g, pr = bs_model_gear(ue)
            for k, v in g.items():
                e = bs_gear.setdefault(k, {"default": False, "option": False, "name": v["name"], "aka": set()})
                e["aka"] |= v.get("aka", set())
                e["default"] |= v["default"]; e["option"] |= v["option"]
            for k, v in pr.items():
                bs_prof[k] += v
        rz_all = static | options
        def ids(k):
            return {k} | bs_gear[k].get("aka", set())
        bs_only = [k for k in sorted(bs_gear) if not any(same(i, r) for i in ids(k) for r in rz_all)]
        bs_all = set().union(*[ids(k) for k in bs_gear]) if bs_gear else set()
        rz_only = [r for r in sorted(rz_all) if bs_gear and not any(same(r, k) for k in bs_all)]
        import difflib
        for k in list(bs_only):   # same weapon, different name (10e vs 11e naming, "The …", plurals)
            best = max(rz_only, key=lambda r: difflib.SequenceMatcher(None, k, r).ratio(), default=None)
            if best and (difflib.SequenceMatcher(None, k, best).ratio() >= 0.75 or k in best or best in k):
                add(b, "options", clean, bs_gear[k]["name"], bs="named differently", rz=best)
                bs_only.remove(k); rz_only.remove(best)
        for k in bs_only:
            add(b, "options", clean, bs_gear[k]["name"], bs="default" if bs_gear[k]["default"] else "option", rz="not offered")
        for r in rz_only:
            add(b, "options", clean, r, bs="not in BSData", rz="default" if r in defaults else "option")
        bs_def = {k for k, v in bs_gear.items() if v["default"]}
        for k in sorted(bs_def):
            if any(same(i, r) for i in ids(k) for r in rz_all) and not any(same(i, r) for i in ids(k) for r in defaults | rz_tree.ruled):
                add(b, "options", clean, bs_gear[k]["name"], bs="default", rz="option only (not default)")
        # weapon profiles
        wa = rz_weapon_assets(b, uk, holders)
        done = set()
        for wb, plist in bs_prof.items():
            for kind, pname, c in plist:
                key = n(pname)
                if (key, kind) in done: continue
                done.add((key, kind))
                cands = wa.get(n(pname.replace("➤", ""))) or []
                cands = [x for x in cands if x.split("§")[0].startswith(kind.split()[0])]
                if not cands:
                    continue
                ra = res(b)[cands[0]]
                wv = waha_profile(b, clean, pname, kind)
                diffs, rz_wrong = [], False
                stat = "BS" if kind == "Ranged Weapons" else "WS"
                for s_bs, s_rz in (("Range", "Range"), ("A", "A"), (stat, stat), ("S", "S"), ("AP", "AP"), ("D", "D")):
                    bv = norm_stat(c.get(s_bs)); rv = norm_stat(fmt(sval(ra, s_rz)))
                    if bv in ("", "-", "n/a") or rv in (None, "none") or (bv == "melee" and rv == "melee"):
                        continue
                    if bv != rv:
                        wvv = norm_stat(wv.get(s_bs)) if wv else None
                        if wvv not in (None, "") and wvv != rv:
                            rz_wrong = True
                        diffs.append(f"{s_rz} Rz {rv} / BSData {bv}" + (f" / Waha {wvv}" if wvv not in (None, "") else ""))
                bk, rk = bs_kw(c.get("Keywords")), rz_kw(ra)
                miss = sorted(x for x in bk - rk if x not in ("", "anti") and not any(x in y or y in x for y in rk))
                if miss:
                    wk = bs_kw(wv["Keywords"]) if wv else None
                    if wk is not None and any(m in wk for m in miss):
                        rz_wrong = True
                    diffs.append(f"keywords not in Rz: {miss}" + (f" (Waha: {sorted(wk)})" if wk is not None else ""))
                note_ = ("Rz differs from Waha too" if rz_wrong else "Rz matches Waha — BSData differs" if wv else "no Waha profile") + f"; {cands[0]}"
                if diffs:
                    add(b, "weapons", clean, pname.replace("➤", "").strip(), bs="; ".join(diffs), note=note_)

# current Rz units the BSData catalogue(s) don't have
for b in sorted(set(CAT_BOOK.values())):
    if b not in raw: continue
    own = raw[b]["rulebook"]["assetCatalog"]
    for k, a in own.items():
        if k.split("§")[0] not in UNITCLS or "(" in k: continue
        ra = res(b)[k]
        if "Legends" in ((ra.get("keywords") or {}).get("Source") or []): continue
        pool = set(seen_bs[b])
        if b.startswith("SM_") or b == "Space_Marines":
            for o in seen_bs:
                if o.startswith("SM_") or o in ("Space_Marines", "Imperial_Agents"):
                    pool |= seen_bs[o]
        if n(k.split("§", 1)[1]) not in pool:
            add(b, "units", k.split("§", 1)[1], "current in Rz, not in the BSData catalogue",
                mfm="listed" if n(k.split("§", 1)[1]) in MFM_UNITS.get(b, {}) else "not listed")

out = {b: {c: v for c, v in cats.items()} for b, cats in sorted(R.items())}
json.dump(out, open(OUT_JSON, "w"), indent=1, ensure_ascii=False)
CATS_ORDER = ["units", "points", "composition", "statline", "weapons", "options"]
with open(OUT_MD, "w") as f:
    f.write("# BSData 11e vs Rosterizer 40k 11e — discrepancies by faction\n\n")
    f.write("BSData = github.com/BSData/wh40k-11e; Rz = the Rosterizer books; MFM = Munitorum Field Manual (points, and what is "
            "current; anything it doesn't list as current is Legends). Statline/weapon notes give a third opinion from the Wahapedia "
            "export: 'Rz differs from Waha too' items are the likeliest Rz errors; 'Rz matches Waha — BSData differs' usually means "
            "BSData still carries an older profile. Options: 'named differently' pairs a BSData item with the Rz item it most likely is.\n\n")
    f.write("| Book | " + " | ".join(CATS_ORDER) + " |\n|---|" + "---|" * len(CATS_ORDER) + "\n")
    for b, cats in out.items():
        f.write(f"| {b} | " + " | ".join(str(len(cats.get(c, []))) for c in CATS_ORDER) + " |\n")
    for b, cats in out.items():
        f.write(f"\n## {b}\n")
        for c in CATS_ORDER:
            items = cats.get(c) or []
            if not items: continue
            prio = lambda it: (0 if "Rz differs" in (it.get("note") or "") or "Rz cost" in it["item"] else
                               2 if "BSData differs" in (it.get("note") or "") else 1, it["unit"])
            items = sorted(items, key=prio)
            f.write(f"\n### {c} ({len(items)})\n")
            for it in items:
                extra = "; ".join(f"{k}: {v}" for k, v in it.items() if k not in ("unit", "item"))
                f.write(f"- **{it['unit']}** — {it['item']}" + (f" ({extra})" if extra else "") + "\n")
tot = Counter()
for b, cats in out.items():
    for c, v in cats.items():
        tot[c] += len(v)
print(dict(tot))
