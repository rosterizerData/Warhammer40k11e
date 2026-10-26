"""Adepta Sororitas Crusade (10e codex, as carried on the 11e site): Trials of a Living Saint.
Source: Wahapedia crus11_adepta-sororitas. The five Saintly Rewards were imported from BSData under their Trial's name."""
SLUG, ED, FACTION = "adepta-sororitas", "11", "Adepta Sororitas"
LISTS = dict(agendas=True, requisitions=True, badges=True)

# Trial → (reward name, Saintly Deeds text)
TRIALS = {
    "Trial of Faith": ("Boundless Faith", "**Beacon of Divine Grace:** gain 2 Saint points at the end of a battle if this model performed 3 or more Acts of Faith during that battle. **Miraculous Feat:** gain 1 Saint point at the end of a battle for each Miracle dice remaining in your Miracle Dice pool (to a maximum of 2 Saint points)."),
    "Trial of Suffering": ("Miraculous Recovery", "**Scars of the Penitent:** gain 3 Saint points each time this model gains a Martyr point. **Martyr’s Wounds:** gain 1 Saint point at the end of a battle if this model is below its Starting Strength, or 2 Saint points instead if this model was destroyed while within range of an objective marker."),
    "Trial of Purity": ("Blazing Soulfire", "**Consecrate Ground:** gain 2 Saint points at the end of a battle if this model is within 6\" of the centre of the battlefield. **Divine Will:** gain 2 Saint points at the end of a battle if this model’s unit did not fail a Battle-shock test during that battle."),
    "Trial of Righteousness": ("Righteous Judgement", "**Slay the Demagogue:** gain 2 Saint points at the end of a battle if this model destroyed one or more enemy CHARACTER units during that battle, and 2 more if one of them contained the enemy WARLORD. **Smite the Unbelievers:** gain 2 Saint points at the end of a battle if this model destroyed 5 or more enemy models during that battle."),
    "Trial of Valour": ("Voice of the Emperor", "**Holy Crusader:** gain 3 Saint points at the end of a battle if this model is wholly within your opponent’s deployment zone. **Pious Reputation:** gain 2 Saint points at the end of a battle if this model gained more XP than any other unit from your Crusade army during that battle."),
}
TEXT = ("**Trials of a Living Saint.** When you start a Crusade force, if there are any ADEPTA SORORITAS CHARACTER models on your Order of Battle (excluding EPIC HEROES), you can select one of them: tick **Saint Potentia** on its card. "
        "Select a Trial for it; it accrues Saint points by accomplishing that Trial’s Saintly Deeds. At 10 or more Saint points the Trial is complete: reset Saint points to 0 and the model gains that Trial’s Saintly Reward Battle Honour "
        "(each is unique; if the model already has its maximum Battle Honours you must replace one, never a Saintly Reward). With 4 or fewer Saintly Rewards you can then select a new Trial. At the end of a battle a SAINT POTENTIA can abandon its Trial for a new one (Saint points reset to 0). "
        "When the model has 5 Saintly Rewards it is a **LIVING SAINT**.\n\n"
        "**Martyr points.** Each time a SAINT POTENTIA or LIVING SAINT fails an Out of Action test it gains 1 Martyr point and takes a Martyrdom test: roll one D6 and add its Martyr points; if the result is greater than its Leadership characteristic it is Martyred — remove it from your Order of Battle, "
        "and every other ADEPTA SORORITAS unit that was in your Crusade army gains XP equal to the number of Saintly Rewards the martyr had. You can then select another ADEPTA SORORITAS CHARACTER (not an EPIC HERO) as your new SAINT POTENTIA.\n\n"
        "**Hymns of Battle (Lead Army in Prayer).** Once per battle, at the start of the battle round, if you have one or more ADEPTA SORORITAS CHARACTER units on the battlefield and your Crusade army was led in prayer before this battle, you can discard two Miracle dice to intone the Hymns of Battle: "
        "until the start of the next battle round all ADEPTA SORORITAS CHARACTER units gain the bonus of one Hymn you choose, or of two determined randomly (2D6, re-rolling doubles). A Battle-shocked unit loses the bonus. "
        "Hymns: 1 Add 2\" to Move and +1 to Advance and Charge rolls. 2 Attacks with an unmodified Damage of 1 allocated to the unit give +1 to armour saves. 3 Each Act of Faith adds 1 to the substituted dice (max 6), and a used Miracle dice of 6 grants a new Miracle dice. "
        "4 Improve the AP of ranged weapons by 1. 5 Improve the Attacks and Strength of melee weapons by 1. 6 Improve Leadership and Objective Control by 1.")


