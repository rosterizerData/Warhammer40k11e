"""Chaos Space Marines Crusade (10e codex, as carried on the 11e site): Chaos Warbands (Warband Champion, Chaos points,
three Glory categories), Chaos Boons, Daemon Weapons. Source: Wahapedia crus11_chaos-space-marines."""
import re
SLUG, ED, FACTION = "chaos-space-marines", "11", "Heretic Astartes"
LISTS = dict(agendas=True, requisitions=True, badges=True)
AGENDA_BLOCKS = ["Agendas", "Glory Agendas"]

BOONS = ["Warp Stalker", "Unholy Speed", "Mutant Form", "Massive Fangs", "Eightfold Eyes", "Daemonic Flesh", "Scorpion Tail", "Iron-hard Talons", "Dark Blessing"]
GLORY = ["Personal Glory", "Dark God Glory", "Warfleet Glory"]
FAVOURED = {
    "Personal Glory": "**Blessed Champion:** After each battle, you can purchase one of the following Requisitions once, and when you do, reduce the cost by 1RP: Renowned Heroes, Ascension to Daemonhood.\n\n**Dark Destiny:** After each battle, in the Update Crusade Cards step, if your WARBAND CHAMPION model destroyed one or more enemy units during that battle, roll one D6. On a 6, your WARBAND CHAMPION gains one Battle Honour of your choice, and change the Leadership characteristic of that model to 5+. Your WARBAND CHAMPION can gain a maximum of 3 Battle Honours using this Favoured Reward (tick them on the Champion's Dark Destiny counter).",
    "Dark God Glory": "**Worthy Offerings:** After each battle, you can purchase one of the following Requisitions once, and when you do, reduce the cost by 1RP: Sacrifice to the Dark Gods, Mortal Empowerment.\n\n**Boon of Power:** After each battle, in the Update Crusade Cards step, you can select one unit from your Crusade army that destroyed one or more enemy units during that battle, then roll one D6. On a 6, that unit gains one Chaos Boon. If that unit is not a CHARACTER unit but it contains a Unit Champion, that Unit Champion gains that Chaos Boon, even though normally only CHARACTER units can gain Chaos Boons.",
    "Warfleet Glory": "**Feared and Respected:** After each battle, you can purchase one of the following Requisitions once, and when you do, reduce the cost by 1RP: Increase Supply Limit, Legendary Veterans, Repair and Recuperate.\n\n**Unrivalled Raiders:** After each battle, in the Update Crusade Cards step, you can select one unit from your Crusade army (excluding your WARBAND CHAMPION) that destroyed one or more enemy units during that battle, then roll one D6. On a 6, that unit gains one Battle Trait or Weapon Enhancement Battle Honour of your choice. No unit from your Crusade force can gain more than 1 Battle Honour using this Favoured Reward."}
FORSAKEN = {
    "Personal Glory": "**Failing Champion:** The RP cost of the following Requisitions is increased by 1RP: Renowned Heroes, Ascension to Daemonhood.\n\n**Circling Rivals:** After losing a battle, in the Update Crusade Cards step, roll one D6. On a 1, a rival declares a challenge: select one other HERETIC ASTARTES CHARACTER model from your Order of Battle (excluding EPIC HEROES) to be the rival (if there are no others, nothing happens). Then roll one D6 for your WARBAND CHAMPION and one D6 for that CHARACTER: the model you roll highest for gains 3XP, and the other model is treated as having failed an Out of Action test.",
    "Dark God Glory": "**Forsaken Faith:** The RP cost of the following Requisitions is increased by 1RP: Sacrifice to the Dark Gods, Mortal Empowerment.\n\n**Anger of the Gods:** During each battle, each time a unit from your Crusade army makes a Dark Pact, subtract 1 from the resulting Leadership test, and if a unit from your Crusade army destroys one or more enemy units in a phase in which it made a Dark Pact, that unit gains 1XP.",
    "Warfleet Glory": "**Fading Notoriety:** The RP cost of the following Requisitions is increased by 1RP: Increase Supply Limit, Legendary Veterans, Repair and Recuperate.\n\n**Dwindling Supplies:** After the battle, in the Update Order of Battle step, roll one D6: on a 1, reduce your Requisition points total by D3; on a 6, you gain 1RP."}
DW_ABILITY = ("**Daemon Weapon:** In the Fight phase, if this model’s unit makes a Dark Pact and fails the resulting Leadership test, until the end of the phase, "
              "melee weapons equipped by this model have the [HAZARDOUS] ability. A Daemon Weapon confers the relevant Chaos God’s keyword on the bearer; with the "
              "Pactbound Zealots Detachment, the Marks of Chaos keyword for a unit with a Daemon Weapon must match it. Each CHARACTER can have only one Daemon Weapon, "
              "gained by completing a Glory Agenda.")


def daemon_weapons(sec):
    """names are Title-case lines ('Zaall, the Wrathful'), each followed by a flavour line and a rules line"""
    lines = [l for l in sec.block("Daemon Weapons") if l.strip()]
    out, i = [], 0
    while i < len(lines):
        l = lines[i].strip()
        if len(l) < 45 and re.match(r"^[A-Z][^.]*$", l) and i + 2 < len(lines) and len(lines[i + 1]) > 60:
            out.append({"name": l, "text": lines[i + 2].strip() + "\n\n" + DW_ABILITY})
            i += 3
        else:
            i += 1
    return out


