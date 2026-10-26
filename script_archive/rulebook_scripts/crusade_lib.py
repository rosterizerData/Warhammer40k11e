"""Shared helpers for building the faction Crusade mini-games (the "trackers") into the 40k 11e books.

Patterns (see the plan: Crusade Mini-games Plan, 2026-10-26):
  P1 tracker trait  – a roster rule `useCrusade<Book>` adds `<Class>§<Item>` to the roster's traits in Narrative play
  P2 counter+level  – numeric stat with increment + a rank/tracked flag that rules derive from thresholds
  P3 currency       – an "earned" counter, a cost stat on the purchasable class, a roster rule that errors when overspent
  P4 role flag      – a "✓" rank on eligible characters with `tracking`, enforced one-per-roster
  P5 tag gates      – honours carry Tags; Unit rules grant the tag from keywords/ranks/tracker state
  P6 child sets     – fixed child assets of the tracker (threats, districts, visions…) with their own stats
  P7 no-XP units    – summoned/legion units: Experience hidden, no Battle Honours, auto-pass Out of Action
  P8 agendas        – faction Agendas appended to the Mission Record's Agenda 1/2 rank lists (per book override)

Books are plain JSON (indent=2, ensure_ascii=False). Everything here is idempotent: re-running a spec rewrites the same
keys. Nothing here touches git.
"""
import copy, json, os, re
from pathlib import Path

RZ = Path(__file__).resolve().parents[2]
BOOK_FILES = {p.stem: p for p in RZ.glob("*.rulebook")}
_cache = {}

NARR = {"actionable": True, "not": False, "operator": "AND", "paths": [["{roster}", "stats", "Play", "value"]], "value": "Narrative"}
NARR_SELF = {"actionable": True, "not": False, "operator": "AND", "paths": [["{self}", "stats", "Play", "value"]], "value": "Narrative"}


# ───────────────────────── books ─────────────────────────
def load(book):
    if book not in _cache:
        _cache[book] = json.load(open(BOOK_FILES[book], encoding="utf-8"))
    return _cache[book]


