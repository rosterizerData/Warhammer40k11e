"""Leagues of Votann Crusade (10e codex, as carried on the 11e site): Kindred Acquisitions and Expeditions.
Source: Wahapedia crus11_leagues-of-votann. No spend validation: resources are dice-rolled gains."""
SLUG, ED, FACTION = "leagues-of-votann", "11", "Leagues of Votann"
LISTS = dict(agendas=True, requisitions=True, badges=True)

RES = ["Raw Minerals", "Biomatter", "Energy Sources", "Galactic Intel"]
ASSETS = [("Mining Outpost", "Raw Minerals ×30, Energy Sources ×30, Galactic Intel ×50", "Each time you gain any amount of raw minerals, add 20 to the amount you gain for each mining outpost you have.",
           "Energy Sources ×50", "Each time you gain any amount of raw minerals, add an additional 10 (for a total of +30 from this mining outpost). You can have up to three mining outposts."),
          ("Trading Hub", "Raw Minerals ×30, Biomatter ×30, Energy Sources ×50", "After each battle, you can use the Guild Patronage Requisition once.",
           "Energy Sources ×100, Rare Raw Minerals ×1", "After each battle, you can use the Guild Patronage Requisition twice."),
          ("Fane Augmentation", "Raw Minerals ×50, Biomatter ×50, Energy Sources ×50, Galactic Intel ×50", "Each time a LEAGUES OF VOTANN unit from your Crusade army is Marked for Greatness, that unit gains an additional 1XP.",
           "Galactic Intel ×100, Rare Energy Sources ×1", "After each battle, select one additional LEAGUES OF VOTANN unit from your Crusade army to be Marked for Greatness."),
          ("Scout Vessel", "Raw Minerals ×100, Biomatter ×50, Energy Sources ×50", "Each time you roll to randomly determine a type of resource, you can re-roll the dice.",
           "Raw Minerals ×100, Rare Biomatter ×1", "After each battle, if your Crusade force is on an expedition, you can remove 1 rare resource from your tracker to increase the maximum length of the expedition by 1 battle."),
          ("Implant Refinery", "Biomatter ×100, Energy Sources ×100", "After each battle, you can re-roll failed Out of Action tests for LEAGUES OF VOTANN units (excluding VEHICLES) from your Crusade army.",
           "Biomatter ×50, Rare Energy Sources ×1", "Each time you roll a D6 to see if your Crusade force has gained a rare resource, you can re-roll the dice."),
          ("Pioneer Fleet", "Raw Minerals ×50, Biomatter ×50, Galactic Intel ×50", "After each battle, randomly determine one fundamental resource. For each Yield point you had at the end of the battle, gain 10 of that resource.",
           "Raw Minerals ×50, Galactic Intel ×50, Rare Biomatter ×1", "At the start of the first battle round, you can spend 20 of any fundamental resource to gain 2 Yield points (these do not count towards your total Yield points)."),
          ("Evaluation Vault", "Raw Minerals ×50, Biomatter ×50, Galactic Intel ×100", "Before each battle, you can use the Field Testing Requisition once for 1RP instead of 2RP.",
           "Raw Minerals ×100, Rare Galactic Intel ×1", "Before each battle, you can use the Field Testing Requisition twice for 1RP instead of 2RP."),
          ("Biorecyc Fabricator", "Raw Minerals ×50, Biomatter ×100, Energy Sources ×50", "After each battle, when you determine which fundamental resource you gain, if it is not biomatter, gain 20 biomatter.",
           "Biomatter ×100, Rare Raw Minerals ×1", "At the end of each battle, each LEAGUES OF VOTANN unit from your Crusade army that is on the battlefield (excluding VEHICLES) gains 1XP.")]
BACKING = {"Lean Operation (no cost, up to 5 battles)": {}, "Balanced Stake (30 resources, up to 6 battles)": {}, "High Investment (60 resources, up to 7 battles)": {}}
GOALS = ["Farstryd Exploration", "Resource Reallocation", "Monopolise Site"]
CONTRACTS = ["Mining: Extraction — Minerals", "Mining: Extraction — Energy", "Science: Research — Biology", "Science: Research — Emergent Field", "Mapping: Exploration — Intelligence", "Mapping: Exploration — New Horizons"]


