"""World Eaters Crusade (10e codex, as carried on the 11e site): The Skull Harvest (Skull points, Judgement of the Blood
God, Lesser and Greater Rewards of Khorne), Boons of Khorne, Blood Legions. Source: Wahapedia crus11_world-eaters."""
import re
SLUG, ED, FACTION = "world-eaters", "11", "World Eaters"
LISTS = dict(agendas=True, requisitions=True, badges=True)

BOONS = ["Collar of Khorne", "Bestial Limbs", "Muscular Bulk", "Jagged Horns", "Daemonic Visage", "Brazen Flesh", "Steel Sinews", "Tearing Claws", "Warp Strength"]
HARVEST = ("**The Skull Harvest.** Each time an enemy unit is destroyed by a melee attack made by a WORLD EATERS unit from your army, that unit gains 1 Skull point, "
           "plus 1 bonus Skull point for each that applies: the enemy unit is a CHARACTER, MONSTER or WALKER; it is a WARLORD; it is TITANIC. A unit cannot gain more than 5 Skull points in one battle. "
           "Enemy EPIC HEROES and Legendary-rank units award 1 Legendary Skull point instead (no limit). For an Attached unit you decide whether the Leader or the Bodyguard unit gains each point. "
           "EPIC HEROES do not track Skull points (track them for bragging rights only). Record the points on each unit's Skull Points and Legendary Skull Points counters.\n\n"
           "**Judgement of the Blood God.** At the start of the Update Crusade Cards step, any unit with 1 or more Skull points can make an offering: roll one D6 and add the unit's Judgement bonus "
           "(+1 per 3 Skull points, rounded down, +1 per Legendary Skull point). 1–3 **Unworthy Offering:** the unit takes a Leadership test; if failed it suffers a Devastating Blow or Battle Scar as if it had failed an Out of Action test. "
           "4–5 **Pleasing Bounty:** the unit is Marked for Greatness in addition to any others. 6–7 **Bloody Harvest:** roll on the Lesser Rewards table. 8+ **Mighty Offering:** roll on the Greater Rewards table. "
           "After an offering (whatever the result) the unit's Skull points and Legendary Skull points reset to 0.\n\n"
           "**Lesser Rewards of Khorne (D6):** 1–2 Lessons of Slaughter — this unit gains 5XP. 3–4 Boon of Khorne — if the unit is a CHARACTER (not a DAEMON PRINCE) it gains one Boon of Khorne of your choice, otherwise 5XP. "
           "5–6 Favoured Champions — the unit gains one Battle Honour of your choice that it could normally have.\n\n"
           "**Greater Rewards of Khorne (D6):** each is unique in your Crusade force (re-roll duplicates); if the unit is at its Battle Honour cap, replace one non-Greater-Reward honour. "
           "While a unit with a Greater Reward is on the battlefield when you make a Blessings of Khorne roll, you also have access to the associated Blessing of Khorne (the double shown).\n\n"
           "**Blood Legions:** with the Khorne Daemonkin Detachment, BLOOD LEGIONS units from your Crusade force can join your Crusade army; they never gain Experience points or Battle Honours and automatically pass Out of Action tests.")


def greater_rewards(sec):
    """'DEATH TO COWARDS (DOUBLE 3+)' heading, flavour line, rules line — under the second 'Greater Rewards of Khorne' heading"""
    lines = [l for l in sec.block("Greater Rewards of Khorne", nth=1) if l.strip()]
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"^([A-Z][A-Z’'\- ]+?) \(DOUBLE (\d)\+\)$", lines[i].strip())
        if m and i + 2 < len(lines):
            out.append({"name": sec.__class__.__dict__["named"].__globals__["title_case"](m.group(1)), "double": m.group(2),
                        "text": lines[i + 2].strip() + f"\n\nBlessing of Khorne unlocked: double {m.group(2)}+. Greater Rewards are unique: only one model in your Crusade force can have each."})
            i += 3
        else:
            i += 1
    return out


