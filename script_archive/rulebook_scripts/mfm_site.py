"""Read the official Munitorum Field Manual site (mfm.warhammer-community.com) and check the BSData
transcription (wh40k-11e-mfm) against it.

The site is a streamed React page: the points sit in `<div hidden id="S:n">` segments that are spliced into
`<template id="P:n">` placeholders client-side. We splice them ourselves and read the text. Legends units are
loaded only when "Show Legends" is ticked, so they are not in the served HTML: the BSData `legends: true`
flags stay the Legends list, and a unit the site shows is current by definition.

  MFM_SITE_DIR=<cached html dir> MFM_DIR=<bsdata clone> PYTHONPATH=<pyyaml> python3 mfm_site.py [--fetch] [out.json]
"""
import html, json, os, re, sys, urllib.request
from pathlib import Path
SITE = "https://mfm.warhammer-community.com/en/"
SLUGS = ["adepta-sororitas", "adeptus-custodes", "adeptus-mechanicus", "aeldari", "astra-militarum", "black-templars", "blood-angels",
         "chaos-daemons", "chaos-knights", "chaos-space-marines", "chaos-titan-legions", "dark-angels", "death-guard", "deathwatch", "drukhari",
         "emperors-children", "genestealer-cults", "grey-knights", "imperial-agents", "imperial-knights", "leagues-of-votann", "necrons", "orks",
         "space-marines", "space-wolves", "tau-empire", "thousand-sons", "titan-legions", "tyranids", "world-eaters"]
CACHE = Path(os.environ.get("MFM_SITE_DIR", "mfm_site_cache"))
TIER = {"YOUR UNIT COSTS": "[1,)", "YOUR 1ST UNIT COSTS": "[1,1]", "YOUR 2ND + UNIT COSTS": "[2,)", "YOUR 1ST TO 2ND UNITS COST": "[1,2]",
        "YOUR 3RD + UNIT COSTS": "[3,)", "YOUR 1ST TO 3RD UNITS COST": "[1,3]", "YOUR 4TH + UNIT COSTS": "[4,)"}
MARKERS = {"UPDATED", "BODYGUARD UNITS UPDATED", "WARGEAR COSTS REMOVED", "NEW"}


