"""Death Guard Crusade (10e codex, as carried on the 11e site): Boons of Nurgle, A Grand Plague, Alchemical Pathogens.
Source: Wahapedia crus11_death-guard. Boons were imported from BSData as Crusade Honour§ and move to their own class."""
SLUG, ED, FACTION = "death-guard", "11", "Death Guard"
LISTS = dict(agendas=True, requisitions=True, badges=True)

BOONS = ["Febrile Vitality", "Slitherswift Limbs", "Writhing Tentacles", "Grossly Swollen", "Leprous Insensibility", "Veil of Flies",
         "Touch of Rot", "Plaguesight", "Billowing Miasma"]
BLESSINGS = [("Burgeoning Fortitude", "After each Crusade battle, you can ignore your first failed Out of Action test."),
             ("Eye of Nurgle", "After each Crusade battle, roll one D6, adding 1 to the result if you won the battle. On a 6+, select one additional unit to be Marked for Greatness."),
             ("Fecund Fervour", "After each Crusade battle, each BATTLELINE unit that was part of your Crusade army and survived the battle gains 2XP."),
             ("Seeping Poisons", "When a unit from your Crusade force gains the Weapon Modifications Battle Honour, you can choose for that weapon to gain [LETHAL HITS] instead of randomly generating Weapon Modifications for that weapon."),
             ("Endless Harvest", "After each Crusade battle, roll one D6: on a 4+, you gain 1 additional Requisition point."),
             ("Vile Possession", "Each time you add a VEHICLE unit to your Crusade force, add the DAEMON keyword to that unit’s keywords (if it does not already have it) and that unit gains 6XP (immediately gaining the Blooded rank); select one Battle Honour for it as normal.")]


