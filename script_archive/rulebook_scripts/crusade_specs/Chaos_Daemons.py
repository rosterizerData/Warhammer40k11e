"""Chaos Daemons Crusade — the 9th edition codex content (no 10e or 11e Crusade section exists), kept until an 11e section
is published: The Great Game tracker, Loci of the Gods, Favoured Rewards, Battle Traits, Relics, Agendas, Requisitions.
Source file crus9_chaos-daemons.txt was typed in from the user's paste (2026-10-26). Psychic Fortitudes are left out
(there is no psychic phase any more)."""
SLUG, ED, FACTION = "chaos-daemons", "9", "Legiones Daemonica"
LISTS = dict(agendas=True, requisitions=True, badges=False)
GODS = ["Khorne", "Tzeentch", "Nurgle", "Slaanesh"]
START = {"Khorne": 4, "Tzeentch": 3, "Nurgle": 2, "Slaanesh": 1}
RENAME = {"G’Rmakht the Destroyer": "G’rmakht the Destroyer"}
DOMINION = {1: "**Dominion — first position:** add 1 to the Leadership characteristic of models in LEGIONES DAEMONICA units from your army that share an Allegiance keyword with this Dark God. Once per battle, you can use an Epic Deed Stratagem for 0CP if the unit selected for that Stratagem shares an Allegiance keyword with this Dark God.",
            2: "**Dominion — second position:** add 1 to the Leadership characteristic of models in LEGIONES DAEMONICA ICON units from your army that share an Allegiance keyword with this Dark God. Once per battle, if your WARLORD shares an Allegiance keyword with this Dark God, you can use the Command Re-roll Stratagem for 0CP.",
            3: "**Dominion — third position:** no additional abilities.",
            4: "**Dominion — fourth position:** subtract 1 from the Leadership characteristic of models in LEGIONES DAEMONICA ICON units from your army that share an Allegiance keyword with this Dark God. Each time a model in a LEGIONES DAEMONICA unit from your army that shares an Allegiance keyword with this Dark God makes an attack against an enemy unit that shares an Allegiance keyword with one of the Dark Gods in first, second or third position, you can re-roll the Hit roll."}


