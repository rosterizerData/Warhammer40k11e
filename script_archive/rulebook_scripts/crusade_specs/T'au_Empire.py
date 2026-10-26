"""T'au Empire Crusade (10e codex, as carried on the 11e site): Expanding the Empire (star systems, planets, Diplomat and
Military points), Kroot Strains. Source: Wahapedia crus11_t-au-empire. The existing bloc was fan-built: this spec also
repairs it (Battle Trait tags per unit table, the Seismic Destabiliser relic, an ungated trait allowance, an agenda typo)."""
SLUG, ED, FACTION = "t-au-empire", "11", "T’au Empire"
LISTS = dict(agendas=True, requisitions=True, badges=True)

STRAINS = ["Blade-sharp Senses", "Great Endurance", "Predatory Swiftness", "Leathery Resilience", "Lethal Instincts", "Corded Muscle"]
TRAIT_GROUPS = {"Battlesuit Units": ["Battlesuit"], "Ethereal Models": ["Ethereal"], "Pathfinders, Strike Team and Breacher Team Units": ["Pathfinder Team", "Strike Team", "Breacher Team"], "Kroot Units": ["Kroot"]}
TEMPERAMENTS = ["Warlike", "Prideful", "Ideologues", "Trade Contacts", "Corrupt and Decadent", "Dictatorship"]
PLANETS = {
    "Shrine World": (5, 2, "Assimilation: Shaken Faith — select up to three planets; −1 Diplomat Power each (min 1). Stir the Flames — +1 Military Power to all planets. Supply Line: Collapse of Faith — while assimilating your next star system, each diplomatic takeover gains you 1RP."),
    "Civilian World": (3, 2, "Assimilation: Threat of Invasion — +1 Military Power to other Civilian Worlds. Recruitment Down — −1 Military Power to Fleet Installations and Military Bases (min 1). Supply Line: A Mingling of Cultures — up to three Battle-ready or Blooded units gain 5XP each."),
    "Mining World": (3, 4, "Assimilation: Harvest Resources — gain D3RP. Starve the War Machines — select up to two planets; −1 Military Power each (min 1). Supply Line: Spoils of War — gain D3+1RP."),
    "Military Base": (4, 6, "Assimilation: Force to the Table — −1 Diplomat Power to each other planet (min 1). Military Supplies — use Fresh Recruits once for free. Supply Line: Repurposed Infrastructure — Supply Limit +400 points."),
    "Fleet Installation": (4, 6, "Assimilation: Invasion Plans — halve one planet's Military Power (rounding up). Orbital Dominance — use Rearm and Resupply once for free. Supply Line: Fleet Intel — −1 Military Power to all planets of your next star system (min 1)."),
    "Agri World": (2, 2, "Assimilation: Empty Bellies — −1 Diplomat Power to up to one Civilian World and one Military Base or Fleet Installation (min 1). Full Stomachs — Repair and Recuperate once for up to 2RP less. Supply Line: Rest and Recuperation — remove one Battle Scar from each of up to two units."),
    "Political Centre": (6, 3, "Assimilation: Sell-outs — halve one planet's Diplomat Power (rounding up). Belief in the Cause — use Renowned Heroes once for free. Supply Line: Diplomatic Contacts — −1 Diplomat Power to all planets of your next star system (min 1)."),
    "Traders’ Hub": (4, 4, "Assimilation: Indirect Influence — swap one planet's Diplomat and Military Power. Supply Line: Trade Networks — after generating your next star system, gain 2D3 Diplomat points and D3 Military points."),
    "Research World": (4, 3, "Assimilation: Review Research — gain 2D3RP. Supply Line: Scientific Integration — use Renowned Heroes and Prototype System once each for free.")}


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    cat, tax = L.catalog(b), L.taxonomy(b)
    notes = []
    # ── repairs to the fan-built bloc ──
    grp, retagged = None, 0
    for e in sec.named("Battle Traits"):
        if e["name"] in TRAIT_GROUPS or e["name"].endswith((" Units", " Models")):
            grp = TRAIT_GROUPS.get(e["name"])
            continue
        if not grp:
            continue
        key = L.existing_key(b, f"Battle Trait§{e['name']}")
        if key in cat:
            cat[key]["keywords"] = {"Tags": list(grp)}
            retagged += 1
    for tag in ("Battlesuit", "Ethereal", "Pathfinder Team", "Strike Team", "Breacher Team", "Kroot"):
        for cls in ("Unit", "Character"):
            L.tag_grant(b, cls, tag)
    notes.append(f"{retagged} Battle Traits re-tagged to their unit tables")
    sd = cat.get("Crusade Relic§Seismic Destabiliser")
    if sd is not None:
        sd.pop("rules", None)
        sd["keywords"] = {"Tags": ["Artificer Relic"]}
        notes.append("Seismic Destabiliser: Artificer tier tag instead of a notAllowed rule")
    if "allowTauTraits" in (tax.get("Unit", {}).get("rules") or {}):
        del tax["Unit"]["rules"]["allowTauTraits"]
        notes.append("removed the ungated allowTauTraits (the core allowance already gates Battle Traits on Narrative play)")
    for stat in ("Agenda 1", "Agenda 2"):
        ranks = tax.get("Mission Record", {}).get("stats", {}).get(stat, {}).get("ranks", {})
        if "Outflank and Encricle" in ranks:
            del ranks["Outflank and Encricle"]
            notes.append(f"{stat}: dropped the misspelt agenda rank")
    # ── Kroot Strains: their own class on KROOT units ──
    L.reclass(b, "Crusade Honour§", "Kroot Strain", STRAINS)
    for n in STRAINS:
        k = f"Kroot Strain§{n}"
        if k in cat:
            cat[k]["keywords"] = {"Tags": ["Kroot"]}
    L.honour_class(b, "Kroot Strain", unique=False, allow_on=("Unit", "Character"), allow_evals=[L.ev_kw("Kroot")],
                   allow_note="Strains: a KROOT unit may take a Strain instead of another Battle Trait")
    # ── planets: an addable class under the tracker ──
    for t, (dp, mp, txt) in PLANETS.items():
        L.ability(b, f"Planet: {t}", f"Diplomat Power {dp}, Military Power {mp}. {txt}")
    pstats = {"Type": L.rank(list(PLANETS), order=1), "Diplomat Power": L.num(0, mn=0, mx=12, order=2), "Military Power": L.num(0, mn=0, mx=12, order=3),
              "Core World": L.flag(order=4), "Taken": L.rank(["Diplomatic takeover", "Military takeover"], order=5), "Razed": L.flag(order=6, label="Razed (no Supply Line)")}
    prules = {f"type{i}": L.rule([L.add(["{self}", "traits"], f"Ability§Planet: {t}")], [L.ev_stat("Type", t)]) for i, t in enumerate(PLANETS)}
    L.ensure_class(b, "Planet", {"aspects": {"Rename": True, "Visibility": "always"}, "stats": pstats, "rules": prules, "templateClass": ""}, replace=True)
    L.put_asset(b, "Planet§Planet", {"text": "Set the Type (D6 1–4: Common table — Mining, Civilian, Military Base, Agri, Traders’ Hub, Shrine; 5–6: High-value table — Research World, Fleet Installation, Political Centre), then copy the Type's Diplomat and Military Power and apply the system's temperament. The first planet generated is the Core World and cannot be taken until all others are. Each time you win a battle you may take over one planet: diplomatic takeover spends Diplomat points equal to its Diplomat Power, military takeover spends Military points equal to its Military Power (then roll a D6: on 1–3 the planet is razed and cannot supply a Supply Line). Apply the planet's Assimilation Abilities when it is taken."})
    text = ("**Expanding the Empire.** Your Crusade force assimilates one star system at a time. Generate it in three steps: the inhabitants' temperament (D6: 1 Warlike +1 Military Power to all planets; 2 Prideful — no Show of Force Requisition; 3 Ideologues +1 Diplomat Power to all planets; "
            "4 Trade Contacts — halve one planet's Diplomat Power; 5 Corrupt and Decadent +2 Diplomat Power to the Core World; 6 Dictatorship +2 Military Power to the Core World), the number of planets (4, 6 or 8) and each planet's Type (add Planets below). "
            "Diplomat and Military points reset to 0 with each new system; each battle won gives 1 Military point, Agendas give both. "
            "After the Core World falls, buy Set Up Supply Lines (1RP for the Core World, 2RP otherwise) to take one planet's Supply Line Effect, then generate a new system.")
    L.tracker(b, "Star System", "Star System", stats={"Temperament": L.rank(TEMPERAMENTS, order=1, label="Inhabitants’ Temperament"), "Planets": L.rank(["4", "6", "8"], order=2, label="Planets in the system"),
                                                     "Diplomat Points": L.num(0, mn=0, mx=99, order=3), "Military Points": L.num(0, mn=0, mx=99, order=4)},
              text=text, allowed_classes=["Planet"])
    tax["Star System"]["aspects"]["Group Includes"] = True
    # ── Set Up Supply Lines (the section prints it inside the rules, not under Requisitions) ──
    L.requisitions(b, [{"name": "Set Up Supply Lines", "rp": 1, "text": "Cost: 1RP for a Core World, 2RP for any other planet. Purchase this Requisition after your Crusade force takes over the Core World in your active star system. Select one of the planets in your active star system to incorporate into your supply lines; the Supply Line Effect of that planet takes effect. After purchasing this Requisition, generate a new active star system for your Crusade force."}])
    cz.note("; ".join(notes) + "; Kroot Strain class; Star System tracker with addable Planet class (9 types as abilities); Set Up Supply Lines requisition")
