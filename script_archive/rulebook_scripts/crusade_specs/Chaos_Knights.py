"""Chaos Knights Crusade (10e codex): Amassing Power (three Power Bases with five standing levels), Idolators' Offerings,
Hunting Packs, Pacts of Damnation. Source: Wahapedia crus10_chaos-knights (the 11e page carries the same text)."""
SLUG, ED, FACTION = "chaos-knights", "10", "Chaos Knights"
LISTS = dict(agendas=True, requisitions=True, badges=True)

LEVELS = ["Hostile", "Distrustful", "Wary", "Cautious Alliance", "Aligned Interests"]
BASES = [("Dark Gods", "ckDarkGods"), ("Idolator Influence", "ckIdolator"), ("War Dog Domination", "ckWarDog")]
ALLEGIANCE = {"Iconoclast House": (1, 3, 2), "Infernal House": (3, 1, 3), "Dreadblades": (2, 2, 1)}
LOCATIONS = ["Legs", "Arms", "Torso", "Head"]
TIER4 = {"Spite Capacitors", "Predatory Machine Spirit", "Shrieking Armour", "Malevolus Lockout"}
TIER5 = {"Raking Talons", "Auto-Fury Cacodaemons", "Damned Construction", "Tyrantus Array"}
MINOR = ["Throne Insidious", "Wrathful Aura", "Beguiler's Maw"]
MAJOR = ["Ensorcelled Shield", "Warp Walker", "Brazen Heart"]


