"""Shared pieces for the Space Marine family Crusade specs (Space_Marines + the four chapter books).
The whole family reads one Wahapedia section (crus10_space-marines: the 11e codex has no Crusade section); the chapter
supplements repeat the heading names, so blocks are picked by occurrence index (nth)."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crusade_lib as L
import crusade_waha as Wh

SEC = Wh.Section("space-marines", "10")
NTH = {"Space_Marines": 0, "SM_Black_Templars": 1, "SM_Dark_Angels": 2, "SM_Blood_Angels": 3, "SM_Space_Wolves": 4}
NARR_PARENT = L.ev(["{parent}", "stats", "Play", "value"], "Narrative")   # the Space Marines allowances test the parent


def costed(entries):
    """entries from SEC.named() whose text opens with the Honour-point / Relic-Fragment cost line → [{name, cost, text}]"""
    out = []
    for e in entries:
        pars = e["text"].split("\n\n")
        cost = None
        if pars and re.fullmatch(r"\d+", pars[0]):
            cost = int(pars[0])
            pars = pars[1:]
            if pars and len(pars) > 1 and not Wh.is_rules(pars[0]):   # the flavour line sits after the cost
                pars = pars[1:]
        out.append({"name": e["name"], "cost": cost, "text": "\n\n".join(pars)})
    return out


def agendas_dedupe(book, names, faction):
    """P8 with a chain-wide duplicate check (the books already carry some agendas with different capitalisation)"""
    have = set()
    for bk in L.chain(book):
        mr = (L.taxonomy(bk).get("Mission Record") or {}).get("stats", {})
        for st in ("Agenda 1", "Agenda 2"):
            have |= {L.norm(n) for n in (mr.get(st, {}).get("ranks") or {})}
    new = [n for n in names if L.norm(n) not in have]
    if new:
        L.agendas(book, new, faction)
    return new


def reqs_nth(nth):
    out = []
    for e in SEC.named("Requisitions", nth=nth):
        if not e["cost"] or not e["text"]:
            continue
        rp = int(re.match(r"\d+", e["cost"]).group())
        text = e["text"] if re.fullmatch(r"\d+RP", e["cost"]) else f"Cost: {e['cost']}. " + e["text"]
        out.append({"name": e["name"], "rp": rp, "cost": e["cost"], "text": text})
    return out


def badges_nth(nth):
    heads = [h for h in SEC.outline() if h[1] == "Crusade Badges"]
    start = heads[nth][2]
    out = []
    outline = SEC.outline()
    for k, (lvl, t, i) in enumerate(outline):
        if i > start and lvl == 2:
            end = outline[k + 1][2] if k + 1 < len(outline) else len(SEC.lines)
            pars = SEC.paragraphs(SEC.lines[i + 1:end])
            if len(pars) > 1 and not re.match(r"^(You have|You |At least|One or more|Or:)", pars[0]):
                pars = pars[1:]
            out.append({"name": t, "text": "\n".join(pars)})
            if len(out) == 3:
                break
    return out


def single_req(nth):
    """the '### Requisition' (singular) block of an Oathsworn Campaign → (name, rp, text)"""
    e = SEC.named("Requisition", nth=nth)[0]
    return e["name"], int(re.match(r"\d+", e["cost"] or "1").group()), e["text"]


def bonus(nth, title="Bonus Agendas"):
    return [{"name": a["name"], "text": a["text"]} for a in SEC.named(title, nth=nth)]


def campaign(book, name, intro, bonus_entries, requisition=None, *, per_battle=None, extra_text=""):
    """an Oathsworn Campaign§ asset shaped like Space_Marines' Precision Strike: Battle 1–3 bonus-agenda ranks and the
    campaign's own Requisition on its allowed list. The bonus agenda texts live in the asset text."""
    a = {"stats": {}}
    for i in (1, 2, 3):
        names = per_battle[i] if per_battle else [e["name"] for e in bonus_entries]
        a["stats"][f"Battle {i}"] = {"ranks": {"-": {"order": 0}, **{n: {"order": j + 1} for j, n in enumerate(names)}}}
    text = (intro + "\n\n" if intro else "") + "**Bonus Agendas** (one per battle, in addition to your two Agendas):\n" + "\n".join(f"- **{e['name']}:** {e['text']}" for e in bonus_entries)
    if requisition:
        rn, rp, rtext = requisition
        L.put_asset(book, f"Requisition§{rn}", {"stats": {"RP": {"value": rp}}, "text": rtext}, keep_text=False)
        a["allowed"] = {"items": [f"Requisition§{rn}"]}
        text += f"\n\n**Requisition — {rn} ({rp}RP):** {rtext}"
    if extra_text:
        text += "\n\n" + extra_text
    a["text"] = text
    return L.put_asset(book, f"Oathsworn Campaign§{name}", a, keep_text=False)


def promotion(book, name, cost, text, *, allow_on=("Character",), evals=(), note=None):
    """a chapter promotion in the Space Marines Promotion economy: Promotion§name (Honour Points cost, one selection) +
    Promotion Ability§name carrying the rules text + an allowance rule on the unit class"""
    L.put_asset(book, f"Promotion Ability§{name}", {"text": text}, keep_text=False)
    L.put_asset(book, f"Promotion§{name}", {"stats": {"Honour Points": {"value": cost}, "Selection": {"ranks": {name: {"order": 1, "term": f"Promotion Ability§{name}"}}}}}, keep_text=False)
    for cls in allow_on:
        L.class_rule(book, cls, "allow" + re.sub(r"\W", "", name),
                     L.rule([L.add(["{self}", "allowed", "items"], f"Promotion§{name}")], [L.NARR] + list(evals), note=note))
    # roster-wide uniqueness (the Unique aspect only stops duplicates under one parent). The roster tally of the name
    # counts both the Promotion§ asset and the Promotion Ability§ trait it adds, so one holder = 2; a free seat (a named
    # character's ability alone) = 1 and then blocks a second holder (3).
    L.roster_rule(book, f"Only one {name} in your Crusade force.", L.error_rule([L.ev(["{self}", "tally", name], mx=2)]))


def intro_of(title, nth=0):
    """first paragraph under a heading (the campaign's description)"""
    pars = SEC.paragraphs(SEC.block(title, nth))
    return pars[0] if pars else ""