def save(book, bump=True):
    """atomic write (the headless runner reads every book in the folder; several builds may run side by side)"""
    d = load(book)
    if bump:
        d["revision"] = bump_rev(d.get("revision") or "11.2.0")
    tmp = BOOK_FILES[book].with_suffix(".rulebook.tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, BOOK_FILES[book])
    return d["revision"]


def bump_rev(rev):
    parts = rev.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def rulebook(book):
    return load(book)["rulebook"]


def catalog(book):
    return rulebook(book)["assetCatalog"]


def taxonomy(book):
    return rulebook(book).setdefault("assetTaxonomy", {})


def by_name():
    """book display name → file stem (dependencies refer to display names)"""
    out = {}
    for stem in BOOK_FILES:
        out[load(stem)["name"].strip()] = stem
    return out


def chain(book):
    """dependency chain, root first, ending with the book itself"""
    names = by_name()
    out, seen = [], set()

    def walk(b):
        if b in seen:
            return
        seen.add(b)
        for dep in load(b).get("dependencies") or []:
            stem = names.get(dep["name"].strip())
            if stem:
                walk(stem)
        out.append(b)
    walk(book)
    return out


def resolved_asset(book, key):
    """asset as the chain sees it (shallow merge of dict sections, later books win)"""
    out = {}
    for b in chain(book):
        v = catalog(b).get(key)
        if v is not None:
            out = merge(out, v)
    return out


def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = merge(a[k], v) if k in a else copy.deepcopy(v)
        return out
    if isinstance(a, list) and isinstance(b, list):
        return a + [x for x in b if x not in a]
    return copy.deepcopy(b)


def faction_value(book):
    r = catalog(book).get("Roster§Roster") or {}
    return ((r.get("stats") or {}).get("Faction") or {}).get("value")


# ───────────────────────── evals / actions ─────────────────────────
def ev(paths, value=None, *, op="AND", not_=False, contains=False, mn=None, mx=None, actionable=True, equation=None):
    """one eval. paths: a single path (list of str) or a list of paths"""
    if paths and isinstance(paths[0], str):
        paths = [paths]
    e = {"actionable": actionable, "not": not_, "operator": op, "paths": paths}
    if value is not None:
        e["value"] = value
    if contains:
        e["contains"] = True
    if mn is not None:
        e["min"] = mn
    if mx is not None:
        e["max"] = mx
    if equation:
        e["equation"] = equation
    return e


def ev_kw(keyword, who="{self}", field="Keywords", not_=False):
    return ev([who, "keywords", field], keyword, contains=True, not_=not_)


def ev_stat(stat, value, who="{self}", not_=False):
    return ev([who, "stats", stat, "value"], value, not_=not_)


def ev_tracked(name, mn=None, mx=None, who="{roster}", not_=False):
    return ev([who, "tracked", name], mn=mn, mx=mx, not_=not_)


def act(kind, path, value, **kw):
    a = {"actionType": kind, "iterations": 1, "paths": [path], "value": value}
    a.update(kw)
    return a


def add(path, value, **kw): return act("add", path, value, **kw)
def set_(path, value, **kw): return act("set", path, value, **kw)
def mod(path, value, **kw): return act("modify", path, value, **kw)
def rem(path, value, **kw): return act("remove", path, value, **kw)


def rule(actions=None, evals=None, *, fail="pass", evaluate="AND", order=None, note=None):
    r = {"actions": actions or [], "evals": evals or [], "evaluate": evaluate, "failState": fail}
    if not actions:
        del r["actions"]
    if order is not None:
        r["order"] = order
    if note:
        r["note"] = note
    return r


def error_rule(evals, *, evaluate="AND", note=None):
    """validation only: errors when the evals fail"""
    return rule(None, evals, fail="error", evaluate=evaluate, note=note)


# ───────────────────────── stats ─────────────────────────
def num(value=0, *, mn=0, mx=None, step=1, tracked=False, visibility="normal", group=None, group_order=None, label=None,
        icons=None, order=None, dynamic=True):
    s = {"statType": "numeric", "value": value, "visibility": visibility}
    if dynamic:
        s["dynamic"] = True
        if step:
            s["increment"] = {"value": step}
    if mn is not None:
        s["min"] = mn
    if mx is not None:
        s["max"] = mx
    if tracked:
        s["tracked"] = True
    if group:
        s["group"] = group
        if group_order is not None:
            s["groupOrder"] = group_order
    if label:
        s["label"] = label
    if icons:
        s["icons"] = icons
    if order is not None:
        s["statOrder"] = order
    return s


def rank(values, value="-", *, tracking=None, traits=None, tracked=None, visibility="normal", group=None, group_order=None,
         label=None, order=None, dash=True, dynamic=True):
    """rank stat. values: list of names (order kept) or dict name → extra rank fields.
    tracking: {name: {tracked: n}} or a single dict applied to every non-dash rank."""
    ranks = {}
    i = 0
    if dash:
        ranks["-"] = {"order": 0}
        i = 1
    items = values.items() if isinstance(values, dict) else [(v, {}) for v in values]
    for name, extra in items:
        r = {"order": i}
        i += 1
        if tracking:
            t = tracking.get(name) if (isinstance(tracking, dict) and name in tracking and isinstance(tracking[name], dict) and all(isinstance(v, (int, float)) for v in tracking[name].values())) else (tracking if all(isinstance(v, (int, float)) for v in tracking.values()) else None)
            if t:
                r["tracking"] = dict(t)
        if traits and name in traits:
            r["traits"] = [{"trait": x} for x in traits[name]]
        r.update(extra)
        ranks[name] = r
    s = {"statType": "rank", "ranks": ranks, "value": value, "visibility": visibility}
    if dynamic:
        s["dynamic"] = True
    # `tracked` bubbles the rank's own number under the STAT's name; rank `tracking` bubbles under its own keys. A flag
    # whose tracking key equals its stat name would count twice with both on, so tracked is opt-in only.
    if tracked:
        s["tracked"] = True
    if group:
        s["group"] = group
        if group_order is not None:
            s["groupOrder"] = group_order
    if label:
        s["label"] = label
    if order is not None:
        s["statOrder"] = order
    return s


def flag(*, tracking=None, traits=None, tracked=None, **kw):
    """a '-' / '✓' toggle; the ✓ rank carries number 1 so SUM evals over `processed numeric current` can count ticks"""
    s = rank({"✓": {"number": 1}}, tracking={"✓": tracking} if tracking else None, traits={"✓": traits} if traits else None,
             tracked=tracked, **kw)
    s["ranks"]["-"]["number"] = 0
    return s


def count_flags(stats_names, who="{self}"):
    """a SUM eval over ✓ flags (use with set_(..., ["{this}", "evals", "0", "result", "integer"]))"""
    return ev([[who, "stats", n, "processed", "numeric", "current"] for n in stats_names], op="SUM", mn=0)


def rankvalue(stat, who="{self}"):
    """path to a rank's current numeric value (for arithmetic)"""
    return [who, "stats", stat, "processed", "numeric", "current"]


# ───────────────────────── taxonomy / assets ─────────────────────────
def ensure_class(book, name, spec, replace=False):
    T = taxonomy(book)
    if replace or name not in T:
        T[name] = copy.deepcopy(spec)
    else:
        T[name] = merge(T[name], spec)
    return T[name]


def class_rule(book, cls, name, r):
    ensure_class(book, cls, {})
    taxonomy(book)[cls].setdefault("rules", {})[name] = copy.deepcopy(r)


def class_rules(book, cls, rules):
    for n, r in rules.items():
        class_rule(book, cls, n, r)


def allow_items(book, cls, items):
    c = ensure_class(book, cls, {})
    al = c.setdefault("allowed", {}).setdefault("items", [])
    for it in items:
        if it not in al:
            al.append(it)


def allow_classes(book, cls, classes):
    c = ensure_class(book, cls, {})
    al = c.setdefault("allowed", {}).setdefault("classifications", [])
    for it in classes:
        if it not in al:
            al.append(it)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("’", "'"))


