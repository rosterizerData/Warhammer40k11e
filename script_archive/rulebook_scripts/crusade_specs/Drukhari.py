"""Drukhari Crusade (10e codex, as carried on the 11e site): Ascendant Lords — Commorragh territories in twelve
districts, Rival Lords, Power. Source: Wahapedia crus11_drukhari. The district abilities were mis-filed in the
Aeldari book by the BSData import (the Aeldari spec deletes them there)."""
import re
SLUG, ED, FACTION = "drukhari", "11", "Drukhari"
LISTS = dict(agendas=True, requisitions=True, badges=True)

DISTRICTS = ["Weapon Forge", "Toxin Distillery", "Arena", "Scourge Spire", "Incubi Shrine", "Dock",
             "Sprawl Slum", "Flesh Market", "Shadow District", "Noble Spire", "Gang Territory", "Raidcraft Workshop"]
RIVAL_TYPES = {"Archon": "Noble Spire", "Succubus": "Arena", "Haemonculus": "Flesh Market"}
TRAIT_TAGS = {"Kabalite Trueborn": ["Kabalite Warriors", "Hand of the Archon"], "Hekatrix Bloodbrides": ["Wyches"], "Haemoxytes": ["Wracks"]}
GROUP_TAGS = {"Haemonculus Covens Units": ["Haemonculus Covens"], "Drukhari Units": ["Drukhari"], "Kabal Units": ["Kabal"], "Wych Cult Units": ["Wych Cult"]}


def territories(sec):
    """district → [(territory, D66)] from the two territory tables"""
    out, cur = {}, None
    for l in sec.block("Hostile Takeovers"):
        l = l.strip()
        m = re.match(r"^\|\s*([A-Z][A-Z ]{3,})\s*$", l)
        if m and m.group(1).strip().title() in [d.upper().title() for d in DISTRICTS]:
            cur = [d for d in DISTRICTS if d.upper() == m.group(1).strip()][0]
            out.setdefault(cur, [])
            continue
        m = re.match(r"^\|\s*(.+?)\s*\|\s*(\d\d)\s*$", l)
        if m and cur:
            out[cur].append((m.group(1).strip(), m.group(2)))
    return out


def district_abilities(sec):
    lines = [l.strip() for l in sec.block("District Abilities") if l.strip() and l.strip() != "|"]
    out, i = {}, 0
    while i < len(lines):
        if lines[i] in DISTRICTS and i + 2 < len(lines):
            out[lines[i]] = lines[i + 2]   # name, flavour, rules
            i += 3
        else:
            i += 1
    return out


