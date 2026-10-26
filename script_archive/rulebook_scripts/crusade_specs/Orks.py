"""Orks Crusade (10e codex; the 11e codex has no Crusade section): Launching the Waaagh! (Waaagh!boss, Stompin' points,
Waaagh! stages, Orky Ructions), Kustom Jobs, Bestest Bossloot. Source: Wahapedia crus10_orks."""
SLUG, ED, FACTION = "orks", "10", "Orks"
LISTS = dict(agendas=True, requisitions=True, badges=True)

BOSSLOOT = ["Da Shootiest Blasta", "Rezmekka's Redder Paint", "Da Irongob", "Frazzle Field Generator", "Da Krushin' Armour"]
STAGES = [("Stage 1: Gathering Waaagh! (0–9)", "After each battle, gain 1 Stompin’ point. You cannot suffer Orky Ructions."),
          ("Stage 2: Escalating Waaagh! (10–24)", "After each battle, gain 1 Stompin’ point and take a Ruction test (−1 if you lost). **Kustom Jobs:** you can apply one Kustom Job to an ORKS VEHICLE unit from your Order of Battle using the Kustom Job Requisition."),
          ("Stage 3: Thunderous Waaagh! (25–49)", "After each battle, gain 2 Stompin’ points and take a Ruction test (−1 if you lost). Kustom Jobs as Stage 2. **Bestest Bossloot:** your Waaagh!boss can be given one Bestest Bossloot relic."),
          ("Stage 4: All-Conquering Waaagh! (50+)", "You no longer gain Stompin’ points. After each battle take a Ruction test (−2 if you lost). Kustom Jobs as Stage 2. Your Waaagh!boss can be given a second Bestest Bossloot relic. **Massive Waaagh!:** after each battle your Crusade force gains 2 Requisition points instead of 1, and you can select one additional unit to be Marked for Greatness.")]
RUCTIONS = ("**Orky Ructions.** After a battle at Stage 2 or higher, take a Ruction test: a Leadership test on your Waaagh!boss’ Leadership with the stage modifier. Passed: nothing happens. "
            "Failed with no double: suffer a Minor Ruction or lose 10 Stompin’ points. Failed on a double: suffer a Major Ruction or lose 15 Stompin’ points.\n\n"
            "**Minor Ructions (D6):** 1 Unruly Mobs — the two lowest-XP ORKS INFANTRY units roll off: higher gains 2XP, the other takes an Out of Action test. 2 Reckless Meks — one ORKS VEHICLE unit is treated as having failed an Out of Action test; one MEK unit gains 2XP. "
            "3 Impatient Irritability — next battle, until you call the Waaagh!, ORKS units have −1 Leadership. 4 Thievin’ Gits — one CHARACTER with an Enhancement or Crusade Relic loses its use next battle; gains 3XP if you win. "
            "5 Rowdy Yoofs — your next Increase Supply Limit costs 1 more RP. 6 Confrazzled by Mind Monsters — next battle ORKS PSYKER units take Battle-shock tests each battle round; survivors gain 3XP.\n\n"
            "**Major Ructions (D6, each once per stage):** 1 Ruckus in da Ranks — one ORKS INFANTRY unit gains a Battle Scar. 2 External Combustion Test — one ORKS VEHICLE unit gains a Battle Scar. "
            "3 Last Boss Standin’ — two ORKS CHARACTER units roll off (+2 for the Waaagh!boss): higher gains 3XP, the other D3 Battle Scars. 4 Unstable Discharge — lose 10 Stompin’ points or a WEIRDBOY/WURRBOY gains a Battle Scar. "
            "5 Fizzlin’ Momentum — no Waaagh! in battle rounds 1–2 of your next battle. 6 Lost in da Warp — Requisition points to 0 (or −10 Stompin’ points if already 0).")
KJ_TAGS = {"Fortress on Wheels": ["Trukk", "Battlewagon"], "Stompamatic Pistons": ["Walker", "notKillaKans"], "Fungus-Fuel Injecta": ["Speed Freeks"]}


