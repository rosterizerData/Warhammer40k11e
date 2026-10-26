"""Genestealer Cults Crusade (10e codex, as carried on the 11e site): Path of Ascension. Source: Wahapedia
crus11_genestealer-cults (world institutions decoded from the page icons). The seven Tyranid-named Requisition§ entries
in this book are deliberate overrides tagged noGSCcrusade that hide the inherited Tyranid requisitions: left alone."""
SLUG, ED, FACTION = "genestealer-cults", "11", "Genestealer Cults"
LISTS = dict(agendas=True, requisitions=True, badges=True)

WORLDS = {"Hive World": (["Community", "Industry", "Politics"], "Strength of the Masses: After each Crusade battle, each BATTLELINE unit that was part of your Crusade army and survived the battle gains 1XP."),
          "Forge World": (["Industry", "Military", "Religion"], "Prized Acquisition: Each time you add a VEHICLE unit to your Order of Battle, that unit gains 6XP (and therefore gains the Blooded Rank); select one Battle Honour for it as normal."),
          "Cardinal World": (["Community", "Politics", "Religion"], "Will of the Faithful: After each Crusade battle, you can ignore your first failed Out of Action test."),
          "Fortress World": (["Military", "Religion", "Resources"], "Looted Armoury: When a unit from your Crusade force gains the Weapon Modifications Battle Honour, you can roll 3D6 (instead of 2D6) to randomly determine three Weapon Modifications for the weapon to gain."),
          "Agri/Mining World": (["Community", "Industry", "Resources"], "Hard Graft: After each Crusade battle, roll one D6: on a 4+, you gain 1 additional Requisition point."),
          "Frontier/Feudal World": (["Military", "Politics", "Resources"], "Cult of Personality: Each time you select a unit to be Marked for Greatness, that unit gains 1 additional XP.")}
INSTITUTIONS = {"Industry": "Use the Rearm and Resupply Requisition up to two times without spending any Requisition points.",
                "Military": "One INFANTRY unit (excluding CHARACTER units) with fewer than 6XP gains XP until it has 6XP.",
                "Community": "Use the Fresh Recruits Requisition up to two times without spending any Requisition points.",
                "Politics": "You gain influence. While you have influence, subtract 1 from your next Setback roll, then you no longer have influence.",
                "Religion": "One CHARACTER unit with fewer than 6XP gains XP until it has 6XP.",
                "Resources": "Use the Increase Supply Limit Requisition up to two times without spending any Requisition points."}
