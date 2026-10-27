"""Imperial Knights Crusade (10e codex; the 11e site carries the same text): Pilot and Knight — Sworn Alignment, Masteries
with three Levels of Honour fed by Chivalric points, Chivalric Quests, Burdens. Pilots live as stats on the Knight.
Source: Wahapedia crus10_imperial-knights. The Knight datasheets sit in the Imperium hub, so the pilot stats are gated by
the Imperial Knights Faction keyword."""
SLUG, ED, FACTION = "imperial-knights", "10", "Imperial Knights"
LISTS = dict(agendas=True, requisitions=True, badges=True)

ALIGN = ["Questor Imperialis", "Questor Mechanicus", "Freeblade"]
MASTERIES = ["Mastery of Obduracy", "Mastery of Clarion", "Mastery of Tuition", "Mastery of Ambush", "Mastery of Condemnation",
             "Mastery of Joust", "Mastery of Mechanisms", "Mastery of Execution"]
TIERS = [("Aspiring", 1, 3), ("Esteemed", 4, 6), ("Virtuous", 7, None)]
QUESTS = ["To Strike Down the Unclean Behemoths", "To Raise High the Pennants of Victory", "To Stamp Out the Champions of Dishonour", "To Secure the Realm"]
BURDENS = ["Desperate For Redemption", "Stain of Dishonour", "Bonded In Shame"]
IK = lambda L: L.ev_kw("Imperial Knights", field="Faction")


def mastery_tiers(sec, name):
    """[(tier ability name, text)] from the Mastery block: three UPPERCASE ability names each followed by its text"""
    blk = [l for l in sec.block(name) if l.strip() and not l.startswith("|")]
    out = []
    for i, l in enumerate(blk):
        if l.isupper() and i + 1 < len(blk):
            out.append((l.strip().title().replace("’S", "’s").replace("Of ", "of ").replace("The ", "the ").replace("By ", "by ").replace("A Duty", "A Duty"), blk[i + 1].strip().rstrip("|").strip()))
    return out[:3]


