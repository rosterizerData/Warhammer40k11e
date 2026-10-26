"""Space Wolves Crusade supplement (10e codex): three Oathsworn Campaigns, Deeds of Making (Honour Points), Lone Wolves,
Wolf Packs, Agendas, Requisitions, Badges. Source: crus10_space-marines (powered by Wahapedia)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _sm_common as C
SLUG, ED, FACTION = "space-marines", "10", "Space Wolves"
LISTS = dict(agendas=False, requisitions=False, badges=False)

GATES = {"Savage Orator": lambda L: [L.ev_kw("Wolf Priest")], "Death Cheat": lambda L: [L.ev_kw("Wolf Priest")], "Storm Speaker": lambda L: [L.ev_kw("Psyker")],
         "Scar Struck": lambda L: [L.ev(["{self}", "tally", "Battle Scar"], mn=1)]}
LONE_WOLF_SCARS = ["Pack of One", "An Honourable End", "Vengeance Before Death"]
LONE_TEXT = ("**Lone Wolves.** When a SPACE WOLVES INFANTRY or MOUNTED unit (not a CHARACTER) of Blooded rank or higher suffers a Devastating Blow, you can instead remove it from "
             "your Order of Battle and replace it with one WOLF GUARD BATTLE LEADER model ticked as a Lone Wolf. It keeps the unit's XP, selects one Battle Honour per honour the "
             "unit had and one Lone Wolf Battle Scar per scar it had; it has Lone Operative instead of Leader and the Oath of Vengeance ability. It subtracts 1 from Out of Action "
             "tests, every failure adds a Lone Wolf Battle Scar (never a Devastating Blow, never removable), and a fourth scar is a glorious death.")
PACKS_TEXT = ("**Wolf Guard Headtakers** split into two Crusade cards (the Space Marines and their Hunting Wolves, bonded, always fielded together; the wolves have a points value of 0). "
              "**Wolf Packs:** WOLF GUARD HEADTAKERS can take any Battle Trait a BLADEGUARD VETERAN SQUAD can, and WOLF GUARD TERMINATORS any a TERMINATOR SQUAD can.")
BOASTS = ("**Audacious Boasts** (select one SPACE WOLVES CHARACTER and one or more Boasts; all achieved → XP equal to the number of Boasts, 4+XP → 4 Honour points): "
          "Go for the Throat (charges first each Charge phase); Never Back Down from a Fight (never Falls Back); Tear Through Their Armour (destroys a VEHICLE); Slay the Beast (destroys a MONSTER); "
          "Bring Back Their Heads (destroys a CHARACTER); Cut Down the Tyrant (destroys the WARLORD or an EPIC HERO); Leave Behind a Trail of Corpses (20+ models); Break Through Their Lines "
          "(ends wholly in the enemy deployment zone); Claim the Prize (ends within range of an objective you control outside your deployment zone); Without a Scratch (not destroyed, not Below Half-strength). "
          "A destroyed unit counts towards one Boast only.")


def build(cz):
    L, b = cz.L, cz.book
    n = C.NTH[b]
    new = C.agendas_dedupe(b, [a["name"] for a in C.SEC.named("Agendas", nth=n) if a["text"]], FACTION)
    reqs = C.reqs_nth(n)
    L.requisitions(b, reqs)
    L.badges(b, C.badges_nth(n))
    # ── Deeds of Making: 12 sagas as Promotions ──
    deeds = C.costed(C.SEC.named("Deeds of Making"))
    for d in deeds:
        C.promotion(b, d["name"], d["cost"], d["text"], evals=GATES.get(d["name"], lambda L: [])(L),
                    note="Deeds of Making: after an Oathsworn Campaign, spend Honour points on a saga for a CHARACTER (one per CHARACTER, each unique)")
    # ── Lone Wolves: a Wolf Guard Battle Leader ticked as Lone Wolf ──
    L.unit_stat(b, "Character", "Lone Wolf", L.flag(tracking={"Lone Wolves": 1}, group="Crusade", group_order=11, order=20), show_when=[L.ev_kw("Battle Leader")])
    L.ability(b, "Oath of Vengeance", "Each time this model makes a melee attack, you can re-roll the Hit roll. If the target of that attack is a MONSTER or VEHICLE unit, you can re-roll the Wound roll as well.")
    L.ability(b, "Lone Wolf", LONE_TEXT)
    L.class_rule(b, "Character", "loneWolf", L.rule([L.add(["{self}", "keywords", "Keywords"], "Lone Wolf"), L.add(["{self}", "constraints", "any"], "Lone Wolf"),
                                                     L.add(["{self}", "traits"], "Ability§Oath of Vengeance"), L.add(["{self}", "traits"], "Ability§Lone Wolf"),
                                                     L.rem(["{self}", "traits"], "Ability§Leader"), L.add(["{self}", "traits"], "Ability§Lone Operative")],
                                                    [L.ev_stat("Lone Wolf", "✓")], note="Lone Wolf: Lone Operative instead of Leader, Oath of Vengeance, Lone Wolf Battle Scars"))
    L.class_rule(b, "Character", "A Lone Wolf cannot survive a fourth Lone Wolf Battle Scar.", L.rule(None, [L.ev_stat("Play", "Narrative", who="{roster}", not_=True), L.ev_stat("Lone Wolf", "-"), L.ev(["{self}", "tally", "Battle Scar"], mx=3)], fail="error", evaluate="OR"))
    for s in LONE_WOLF_SCARS:
        L.patch_asset(b, f"Battle Scar§{s}", {"keywords": {"Tags": ["Lone Wolf"], "Keywords": ["Lone Wolf Battle Scar"]}, "stats": {"Crusade Pts": {"value": 0}}})
        L.catalog(b)[f"Battle Scar§{s}"]["keywords"]["Tags"] = ["Lone Wolf"]
    # ── Oathsworn Campaigns ──
    C.campaign(b, "Worthy of a Saga", C.intro_of("Worthy of a Saga"), C.bonus(9), C.single_req(9), extra_text=PACKS_TEXT)
    C.campaign(b, "Glory Seekers", C.intro_of("Glory Seekers"), C.bonus(10), C.single_req(10), extra_text=BOASTS)
    C.campaign(b, "Hunters Unleashed", C.intro_of("Hunters Unleashed"), C.bonus(11), C.single_req(11))
    cz.note(f"agendas new {new}; requisitions {len(reqs)}; badges 3; Deeds of Making {len(deeds)} promotions; Lone Wolf flag + 3 scars; campaigns 3")