def existing_key(book, key):
    """the book's key for the same class+name ignoring case/punctuation (so 'Earning of A Name' finds 'Earning of a Name')"""
    cat = catalog(book)
    if key in cat:
        return key
    cls, _, name = key.partition("§")
    n = norm(name)
    for k in cat:
        if k.startswith(cls + "§") and norm(k.split("§", 1)[1]) == n:
            return k
    return key


def put_asset(book, key, asset, *, keep_text=False, reuse_key=True):
    """write an asset; with keep_text an existing text wins (hand edits survive); reuse_key keeps the book's spelling"""
    cat = catalog(book)
    if reuse_key:
        key = existing_key(book, key)
    a = copy.deepcopy(asset)
    if keep_text and key in cat and cat[key].get("text"):
        a["text"] = cat[key]["text"]
    cat[key] = a
    return key


def patch_asset(book, key, patch):
    cat = catalog(book)
    cat[key] = merge(cat.get(key, {}), patch)
    return cat[key]


def asset_rule(book, key, name, r):
    cat = catalog(book)
    cat.setdefault(key, {}).setdefault("rules", {})[name] = copy.deepcopy(r)


def del_assets(book, keys):
    cat = catalog(book)
    n = 0
    for k in list(keys):
        if k in cat:
            del cat[k]
            n += 1
    return n


def keys_with_prefix(book, prefix):
    return [k for k in catalog(book) if k.startswith(prefix)]


# ───────────────────────── higher-level pieces ─────────────────────────
def roster_rule(book, name, r):
    cat = catalog(book)
    cat.setdefault("Roster§Roster", {}).setdefault("rules", {})[name] = copy.deepcopy(r)


def tracker(book, cls, item, *, stats=None, children=None, text=None, faction=None, rule_name=None, visibility="always",
            allowed_items=None, allowed_classes=None, class_rules_=None, order=0):
    """P1: class + item + roster rule that adds the item to the roster's traits in Narrative play.
    children: list of "<Class>§<Item>" fixed traits of the tracker (make them with child()).
    The adding rule runs at `order` 0: the engine injects a rule-added asset's rules only when their order is GREATER
    than the adding rule's order (registry-asset-mutations.addRules), and an unordered adder makes every rule of the
    added asset stale ("added too late"). So the tracker's own rules use order ≥ 1 or stay unordered."""
    spec = {"allowed": {"classifications": list(allowed_classes or []), "items": list(allowed_items or [])},
            "aspects": {"Visibility": visibility}, "assets": {"traits": []}, "templateClass": ""}
    if stats:
        spec["stats"] = copy.deepcopy(stats)
    ensure_class(book, cls, spec, replace=True)
    if class_rules_:
        class_rules(book, cls, class_rules_)
    a = {}
    if children:
        a["assets"] = {"traits": list(children)}
    if text:
        a["text"] = text
    put_asset(book, f"{cls}§{item}", a, keep_text=False)
    evals = [NARR_SELF]
    if faction:
        evals.append(ev(["{self}", "stats", "Faction", "value"], faction))
    roster_rule(book, rule_name or "useCrusade" + re.sub(r"\W", "", book), rule([add(["{self}", "traits"], f"{cls}§{item}")], evals, order=order,
                note="Crusade: adds the faction's Crusade tracker in Narrative play (early order so the tracker's own rules still run)"))
    return f"{cls}§{item}"