def build(cz):
    L, b = cz.L, cz.book
    # ── Chaos Boons: own class, Characters (not DAEMON models), max three per model; Damned units via Mortal Empowerment ──
    L.reclass(b, "Crusade Honour§", "Chaos Boon", BOONS, patch={"keywords": {"Tags": [], "Keywords": []}})
    L.honour_class(b, "Chaos Boon", unique=False, allow_on=("Character",), allow_evals=[L.ev_kw("Daemon", not_=True)],
                   allow_note="Chaos Boons: HERETIC ASTARTES CHARACTER models (not DAEMON models) may take a Chaos Boon instead of another Battle Honour; a duplicate D33 roll means Spawndom",
                   cap=3, cap_text="No model can have more than three Chaos Boons.")
    L.class_rule(b, "Unit", "allowChaosBoonDamned", L.rule([L.add(["{self}", "allowed", "classifications"], "Chaos Boon")], [L.NARR, L.ev_kw("Damned")],
                                                         note="Mortal Empowerment: a DAMNED unit that destroyed enemy units can gain one Chaos Boon"))
    L.class_rule(b, "Unit", "No model can have more than three Chaos Boons.", L.error_rule([L.ev(["{self}", "tally", "Chaos Boon"], mx=3)]))
    # ── Warband Champion (one non-Epic Character) with Chaos points and the Dark Destiny counter ──
    L.unit_stat(b, "Character", "Warband Champion", L.flag(tracking={"Warband Champion": 1}, group="Crusade", group_order=11, order=20),
                show_when=[L.ev_kw("Epic Hero", not_=True)])
    L.unit_stat(b, "Character", "Chaos Points", L.num(0, mn=0, mx=99, group="Crusade", group_order=11, order=21, icons=["skull-shield"]),
                show_when=[L.ev_stat("Warband Champion", "✓")], show_rule="crusadeShowChaosPoints")
    L.unit_stat(b, "Character", "Dark Destiny", L.num(0, mn=0, mx=3, group="Crusade", group_order=11, order=22, label="Dark Destiny honours"),
                show_when=[L.ev_stat("Warband Champion", "✓")], show_rule="crusadeShowDarkDestiny")
    L.class_rule(b, "Character", "warbandChampionKeyword", L.rule([L.add(["{self}", "keywords", "Keywords"], "Warband Champion")], [L.ev_stat("Warband Champion", "✓")]))
    L.class_rule(b, "Character", "darkDestinyHonours", L.rule([L.mod(["{self}", "stats", "Battle Honour", "max"], ["{self}", "stats", "Dark Destiny", "value"])],
                                                           [L.ev_stat("Warband Champion", "✓"), L.ev(["{self}", "stats", "Dark Destiny", "value"], mn=1)],
                                                           note="Dark Destiny: up to three extra Battle Honours on the Warband Champion"))
    L.roster_rule(b, "One Warband Champion only.", L.error_rule([L.ev_tracked("Warband Champion", mx=1, who="{self}")]))
    # ── the warband tracker: three Glory categories 1–8 (start 4), Favoured at 7–8, Forsaken at 1–2 ──
    stats = {g: L.num(4, mn=1, mx=8, order=i + 1, label=g + " (level)") for i, g in enumerate(GLORY)}
    rules = {}
    for g in GLORY:
        L.ability(b, f"Favoured — {g}", FAVOURED[g])
        L.ability(b, f"Forsaken — {g}", FORSAKEN[g])
        rules[f"favoured{g.replace(' ', '')}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Favoured — {g}")], [L.ev(["{self}", "stats", g, "value"], mn=7)])
        rules[f"forsaken{g.replace(' ', '')}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Forsaken — {g}")], [L.ev(["{self}", "stats", g, "value"], mx=2)])
    text = ("**Chaos Warbands.** Select one HERETIC ASTARTES CHARACTER (not an EPIC HERO) from your Order of Battle as your Warband Champion (tick Warband Champion on its card). "
            "After each battle your Champion fought in, it gains Chaos points: D3+3 for a win, 3 for a draw, D3 for a loss. Spend Chaos points one for one to raise a Glory category; "
            "all three start at Level 4, drop by 1 after every battle (before the Champion gains Chaos points), and never go below 1 or above 8. "
            "Levels 7–8 are **Favoured** (the Glory's rewards apply), levels 1–2 are **Forsaken** (its punishments apply). Some Chaos Space Marines Agendas also raise Glory.")
    L.tracker(b, "Chaos Warband", "Chaos Warband Tracker", stats=stats, text=text, class_rules_=rules)
    # ── Daemon Weapons: one per Character, gained through a Glory Agenda ──
    L.honour_class(b, "Daemon Weapon", unique=True, allow_on=("Character",), allow_evals=[L.ev_kw("Epic Hero", not_=True)],
                   allow_note="Daemon Weapons: a HERETIC ASTARTES CHARACTER that completes a Glory Agenda may claim one Daemon Weapon",
                   cap=1, cap_text="A model can have only one Daemon Weapon.")
    dws = daemon_weapons(cz.sec)
    L.honours(b, "Daemon Weapon", dws, keywords=["Relic"], tags=["Heretic Astartes"])
    cz.note(f"Chaos Boons reclassed; Warband Champion + Chaos Warband tracker; Daemon Weapons {len(dws)}: " + ", ".join(d["name"] for d in dws))