REWARDS = [w for w in WORLDS]   # one Ascension reward per world classification


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    cat = L.catalog(b)
    # ── Cult honours: Tactical Strategist (one per force) and Beloved of the Cult (Heroic+, one per force) ──
    L.reclass(b, "Crusade Honour§", "Cult Honour", ["Tactical Strategist", "Beloved of the Cult"])
    for k in ("Cult Honour§Tactical Strategist", "Cult Honour§Beloved of the Cult"):
        if k in cat:
            cat[k]["keywords"] = {"Tags": []}
    if "Cult Honour§Beloved of the Cult" in cat:
        cat["Cult Honour§Beloved of the Cult"].setdefault("stats", {})["Crusade Pts"] = {"value": 1}
        cat["Cult Honour§Beloved of the Cult"]["rules"] = {"Heroic rank or higher.": L.error_rule([L.ev(["{parent}", "stats", "Experience", "value"], mn=31)])}
        cat["Cult Honour§Beloved of the Cult"]["text"] = ("Beloved of the Cult Requisition (1RP): a GENESTEALER CULTS unit with the Heroic rank or higher; only one unit at a time. " + cat["Cult Honour§Beloved of the Cult"]["text"])
    if "Cult Honour§Tactical Strategist" in cat:
        cat["Cult Honour§Tactical Strategist"]["text"] = ("Shrewd Strategy: your Crusade force gains 6 Planning points each battle to buy Shrewd Strategy abilities for GENESTEALER CULTS units (Crossfire 1, Suppressing Crossfire 2, Stealth 2, Booby Traps 2, Ambushing Crossfire 3, Vanishing Act 3; one ability per unit per battle, unspent points are lost). "
                                                         + cat["Cult Honour§Tactical Strategist"]["text"])
    L.honour_class(b, "Cult Honour", unique=True, allow_on=("Unit", "Character"), allow_note="Genestealer Cults Crusade honours: Tactical Strategist (Shrewd Strategy) and Beloved of the Cult")
    # the Unique aspect only stops duplicates under the same parent: roster-wide uniqueness through the lib helper
    rr = (cat.get("Roster§Roster") or {}).get("rules", {})
    for n in ("Tactical Strategist", "Beloved of the Cult"):
        k = f"Cult Honour§{n}"
        if k in cat and k in cat and "stats" in cat[k]:
            cat[k]["stats"].pop(f"count{n.replace(' ', '')}", None)
        rr.pop("Only one unit can be Beloved of the Cult at a time.", None)
        rr.pop("Only one Tactical Strategist per Crusade force.", None)
    L.unique_in_roster(b, ["Tactical Strategist", "Beloved of the Cult"])
    # ── world classification abilities ──
    for w, (insts, reward) in WORLDS.items():
        L.ability(b, f"World: {w}", f"Institutions: {', '.join(insts)}. Ascension reward — {reward}")
    # ── institutions ──
    inst_text = "Controlled Institution benefits: " + " ".join(f"**{n}:** {t}" for n, t in INSTITUTIONS.items())
    children = [L.child(b, "Institution", f"Institution {i}", stats={"Institution": L.rank(list(INSTITUTIONS), order=1), "State": L.rank(["Infiltrated", "Target", "Controlled"], order=2)},
                        text=inst_text if i == 1 else "See Institution 1 for the Controlled Institution benefits.") for i in (1, 2, 3)]
    # ── the path tracker ──
    stats = {"World": L.rank(list(WORLDS), order=1, label="World classification"),
             "Ascension Points": L.num(0, mn=0, mx=3, order=2), "Control": L.num(0, mn=0, mx=4, order=3, label="Control count"), "Propagation": L.num(0, mn=0, mx=5, order=4, label="Propagation count"),
             "Prepared for the Ordeal": L.flag(order=5), "Silenced a Detractor": L.flag(order=6), "Influence": L.flag(order=7), "Great Ordeal": L.flag(order=8, label="Great Ordeal triggered"),
             "Crusade Pts": {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}}
    for i, w in enumerate(REWARDS):
        stats[f"Reward: {w}"] = L.flag(group="Ascension Rewards", group_order=2, order=10 + i)
    rules = {f"world{i}": L.rule([L.add(["{self}", "traits"], f"Ability§World: {w}")], [L.ev_stat("World", w)]) for i, w in enumerate(WORLDS)}
    rules["rewardsCrusadePts"] = L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], ["{this}", "evals", "0", "result", "integer"])], [L.count_flags([f"Reward: {w}" for w in REWARDS])], order=1,
                                        note="each Ascension reward adds 1 Crusade point when determining Crusade Blessings")
    rules["glorious"] = L.rule([L.mod(["{self}", "designation"], " — GLORIOUS ASCENSION", append="")], [L.ev(["{self}", "stats", "Control", "value"], mn=4)], order=1)
    rules["seed"] = L.rule([L.mod(["{self}", "designation"], " — SEED THE STARS", append="")], [L.ev(["{self}", "stats", "Propagation", "value"], mn=5)], order=1)
    text = ("**Path of Ascension.** If your Crusade force includes a PATRIARCH, PRIMUS or MAGUS and is not on a Path, it can begin one: pick or roll the world classification (D6 1–6 in the order listed), choose which of its three institutions your uprising has infiltrated, name the world. "
            "Before each battle, if you do not already control three institutions, select a target institution you do not control.\n\n"
            "**After each battle:** Exploit Advantage (if the target is infiltrated, each surviving unit of your army gains 1XP) → Gain Ascension Points (D6, +1 won, +1 target infiltrated, +1 a unit earned XP from a Genestealer Cults Agenda: 4–7 = 1 point, 8+ = 2) → "
            "Gain Control (at 3 Ascension points spend them: Control +1, the target becomes Controlled; at Control 4 you win a Glorious Ascension; otherwise take the institution's benefit or 1RP) → "
            "Setback (2D6, +1 lost, +1 no Agenda XP, +Control: on 13+ you are set back and must fight the Great Ordeal) → Propagate (optional: D6 + Control, on 5+ Propagation +1 and Control −1; at Propagation 5 you win Seed the Stars).\n\n"
            "**Path's End.** Glorious Ascension: one PATRIARCH gains 2XP and you claim the world's Ascension reward. Seed the Stars: up to three CHARACTERS gain 2XP. The Great Ordeal: a battle with Zealous Fury (+Control to your Battle-shock tests) and Persecuted (your opponent starts with CP by battle size and your Control: "
            "Combat Patrol 1/1/0/0, Incursion 2/1/1/0, Strike Force 3/2/1/1, Onslaught 3/3/2/1 for Control 0/1/2/3; Prepared for the Ordeal gives you 2CP); win it for 2XP on a PATRIARCH and the Ascension reward, lose it and you must abandon the Path. "
            "Abandoning (The Cycle Begins Anew) costs an Ignominy: every PATRIARCH, PRIMUS and MAGUS gains a Battle Scar, or you remove one Ascension reward. Each ending resets Ascension points, Propagation and Control to 0; after a victory your next Path starts with two infiltrated institutions.\n\n"
            "Each Ascension reward claimed adds 1 to your Crusade points when determining Crusade Blessings.")
    L.tracker(b, "Path of Ascension", "Path of Ascension", stats=stats, children=children, text=text, class_rules_=rules)
    cz.note("Cult Honour class (Tactical Strategist, Beloved of the Cult); Path of Ascension tracker with 3 Institution children, 6 world abilities, 6 reward ticks")