def build(cz):
    L, b = cz.L, cz.book
    children = []
    for name, cost, effect, ucost, ueffect in ASSETS:
        stats = {"Upgraded": L.flag(order=2), "Inactive": L.flag(order=3, label="Inactive (Cost of Failure)")}
        if name == "Mining Outpost":
            stats["Outposts"] = L.num(0, mn=0, mx=3, order=1, label="Mining outposts owned")
        else:
            stats["Owned"] = L.flag(order=1)
        children.append(L.child(b, "Kindred Asset", name, stats=stats,
                                text=f"**Cost:** {cost}. **Crusade effect:** {effect}\n\n**Upgrade cost:** {ucost}. **Upgraded effect:** {ueffect}\n\nAn inactive asset's effects do not apply; reactivate it for half its original cost."))
    exp_stats = {"Backing": L.rank(list(BACKING), order=1), "Goal": L.rank(GOALS, order=2), "Guild Contract": L.rank(CONTRACTS, order=3), "Battles": L.num(0, mn=0, mx=7, order=4, label="Battles this expedition")}
    for i, r in enumerate(RES):
        exp_stats[f"Expedition {r}"] = L.num(0, mn=0, mx=999, step=10, group="Expedition totals", group_order=2, order=10 + i)
    exp_text = ("**Goals.** Farstryd Exploration: units gained 2XP or more from the Prospecting Agenda in three or more battles — one CHARACTER gains 3XP and you add a mining outpost (max 3). "
                "Resource Reallocation: you used the Red-handed Harvest Requisition three or more times — one CHARACTER gains 3XP and you double one fundamental resource. "
                "Monopolise Site: you won three or more battles — one CHARACTER gains 3XP and you upgrade one kindred asset for free.\n\n"
                "**Guild Contracts** (reward / penalty until your next completed expedition). Mining — Extraction Minerals: expedition total of 60+ raw minerals → 1 rare raw mineral; Extraction Energy: 60+ energy sources → 1 rare energy source; failing a Mining contract bars the Guild Patronage Requisition. "
                "Science — Research Biology: 60+ biomatter → 1 rare biomatter; Research Emergent Field: 1+ rare resource → 50 of one fundamental resource; failing a Science contract bars buying, upgrading or reactivating kindred assets. "
                "Mapping — Exploration Intelligence: 60+ galactic intel → 1 rare galactic intel; Exploration New Horizons: units gained 30XP+ during the expedition → 25 each of two fundamental resources; failing a Mapping contract gives −1 to your resource type and amount rolls (minimum 1).\n\n"
                "The expedition ends when you choose after a battle or when its battles reach the backing's maximum: take the goal reward if met, then the contract's reward or penalty.")
    children.append(L.child(b, "Expedition", "Expedition", stats=exp_stats, text=exp_text))
    stats = {}
    for i, r in enumerate(RES):
        stats[r] = L.num(0, mn=0, mx=999, step=10, group="Fundamental resources", group_order=1, order=i + 1)
    for i, r in enumerate(RES):
        stats[f"Rare {r}"] = L.num(0, mn=0, mx=9, group="Rare resources", group_order=2, order=10 + i)
    text = ("**Kindred Acquisitions.** After each battle in which your WARLORD was a LEAGUES OF VOTANN CHARACTER, roll for a fundamental resource (D6: 1 Raw Minerals, 2 Biomatter, 3 Energy Sources, 4 Galactic Intel, 5–6 your choice) and its amount by battle size "
            "(Combat Patrol D6×5, Incursion D6×10, Strike Force 2D6×10, Onslaught 3D6×10). After a win, roll one D6: on a 6 you also gain one rare resource (roll its type); a rare resource can be converted into 50 regular units of its type at any time. "
            "After gaining resources you can buy one kindred asset or upgrade one you own (each asset once, at most one of each except up to three mining outposts). "
            "**Cost of Failure:** after a lost battle with four or more kindred assets, roll one D6: on a 1 a random asset becomes inactive until you pay half its original cost.")
    L.tracker(b, "Acquisitions", "Acquisitions", stats=stats, children=children, text=text)
    cz.note(f"Acquisitions tracker: 8 resource counters, {len(ASSETS)} Kindred Asset children, Expedition child")
