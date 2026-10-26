"""Blood Angels Crusade supplement (10e codex): three Oathsworn Campaigns, Angels Ascendant (Honour Points), The Flaw
(Death Company), Agendas, Requisitions, Badges. Source: crus10_space-marines (powered by Wahapedia)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _sm_common as C
SLUG, ED, FACTION = "space-marines", "10", "Blood Angels"
LISTS = dict(agendas=False, requisitions=False, badges=False)

ASCENDANT = {"Shield of Baal": (20, lambda L: [L.ev_kw("Captain")]),
             "Sanguinary High Priest": (20, lambda L: [L.ev_kw("Sanguinary Priest")]),
             "Custodian of the Lost": (20, lambda L: [L.ev_kw("Chaplain")])}
DC_SCARS = [("Consumed by Rage", "Each time this unit makes a Charge move, until the end of the turn, add 1 to the Attacks characteristic of melee weapons equipped by DEATH COMPANY models in this unit.\n\nThis unit can never Fall Back, even when within 12\" of one or more friendly CHAPLAINS."),
            ("Visions of Bloodshed", "Unless this unit starts the battle embarked within a TRANSPORT, all DEATH COMPANY models in this unit have the Scouts 6\" ability.\n\nAt the start of every Command phase, this unit must take a Battle-shock test."),
            ("Inured to Agony", "DEATH COMPANY models in this unit have the Feel No Pain 5+ ability.\n\nThis unit fails Out of Action tests on rolls of 1-3.")]
FLAW_TEXT = ("**The Flaw.** DEATH COMPANY units cannot gain XP, ranks or Battle Honours. At the end of every battle each DEATH COMPANY unit in your Crusade army takes an Out of Action "
             "test even if it survived (a destroyed one fails on 1-2); each failure gives it a Death Company Battle Scar instead of a Devastating Blow. These scars cannot be "
             "removed, do not reduce Crusade points, and a fourth one removes the unit from your Order of Battle. While a DEATH COMPANY CHARACTER leads a DEATH COMPANY INFANTRY "
             "unit, only the scars of the unit with more apply.")


def build(cz):
    L, b = cz.L, cz.book
    n = C.NTH[b]
    new = C.agendas_dedupe(b, [a["name"] for a in C.SEC.named("Agendas", nth=n) if a["text"]], FACTION)
    reqs = C.reqs_nth(n)
    L.requisitions(b, reqs)
    L.badges(b, C.badges_nth(n))
    # ── Angels Ascendant ──
    aa = {e["name"]: e for e in C.costed(C.SEC.named("Angels Ascendant"))}
    for name, (cost, evf) in ASCENDANT.items():
        C.promotion(b, name, cost, aa[name]["text"], evals=evf(L), note="Angels Ascendant: after an Oathsworn Campaign, spend Honour points to promote a CHARACTER (one such honour per unit, each unique)")
        L.del_assets(b, [f"Crusade Honour§{name}"])
    # Exemplars of the Host: a Battle-hardened JUMP PACK unit (not CHARACTER, not DEATH COMPANY) becomes Sanguinary Guard for 5 Honour points
    swap = L.catalog("Space_Marines")["Promotion§1st Company Promotion"]["rules"]["changeType"]
    L.put_asset(b, "Promotion§Exemplars of the Host", {"rules": {"changeType": swap}, "text": aa["Exemplars of the Host"]["text"],
                                                       "stats": {"Honour Points": {"value": 5}, "Selection": {"ranks": {"Sanguinary Guard": {"order": 1, "term": "Infantry/Mounted§Sanguinary Guard"}}}}}, keep_text=False)
    L.class_rule(b, "Infantry/Mounted", "allowExemplarsoftheHost",
                 L.rule([L.add(["{self}", "allowed", "items"], "Promotion§Exemplars of the Host")],
                        [L.NARR, L.ev_kw("Jump Pack"), L.ev_kw("Death Company", not_=True), L.ev(["{self}", "stats", "Experience", "value"], mn=16)],
                        note="Angels Ascendant: a JUMP PACK unit of Battle-hardened rank or higher can be promoted to the Sanguinary Guard"))
    # ── The Flaw: Death Company never gain XP; Death Company Battle Scars (max 3, no Crusade point loss) ──
    for cls in ("Infantry/Mounted", "Character"):
        L.no_xp(b, cls, "Death Company", label="DEATH COMPANY")
        L.tag_grant(b, cls, "Death Company")
        L.class_rule(b, cls, "No more than three Death Company Battle Scars.", L.rule(None, [L.ev_stat("Play", "Narrative", who="{roster}", not_=True), L.ev_kw("Death Company", not_=True), L.ev(["{self}", "tally", "Battle Scar"], mx=3)], fail="error", evaluate="OR"))
    for name, text in DC_SCARS:
        L.put_asset(b, f"Battle Scar§{name}", {"keywords": {"Tags": ["Death Company"], "Keywords": ["Death Company Battle Scar"]}, "stats": {"Crusade Pts": {"value": 0}}, "text": text}, keep_text=False)
    L.ability(b, "The Flaw", FLAW_TEXT)
    for cls in ("Infantry/Mounted", "Character"):
        L.class_rule(b, cls, "theFlaw", L.rule([L.add(["{self}", "traits"], "Ability§The Flaw")], [L.NARR, L.ev_kw("Death Company")]))
    # ── Oathsworn Campaigns ──
    C.campaign(b, "Legacy of the Black Rage", C.intro_of("Legacy of the Black Rage"), C.bonus(6), C.single_req(6))
    C.campaign(b, "Angels of Deliverance", C.intro_of("Angels of Deliverance"), C.bonus(7), C.single_req(7))
    C.campaign(b, "Blade of Sanguinius", C.intro_of("Blade of Sanguinius"), C.bonus(8), C.single_req(8))
    cz.note(f"agendas new {new}; requisitions {len(reqs)}; badges 3; Angels Ascendant 3 promotions + Exemplars of the Host swap; The Flaw (no-XP + 3 scars); campaigns 3")