def build(cz):
    L, b = cz.L, cz.book
    # ── Boons of Khorne: Characters (not Daemon Princes), three per model ──
    L.reclass(b, "Crusade Honour§", "Boon of Khorne", BOONS, patch={"keywords": {"Tags": [], "Keywords": []}})
    L.honour_class(b, "Boon of Khorne", unique=False, allow_on=("Character",), allow_evals=[L.ev_kw("Daemon Prince", not_=True)],
                   allow_note="Boons of Khorne: WORLD EATERS CHARACTER models (not DAEMON PRINCES) may take a Boon of Khorne instead of another Battle Honour; a duplicate D33 roll means Spawndom",
                   cap=3, cap_text="No model can have more than three Boons of Khorne.")
    # ── Skull points on every World Eaters unit (Characters and Vehicles inherit the Unit class) ──
    we = [L.ev_kw("World Eaters", field="Faction")]
    L.unit_stat(b, "Unit", "Skull Points", L.num(0, mn=0, mx=50, group="Crusade", group_order=11, order=30, icons=["skull"]), show_when=we)
    L.unit_stat(b, "Unit", "Legendary Skull Points", L.num(0, mn=0, mx=50, group="Crusade", group_order=11, order=31), show_when=we)
    L.unit_stat(b, "Unit", "Judgement Bonus", L.num(0, mn=0, mx=99, dynamic=False, group="Crusade", group_order=11, order=32, label="Judgement bonus (+D6)"), show_when=we)
    L.class_rule(b, "Unit", "judgementBonus",
                 L.rule([L.set_(["{self}", "stats", "Judgement Bonus", "value"], ["{this}", "evals", "2", "result", "integer"])],
                        [L.ev(["{self}", "stats", "Skull Points", "value"], mn=0, equation={"operator": "T/O", "value": 3}),
                         L.ev(["{self}", "stats", "Legendary Skull Points", "value"], mn=0),
                         L.ev([["{this}", "evals", "0", "result", "integer"], ["{this}", "evals", "1", "result", "integer"]], op="SUM", mn=0)],
                        order=2, note="Judgement roll bonus: +1 per 3 Skull points (rounded down) +1 per Legendary Skull point"))
    # ── Greater Rewards of Khorne: six unique honours on any World Eaters unit ──
    L.honour_class(b, "Greater Reward of Khorne", unique=True, allow_on=("Unit",), allow_evals=we,
                   allow_note="Greater Rewards of Khorne: gained on a Mighty Offering (Judgement roll 8+); unique in the Crusade force")
    gr = greater_rewards(cz.sec)
    # a child with no Tags fails a parent's constraints.any; every unit's constraints carry its Faction keyword, so tag by faction
    L.honours(b, "Greater Reward of Khorne", gr, keywords=["Greater Rewards of Khorne"], tags=[FACTION])
    L.unique_in_roster(b, [g["name"] for g in gr])   # unique in the Crusade force (the Unique aspect only covers one parent)
    # ── the Skull Harvest reference trait ──
    L.tracker(b, "Skull Harvest", "The Skull Harvest", text=HARVEST)
    # ── Blood Legions never gain XP ──
    L.class_rule(b, "Unit", "noCrusadeXpBloodLegions",
                 L.rule([L.set_(["{self}", "stats", "Experience", "visibility"], "hidden"), L.set_(["{self}", "stats", "Battle Honour", "max"], 0)],
                        [L.NARR, L.ev_kw("Blood Legions", field="Faction")],
                        note="Crusade: BLOOD LEGIONS units never gain Experience points or Battle Honours and automatically pass Out of Action tests"))
    cz.note(f"Boons of Khorne reclassed; Skull/Legendary Skull counters + Judgement bonus; Greater Rewards {len(gr)}: " + ", ".join(g["name"] for g in gr) + "; Skull Harvest reference; Blood Legions no-XP")
