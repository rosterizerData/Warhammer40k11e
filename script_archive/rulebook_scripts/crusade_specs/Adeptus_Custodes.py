"""Adeptus Custodes Crusade (10e codex; the 11e codex has no Crusade section). The hand-built bloc (Earning of a Name,
Artefacts of the Vaults, 4 Requisitions, 3 Badges) stays. The Magisterium Lex Ultima Endeavour is rebuilt from the
section: three Imperatives picked from the twelve named ones (each attaching its goal and its Endeavour Reward), the
completion ticks, the nine-battle limit, abandonment with the three Dishonours, and the reward claimed (a Persistent
reward made active adds 1 Crusade point). The Endeavour class keeps its name and its place under the Campaign so
existing rosters still load. Source: Wahapedia crus10_adeptus-custodes."""
import re
SLUG, ED, FACTION = "adeptus-custodes", "10", "Adeptus Custodes"
LISTS = dict(agendas=True, requisitions=False, badges=False)

IMPERATIVES = {   # name: (table, goal, reward)
    "Emperor's Domain": (1, "Complete two battles where, at the end of the battle, you have more friendly units wholly within your deployment zone than enemy units (excluding AIRCRAFT).", "Instant — Gain 3RP."),
    "Wrath of the Emperor": (1, "Complete two battles in which you have destroyed four or more units by the start of the third battle round.", "Instant — You can select two additional units to be Marked for Greatness after the battle in which you completed your final Imperative."),
    "Make an Example": (1, "Win a battle by more than 10 Victory points.", "Instant — Every unit from your Crusade force gains 1XP."),
    "Vital Targets": (1, "Complete two battles in which you destroy the three units from your opponent’s army with the highest points values (if one or more units are tied in this way, then the destruction of any of them counts towards this Imperative).", "Instant — Gain 1RP. The unit from your Crusade army that earned the most XP from an Agenda in the battle in which you completed your final Imperative gains 5XP."),
    "Shadowed Directive": (1, "Complete two battles in which you earned XP from an Adeptus Custodes Agenda.", "Instant — Every unit in your Crusade force gains 1XP. If that unit earned XP from an Agenda in the battle in which you completed your final Imperative, it gains 2XP."),
    "Absolute Mastery": (1, "Complete two battles in which you earned XP from non-ADEPTUS CUSTODES Agendas (such as those found in the main Crusade rules).", "Instant — Your WARLORD from the battle in which you completed your final Imperative gains 5XP."),
    "Shadow of the Throne": (2, "At the end of the battle, both of the following are satisfied: you control three or more objective markers; you control at least double the number of objective markers that your opponent does.", "Persistent — Once per battle, you can target a friendly unit with an Adeptus Custodes Stratagem for 0CP."),
    "Martial Supremacy": (2, "At the end of a battle, at least twice as many enemy units were destroyed in that battle than units from your Crusade army.", "Persistent — Once per battle, you can target a friendly unit with the Fire Overwatch Stratagem or the Heroic Intervention Stratagem for 0CP."),
    "Alpha Threat Confirmed": (2, "At the end of the battle, the enemy WARLORD is destroyed.", "Instant — If the enemy WARLORD was destroyed in the battle in which you completed your final Imperative, the friendly unit that destroyed it gains a Battle Honour. If no friendly unit achieved this, claim the Endeavour reward from the Wrath of the Emperor Imperative instead."),
    "Annihilation": (2, "At the end of a battle, every enemy unit is destroyed, or is Below Half-strength.", "Persistent — Once per battle, you can target a friendly unit with the Counter-offensive Stratagem or the Epic Challenge Stratagem for 0CP."),
    "Emperor's Will Be Done": (2, "Complete two battles where, at the end of the battle, you have more friendly units wholly within your opponent’s deployment zone than enemy units (excluding AIRCRAFT).", "Persistent — Once per battle, you can target a friendly unit with the Command Re-roll Stratagem or the Rapid Ingress Stratagem for 0CP."),
    "Inspirational Example": (2, "At the end of the battle, two or more enemy units were destroyed by melee attacks made by an ADEPTUS CUSTODES CHARACTER model from your Crusade army.", "Instant — The ADEPTUS CUSTODES CHARACTER that completed this Imperative gains a Battle Honour."),
}
DISHONOURS = {
    "Command in Question": "Select one SHIELD-CAPTAIN unit from your Crusade force. That unit gains the Disgraced Battle Scar and the Mark of Shame Battle Scar from the main Crusade rules. If your Crusade force does not contain any SHIELD-CAPTAIN units, re-roll this result.",
    "Damage Limitation": "Halve the XP (rounding down) that units in your Crusade force earn for a number of battles equivalent to the number of your Endeavour’s Imperatives that were not completed (the previous battle counts as the first of such battles).",
    "Petition the Tower of Hegemon": "Reduce your Requisition points to 0. You cannot gain Requisition points for a number of battles equivalent to the number of Imperatives of your Endeavour that were not completed (the previous battle counts as the first of such battles).",
}
TEXT = ("**Magisterium Lex Ultima.** If your Crusade force includes TRAJANN VALORIS or any other SHIELD-CAPTAIN and you are not on an Endeavour, you can claim the Magisterium Lex Ultima before a battle and commence an Endeavour (add an Endeavour to your Campaign). "
        "Determine its three Imperatives: roll a D6 for the table (1–3 / 4–6), then a D6 on that table; no Imperative twice in one Endeavour. Complete them in order; at the end of a battle in which you completed the active Imperative, tick it and the next one becomes active.\n\n"
        "When all three are complete, claim one Endeavour Reward from the three Imperatives. Instant rewards apply at once; Persistent rewards are noted in your Order of Battle, and before each battle you can make one of them active (+1 to your Crusade army’s Crusade points). "
        "You can abandon an Endeavour at the end of a battle (with two Imperatives complete, randomly claim one of those two rewards); an Endeavour not completed within nine battles is abandoned. Abandoning means a Dishonour (select one or roll a D6).")


