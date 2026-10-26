"""Emperor's Children Crusade (10e codex, as carried on the 11e site): Combat Elixirs (ingredients, Army and Personal
Elixirs, equipping), Boons of Slaanesh, Legions of Excess. Source: Wahapedia crus11_emperor-s-children; the elixir
recipes were decoded from the page's ingredient icons."""
SLUG, ED, FACTION = "emperor-s-children", "11", "Emperor’s Children"
LISTS = dict(agendas=True, requisitions=True, badges=True)

BOONS = ["Dark Majesty", "Odious Grace", "Fickle Speed", "Whipcord Sinews", "Razor Claws", "Psychotropic Aura", "Betentacled Limbs", "Perfection of the Body", "Silver Skin"]
EXOTICS = ["Concentrate of Tormented Souls", "Dilution of False Hope", "Distillate of Hatred", "Essence of Fear", "Extract of Xeno-matter", "Infusion of Traitor’s Blood"]
ARMY = [("Anfrak Silk", "Common + Rare (or Extract of Xeno-matter)", "Add 2\" to the Move characteristic of EMPEROR’S CHILDREN units from your Crusade army."),
        ("Xylocil", "Common + Rare (or Extract of Xeno-matter)", "Add 1 to the Strength characteristic of melee weapons equipped by EMPEROR’S CHILDREN models from your Crusade army."),
        ("Shivversplit", "Common + Rare (or Essence of Fear)", "Add 1 to the Toughness characteristic of EMPEROR’S CHILDREN units from your Crusade army."),
        ("Heliotrophos", "2× Common + Rare", "Add 1 to the Attacks characteristic of melee weapons equipped by EMPEROR’S CHILDREN models from your Crusade army."),
        ("Skorflense", "2× Common (or Extract of Xeno-matter)", "Improve the Ballistic Skill and Weapon Skill characteristics of weapons equipped by EMPEROR’S CHILDREN models from your Crusade army by 1."),
        ("Quail", "Common + Rare", "Improve the Leadership and Objective Control characteristics of EMPEROR’S CHILDREN units from your Crusade army by 1.")]
PERSONAL = [("Alacrine", "2× Common, or Rare + Extract of Xeno-matter", "The bearer’s unit has the Fights First ability."),
            ("Cerebresec", "2× Common + Concentrate of Tormented Souls", "Once per battle round, when you target the bearer’s unit with a Stratagem, reduce the CP cost of that usage of that Stratagem by 1."),
            ("Thrynicine", "2× Rare (or Distillate of Hatred) + Rare (or Dilution of False Hope)", "Each time the bearer makes an attack, a successful Wound roll inflicts 1 mortal wound on the target in addition to any normal damage, or 2 mortal wounds in addition to any normal damage instead if the bearer has lost one or more wounds."),
            ("Salviqine Tears", "Common + Rare (or Essence of Fear)", "At the start of the Battle-shock step of each player’s Command phase, each enemy unit that is within 12\" of the bearer and is below its Starting Strength must take a Battle-shock test, subtracting 1 from that test if that unit is Below Half-strength."),
            ("Sanctus Vi", "Common + Rare (or Concentrate of Tormented Souls) + Infusion of Traitor’s Blood", "The bearer has a 2+ invulnerable save."),
            ("Excelsor X", "4× Common (or Dilution of False Hope) + Rare", "In your Shooting phase, after the bearer’s unit has shot, if that unit is not within Engagement Range of one or more enemy units, it can make a Normal move of up to 6\".")]