def child(book, cls, item, *, stats=None, text=None, rules=None, aspects=None, allowed_items=None, allowed_classes=None,
          children=None, class_rules_=None, rename=False, describe=False):
    """P6: a fixed child of a tracker (its own class; stats on the class, texts/rules on the item)"""
    spec = {"aspects": {"Visibility": "always", **({"Rename": True} if rename else {}), **({"Describe": True} if describe else {}), **(aspects or {})},
            "templateClass": ""}
    if stats:
        spec["stats"] = copy.deepcopy(stats)
    if allowed_items or allowed_classes:
        spec["allowed"] = {"classifications": list(allowed_classes or []), "items": list(allowed_items or [])}
    T = taxonomy(book)
    if cls in T:
        T[cls] = merge(T[cls], spec)
        if stats:   # a stat definition is replaced whole (a re-run must be able to drop keys such as `tracked`)
            T[cls].setdefault("stats", {}).update(copy.deepcopy(stats))
    else:
        T[cls] = spec
    if class_rules_:
        class_rules(book, cls, class_rules_)
    a = {}
    if text:
        a["text"] = text
    if rules:
        a["rules"] = copy.deepcopy(rules)
    if children:
        a["assets"] = {"traits": list(children)}
    put_asset(book, f"{cls}§{item}", a)
    return f"{cls}§{item}"


def honour_class(book, cls, *, parent="Battle Honour", unique=True, lock=True, stats=None, allow_on=("Character",),
                 allow_evals=None, allow_note=None, cap=None, cap_text=None, cap_on=None):
    """a family of honours with its own class, templated on Battle Honour (never on Crusade Honour: an allowance on a
    classification admits every class templated on it, and the core allows Crusade Honour on every unit), or on
    Crusade Relic / Battle Scar when the family counts as relics or scars. Adds an allowance rule on the given unit
    classes (Narrative play + allow_evals) and an optional per-model cap."""
    spec = {"aspects": {}, "keywords": {"Tags": [], "Keywords": []}, "templateClass": parent}
    if lock:
        spec["aspects"]["Lock Qty"] = True
    if unique:
        spec["aspects"]["Unique"] = True
    if stats:
        spec["stats"] = copy.deepcopy(stats)
    ensure_class(book, cls, spec, replace=True)
    evals = [NARR] + list(allow_evals or [])
    for ucls in allow_on:
        class_rule(book, ucls, "allow" + re.sub(r"\W", "", cls), rule([add(["{self}", "allowed", "classifications"], cls)], evals,
                                                                   note=allow_note or f"Crusade: may take {cls} honours"))
        if cap:
            class_rule(book, cap_on or ucls, cap_text or f"No more than {cap} {cls} honours per model.",
                       error_rule([ev(["{self}", "tally", cls], mx=cap)]))
    return cls


def honours(book, cls, items, *, tags=None, keywords=None, pts=None, keep_text=True):
    """items: list of dicts {name, text, tags?, keywords?, stats?, rules?}"""
    keys = []
    for it in items:
        a = {"keywords": {"Tags": list(it.get("tags") or tags or []), "Keywords": list(it.get("keywords") or keywords or [])}, "text": it["text"]}
        if not a["keywords"]["Keywords"]:
            del a["keywords"]["Keywords"]
        st = dict(it.get("stats") or {})
        if pts is not None and "Crusade Pts" not in st:
            st["Crusade Pts"] = {"value": pts}
        if st:
            a["stats"] = st
        if it.get("rules"):
            a["rules"] = copy.deepcopy(it["rules"])
        keys.append(put_asset(book, f"{cls}§{it['name']}", a, keep_text=keep_text))
    return keys


def reclass(book, old_prefix, new_cls, names=None, *, patch=None):
    """move assets from one class to another (e.g. Crusade Honour§Veil of Flies → Boon of Nurgle§Veil of Flies)"""
    cat = catalog(book)
    moved = []
    for k in list(cat):
        if not k.startswith(old_prefix):
            continue
        name = k.split("§", 1)[1]
        if names is not None and name not in names:
            continue
        a = cat.pop(k)
        if patch:
            a = merge(a, patch)
        cat[f"{new_cls}§{name}"] = a
        moved.append(name)
    return moved