def build(cz):
    L, b = cz.L, cz.book
    # ── Boons of Nurgle: own class, Characters only (not Daemon Princes), max three per model ──
    L.reclass(b, "Crusade Honour§", "Boon of Nurgle", BOONS, patch={"keywords": {"Tags": [], "Keywords": []}})
    L.honour_class(b, "Boon of Nurgle", unique=False, allow_on=("Character",),
                   allow_evals=[L.ev_kw("Daemon Prince", not_=True), L.ev_kw("Daemon Prince with Wings", not_=True)],
                   allow_note="Boons of Nurgle: DEATH GUARD CHARACTER models (not DAEMON PRINCES) may take a Boon of Nurgle instead of another Battle Honour; a duplicate roll means Spawndom",
                   cap=3, cap_text="No model can have more than three Boons of Nurgle.")
    # ── A Grand Plague tracker ──
    G = "Crusade"
    world = {"Fecundity": L.num(1, mn=1, mx=6, group="World", group_order=1, order=1),
             "Population Density": L.num(1, mn=0, mx=6, group="World", group_order=1, order=2),
             "Vulnerability": L.num(1, mn=1, mx=6, group="World", group_order=1, order=3),
             "Suitability Score": L.num(3, mn=3, mx=18, group="World", group_order=1, order=4),
             "Rate of Reproduction": L.num(1, mn=1, mx=6, group="Plague", group_order=2, order=5),
             "Survival Rate": L.num(1, mn=1, mx=6, group="Plague", group_order=2, order=6),
             "Adaptability": L.num(1, mn=1, mx=6, group="Plague", group_order=2, order=7),
             "Reproduction Total": L.num(2, mn=0, mx=12, dynamic=False, group="Plague Totals", group_order=3, order=8),
             "Density Total": L.num(2, mn=0, mx=12, dynamic=False, group="Plague Totals", group_order=3, order=9),
             "Vulnerability Total": L.num(2, mn=0, mx=12, dynamic=False, group="Plague Totals", group_order=3, order=10),
             "Concocting": L.flag(group="Plague Totals", group_order=3, order=0, label="Concocting a Plague")}
    sum_rule = lambda tot, a, c: L.rule([L.set_(["{self}", "stats", tot, "value"], ["{this}", "evals", "0", "result", "integer"])],
                                        [L.ev([["{self}", "stats", a, "value"], ["{self}", "stats", c, "value"]], op="SUM", mn=0)],
                                        order=1, note="Plague Total = world characteristic + plague characteristic")
    rules = {"sumReproduction": sum_rule("Reproduction Total", "Fecundity", "Rate of Reproduction"),
             "sumDensity": sum_rule("Density Total", "Population Density", "Survival Rate"),
             "sumVulnerability": sum_rule("Vulnerability Total", "Vulnerability", "Adaptability"),
             "Plague concocted! All three Plague Totals equal 7 — claim the reward for your Suitability Score.":
                 L.rule(None, [L.ev_stat("Concocting", "✓"), L.ev_stat("Reproduction Total", 7, not_=True)], fail="info", evaluate="AND", order=9,
                        note="informational: shows while concocting and not yet at 7/7/7"),
             # failState 'error' fires when the evals are NOT met: pass while not concocting OR density ≥ 1
             "Quest failed: Population Density is 0.": L.rule(None, [L.ev_stat("Concocting", "-"), L.ev(["{self}", "stats", "Population Density", "value"], mn=1)], fail="error", evaluate="OR", order=5)}
    # the 'concocted' info is inverted above (info when NOT 7); a cleaner flag:
    rules["concocted"] = L.rule([L.mod(["{self}", "designation"], " — PLAGUE CONCOCTED", append="")],
                                [L.ev_stat("Concocting", "✓"), L.ev_stat("Reproduction Total", 7), L.ev_stat("Density Total", 7), L.ev_stat("Vulnerability Total", 7)],
                                order=5, note="all three Plague Totals are exactly 7")
    del rules["Plague concocted! All three Plague Totals equal 7 — claim the reward for your Suitability Score."]
    text = ("**A Grand Plague.** If your Crusade force includes a DEATH GUARD CHARACTER unit and is not attempting to Concoct a Plague, it can attempt to Concoct a Plague. "
            "Create the world (Fecundity, Population Density and Vulnerability each 1–6: roll a D6 each or pick an example world, then note the Suitability Score = their sum, which never changes during the attempt). "
            "Your plague starts with Rate of Reproduction 1, Survival Rate 1 and Adaptability 1. Your goal is a total of exactly 7 for each of the three Plague Totals.\n\n"
            "**Path of Contagion (after each battle):** Reap the Rewards (apply Agenda results) → Check for a Breakthrough → Cultivation (D6, +2 if you won: on 4+ add or subtract 1 from one plague characteristic) → "
            "Counteragents (D6: if higher than Adaptability, Vulnerability −1) → Death Toll (D6: if higher than Survival Rate, Population Density −1; at 0 the quest fails) → Final Check for a Breakthrough.\n\n"
            "**Success by Suitability Score:** 15–18 Acceptable Offering (one DEATH GUARD CHARACTER gains 2XP; re-roll 5s and 6s when rolling your next world). 11–14 Foul Bounty (2XP; one unit gains a Death Guard Battle Trait). "
            "7–10 A Mighty Pestilence (3XP; claim a permanent Blessing of Nurgle). 3–6 Malign Masterpiece (5XP; claim a permanent Blessing of Nurgle).\n\n"
            "Blessings of Nurgle are permanent; each adds 1 to your Crusade points when determining Crusade Blessings. You cannot gain the same Blessing twice.")
    bless_stats = {n: L.flag(tracking={"Blessing of Nurgle": 1}, order=i + 1) for i, (n, _) in enumerate(BLESSINGS)}
    # the child's own Crusade Pts (tracked, so it sums into the roster's) = number of Blessings ticked
    bless_stats["Crusade Pts"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}
    bless_rules = {f"Blessing {n}": L.rule([L.add(["{self}", "traits"], f"Ability§{n}")], [L.ev_stat(n, "✓")]) for n, _ in BLESSINGS}
    bless_rules["blessingsCrusadePts"] = L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                               [L.count_flags([n for n, _ in BLESSINGS])], order=1,
                                               note="each Blessing of Nurgle adds 1 Crusade point when determining Crusade Blessings")
    for n, t in BLESSINGS:
        L.ability(b, n, t)
    blessings = L.child(b, "Blessings of Nurgle", "Blessings of Nurgle", stats=bless_stats, rules=bless_rules,
                        text="Tick each Blessing of Nurgle your Crusade force has claimed. Each adds 1 to your Crusade points total when determining Crusade Blessings.")
    # Alchemical Pathogen
    path_stats = {"Duration": L.num(1, mn=1, mx=5, order=1),
                  "Properties": L.num(0, mn=0, mx=7, order=2, label="Properties added"),
                  "Drawbacks suppressed": L.num(0, mn=0, mx=7, order=3),
                  "Potency": L.num(1, mn=0, mx=12, dynamic=False, order=4, label="Pathogen Potency (max 7)")}
    path_rules = {"potency": L.rule([L.set_(["{self}", "stats", "Potency", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                    [L.ev([["{self}", "stats", "Duration", "value"], ["{self}", "stats", "Properties", "value"], ["{self}", "stats", "Drawbacks suppressed", "value"]], op="SUM", mn=0)], order=1),
                  "Pathogen Potency can never exceed 7 — Tailor the Toxins before you Brew Your Batch.": L.error_rule([L.ev_stat("Potency", 7, not_=False)], evaluate="AND")}
    # the error rule above would fire whenever Potency == 7; what we want is Potency > 7:
    path_rules["Pathogen Potency can never exceed 7 — Tailor the Toxins before you Brew Your Batch."] = L.rule(None, [L.ev(["{self}", "stats", "Potency", "value"], mx=7)], fail="error", order=5)
    pathogen = L.child(b, "Alchemical Pathogen", "Alchemical Pathogen", stats=path_stats, rules=path_rules, describe=True,
                       text=("Your Pathogen starts with a Duration of 1 and no Properties. Each time a rule lets you **Brew Your Batch**: add 1 to the Duration (max 5), add a Property (with its Drawback, if any), or suppress a Drawback of a Property you have. "
                             "Pathogen Potency = Duration + Properties + suppressed Drawbacks and can never exceed 7; at 7 you can only **Tailor the Toxins** (Duration −1, remove a Property, or un-suppress a Drawback) and then Brew Your Batch. "
                             "In your Command phase you can declare your Pathogen active: it lasts a number of your Command phases equal to its Duration; while active, every DEATH GUARD model equipped with a Lethal Hits weapon has each Property's ability (and its Drawback unless suppressed). "
                             "Note which Properties and Drawbacks you have in the description."))
    L.tracker(b, "Grand Plague", "A Grand Plague", stats=world, children=[blessings, pathogen], text=text, class_rules_=rules)
    cat = L.catalog(b)
    (cat.get("Roster§Roster") or {}).get("rules", {}).pop("blessingsOfNurgleCrusadePts", None)
    # ── units that never gain XP ──
    L.no_xp(b, "Unit", "Poxwalkers", label="POXWALKERS")
    L.class_rule(b, "Unit", "noCrusadeXpPlagueLegions",
                 L.rule([L.set_(["{self}", "stats", "Experience", "visibility"], "hidden"), L.set_(["{self}", "stats", "Battle Honour", "max"], 0)],
                        [L.NARR, L.ev_kw("Legiones Daemonica", field="Faction")],
                        note="Crusade: PLAGUE LEGIONS units never gain Experience points or Battle Honours and automatically pass Out of Action tests"))
    cz.note("Boons of Nurgle reclassed; Grand Plague tracker with Blessings and Pathogen; no-XP for Poxwalkers and Plague Legions")