def quest_text(sec, name):
    blk = [l for l in sec.block(name) if l.strip() and not l.startswith("|")]
    return blk[1] if len(blk) > 1 else blk[0]


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    cat = L.catalog(b)
    G = dict(group="Pilot", group_order=11)
    # ── pilot stats on every Imperial Knights unit (not Epic Heroes): alignment, mastery, chivalric points ──
    align_track = {a: {"pilot" + a.split()[-1]: 1} for a in ALIGN}
    mastery_track = {m: {"mastery" + m.split()[-1]: 1} for m in MASTERIES}
    for cls in ("Unit", "Character"):
        show = [IK(L), L.ev_kw("Epic Hero", not_=True)]
        L.unit_stat(b, cls, "Sworn Alignment", L.rank(ALIGN, tracking=align_track, order=20, **G), show_when=show)
        L.unit_stat(b, cls, "Mastery", L.rank(MASTERIES, tracking=mastery_track, order=21, **G), show_when=show)
        L.unit_stat(b, cls, "Chivalric Points", L.num(0, mn=0, mx=12, order=22, **G), show_when=show)
        # a Mastery adds 1 Crusade point
        L.class_rule(b, cls, "masteryCrusadePt", L.rule([L.mod(["{self}", "stats", "Crusade Pts", "value"], 1)], [L.NARR, L.ev_stat("Mastery", "-", not_=True)],
                                                      note="Add 1 to an IMPERIAL KNIGHTS unit's Crusade points while its pilot has a Mastery"))
        # tier abilities: the pilot's Level of Honour (1–3 / 4–6 / 7+) selects which tier text applies
        for m in MASTERIES:
            tiers = mastery_tiers(sec, m)
            for (tier, lo, hi), (aname, atext) in zip(TIERS, tiers):
                key = f"{m} — {aname} ({tier})"
                L.ability(b, key, atext)
                evs = [L.NARR, L.ev_stat("Mastery", m), L.ev(["{self}", "stats", "Chivalric Points", "value"], mn=lo)]
                if hi is not None:
                    evs.append(L.ev(["{self}", "stats", "Chivalric Points", "value"], mx=hi))
                L.class_rule(b, cls, f"tier{m.split()[-1]}{tier}", L.rule([L.add(["{self}", "traits"], f"Ability§{key}")], evs))
        # gates
        MATCHED = L.ev_stat("Play", "Narrative", who="{roster}", not_=True)   # validations only bite in Narrative play
        L.class_rule(b, cls, "Mastery of Clarion: pilot of a TITANIC unit only.", L.rule(None, [MATCHED, L.ev_stat("Mastery", "Mastery of Clarion", not_=True), L.ev_kw("Titanic")], fail="error", evaluate="OR"))
        L.class_rule(b, cls, "Mastery of Joust: Questor Imperialis pilots only.", L.rule(None, [MATCHED, L.ev_stat("Mastery", "Mastery of Joust", not_=True), L.ev_stat("Sworn Alignment", "Questor Imperialis")], fail="error", evaluate="OR"))
        L.class_rule(b, cls, "Mastery of Mechanisms: Questor Mechanicus pilots only.", L.rule(None, [MATCHED, L.ev_stat("Mastery", "Mastery of Mechanisms", not_=True), L.ev_stat("Sworn Alignment", "Questor Mechanicus")], fail="error", evaluate="OR"))
        L.class_rule(b, cls, "Mastery of Execution: Freeblade pilots only.", L.rule(None, [MATCHED, L.ev_stat("Mastery", "Mastery of Execution", not_=True), L.ev_stat("Sworn Alignment", "Freeblade")], fail="error", evaluate="OR"))
        L.class_rule(b, cls, "A Mastery needs Chivalric points (allocate at least 1).", L.rule(None, [MATCHED, L.ev_stat("Mastery", "-"), L.ev(["{self}", "stats", "Chivalric Points", "value"], mn=1)], fail="error", evaluate="OR"))
        L.class_rule(b, cls, "An ARMIGER pilot cannot be assigned more than 6 Chivalric points.", L.rule(None, [MATCHED, L.ev_kw("Armiger", not_=True), L.ev(["{self}", "stats", "Chivalric Points", "value"], mx=6)], fail="error", evaluate="OR"))
        # Burdens are Battle Scars for Freeblade pilots: grant the Freeblade tag from the alignment
        L.class_rule(b, cls, "crusadeTagFreeblade", L.rule([L.add(["{self}", "constraints", "any"], "Freeblade")], [L.NARR, L.ev_stat("Sworn Alignment", "Freeblade")],
                                                         note="Crusade: Freeblade pilots may bear the Burdens"))
    # roster rules: alignments cannot mix; each Mastery once per force
    NOT_NARR = L.ev_stat("Play", "Narrative", not_=True)
    L.roster_rule(b, "You cannot include Questor Imperialis and Questor Mechanicus pilots in the same Crusade army.",
                  L.rule(None, [NOT_NARR, L.ev_tracked("pilotImperialis", mx=0, who="{self}"), L.ev_tracked("pilotMechanicus", mx=0, who="{self}")], fail="error", evaluate="OR"))
    for m in MASTERIES:
        L.roster_rule(b, f"Only one pilot in your Crusade force can have the {m}.", L.rule(None, [NOT_NARR, L.ev_tracked("mastery" + m.split()[-1], mx=1, who="{self}")], fail="error", evaluate="OR"))
    # ── Burdens: Battle Scars (Freeblade), replacing the imported honours; drop the flat mastery honours ──
    L.reclass(b, "Crusade Honour§", "Battle Scar", BURDENS, patch={"keywords": {"Tags": ["Freeblade"], "Keywords": ["Burden"]}})
    L.del_assets(b, [f"Crusade Honour§{m.replace('Mastery', 'Master')}" for m in MASTERIES] + ["Crusade Honour§Master of the Clarion", "Crusade Honour§Master of the Joust"])
    # ── Chivalric Quest tracker ──
    qstats = {"Quest": L.rank(QUESTS, order=1, label="Chivalric Quest"),
              "Battles fought": L.num(0, mn=0, mx=3, order=2),
              "Tally": L.num(0, mn=0, mx=40, order=3),
              "Dishonoured": L.flag(order=4)}
    qrules = {}
    for q in QUESTS:
        L.ability(b, q, quest_text(sec, q))
        qrules["quest" + q.split()[-1]] = L.rule([L.add(["{self}", "traits"], f"Ability§{q}")], [L.ev_stat("Quest", q)])
    qrules["Three battles fought: consult the Tally Rewards and allocate the Chivalric points (fewer than four tallies: Dishonoured)."] = L.rule(None, [L.ev(["{self}", "stats", "Battles fought", "value"], mx=2)], fail="info", order=5)
    text = ("**Chivalric Quests.** When mustering, if you have no active Quest and your WARLORD is an IMPERIAL KNIGHTS model, swear your Knights to one of the four Quests and keep its tally for your next three battles. "
            "After three battles consult the Tally Rewards of the Quest (4–6 tally marks: 1 Chivalric point; 7–10: 2 Chivalric points; 11+: 3 Chivalric points; fewer than 4: Dishonoured) and allocate the Chivalric points to your pilots in the Update Crusade Cards step. "
            "Fewer than four tally marks, or abandoning a Quest, makes your Crusade force **Dishonoured**: you cannot swear a new Quest until you complete the Death Before Dishonour Agenda.\n\n"
            "**Pilots.** Every IMPERIAL KNIGHTS model (not EPIC HEROES) has a pilot with a Sworn Alignment; Questor Imperialis and Questor Mechanicus pilots never fight in the same army. "
            "The first time a pilot is allocated Chivalric points, select a Mastery no other pilot has (Clarion: TITANIC only; Joust: Questor Imperialis; Mechanisms: Questor Mechanicus; Execution: Freeblade). "
            "Levels of Honour: Aspiring 1–3, Esteemed 4–6, Virtuous 7+ Chivalric points; an ARMIGER pilot holds at most 6 points. A pilot with a Mastery adds 1 to the unit's Crusade points. "
            "A Knight without a pilot is vacant and cannot be fielded; an unseated pilot can be assigned to a new or vacant Knight (a Virtuous pilot or one with Mastery of the Clarion never to an ARMIGER).")
    L.tracker(b, "Chivalric Quest", "Chivalric Quest", stats=qstats, text=text, class_rules_=qrules)
    cz.note("pilot stats (alignment, mastery, chivalric points, 24 tier abilities) on Unit+Character; Chivalric Quest tracker; Burdens → Battle Scars; 8 flat mastery honours deleted")