def unit_stat(book, cls, name, stat, *, show_when=None, show_rule=None):
    """a stat on a unit class, hidden until the show rule fires (default: Narrative play)"""
    s = copy.deepcopy(stat)
    s["visibility"] = "hidden"
    ensure_class(book, cls, {})
    taxonomy(book)[cls].setdefault("stats", {})[name] = s
    class_rule(book, cls, show_rule or "crusadeShow" + re.sub(r"\W", "", name),
               rule([set_(["{self}", "stats", name, "visibility"], "normal")], [NARR] + list(show_when or []),
                    note="Crusade: shown in Narrative play"))


def tag_grant(book, cls, tag, keyword=None, *, field="Keywords", extra_evals=None):
    """P5: units with the keyword (default: the tag itself) may take honours tagged `tag` (constraints.any)"""
    kw = keyword or tag
    class_rule(book, cls, "crusadeTag" + re.sub(r"\W", "", tag),
               rule([add(["{self}", "constraints", "any"], tag)], [NARR, ev_kw(kw, field=field)] + list(extra_evals or []),
                    note=f"Crusade: units with the {kw} keyword may take the honours tagged {tag}"))


def tag_block(book, cls, tag, keyword=None, *, field="Keywords"):
    """P5: units with the keyword cannot take honours tagged not<Tag> (constraints.none)"""
    kw = keyword or tag
    class_rule(book, cls, "crusadeNot" + re.sub(r"\W", "", tag),
               rule([add(["{self}", "constraints", "none"], "not" + re.sub(r"\s", "", tag))], [NARR, ev_kw(kw, field=field)],
                    note=f"Crusade: units with the {kw} keyword cannot take the honours tagged not{tag}"))


def no_xp(book, cls, keyword, *, label=None):
    """P7: units with the keyword never gain XP or Battle Honours"""
    nm = re.sub(r"\W", "", keyword)
    class_rule(book, cls, f"noCrusadeXp{nm}",
               rule([set_(["{self}", "stats", "Experience", "visibility"], "hidden"), set_(["{self}", "stats", "Battle Honour", "max"], 0)],
                    [NARR, ev_kw(keyword)], note=f"Crusade: {label or keyword} units never gain Experience points or Battle Honours and automatically pass Out of Action tests"))


def agendas(book, names, faction, *, start=100):
    """P8: append agendas to the Mission Record's Agenda 1/2 rank lists"""
    T = taxonomy(book)
    mr = T.setdefault("Mission Record", {}).setdefault("stats", {})
    for stat in ("Agenda 1", "Agenda 2"):
        ranks = mr.setdefault(stat, {}).setdefault("ranks", {})
        i = start
        for n in names:
            ranks[n] = {"order": i, "tracking": {f"{faction} Agenda": 1}}
            i += 1


def requisitions(book, items, *, on="Order of Battle", keep_text=True):
    keys = []
    for it in items:
        a = {"stats": {"RP": {"value": it.get("rp", 1)}}, "text": it["text"]}
        if it.get("tags"):
            a["keywords"] = {"Tags": list(it["tags"])}
        if it.get("rules"):
            a["rules"] = copy.deepcopy(it["rules"])
        keys.append(put_asset(book, f"Requisition§{it['name']}", a, keep_text=keep_text))
    if on:
        allow_items(book, on, keys)
    return keys


def badges(book, items, *, on="Order of Battle"):
    keys = []
    for it in items:
        keys.append(put_asset(book, f"Crusade Badge§{it['name']}", {"text": it["text"]}, keep_text=True))
    if on:
        allow_items(book, on, keys)
    return keys


def unique_in_roster(book, names, *, label=None):
    """roster-wide uniqueness. The `Unique` aspect only stops duplicates under the SAME parent (validate-roster
    appendUniquenessError), so an honour that may exist once per Crusade force needs a roster rule counting the roster's
    tally of its designation."""
    for n in names:
        roster_rule(book, f"Only one {n} in your Crusade force.", error_rule([ev(["{self}", "tally", n], mx=1)]))


def ability(book, name, text, *, aura=False):
    """an Ability§ trait (what a level or a controlled district grants)"""
    put_asset(book, f"Ability§{name}", {"text": text}, keep_text=False)
    return f"Ability§{name}"
