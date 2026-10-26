"""Imperial Agents Crusade (10e codex, as carried on the 11e site): Shadow Operations, Vermilion-level Assets.
Source: Wahapedia crus11_imperial-agents. Vermilion assets were imported from BSData as Crusade Honour§ (tags kept)."""
SLUG, ED, FACTION = "imperial-agents", "11", "Agents of the Imperium"
LISTS = dict(agendas=True, requisitions=True, badges=True)

LEVELS = {"Minoris": "Threat Score 1 · Covert Level 4+ · Time Remaining 3", "Majoris": "Threat Score 2 · Covert Level 5+ · Time Remaining 5", "Extremis": "Threat Score 3 · Covert Level 6+ · Time Remaining 7"}
PLOTS = {"Compromised Agent (Minoris)": "Influence goal 4+ · Intrigue goal 6+", "Enemy Sympathiser (Minoris)": "Influence goal 5+ · Intrigue goal 5+", "Spy Network (Minoris)": "Influence goal 6+ · Intrigue goal 4+",
         "Ancient Artefact (Majoris)": "Influence goal 6+ · Intrigue goal 6+", "Agent Provocateur (Majoris)": "Influence goal 7+ · Intrigue goal 5+", "Saboteur Matrix (Majoris)": "Influence goal 5+ · Intrigue goal 7+",
         "Arch-nemesis (Extremis)": "Influence goal 7+ · Intrigue goal 7+", "Diabolical Ritual (Extremis)": "Influence goal 6+ · Intrigue goal 8+", "Cult Uprising (Extremis)": "Influence goal 8+ · Intrigue goal 6+"}
TEXT = ("**Shadow Operations.** With any AGENTS OF THE IMPERIUM CHARACTERS in your Crusade force you can run a Shadow Operation: name a sub-sector and set three Threats (choose or roll each Level). Sub-sector Control and all tallies start at 0.\n\n"
        "**After each battle** (Update Order of Battle step), if your Crusade army included an AGENTS OF THE IMPERIUM CHARACTER: gain 1 Investigation point and allocate it to an active Threat; then you may try to uncover one Threat — roll a D6 and add its Investigation points; equal to or above its Covert Level uncovers it (roll on the matching plot table and set its Plot). "
        "Allocate any Influence and Intrigue points from Agendas to uncovered Threats, then you may attempt to Thwart one uncovered Threat: D6 + Intrigue points against its Intrigue goal, else D6 + Influence points against its Influence goal. "
        "A Thwarted Threat adds its Threat Score to Sub-sector Control. Then add 1 to the Time tally of every active Threat and roll a Plot Twist; a Threat whose Time tally reaches its Time Remaining is Fulfilled and subtracts its Threat Score from Sub-sector Control.\n\n"
        "**Plot Twist (D6):** 1 Plans Within Plans — a random active Threat's Threat Score +1. 2 Escalating Threat — a random active Threat's Time tally +1. 3 Counter-agents — all uncovered Threats' Intrigue goals +1. 4 Fierce Resistance — all uncovered Threats' Influence goals +1. "
        "5 Delaying Action — one active Threat's Time tally −1. 6 A Promising Lead — one active uncovered Threat's Investigation tally +1.\n\n"
        "**Cease Shadow Operations** when all three Threats are Thwarted or Fulfilled, and apply the Sub-sector Control result: −9 to −7 Total Collapse (each AGENTS OF THE IMPERIUM unit gains a Battle Scar or suffers a Devastating Blow); −6 to −2 Shameful Losses (one CHARACTER gains the Disgraced or Mark of Shame Battle Scar or suffers a Devastating Blow); "
        "−1 to 1 Ongoing Unrest (gain 1RP); 2 to 6 Purgation Complete (gain D3RP and one CHARACTER gains a Vermilion-level Asset); 7 to 9 Masterful Execution (gain D6RP and up to two CHARACTERS each gain a Vermilion-level Asset). Then you may start a new Shadow Operation.")