def page(slug, fetch=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{slug}.html"
    if fetch or not f.exists():
        req = urllib.request.Request(SITE + slug, headers={"User-Agent": "Mozilla/5.0"})
        f.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return f.read_text(encoding="utf-8")


def segments(s):
    """{id: content} of the streamed `<div hidden id="S:n">` segments; a segment ends at the script that splices it
    (`$RS("S:n","P:n")` or `$RC("B:m","S:n")`), so nested markup inside it doesn't cut it short; a segment streamed
    inside another's extent is its own placeholder's content and is cut out of the outer one"""
    found = []
    for m in re.finditer(r'<div hidden id="(S:[0-9a-f]+)">', s):
        sid = m.group(1)
        j = s.find(f'$RS("{sid}"', m.end())
        j2 = s.find(f'"{sid}")', m.end())
        j = min(x for x in (j, j2) if x >= 0) if max(j, j2) >= 0 else -1
        if j < 0:
            continue
        k = s.rfind("<script>", m.end(), j)
        found.append((sid, m.start(), m.end(), k, s.find("</script>", j) + 9))
    out, spans = {}, []
    for sid, a, c, k, b in found:
        inner = sorted((x[1], x[4]) for x in found if a < x[1] and x[4] <= b)
        parts, last = [], c
        for ia, ib in inner:
            if ia >= last:
                parts.append(s[last:ia]); last = ib
        parts.append(s[last:k])
        body = "".join(parts).rstrip()
        if body.endswith("</div>"):
            body = body[:-6]
        out[sid] = body
        spans.append((a, b))
    return out, spans


def resolve(s):
    """splice the streamed segments into their placeholders and drop the staging copies"""
    segs, spans = segments(s)
    body, last = [], 0
    for a, b in sorted(spans):   # the hidden segments sit at the end; remove them from the live tree
        if a >= last:
            body.append(s[last:a]); last = b
    body.append(s[last:]); body = "".join(body)
    for _ in range(30):
        before = body
        body = re.sub(r'<template id="P:([0-9a-f]+)"></template>', lambda m: segs.get("S:" + m.group(1), ""), body)
        body = re.sub(r'<!--\$\?--><template id="B:([0-9a-f]+)"></template><!--/\$-->', lambda m: segs.get("S:" + m.group(1), ""), body)
        body = re.sub(r'<!--\$\?--><template id="B:([0-9a-f]+)"></template>(?:(?!<!--\$\?-->).)*?<!--/\$-->', lambda m: segs.get("S:" + m.group(1), ""), body, flags=re.S)
        if body == before:
            break
    return body


def lines_of(s, resolved=False):
    t = re.sub(r"<script.*?</script>", "", s if resolved else resolve(s), flags=re.S)
    t = re.sub(r"<(br|/p|/div|/li|/h\d|/span|/section|/header|/ul)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return [l.strip() for l in t.split("\n") if l.strip()]


BLOCK = '<div class="flex flex-col space-y-1 m-1 print:break-inside-avoid-page">'
PTS = re.compile(r"(?:[▲▼]\s*\(([+-]\d[\d,]*)\)\s*)?(\d[\d,]*) pts$")


def pts(l):
    m = PTS.search(l)
    return (int(m.group(2).replace(",", "")), int(m.group(1).replace(",", "")) if m.group(1) else None) if m else None


def parse_unit(block):
    L = lines_of(block, resolved=True)
    while L and L[0] in ("▲", "▼"):
        L.pop(0)
    if not L:
        return None
    u = {"name": L[0], "updated": False, "markers": [], "pricing": [], "wargear": [], "leaderTo": [], "supportTo": []}
    k = 1
    while k < len(L):
        l = L[k]
        if l in TIER:
            t = {"range": TIER[l], "label": l.title(), "costs": []}; k += 1
            while k + 1 < len(L) and re.match(r"\d", L[k]) and pts(L[k + 1]):
                p, d = pts(L[k + 1]); models = sum(int(x) for x in re.findall(r"(\d+)(?:-\d+)? ", L[k] + " "))
                t["costs"].append({"models": models, "points": p, "desc": L[k], **({"delta": d} if d is not None else {})}); k += 2
            u["pricing"].append(t)
        elif l == "WARGEAR OPTIONS":
            k += 1
            while k + 1 < len(L) and L[k].startswith("per ") and pts(L[k + 1]):
                u["wargear"].append({"item": L[k][4:], "points": pts(L[k + 1])[0]}); k += 2
        elif l in ("LEADER", "SUPPORT") and k + 1 < len(L):
            u["leaderTo" if l == "LEADER" else "supportTo"] = [x.strip() for x in L[k + 1].split(",")]; k += 2
        elif l in MARKERS or l in ("▲", "▼"):
            if l in MARKERS:
                u["markers"].append(l)
            k += 1
        else:
            u.setdefault("unparsed", []).append(l); k += 1
    u["updated"] = "UPDATED" in u["markers"] or any("delta" in c for t in u["pricing"] for c in t["costs"])
    return u


def parse(slug, fetch=False):
    body = resolve(page(slug, fetch))
    L = lines_of(body, resolved=True)
    out = {"slug": slug, "version": next((l for l in L if re.fullmatch(r"v\d+\.\d+", l)), None), "detachments": [], "units": []}
    i = L.index("DETACHMENTS") if "DETACHMENTS" in L else None
    j = next((x for x in range(i + 1, len(L)) if L[x] == "UNITS"), len(L)) if i is not None else len(L)   # the nav has a UNITS link too
    k = (i or 0) + 1
    while i is not None and k < j:   # NAME, nDP, ROLE, [UNIQUE: X], ENHANCEMENTS, (name, pts)*
        if re.fullmatch(r"\d+DP", L[k]) and k > 0:
            d = {"name": L[k - 1], "dp": int(L[k][:-2]), "roles": [], "unique": None, "enhancements": []}
            k += 1
            while k < j and L[k].isupper() and not L[k].startswith("UNIQUE") and L[k] != "ENHANCEMENTS":   # one role per DP
                d["roles"].append(L[k]); k += 1
            if k < j and L[k].startswith("UNIQUE:"):
                d["unique"] = L[k][7:].strip(); k += 1
            if k < j and L[k] == "ENHANCEMENTS":
                k += 1
                while k < j:
                    if L[k] in ("LEADER:", "SUPPORT:"):   # a detachment-level attach note sits between the enhancements
                        d.setdefault(L[k][:-1].lower() + "To", [])
                        k += 1
                        while k < j and L[k].isupper() and not re.fullmatch(r"\d+DP", L[k]) and not (k + 1 < j and re.fullmatch(r"\d+DP", L[k + 1])):
                            d[L[k - 1][:-1].lower() + "To" if L[k - 1] in ("LEADER:", "SUPPORT:") else list(d)[-1]].append(L[k]); k += 1
                        continue
                    if k + 1 < j and pts(L[k + 1]):
                        d["enhancements"].append({"name": L[k], "points": pts(L[k + 1])[0]}); k += 2
                    else:
                        break
            out["detachments"].append(d)
        else:
            k += 1
    units_html = body[body.find("UNITS</h3>"):] if "UNITS</h3>" in body else ""
    seen = set(); group = None
    parts = units_html.split(BLOCK)[1:]
    for blk in parts:
        u = parse_unit(blk)
        if not u:
            continue
        tail = [x for x in u.pop("unparsed", []) if x.isupper()]
        if u["pricing"] and u["name"] not in seen:
            if group:
                u["groupTitle"] = group
            seen.add(u["name"]); out["units"].append(u)
        if tail:
            group = tail[-1]
    return out


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("‑", "-").replace("’", "'"))


LEG_FILES, CUR_FILES, SITE_UNITS = {}, {}, set()


def check(site, mfm_dir):
    """differences between the site and the BSData YAML: returns a list of strings"""
    import yaml
    if not LEG_FILES and not CUR_FILES:
        for f in Path(mfm_dir).glob("data/*.yaml"):
            for x in yaml.safe_load(open(f)).get("units") or []:
                (LEG_FILES if x.get("legends") else CUR_FILES).setdefault(norm(x["name"]), set()).add(f.stem)
    y = yaml.safe_load(open(Path(mfm_dir) / "data" / f"{site['slug']}.yaml"))
    # a leader target the site omits because it is Legends: flagged here, or (a shared unit) flagged wherever it is listed
    def is_legends(nm):
        return site["slug"] in LEG_FILES.get(nm, ()) or (site["slug"] not in CUR_FILES.get(nm, ()) and bool(LEG_FILES.get(nm)))
    out = []
    if str(y.get("version")) != (site["version"] or "")[1:]:
        out.append(f"version: site {site['version']} vs yaml {y.get('version')}")
    by = {}
    for u in y.get("units") or []:
        by.setdefault(norm(u["name"]), []).append(u)
    for u in site["units"]:
        cands = by.get(norm(u["name"]))
        if not cands:
            out.append(f"site unit not in yaml: {u['name']}"); continue
        yu = next((c for c in cands if not c.get("groupTitle")), cands[0])
        if yu.get("legends"):
            out.append(f"yaml says Legends but the site shows it: {u['name']}")
        sc = [(t["range"], c["models"], c["points"]) for t in u["pricing"] for c in t["costs"]]
        yc = [(t["range"], c["models"], c["points"]) for t in yu["pricing"] for c in t["costs"] if not c.get("addon")]
        if sc != yc:
            out.append(f"points: {u['name']}: site {sc} vs yaml {yc}")
        sw = sorted((w["item"].lower(), w["points"]) for w in u["wargear"]); yw = sorted((w["item"].lower(), w["points"]) for w in yu.get("wargear") or [])
        if sw != yw:
            out.append(f"wargear: {u['name']}: site {sw} vs yaml {yw}")
        # the site's LEADER lists are the full codex lists, Legends targets included (those have no block anywhere)
        sl = sorted(norm(x) for x in u["leaderTo"] if norm(x) in SITE_UNITS); yl = sorted(norm(x) for x in yu.get("leaderTo") or [] if not is_legends(norm(x)))
        if sl != yl:
            out.append(f"leaderTo: {u['name']}: site only {sorted(set(sl) - set(yl))} / yaml only {sorted(set(yl) - set(sl))}")
    site_names = {norm(u["name"]) for u in site["units"]}
    for u in y.get("units") or []:
        if not u.get("legends") and norm(u["name"]) not in site_names:
            out.append(f"yaml current unit not on the site: {u['name']}")
    yd = {norm(d["name"]): d for d in y.get("detachments") or []}
    for d in site["detachments"]:
        q = yd.get(norm(d["name"]))
        if not q:
            out.append(f"site detachment not in yaml: {d['name']}"); continue
        se = sorted((norm(e["name"]), e["points"]) for e in d["enhancements"]); ye = sorted((norm(e["name"]), e["points"]) for e in q.get("enhancements") or [])
        if se != ye:
            out.append(f"enhancements: {d['name']}: site {se} vs yaml {ye}")
        if q.get("dp") not in (None, d["dp"]):
            out.append(f"dp: {d['name']}: site {d['dp']} vs yaml {q.get('dp')}")
    return out


if __name__ == "__main__":
    fetch = "--fetch" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    data = {s: parse(s, fetch) for s in SLUGS}
    if args:
        json.dump(data, open(args[0], "w"), ensure_ascii=False, indent=1)
    mfm = os.environ.get("MFM_DIR")
    SITE_UNITS.update(norm(u["name"]) for d in data.values() for u in d["units"])
    total = 0
    for s in SLUGS:
        d = data[s]
        print(f"== {s}: {d['version']}, {len(d['units'])} units, {len(d['detachments'])} detachments")
        if mfm:
            for line in check(d, mfm):
                print("   ", line); total += 1
    if mfm:
        print(f"\n{total} differences between the site and {mfm}")