def table_lines(sec, title, pat):
    return [re.sub(r"\s*\|\s*$", "", re.sub(r"^\|\s*", "", l.strip())) for l in sec.block(title) if re.match(pat, l.strip())]


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    # ── Ascendant Lord: one non-Epic Character, must be the Warlord ──
    L.unit_stat(b, "Character", "Ascendant Lord", L.flag(tracking={"Ascendant Lord": 1}, group="Crusade", group_order=11, order=20),
                show_when=[L.ev_kw("Epic Hero", not_=True)])
    L.class_rule(b, "Character", "ascendantLordKeyword", L.rule([L.add(["{self}", "keywords", "Keywords"], "Ascendant Lord")], [L.ev_stat("Ascendant Lord", "✓")]))
    # guarded with "not Narrative": stored ✓ values survive a switch to Matched play
    L.class_rule(b, "Character", "Your Ascendant Lord must be your Warlord.",
                 L.rule(None, [L.ev_stat("Play", "Narrative", who="{roster}", not_=True), L.ev_stat("Ascendant Lord", "-"), L.ev_stat("Warlord", "✓")], fail="error", evaluate="OR"))
    L.roster_rule(b, "One Ascendant Lord only.", L.rule(None, [L.ev_stat("Play", "Narrative", not_=True), L.ev_tracked("Ascendant Lord", mx=1, who="{self}")], fail="error", evaluate="OR"))
    # ── districts ──
    terr = territories(sec)
    abil = district_abilities(sec)
    children = []
    for d in DISTRICTS:
        L.ability(b, f"District: {d}", abil.get(d, ""))
        tlist = ", ".join(f"{n} ({c})" for n, c in terr.get(d, []))
        children.append(L.child(b, "District", d,
                                stats={"Territories held": L.num(0, mn=0, mx=6, order=1), "Controlled": L.flag(tracking={"District": 1}, order=2)},
                                rules={"controlled": L.rule([L.add(["{self}", "traits"], f"Ability§District: {d}")], [L.ev_stat("Controlled", "✓")])},
                                text=f"Territories (D66): {tlist}. Tick Controlled while your Ascendant Lord holds more territories in this district than any Rival Lord."))
    # ── rival lords ──
    rtraits = table_lines(sec, "Rival Lords", r"^\|\s*[A-Z][\w ]+:")
    activity = table_lines(sec, "Rival Activity", r"^\|\s*(\d\+?|\d or less)\s*\|")
    price = table_lines(sec, "Rival Activity", r"^\|\s*(SUFFER NO RIVALS|AGENT OF VECT|INTO SHADOW)")
    death = " ".join(l.strip() for l in sec.block("Death of a Lord") if l.strip())
    rival_text = ("**Rival Lords.** When you add an Ascendant Lord, generate three Rival Lords (D6: 1–2 Archon, 3–4 Succubus, 5–6 Haemonculus); each starts with three territories, the first in its home district "
                  "(Noble Spire / Arena / Flesh Market), and a Rival Trait. A Rival Lord's Power is the number of districts it controls. **Rival Traits (D6):** " + " ".join(f"{i + 1}. {t}" for i, t in enumerate(rtraits)) +
                  "\n\n**Rival Activity.** After each battle, if your Ascendant Lord claims 3 or more territories, make one Activity roll (D6) per Rival Lord, +1 if its Power is greater than your lord's, −1 if less: " +
                  " ".join(activity) + "\n\nA Rival Lord with no territories is defeated; if all are defeated, generate D3 new ones after your next battle.")
    rival_children = []
    for i in (1, 2, 3):
        rival_children.append(L.child(b, "Rival Lord", f"Rival Lord {i}", rename=True,
                                      stats={"Lord": L.rank(list(RIVAL_TYPES), order=1), "Rival Trait": L.rank([t.split(":")[0] for t in rtraits], order=2),
                                             "Power": L.num(0, mn=0, mx=12, order=3), "Territories": L.num(3, mn=0, mx=72, order=4)},
                                      text=rival_text if i == 1 else "See Rival Lord 1 for the Rival Traits and the Rival Activity table."))
    # ── the holdings tracker ──
    flag_paths = [["{self}", "traits", "item", f"District§{d}", "stats", "Controlled", "processed", "numeric", "current"] for d in DISTRICTS]
    rules = {"power": L.rule([L.set_(["{self}", "stats", "Power", "value"], ["{this}", "evals", "0", "result", "integer"])], [L.ev(flag_paths, op="SUM", mn=0)], order=1,
                             note="Power = districts controlled")}
    for k, thr in enumerate((1, 3, 5, 7, 9, 11)):
        rules[f"crusadePts{k + 1}"] = L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], k + 1)], [L.ev(["{self}", "stats", "Power", "processed", "numeric", "current"], mn=thr)], order=2 + k,
                                             note="+1 Crusade point per two districts controlled (rounding up)")
    text = ("**Ascendant Lords.** Tick Ascendant Lord on one DRUKHARI CHARACTER (not an EPIC HERO); it must be your WARLORD whenever it is in your Crusade army. "
            "After each battle roll one D6 (+1 if the lord was in your army, +2 if you were the victor): on 4+ claim one territory, on 6+ claim two. To claim, roll a D6 (1–3 table A, 4–6 table B) then a D66 on each district's list; "
            "an unclaimed territory is yours, one held by a Rival Lord triggers a **Hostile Takeover** (each lord rolls a D6, +1 for the higher Power; highest wins; a tie: 1–3 it stays, 4–6 it becomes unclaimed). "
            "You control a district while you hold more of its territories than every Rival Lord; Power = districts controlled; your Crusade army's Crusade points rise by 1 per two districts (rounding up).\n\n"
            "**Price of Success.** If your Ascendant Lord ever controls all 12 districts, roll a D6: " + " ".join(price) + "\n\n**Death of a Lord.** " + death)
    L.tracker(b, "Commorragh Holdings", "Commorragh Holdings",
              stats={"Power": L.num(0, mn=0, mx=12, dynamic=False, order=1, label="Power (districts controlled)"),
                     "Crusade Pts": {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}},
              children=children + rival_children, text=text, class_rules_=rules)
    # ── the nine missing Battle Traits (unit-specific ones need Battle-hardened or better) ──
    have = {L.norm(k.split("§", 1)[1]) for k in L.keys_with_prefix(b, "Battle Trait§")}
    group, added = None, []
    for e in sec.named("Battle Traits"):
        if e["name"] in GROUP_TAGS or e["name"].endswith(" Units"):
            group = GROUP_TAGS.get(e["name"], [FACTION])
            continue
        if not e["text"] or L.norm(e["name"]) in have:
            continue
        a = {"keywords": {"Tags": TRAIT_TAGS.get(e["name"], group or [FACTION])}, "text": e["text"]}
        if e["name"] in TRAIT_TAGS:
            a["rules"] = {"Battle-hardened rank or better.": L.error_rule([L.ev(["{parent}", "stats", "Experience", "value"], mn=16)])}
        L.put_asset(b, f"Battle Trait§{e['name']}", a)
        added.append(e["name"])
    for tag in ("Kabalite Warriors", "Hand of the Archon", "Wyches", "Wracks", "Haemonculus Covens", "Kabal", "Wych Cult"):
        L.tag_grant(b, "Unit", tag)
        L.tag_grant(b, "Character", tag)
    cz.note(f"Ascendant Lord flag; Commorragh Holdings tracker with {len(children)} districts ({sum(len(v) for v in terr.values())} territories) and 3 Rival Lords; Battle Traits added: {added}")