def build(cz):
    L, b = cz.L, cz.book
    # ── Vermilion-level Assets: own class (tags Radical/Puritan already gate through the book's crusadeTag rules) ──
    L.reclass(b, "Crusade Honour§", "Vermilion-level Asset")
    cat = L.catalog(b)
    for k in [k for k in cat if k.startswith("Vermilion-level Asset§")]:
        cat[k].get("rules", {}).pop("Each Vermilion-level Asset is unique: only one in your Crusade force.", None)
    L.unique_in_roster(b, [k.split("§", 1)[1] for k in cat if k.startswith("Vermilion-level Asset§")])
    L.honour_class(b, "Vermilion-level Asset", unique=True, allow_on=("Character",),
                   allow_note="Vermilion-level Assets: unique Battle Honours awarded by a Shadow Operation's outcome to AGENTS OF THE IMPERIUM CHARACTERS")
    # ── an Inquisitor's alignment grants the PURITAN / RADICAL keyword (Battle Traits and Shadow Operations hand it out) ──
    L.unit_stat(b, "Character", "Alignment", L.rank(["Puritan", "Radical"], group="Crusade", group_order=11, order=20, label="Inquisitorial alignment"),
                show_when=[L.ev_kw("Inquisitor")])
    L.class_rule(b, "Character", "alignmentPuritan", L.rule([L.add(["{self}", "keywords", "Keywords"], "Puritan")], [L.NARR, L.ev_stat("Alignment", "Puritan")], order=1,
                                                         note="PURITAN keyword (gained from Battle Traits such as Intolerant Zeal); the crusadeTag rules then admit PURITAN-only honours"))
    L.class_rule(b, "Character", "alignmentRadical", L.rule([L.add(["{self}", "keywords", "Keywords"], "Radical")], [L.NARR, L.ev_stat("Alignment", "Radical")], order=1,
                                                         note="RADICAL keyword (gained from Battle Traits such as Extreme Methods)"))
    # ── Shadow Operation tracker with three Threat children ──
    for lv, t in LEVELS.items():
        L.ability(b, f"Threat {lv}", t)
    for p, t in PLOTS.items():
        L.ability(b, f"Plot: {p}", t)
    tstats = {"Level": L.rank({lv: {"traits": [{"trait": f"Ability§Threat {lv}"}]} for lv in LEVELS}, order=1),
              "State": L.rank({"Active": {}, "Uncovered": {}, "Thwarted": {"tracking": {"Threat Thwarted": 1}}, "Fulfilled": {"tracking": {"Threat Fulfilled": 1}}}, value="Active", dash=False, order=2),
              "Plot": L.rank({p: {"traits": [{"trait": f"Ability§Plot: {p}"}]} for p in PLOTS}, order=3, label="Plot (once uncovered)"),
              "Investigation": L.num(0, mn=0, mx=9, order=4, label="Investigation points"), "Influence": L.num(0, mn=0, mx=9, order=5, label="Influence points"),
              "Intrigue": L.num(0, mn=0, mx=9, order=6, label="Intrigue points"), "Time": L.num(0, mn=0, mx=9, order=7, label="Time tally")}
    threats = [L.child(b, "Threat", f"Threat {i}", stats=tstats, rename=True, describe=True) for i in (1, 2, 3)]
    stats = {"Sub-sector Control": L.num(0, mn=-9, mx=9, order=1, icons=["aquila"]),
             "Threats resolved": L.num(0, mn=0, mx=3, dynamic=False, order=2, label="Threats thwarted or fulfilled")}
    rules = {"resolved": L.rule([L.set_(["{self}", "stats", "Threats resolved", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                [L.ev([["{self}", "tracked", "Threat Thwarted"], ["{self}", "tracked", "Threat Fulfilled"]], op="SUM", mn=0)], order=1),
             "operationOver": L.rule([L.mod(["{self}", "designation"], " — OPERATION COMPLETE: apply the Sub-sector Control result", append="")],
                                     [L.ev(["{self}", "stats", "Threats resolved", "value"], mn=3)], order=5)}
    L.tracker(b, "Shadow Operation", "Shadow Operation", stats=stats, children=threats, text=TEXT, class_rules_=rules)
    cz.note("Vermilion assets reclassed; Inquisitor Alignment rank grants PURITAN/RADICAL; Shadow Operation tracker with 3 Threat children (level, state, plot, four tallies) and Sub-sector Control")
