"""Astra Militarum Crusade (10e codex, as carried on the 11e site): Tours of Duty, Logistics, Commendations.
Source: Wahapedia crus11_astra-militarum. Personal Commendations were imported from BSData as Crusade Honour§ (tags kept)."""
import re
SLUG, ED, FACTION = "astra-militarum", "11", "Astra Militarum"
LISTS = dict(agendas=True, requisitions=True, badges=True)

LOGISTICS = {
    "Lexmechanicus": ("When selecting Agendas for a battle, you can select one additional Astra Militarum Agenda to be active for that battle in addition to any others selected for that battle.",
                      "Each time an OFFICER from your army issues an Order, roll one D6: on a 1, that Order is not issued."),
    "Materiel": ("Each time an ASTRA MILITARUM unit from your army is selected to shoot, you can re-roll one Hit roll when resolving that unit’s attacks.",
                 "Subtract 2\" from the Move characteristic of ASTRA MILITARUM VEHICLE models from your Crusade force."),
    "Tithe Pool": ("In your Command phase, 1 destroyed model (excluding CHARACTERS) is returned to each REGIMENT INFANTRY unit from your army that is on the battlefield and not at its Starting Strength.",
                   "In your Command phase, if your WARLORD is not on the battlefield, you do not gain a Command point."),
    "Morale": ("Improve the Leadership characteristic of ASTRA MILITARUM models in your Crusade force by 1.",
               "You cannot use the Insane Bravery Stratagem."),
}
TEXT = ("**Tours of Duty.** Each time your Crusade force starts a Tour of Duty, roll for its length: D6+4 battles to fight and D3+2 victories required (note both here). After each battle reduce the battles remaining by 1, and the victories remaining by 1 if you won. "
        "When both reach 0 the Tour is complete: spend Commendation points on Commendations, then start a new Tour (any unspent Commendation points are lost).\n\n"
        "**Logistics points.** At the start of each Tour assign 4 Logistics points across Lexmechanicus, Materiel, Tithe Pool and Morale, no more than 2 in any one category. "
        "A category with 0 Logistics points is in **deficiency**, 1 point has no effect and 2 points is a **surplus**; the surplus and deficiency effects attach below as abilities while they apply.\n\n"
        "**Commendation points.** Your Crusade force earns 1 Commendation point after each battle (D3 if you won); Agendas can earn more. At the end of a Tour spend them on Personal Commendations (Battle Honours for individual ASTRA MILITARUM units: an OFFICER may hold two, other units one, "
        "never the same one twice on a unit, never on EPIC HEROES) and Regimental Commendations (at most two on your Order of Battle, each adding 3 to the Crusade points of every army you muster). You can remove Commendations at any time to buy different ones.")


def costed(sec, title):
    """entries of the form NAME / cost digit / flavour / rules…; returns {name: (cost, text)}"""
    lines = [l for l in sec.block(title) if l.strip()]
    out, i = {}, 0
    while i < len(lines):
        nm = sec.is_name(lines[i])
        if nm and i + 1 < len(lines) and re.fullmatch(r"\d", lines[i + 1].strip()):
            j, body = i + 2, []
            while j < len(lines) and not (sec.is_name(lines[j]) and j + 1 < len(lines) and re.fullmatch(r"\d", lines[j + 1].strip())):
                body.append(lines[j].strip())
                j += 1
            from crusade_waha import is_rules, title_case
            if body and not is_rules(body[0]):
                body = body[1:]
            out[title_case(nm[0])] = (int(lines[i + 1]), "\n\n".join(body))
            i = j
        else:
            i += 1
    return out