def build(cz):
    L, b = cz.L, cz.book
    # ── the Saint Potentia flag and its counters on Characters ──
    not_epic = L.ev_kw("Epic Hero", not_=True)
    L.unit_stat(b, "Character", "Saint Potentia", L.flag(tracking={"Saint Potentia": 1}, group="Crusade", group_order=11, order=20), show_when=[not_epic])
    L.unit_stat(b, "Character", "Trial", L.rank({t: {"traits": [{"trait": f"Ability§{t}"}]} for t in TRIALS}, group="Crusade", group_order=11, order=21, label="Trial undertaken"),
                show_when=[L.ev_stat("Saint Potentia", "✓")], show_rule="crusadeShowTrial")
    for t, (_, deeds) in TRIALS.items():
        L.ability(b, t, deeds)
    L.unit_stat(b, "Character", "Saint Points", L.num(0, mn=0, mx=10, group="Crusade", group_order=11, order=22, icons=["halo"]),
                show_when=[L.ev_stat("Saint Potentia", "✓")], show_rule="crusadeShowSaintPoints")
    L.unit_stat(b, "Character", "Martyr Points", L.num(0, mn=0, mx=12, group="Crusade", group_order=11, order=23),
                show_when=[L.ev_stat("Saint Potentia", "✓")], show_rule="crusadeShowMartyrPoints")
    L.class_rule(b, "Character", "saintPotentiaKeyword", L.rule([L.add(["{self}", "keywords", "Keywords"], "Saint Potentia")], [L.ev_stat("Saint Potentia", "✓")], order=1))
    not_narr = L.ev(["{roster}", "stats", "Play", "value"], "Narrative", not_=True)
    L.class_rule(b, "Character", "Trial complete: 10 Saint points — take the Saintly Reward and reset to 0.",
                 L.rule(None, [not_narr, L.ev(["{self}", "stats", "Saint Points", "value"], mx=9)], fail="warning", evaluate="OR", order=5))
    L.class_rule(b, "Character", "livingSaint", L.rule([L.mod(["{self}", "designation"], " (Living Saint)", append="")],
                                                       [L.NARR, L.ev_stat("Saint Potentia", "✓"), L.ev(["{self}", "tally", "Saintly Reward"], mn=5)], order=5,
                                                       note="five Saintly Rewards: the SAINT POTENTIA keyword becomes LIVING SAINT"))
    L.roster_rule(b, "One Saint Potentia only.", L.error_rule([L.ev_tracked("Saint Potentia", mx=1, who="{self}")]))
    # ── Saintly Rewards: own class, renamed, only on the Saint Potentia ──
    cat = L.catalog(b)
    for trial, (reward, _) in TRIALS.items():
        old = cat.pop(f"Crusade Honour§{trial}", None)
        if old is not None:   # the faction Tag matters: a parent's constraints.any admits only children carrying one of its tags
            cat[f"Saintly Reward§{reward}"] = {"keywords": {"Tags": [FACTION], "Keywords": [trial]}, "text": old.get("text", "")}
    rewards = [k for k in cat if k.startswith("Saintly Reward§")]
    for k in rewards:   # idempotent: the faction Tag (a Character's constraints.any needs one of the child's keywords) on every re-run
        cat[k].setdefault("keywords", {})["Tags"] = [FACTION]
        cat[k].get("rules", {}).pop("Each Saintly Reward is unique: only one in your Crusade force.", None)
    L.unique_in_roster(b, [k.split("§", 1)[1] for k in rewards])
    L.honour_class(b, "Saintly Reward", unique=True, allow_on=("Character",), allow_evals=[L.ev_stat("Saint Potentia", "✓")],
                   allow_note="Saintly Rewards: the Battle Honour gained when the Saint Potentia completes the matching Trial (10 Saint points)")
    # ── Hymns of Battle is per-battle: its text lives on the tracker ──
    cat.pop("Crusade Honour§Lead Army in Prayer", None)
    L.tracker(b, "Trials of a Living Saint", "Trials of a Living Saint", text=TEXT)
    cz.note("Saint Potentia flag + Trial/Saint/Martyr counters; 5 Saintly Rewards reclassed and renamed; Hymns text on the tracker")