def god_tag(e):
    """'KHORNE model only.' / 'SLAANESH PSYKER model only.' → god keyword"""
    for g in GODS:
        if e["text"].upper().startswith(g.upper()):
            return g
    return None


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    cat = L.catalog(b)
    for k in ("Battle Trait§PLACEHOLDER_NAME", "Crusade Relic§PLACEHOLDER_NAME"):
        cat.pop(k, None)
    for g in GODS:   # god tags for Loci / relics / traits
        L.tag_grant(b, "Character", g)
        L.tag_grant(b, "Unit", g)
    # ── The Great Game: four Dark God children with Ascendancy points and a derived Position ──
    for i in range(1, 5):
        L.ability(b, f"Dominion — {['first', 'second', 'third', 'fourth'][i - 1]} position", DOMINION[i])
    god_stats = {"Ascendancy": L.num(1, mn=0, mx=99, order=1, label="Ascendancy points"),
                 "Position": L.num(1, mn=1, mx=4, dynamic=False, order=2, label="Position in the Great Game")}
    pos_rules = {f"dominion{i}": L.rule([L.add(["{self}", "traits"], f"Ability§Dominion — {['first', 'second', 'third', 'fourth'][i - 1]} position")],
                                        [L.ev_stat("Position", i)], order=3) for i in range(1, 5)}
    children = []
    for g in GODS:
        rules = {}
        for o in GODS:
            if o == g:
                continue
            # behind `o` when o − 1 ≥ mine, i.e. o has strictly more Ascendancy points
            rules[f"behind{o}"] = L.rule([L.mod(["{self}", "stats", "Position", "value"], 1)],
                                         [{"actionable": True, "not": False, "operator": "AND", "equation": {"operator": "T-O", "value": 1},
                                           "paths": [["{parent}", "traits", "item", f"Dark God§{o}", "stats", "Ascendancy", "value"]],
                                           "min": ["{self}", "stats", "Ascendancy", "value"]}], order=2)
        children.append(L.child(b, "Dark God", g, stats=None, rules=rules, text=f"{g}'s standing in the Great Game. Starts the first round with {START[g]} Ascendancy points; later rounds start at 4/3/2/1 by the previous round's position."))
    T = L.taxonomy(b)["Dark God"]
    T["stats"] = god_stats
    T.setdefault("rules", {}).update(pos_rules)
    for g in GODS:   # per-god starting values
        cat[f"Dark God§{g}"].setdefault("stats", {})["Ascendancy"] = {"value": START[g]}
    text = "\n\n".join(sec.block("The Great Game"))
    L.tracker(b, "The Great Game", "The Great Game", stats={"Battles this round": L.num(0, mn=0, mx=8, order=1)}, children=children,
              text="Chaos Daemons use the 9th edition codex's Crusade rules until an 11e Crusade section is published.\n\n" + text)
    # ── Loci of the Gods: one per Character of the matching god ──
    loci = [{"name": e["name"], "text": e["text"], "tags": [god_tag(e)]} for e in sec.named("Loci of the Gods")]
    L.honour_class(b, "Locus of the Gods", unique=False, allow_on=("Character",), allow_evals=[L.ev_kw("Legiones Daemonica", field="Faction")],
                   allow_note="Loci of the Gods: GREATER DAEMON and HERALD models may take a Locus instead of another Battle Honour (aura: 6\" on a Greater Daemon, 3\" otherwise)",
                   cap=1, cap_text="Each model can have only one Locus of the Gods.")
    L.honours(b, "Locus of the Gods", loci)
    # ── Favoured Rewards: Greater Daemons only (Monster Characters of the four gods), 1/2/3 Crusade points by tier ──
    tier_pts = {"Lesser": 1, "Greater": 2, "Exalted": 3}
    favs = []
    for e in sec.named("Favoured Rewards"):
        tier = next((t for t in tier_pts if e["text"].startswith(t + " Reward")), "Lesser")
        # the tier stays in the text only: a child's Keywords take part in the parent's constraint check like Tags do
        favs.append({"name": e["name"], "text": e["text"], "stats": {"Crusade Pts": {"value": tier_pts[tier]}}})
    L.honour_class(b, "Favoured Reward", unique=False, allow_on=("Character",),
                   allow_evals=[L.ev_kw("Legiones Daemonica", field="Faction"), L.ev_kw("Monster"), L.ev_kw("Daemon Prince of Chaos", not_=True), L.ev_kw("Daemon Prince of Chaos with Wings", not_=True)],
                   allow_note="Favoured Rewards: a GREATER DAEMON gains one at the end of a round of the Great Game by its god's position (first: Exalted/Greater/Lesser, second: Greater/Lesser, third: Lesser); each reward once per model")
    L.honours(b, "Favoured Reward", favs)
    # ── Battle Traits by unit ──
    traits = []
    for e in sec.named("Battle Traits"):
        unit = e["text"].split(" unit only")[0].strip().title()
        traits.append({"name": e["name"], "text": e["text"], "tags": [unit]})
        L.tag_grant(b, "Unit", unit)
    L.honours(b, "Battle Trait", traits)
    # ── Relics: Antiquity (Heroic+, 2 pts) and Legendary (Legendary rank, 3 pts, +1RP) with god gates ──
    rel = []
    for tier, pts, title in (("Antiquity Relic", 2, "Antiquity Relics"), ("Legendary Relic", 3, "Legendary Relics")):
        for e in sec.named(title):
            g = god_tag(e)
            a = {"name": RENAME.get(e["name"], e["name"]), "text": e["text"], "tags": [tier], "stats": {"Crusade Pts": {"value": pts}}}
            if g:
                a["rules"] = {f"{g.upper()} only.": L.error_rule([L.ev_kw(g, who="{parent}")])}
            rel.append(a)
    L.honours(b, "Crusade Relic", rel)
    cz.note(f"Great Game tracker (4 gods); Loci {len(loci)}; Favoured Rewards {len(favs)}; Battle Traits {len(traits)}; Relics {len(rel)}")