def build(cz):
    L, b = cz.L, cz.book
    L.del_assets(b, ["Battle Trait§Genalchimic Warding"])   # misspelt duplicate of the imported trait
    names = list(IMPERATIVES)
    for n, (tbl, goal, rew) in IMPERATIVES.items():
        L.ability(b, f"Imperative: {n}", f"**Imperative (D6 {'1–3' if tbl == 1 else '4–6'}).** {goal}\n\n**Endeavour Reward:** {rew}")
    for n, t in DISHONOURS.items():
        L.ability(b, f"Dishonour: {n}", t)
    persistent = [n for n, v in IMPERATIVES.items() if v[2].startswith("Persistent")]
    stats = {}
    rules = {}
    for i in (1, 2, 3):
        stats[f"Imperative {i}"] = L.rank(names, tracking={n: {f"imperative{re.sub(r'\W', '', n)}": 1} for n in names}, order=2 * i - 1, group="Imperatives", group_order=2)
        stats[f"Imperative {i} completed"] = L.flag(order=2 * i, group="Imperatives", group_order=2)
        for n in names:
            rules[f"imp{i}{re.sub(r'\W', '', n)}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Imperative: {n}")], [L.ev_stat(f"Imperative {i}", n)], order=2)
    stats["Battles"] = L.num(0, mn=0, mx=9, order=7, label="Battles on this Endeavour (max 9)")
    stats["Abandoned"] = L.flag(order=8)
    stats["Dishonour"] = L.rank(list(DISHONOURS), order=9)
    stats["Reward claimed"] = L.rank(names, order=10, label="Endeavour Reward claimed")
    stats["Persistent reward active"] = L.flag(order=11, label="Persistent reward active this battle")
    stats["Crusade Pts"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}
    for n in DISHONOURS:
        rules[f"dishonour{re.sub(r'\W', '', n)}"] = L.rule([L.add(["{self}", "traits"], f"Ability§Dishonour: {n}")], [L.ev_stat("Dishonour", n)], order=2)
    for n in names:
        rules[f"An Endeavour cannot have {n} twice."] = L.rule(None, [L.ev(["{self}", "tracked", f"imperative{re.sub(r'\W', '', n)}"], mx=1)], fail="error", order=5)
    rules["Claim the reward of one of this Endeavour's Imperatives."] = L.rule(
        None, [L.ev_stat("Reward claimed", "-")] + [L.ev(["{self}", "stats", "Reward claimed", "value"], ["{self}", "stats", f"Imperative {i}", "value"]) for i in (1, 2, 3)], fail="error", evaluate="OR", order=5)
    rules["Only a Persistent reward can be made active."] = L.rule(
        None, [L.ev_stat("Persistent reward active", "-")] + [L.ev_stat("Reward claimed", n) for n in persistent], fail="error", evaluate="OR", order=5)
    rules["persistentCrusadePt"] = L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], 1)], [L.ev_stat("Persistent reward active", "✓")], order=2,
                                          note="an active Persistent Endeavour Reward adds 1 to the Crusade army's Crusade points")
    rules["completed"] = L.rule([L.mod(["{self}", "designation"], " — COMPLETE", append="")],
                                [L.ev_stat(f"Imperative {i} completed", "✓") for i in (1, 2, 3)], order=6)
    rules["abandonedMark"] = L.rule([L.mod(["{self}", "designation"], " — ABANDONED", append="")], [L.ev_stat("Abandoned", "✓")], order=6)
    rules["The Endeavour has run nine battles: it is abandoned (select a Dishonour)."] = L.rule(
        None, [L.ev(["{self}", "stats", "Battles", "value"], mx=8), L.ev_stat("Imperative 3 completed", "✓"), L.ev_stat("Abandoned", "✓")], fail="warning", evaluate="OR", order=6)
    T = L.taxonomy(b)
    T["Endeavour"] = {"aspects": {"Rename": True, "Describe": True}, "stats": stats, "rules": rules, "templateClass": "Magisterium Lex Ultima"}
    L.put_asset(b, "Endeavour§Endeavour", {"text": TEXT})
    cz.note(f"Endeavour rebuilt: 12 Imperatives (4 Persistent rewards), 3 Dishonours")