def build(cz):
    L, b = cz.L, cz.book
    sec = cz.sec
    # ── Personal Commendations: own class, costs from the text, caps ──
    pcs = costed(sec, "Personal Commendations")
    L.reclass(b, "Crusade Honour§", "Personal Commendation")
    cat = L.catalog(b)
    for k in [k for k in cat if k.startswith("Personal Commendation§")]:
        name = k.split("§", 1)[1]
        cost = next((c for n, (c, _) in pcs.items() if L.norm(n) == L.norm(name)), None)
        if cost is None:
            cz.note(f"no cost found for {name}")
            cost = 1
        cat[k].setdefault("stats", {})["Commendation Pts"] = {"value": cost}
        cat[k].setdefault("keywords", {})["Keywords"] = ["Personal Commendation"]
    L.honour_class(b, "Personal Commendation", unique=False, allow_on=("Unit", "Character"), allow_evals=[L.ev_kw("Epic Hero", not_=True)],
                   stats={"Commendation Pts": {"statType": "numeric", "tracked": True, "value": 1, "visibility": "always", "group": "Cost", "groupOrder": -1}},
                   allow_note="Personal Commendations: bought with Commendation points at the end of a Tour of Duty; an OFFICER may hold two, other units one; not EPIC HEROES")
    not_narr = L.ev(["{roster}", "stats", "Play", "value"], "Narrative", not_=True)
    for ucls in ("Unit", "Character"):
        L.class_rule(b, ucls, "Personal Commendations: one per unit (two for an OFFICER).",
                     L.rule(None, [not_narr, L.ev(["{self}", "tally", "Personal Commendation"], mx=1), L.ev_kw("Officer")], fail="error", evaluate="OR"))
        L.class_rule(b, ucls, "No unit can have more than two Personal Commendations.",
                     L.rule(None, [not_narr, L.ev(["{self}", "tally", "Personal Commendation"], mx=2)], fail="error", evaluate="OR"))
        (L.taxonomy(b).get(ucls, {}).get("rules") or {}).pop("A unit cannot have the same Personal Commendation twice.", None)
    # ── Regimental Commendations as children of the tracker ──
    rcs = costed(sec, "Regimental Commendations")
    reg_rules, reg_stats = {}, {}
    for i, (name, (cost, text)) in enumerate(rcs.items()):
        L.ability(b, name, text)
        reg_stats[name] = L.flag(tracking={"Regimental Commendation": 1}, order=i + 1)
        reg_rules[f"regimental{i}"] = L.rule([L.add(["{self}", "traits"], f"Ability§{name}")], [L.ev_stat(name, "✓")])
    reg_stats["Commendation Pts"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}
    reg_stats["Crusade Pts"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}
    reg_rules["regimentalCosts"] = L.rule([L.set_(["{self}", "stats", "Commendation Pts", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                          [L.ev([["{self}", "stats", n, "processed", "numeric", "current"] for n in rcs], op="SUM", mn=0, equation={"operator": "T*O", "value": 8})], order=1,
                                          note="each Regimental Commendation costs 8 Commendation points")
    reg_rules["regimentalCrusadePts"] = L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                               [L.ev([["{self}", "stats", n, "processed", "numeric", "current"] for n in rcs], op="SUM", mn=0, equation={"operator": "T*O", "value": 3})], order=1,
                                               note="each Regimental Commendation adds 3 Crusade points to the mustered army")
    reg_rules["No more than two Regimental Commendations."] = L.rule(None, [L.count_flags(list(rcs))], fail="error", order=5)
    reg_rules["No more than two Regimental Commendations."]["evals"][0]["max"] = 2
    regimental = L.child(b, "Regimental Commendations", "Regimental Commendations", stats=reg_stats, rules=reg_rules,
                         text="Tick the Regimental Commendations your Order of Battle holds (at most two, 8 Commendation points each). Each adds 3 Crusade points to every army you muster and its abilities apply to all ASTRA MILITARUM units in your Crusade force.")
    # ── Tour of Duty tracker ──
    stats = {"Battles remaining": L.num(0, mn=0, mx=10, order=1), "Victories remaining": L.num(0, mn=0, mx=5, order=2),
             "Commendation Points": L.num(0, mn=0, mx=99, order=3, label="Commendation points earned", icons=["medal"]),
             "Commendation Pts spent": L.num(0, mn=0, mx=999, dynamic=False, order=4, label="Commendation points spent")}
    for i, cat_ in enumerate(LOGISTICS):
        stats[cat_] = L.num(1, mn=0, mx=2, group="Logistics (4 points, max 2 each)", group_order=2, order=10 + i)
    rules = {"Logistics: no more than 4 Logistics points in total.": L.rule(None, [L.ev([["{self}", "stats", c, "value"] for c in LOGISTICS], op="SUM", mx=4)], fail="error", order=5)}
    for cat_, (sur, dfc) in LOGISTICS.items():
        L.ability(b, f"Surplus: {cat_}", sur)
        L.ability(b, f"Deficiency: {cat_}", dfc)
        rules[f"surplus{cat_.replace(' ', '')}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Surplus: {cat_}")], [L.ev_stat(cat_, 2)], order=1)
        rules[f"deficiency{cat_.replace(' ', '')}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Deficiency: {cat_}")], [L.ev_stat(cat_, 0)], order=1)
    # spent = sum of Commendation Pts tracked across the roster (units' commendations + regimental child); earned must cover it
    rules["commendationSpent"] = L.rule([L.set_(["{self}", "stats", "Commendation Pts spent", "value"], ["{roster}", "tracked", "Commendation Pts"])], [], order=2)
    rules["Commendation points spent exceed the points earned."] = L.rule(None, [L.ev(["{roster}", "tracked", "Commendation Pts"], mx=["{self}", "stats", "Commendation Points", "value"])], fail="error", order=5)
    L.tracker(b, "Tour of Duty", "Tour of Duty", stats=stats, children=[regimental], text=TEXT, class_rules_=rules)
    cz.note(f"Personal Commendations reclassed with costs ({len(pcs)} costed); Regimental Commendations {len(rcs)}; Tour of Duty tracker with Logistics surplus/deficiency abilities and Commendation ledger")
