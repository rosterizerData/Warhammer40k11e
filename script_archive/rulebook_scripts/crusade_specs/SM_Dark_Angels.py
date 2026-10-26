"""Dark Angels Crusade supplement (10e codex, carried on the 11e site inside the Space Marines section): three Oathsworn
Campaigns, Inner Circle Advancement (Honour Points), Agendas, Requisitions, Badges. Source: crus10_space-marines (powered by Wahapedia)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _sm_common as C
SLUG, ED, FACTION = "space-marines", "10", "Dark Angels"
LISTS = dict(agendas=False, requisitions=False, badges=False)

INNER_CIRCLE = {  # name → (cost, keyword evals)
    "Master of the Deathwing": (20, lambda L: [L.ev_kw("Terminator"), L.ev_kw("Captain")]),
    "Master of the Ravenwing": (20, lambda L: [L.ev_kw("Ravenwing")]),
    "Keeper of the Unseen Ritual": (20, lambda L: [L.ev_kw("Captain")]),
    "Master of Watchers": (15, lambda L: [])}
NAMED = {"Belial": "Master of the Deathwing", "Sammael": "Master of the Ravenwing", "Lazarus": "Keeper of the Unseen Ritual"}
HUNT_TEXT = ("You can only embark on this Oathsworn Campaign if your Crusade force has already completed a Secrets of the Unforgiven Oathsworn Campaign and at least one "
             "other Dark Angels or Adeptus Astartes Oathsworn Campaign. Its three Bonus Agendas must be completed in order, one per battle (Battle 1: A Trail Uncovered, "
             "Battle 2: Pursuit Across Worlds, Battle 3: Capture the Fallen); failing one ends the campaign as the trail is lost (Penitent’s Hope lets you re-attempt "
             "Capture the Fallen). After a Hunt the Fallen campaign you cannot start another until two other Oathsworn Campaigns are complete.")


def build(cz):
    L, b = cz.L, cz.book
    n = C.NTH[b]
    new = C.agendas_dedupe(b, [a["name"] for a in C.SEC.named("Agendas", nth=n) if a["text"]], FACTION)
    reqs = C.reqs_nth(n)
    L.requisitions(b, reqs)
    L.badges(b, C.badges_nth(n))
    # ── Inner Circle Advancement: Promotions in the Honour Points economy; the Crusade Honour copies go ──
    ic = {e["name"]: e for e in C.costed(C.SEC.named("Inner Circle Advancement"))}
    for name, (cost, evf) in INNER_CIRCLE.items():
        C.promotion(b, name, cost, ic[name]["text"], evals=evf(L), note="Inner Circle Advancement: after an Oathsworn Campaign, spend Honour points to promote a CHARACTER (one such honour per CHARACTER, each unique)")
        L.del_assets(b, [f"Crusade Honour§{name}"])
    # named characters hold their seats: they gain the ability for free and nobody else may hold it
    for who, seat in NAMED.items():
        L.class_rule(b, "Character", f"innerCircle{who}", L.rule([L.add(["{self}", "traits"], f"Promotion Ability§{seat}")], [L.NARR, L.ev(["{self}", "designation"], who)],
                                                                  order=1, note=f"{who} automatically holds the {seat} honour (early, so the roster's one-holder check sees it)"))
        L.asset_rule(b, f"Promotion§{seat}", f"{who} already holds this seat.", L.error_rule([L.ev(["{roster}", "tally", who], mx=0)]))
    # ── Oathsworn Campaigns ──
    C.campaign(b, "Secrets of the Unforgiven", C.intro_of("Secrets Of The Unforgiven"), C.bonus(4), C.single_req(4))
    C.campaign(b, "For the Lion!", C.intro_of("For The Lion!"), C.bonus(5), C.single_req(5))
    hunt = C.SEC.named("Hunt The Fallen")
    hunt_entries = [{"name": nm, "text": e["text"]} for nm, e in zip(["A Trail Uncovered", "Pursuit Across Worlds", "Capture the Fallen"], hunt)]
    C.campaign(b, "Hunt the Fallen", C.intro_of("Hunt The Fallen"), hunt_entries,
               per_battle={1: ["A Trail Uncovered"], 2: ["Pursuit Across Worlds"], 3: ["Capture the Fallen"]}, extra_text=HUNT_TEXT)
    cz.note(f"agendas new {new}; requisitions {len(reqs)}; badges 3; Inner Circle 4 promotions (Belial/Sammael/Lazarus seats); campaigns 3")