def build(cz):
    L, b = cz.L, cz.book
    sec = cz.sec
    # ── tracker: Allegiance + three Power Bases, each standing level tracked for the gates ──
    stats = {"Allegiance": L.rank(list(ALLEGIANCE), order=1)}
    for i, (base, key) in enumerate(BASES):
        stats[base] = L.rank({lvl: {} for lvl in LEVELS}, value="Hostile", dash=False, tracking={lvl: {key: n + 1} for n, lvl in enumerate(LEVELS)}, order=i + 2)
    starts = "; ".join(f"{a}: Dark Gods {LEVELS[d - 1]}, Idolator Influence {LEVELS[ii - 1]}, War Dog Domination {LEVELS[w - 1]}" for a, (d, ii, w) in ALLEGIANCE.items())
    text = ("**Amassing Power.** Pick your Allegiance; it sets the starting standing of your three Power Bases (" + starts + "). "
            "Standing runs Hostile → Distrustful → Wary → Cautious Alliance → Aligned Interests and never leaves that range. Each time you win a battle, raise one Power Base by 1 and roll a D6 for each other base: on a 1–2 it drops by 1. "
            "Each draw or loss: roll a D6, on a 1–3 a random base drops by 1. Agendas can raise standings too; Dark Ambition (1RP) drops one base to Hostile and spreads the lost levels over the others.\n\n"
            "**Idolators’ Offerings** (Battle Traits for CHAOS KNIGHTS TITANIC models, one per suit location: Legs, Arms, Torso, Head) need Idolator Influence at Wary or better; the fourth of each location needs Cautious Alliance, "
            "the fifth needs Aligned Interests and only one model in your Order of Battle can have it. Vile Reworking (1RP) swaps one; at Wary or worse roll a D6 afterwards, on a 1 the model gains a Battle Scar.\n\n"
            "**Hunting Packs:** War Dog models take Hunt Tactics (Battle Traits) from War Dog Domination at Wary or better. At the start of the first battle round form your WAR DOG models into Hunting Packs of 2 models "
            "(2–3 at Aligned Interests); each pack picks one Hunt Tactic that its models have while within 12\" of another pack member, and becomes Ascendant once a pack member destroys an enemy unit.\n\n"
            "**Pacts of Damnation:** the Path to Damnation Requisition (1RP, after a win, not at Hostile or Distrustful) lets a TITANIC model attempt a pact; success on a D6 of 6+ at Wary, 4+ at Cautious Alliance, 2+ at Aligned Interests. "
            "A pact is one Dark Boon (Minor from Wary, Major only at Aligned Interests; no two models share a boon) plus a Cursed Price: a randomly generated Chaos Knights Battle Scar that stays until the pact is broken. One pact per model.")
    L.tracker(b, "Amassing Power", "Amassing Power", stats=stats, text=text)
    titanic = [L.ev_kw("Titanic")]
    # ── Idolators' Offerings: twenty, by location, gated by standing ──
    L.honour_class(b, "Idolators’ Offering", unique=False, allow_on=("Unit",), allow_evals=titanic + [L.ev_tracked("ckIdolator", mn=3)],
                   allow_note="Idolators’ Offerings: CHAOS KNIGHTS TITANIC models with Idolator Influence at Wary or better take these instead of other Battle Traits, one per suit location")
    items = []
    for loc in LOCATIONS:
        for e in sec.named(loc):
            rules = {}
            if e["name"] in TIER4:
                rules["Needs Idolator Influence at Cautious Alliance or better."] = L.error_rule([L.ev_tracked("ckIdolator", mn=4)])
            if e["name"] in TIER5:
                rules["Needs Idolator Influence at Aligned Interests."] = L.error_rule([L.ev_tracked("ckIdolator", mn=5)])
            items.append({"name": e["name"], "tags": [FACTION], "keywords": [loc, "Idolators’ Offering"], "text": f"*{loc}.* " + e["text"], "rules": rules})
    L.honours(b, "Idolators’ Offering", items, keep_text=False)
    L.unique_in_roster(b, sorted(TIER5))   # the fifth Offering of each location: one model in the Order of Battle
    for loc in LOCATIONS:
        L.class_rule(b, "Unit", f"One Idolators’ Offering per suit location ({loc}).", L.error_rule([L.ev(["{self}", "tally", loc], mx=1)]))
    # ── Hunt Tactics for War Dogs ──
    L.honour_class(b, "Hunt Tactic", unique=False, allow_on=("Unit",), allow_evals=[L.ev_kw("War Dog"), L.ev_tracked("ckWarDog", mn=3)],
                   allow_note="Hunt Tactics: WAR DOG models with War Dog Domination at Wary or better take these instead of other Battle Traits")
    tactics = [{"name": e["name"], "tags": [FACTION], "keywords": ["Hunt Tactic"], "text": e["text"]} for e in sec.named("Hunt Tactics")]
    L.honours(b, "Hunt Tactic", tactics, keep_text=False)
    # ── Dark Boons (Pacts of Damnation) ──
    L.reclass(b, "Crusade Honour§", "Dark Boon", MINOR + MAJOR)
    L.honour_class(b, "Dark Boon", unique=True, allow_on=("Unit",), allow_evals=titanic + [L.ev_tracked("ckDarkGods", mn=3)],
                   allow_note="Dark Boons: the benefit of a Pact of Damnation (Path to Damnation Requisition); Minor boons from Dark Gods at Wary, Major only at Aligned Interests; the Cursed Price is a Chaos Knights Battle Scar",
                   cap=1, cap_text="A model can have only one Pact of Damnation.")
    for n in MAJOR:
        L.asset_rule(b, f"Dark Boon§{n}", "Major Dark Boon: needs Dark Gods at Aligned Interests.", L.error_rule([L.ev_tracked("ckDarkGods", mn=5)]))
    for n in MINOR + MAJOR:
        L.patch_asset(b, f"Dark Boon§{n}", {"keywords": {"Keywords": ["Major Dark Boon" if n in MAJOR else "Minor Dark Boon"]}})
    L.unique_in_roster(b, MINOR + MAJOR)   # no two models share a Dark Boon
    cz.note(f"Amassing Power tracker (allegiance + 3 standings); Offerings {len(items)}; Hunt Tactics {len(tactics)}; Dark Boons reclassed (3 minor, 3 major)")