def build(cz):
    L, b = cz.L, cz.book
    ec = [L.ev_kw("Emperor’s Children", field="Faction")]
    # ── Boons of Slaanesh ──
    L.reclass(b, "Crusade Honour§", "Boon of Slaanesh", BOONS)
    L.honour_class(b, "Boon of Slaanesh", unique=False, allow_on=("Character",), allow_evals=[L.ev_kw("Daemon Prince", not_=True), L.ev_kw("Daemon Prince with Wings", not_=True)],
                   allow_note="Boons of Slaanesh: EMPEROR’S CHILDREN CHARACTER models (not DAEMON PRINCES) may take a Boon of Slaanesh instead of another Battle Honour; a duplicate D33 roll means Spawndom",
                   cap=3, cap_text="No model can have more than three Boons of Slaanesh.")
    # ── the stash tracker ──
    stats = {"Common Ingredients": L.num(0, mn=0, mx=20, group="Ingredients", group_order=1, order=1),
             "Rare Ingredients": L.num(0, mn=0, mx=20, group="Ingredients", group_order=1, order=2)}
    for i, x in enumerate(EXOTICS):
        stats[x] = L.num(0, mn=0, mx=9, group="Exotic ingredients", group_order=2, order=10 + i)
    for i, (n, _, _) in enumerate(ARMY):
        stats[n + " (doses)"] = L.num(0, mn=0, mx=9, group="Army Elixirs", group_order=3, order=20 + 2 * i, label=n + " doses")
        stats[n + " equipped"] = L.flag(tracking={"Army Elixir equipped": 1}, group="Army Elixirs", group_order=3, order=21 + 2 * i, label=n + " equipped")
    for i, (n, _, _) in enumerate(PERSONAL):
        stats[n + " (doses)"] = L.num(0, mn=0, mx=9, group="Personal Elixirs", group_order=4, order=40 + i, label=n + " doses")
    stats["Crusade Pts"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}
    stats["Elixirs equipped"] = L.num(0, mn=0, mx=12, dynamic=False, order=60, label="Elixirs equipped this battle")
    rules = {"equippedCount": L.rule([L.set_(["{self}", "stats", "Elixirs equipped", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                     [L.ev([["{roster}", "tracked", "Army Elixir equipped"], ["{roster}", "tracked", "Personal Elixir equipped"]], op="SUM", mn=0)], order=2),
             "elixirCrusadePts": L.rule([L.set_(["{self}", "stats", "Crusade Pts", "value"], ["{this}", "evals", "2", "result", "integer"])],
                                        [L.ev([["{roster}", "tracked", "Army Elixir equipped"], ["{roster}", "tracked", "Personal Elixir equipped"]], op="SUM", mn=0),
                                         L.ev(["{this}", "evals", "0", "result", "float"], mn=0, equation={"operator": "T+O", "value": 1}),
                                         L.ev(["{this}", "evals", "1", "result", "float"], mn=0, equation={"operator": "T/O", "value": 2})],
                                        order=3, note="+1 Crusade point per two elixirs equipped (rounding up)")}
    recipes = "\n".join(f"• **{n}** ({r}): {e}" for n, r, e in ARMY)
    precipes = "\n".join(f"• **{n}** ({r}): {e}" for n, r, e in PERSONAL)
    text = ("**Combat Elixirs.** If your Crusade force has an EMPEROR’S CHILDREN CHARACTER, it collects ingredients and crafts elixirs; the stash holds what is listed here (anything over the caps is lost). "
            "The first EMPEROR’S CHILDREN unit added to your Order of Battle also adds one dose of Anfrak Silk.\n\n"
            "**Ingredients:** after every battle roll a D6 (+2 if you won): on a 4+ gain 1 Common ingredient, on a 6+ gain D3 instead. Roll another D6 (+1 if you won): on a 6+ gain 1 Rare ingredient. "
            "Exotic ingredients come only from Agendas, Requisitions and some Battle Honours.\n\n"
            "**Crafting:** before or after a battle, spend the listed ingredients to add one dose of an elixir. Army Elixirs equip the whole army for one battle; Personal Elixirs equip one CHARACTER for one battle.\n\n"
            "**Equipping:** when mustering an EMPEROR’S CHILDREN Crusade army, tick the Army Elixirs you equip (one dose each) and set each CHARACTER's Personal Elixir; remove the doses from the stash. "
            "You cannot equip the same elixir in two consecutive battles. Every two elixirs equipped (rounding up) add 1 to the army's Crusade points. If you equip none, every EMPEROR’S CHILDREN unit is Battle-shocked for the first battle round. "
            "Once per battle, at the start of a battle round, all equipped elixirs take effect until the next battle round; all equipped doses are lost at the end of the battle.\n\n"
            "**Army Elixirs:**\n" + recipes + "\n\n**Personal Elixirs:**\n" + precipes + "\n\n"
            "**Legions of Excess:** units from your Order of Battle that join through a Detachment such as Carnival of Excess never gain Experience points or Battle Honours and automatically pass Out of Action tests.")
    L.tracker(b, "Combat Elixirs Stash", "Combat Elixirs Stash", stats=stats, text=text, class_rules_=rules)
    # ── Personal Elixir pick on Characters ──
    L.unit_stat(b, "Character", "Personal Elixir", L.rank([n for n, _, _ in PERSONAL], tracking={"Personal Elixir equipped": 1}, group="Crusade", group_order=11, order=20),
                show_when=ec)
    # ── Legions of Excess never gain XP ──
    L.class_rule(b, "Unit", "noCrusadeXpLegionOfExcess",
                 L.rule([L.set_(["{self}", "stats", "Experience", "visibility"], "hidden"), L.set_(["{self}", "stats", "Battle Honour", "max"], 0)],
                        [L.NARR, L.ev_kw("Legion of Excess", field="Faction")],
                        note="Crusade: LEGIONS OF EXCESS units never gain Experience points or Battle Honours and automatically pass Out of Action tests"))
    cz.note("Boons of Slaanesh reclassed; Combat Elixirs Stash tracker (2 ingredient counters, 6 exotics, 12 dose counters, 6 army equip flags, Crusade Pts from equipped count); Personal Elixir rank on Characters; Legion of Excess no-XP")