def build(cz):
    L, b = cz.L, cz.book
    # ── Waaagh!boss: one WARBOSS Character ──
    L.unit_stat(b, "Character", "Waaagh!boss", L.flag(tracking={"Waaagh!boss": 1}, group="Crusade", group_order=11, order=20),
                show_when=[L.ev_kw("Warboss")])
    L.class_rule(b, "Character", "waaaghBossKeyword", L.rule([L.add(["{self}", "keywords", "Keywords"], "Waaagh!boss")], [L.ev_stat("Waaagh!boss", "✓")]))
    L.roster_rule(b, "One Waaagh!boss only.", L.error_rule([L.ev_tracked("Waaagh!boss", mx=1, who="{self}")]))
    L.roster_rule(b, "Select your Waaagh!boss (a WARBOSS unit from your Order of Battle).",
                  L.rule(None, [L.ev_stat("Play", "Narrative", not_=True), L.ev_tracked("Waaagh!boss", mn=1, who="{self}")], fail="warning", evaluate="OR"))
    # ── Da Waaagh! tracker: Stompin' points → stage (roster tracked waaaghStage 0–3) ──
    stats = {"Stompin’ Points": L.num(0, mn=0, mx=200, order=1, icons=["stomp"])}
    rules = {}
    for i, (name, txt) in enumerate(STAGES):
        L.ability(b, name, txt)
        lo = [0, 10, 25, 50][i]
        hi = [9, 24, 49, None][i]
        ev = [L.ev(["{self}", "stats", "Stompin’ Points", "value"], mn=lo)] + ([L.ev(["{self}", "stats", "Stompin’ Points", "value"], mx=hi)] if hi is not None else [])
        rules[f"stage{i + 1}Ability"] = L.rule([L.add(["{self}", "traits"], f"Ability§{name}")], ev, order=1)
        if i:
            rules[f"stage{i + 1}Tracked"] = L.rule([L.mod(["{roster}", "tracked", "waaaghStage"], 1)], [L.ev(["{self}", "stats", "Stompin’ Points", "value"], mn=lo)], order=1,
                                                   note="each threshold reached adds 1 to the roster's waaaghStage (0 = Gathering … 3 = All-Conquering)")
    text = ("**Launching the Waaagh!** Select one WARBOSS unit from your Crusade force as your Waaagh!boss (tick Waaagh!boss on its card); if it leaves your Order of Battle you lose 20 Stompin’ points and must pick another. "
            "Gain Stompin’ points: +1 each time you increase your Supply Limit, +2 each battle you win, +2 each time you destroy the enemy WARLORD, +5 each time an ORKS CHARACTER reaches Legendary rank, plus the per-battle gain of your current stage.\n\n" + RUCTIONS)
    L.tracker(b, "Da Waaagh!", "Da Waaagh!", stats=stats, text=text, class_rules_=rules)
    # ── Kustom Jobs: vehicle Battle Traits from Stage 2 ──
    jobs = cz.sec.named("Kustom Jobs", upto="Crusade Relics")
    for j in jobs:
        j["tags"] = KJ_TAGS.get(j["name"], ["Vehicle"])
    L.honour_class(b, "Kustom Job", unique=False, allow_on=("Unit", "Character"), allow_evals=[L.ev_kw("Vehicle"), L.ev_tracked("waaaghStage", mn=1)],
                   allow_note="Kustom Jobs: from Stage 2 of the Waaagh!, one Kustom Job per ORKS VEHICLE unit (Kustom Job Requisition, needs a MEK on your Order of Battle)",
                   cap=1, cap_text="One Kustom Job per vehicle.")
    L.honours(b, "Kustom Job", jobs, keep_text=False)
    for tag in ("Trukk", "Battlewagon", "Walker", "Speed Freeks", "Vehicle"):
        for cls in ("Unit", "Character"):
            L.tag_grant(b, cls, tag)
    L.tag_block(b, "Unit", "Killa Kans")
    # ── Bestest Bossloot: the Waaagh!boss only, one from Stage 3, two from Stage 4 ──
    L.reclass(b, "Crusade Honour§", "Bestest Bossloot", BOSSLOOT, patch={"keywords": {"Tags": [], "Keywords": ["Relic"]}})
    L.honour_class(b, "Bestest Bossloot", unique=True, allow_on=("Character",), allow_evals=[L.ev_stat("Waaagh!boss", "✓"), L.ev_tracked("waaaghStage", mn=2)],
                   allow_note="Bestest Bossloot: unique Crusade Relics for your Waaagh!boss — one from Stage 3 (Thunderous), a second from Stage 4 (All-Conquering); Bestest Bossloot Requisition, needs a MEK")
    L.class_rule(b, "Character", "Bestest Bossloot: one relic at Stage 3, two at Stage 4.",
                 L.rule(None, [L.ev(["{self}", "tally", "Bestest Bossloot"], mx=1), L.ev_tracked("waaaghStage", mn=3)], fail="error", evaluate="OR"))
    L.class_rule(b, "Character", "No more than two Bestest Bossloot relics.", L.error_rule([L.ev(["{self}", "tally", "Bestest Bossloot"], mx=2)]))
    # 'Elmet Rack came from BSData (filed under the Bosspole relic there); it reads as a vehicle Kustom Job, keep it as one
    L.reclass(b, "Crusade Honour§", "Kustom Job", ["'Elmet Rack"], patch={"keywords": {"Tags": ["Vehicle"], "Keywords": []}})
    cz.note(f"Waaagh!boss flag; Da Waaagh! tracker ({len(STAGES)} stages); Kustom Jobs {len(jobs)}: " + ", ".join(j["name"] for j in jobs) + "; Bossloot reclassed")
