"""Black Templars Crusade supplement (10e codex): the Honouring the Creed Oathsworn Campaign (oaths of Deed, Foe, Passion,
Condition), Relic Fragments and Reclaimed Relics, Anoint a Champion with the Champion's Virtues, Agendas, Requisitions,
Badges. Source: crus10_space-marines (powered by Wahapedia)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _sm_common as C
SLUG, ED, FACTION = "space-marines", "10", "Black Templars"
LISTS = dict(agendas=False, requisitions=False, badges=False)

VIRTUES = ["Master of Arms", "Epitome of Piety", "Instrument of the Emperor", "Adaptable Executioner", "Inspirational Fighter", "Front-line Crusader"]
DEEDS = [("…bring glory to His name…", "Completed if you are the victor. Reward: 1 Relic Fragment or 1XP for your WARLORD."),
         ("…shatter the holdings of the enemy…", "Completed if you control one or more objective markers in your opponent’s deployment zone. Reward: 2RP or 1 Relic Fragment."),
         ("…reclaim our holy relics…", "Completed if you control more objective markers than your opponent. Reward: 2 Relic Fragments.")]
FOES = [("…and lay low the mightiest tyrants…", "At the start of the battle select CHARACTER or WARLORD; completed if an ADEPTUS ASTARTES unit from your Crusade army destroyed an enemy unit with that keyword. Reward: CHARACTER 1 Honour point; WARLORD 2 Honour points and 1 Relic Fragment."),
        ("…and strike down the most dire foes…", "At the start of the battle select MONSTER, VEHICLE or TITANIC; completed if an ADEPTUS ASTARTES unit from your Crusade army destroyed an enemy unit with that keyword. Reward: MONSTER/VEHICLE 1 Honour point; TITANIC 2 Honour points and 1 Relic Fragment."),
        ("…and slaughter the faithless…", "At the start of the battle select 3 or more units or 6 or more units; completed if that many enemy units were destroyed by ADEPTUS ASTARTES units from your Crusade army. Reward: 3+ → 1 Honour point; 6+ → 2 Honour points and 1 Relic Fragment.")]
PASSIONS = [("…whilst bearing our artefacts proudly…", "Completed if one or more ANCIENT or RELIC BEARER units from your Crusade army are wholly within 6\" of the centre of the battlefield. Reward: 1 Honour point."),
            ("…ere our blades strike at their heart…", "Completed if one or more CHARACTER units from your Crusade army are wholly within your opponent’s deployment zone. Reward: 1 Honour point."),
            ("…as righteousness courses through us…", "Completed if one or more enemy units were destroyed by a CHAPLAIN or JUDICIAR unit from your Crusade army. Reward: 1 Honour point.")]
CONDITIONS = [("…yet with never a backwards step.", "Completed if no ADEPTUS ASTARTES units from your Crusade army made a Fall Back move. Reward: 1 Honour point."),
              ("…in order to keep His domain sanctified.", "Completed if no enemy units are wholly within your deployment zone. Reward: 1 Honour point."),
              ("…with the strength to crusade anew.", "Completed if half or more (rounding down) of the units from your Crusade army are on the battlefield. Reward: 1 Honour point.")]
OATH_TEXT = ("**Oaths of Crusade** (the Bonus Agenda of every battle in this campaign): select one Deed and one Foe, optionally one Passion and one Condition (choose, or roll a D6 "
             "on each table; the Devotional Codicil allows two Passions and two Conditions). The oath reads: ‘In the name of the immortal God-Emperor, I hereby vow to [Deed] [Foe] "
             "[Passion] [Condition].’ At the end of the battle, if every part was completed you gain all the listed rewards (+1 Honour point if you rolled the parts); otherwise nothing. "
             "Add one Oath of Crusade to this campaign per battle and tick it when completed.")
CHAMPION_TEXT = ("**Anoint a Champion.** When your Black Templars Crusade force starts an Oathsworn Campaign you can add one EMPEROR’S CHAMPION to your Order of Battle; its points do not count "
                 "towards Supply Used (but do count in any Crusade army) and it leaves when the campaign ends. It cannot earn XP or Battle Honours: at the end of each battle it gains one "
                 "Champion’s Virtue (choose, or roll two D6 and gain both). Each enemy CHARACTER it destroys earns 1 Honour point. When it is destroyed, take its Out of Action test at once: "
                 "if failed it is slain and removed; place a Sacred Wargear objective marker where it fell and use the Recovering Sacred Wargear Agenda (the player controlling the marker at "
                 "the end of the battle gives one unit within range 3XP; if you do not control it you lose 5 Honour points). You cannot anoint another Champion until a new Oathsworn Campaign.")
RELIC_TEXT = ("**Relic Bearers.** After an Oathsworn Campaign ends, spend Relic Fragments on Reclaimed Relics for BLACK TEMPLARS INFANTRY units of Blooded rank or higher (not CHARACTERS): one per "
              "unit, each unique; the bearer gains the RELIC BEARER keyword. Track Relic Fragments gained on this card; the Reclaimed Relics on your units spend them.")


def build(cz):
    L, b = cz.L, cz.book
    n = C.NTH[b]
    new = C.agendas_dedupe(b, [a["name"] for a in C.SEC.named("Agendas", nth=n) if a["text"]], FACTION)
    reqs = C.reqs_nth(n)
    L.requisitions(b, reqs)
    L.badges(b, C.badges_nth(n))
    # ── Relic Fragments ledger (P1 + P3) ──
    stats = {"Relic Fragments gained": L.num(0, mn=0, mx=99, order=1, icons=["shield"]),
             "Relic Fragments remaining": L.num(0, mn=-99, mx=99, dynamic=False, order=2)}
    rules = {"relicFragmentsRemaining": L.rule([L.set_(["{self}", "stats", "Relic Fragments remaining", "value"], ["{this}", "evals", "0", "result", "integer"])],
                                               [L.ev(["{self}", "stats", "Relic Fragments gained", "value"], equation={"operator": "T-O", "value": ["{roster}", "tracked", "Relic Fragments"]})],
                                               order=1, note="gained minus the Relic Fragments spent on Reclaimed Relics"),
             "Your Reclaimed Relics cost more Relic Fragments than your Crusade force has gained.": L.rule(None, [L.ev(["{self}", "stats", "Relic Fragments remaining", "value"], mn=0)], fail="error", order=5)}
    L.tracker(b, "Black Templars Crusade", "Relic Fragments", stats=stats, text=RELIC_TEXT + "\n\n" + CHAMPION_TEXT, class_rules_=rules)
    # ── Reclaimed Relics: own class with a tracked Relic Fragments cost ──
    L.honour_class(b, "Reclaimed Relic", unique=True, allow_on=("Infantry/Mounted",),
                   stats={"Relic Fragments": {"group": "Cost", "groupOrder": -1, "icons": ["shield"], "statType": "numeric", "tracked": True, "value": 0, "visibility": "always"}},
                   allow_evals=[L.ev_kw("Infantry"), L.ev(["{self}", "stats", "Experience", "value"], mn=6)],
                   allow_note="Relic Bearers: a BLACK TEMPLARS INFANTRY unit of Blooded rank or higher may bear one Reclaimed Relic", cap=1, cap_text="One Reclaimed Relic per unit.")
    relics = C.costed(C.SEC.named("Relic Bearers"))
    for r in relics:
        L.put_asset(b, f"Reclaimed Relic§{r['name']}", {"stats": {"Relic Fragments": {"value": r["cost"]}}, "text": r["text"],
                                                        "rules": {"relicBearer": L.rule([L.add(["{parent}", "keywords", "Keywords"], "Relic Bearer")], [])}}, keep_text=False)
    L.unique_in_roster(b, [r["name"] for r in relics])
    # ── Champion's Virtues: the Emperor's Champion only; it never gains XP, one Virtue per battle ──
    L.reclass(b, "Crusade Honour§", "Champion's Virtue", VIRTUES, patch={"keywords": {"Tags": [], "Keywords": []}})
    L.honour_class(b, "Champion's Virtue", unique=True, allow_on=("Character",), allow_evals=[L.ev_kw("Emperor’s Champion")],
                   allow_note="Anoint a Champion: the EMPEROR’S CHAMPION gains one Champion’s Virtue at the end of each battle instead of XP")
    L.class_rule(b, "Character", "emperorsChampionCrusade", L.rule([L.set_(["{self}", "stats", "Experience", "visibility"], "hidden"), L.set_(["{self}", "stats", "Battle Honour", "max"], 6)],
                                                                   [L.NARR, L.ev_kw("Emperor’s Champion")], note="the Emperor’s Champion cannot earn XP; its Battle Honours are its Champion’s Virtues"))
    # Black Templars have no Chapter Master
    L.class_rule(b, "Character", "noChapterMaster", L.rule([L.add(["{self}", "disallowed", "items"], "Promotion§Chapter Master")], [L.NARR], note="Black Templars have no Chapter Master seat"))
    # ── Honouring the Creed: the campaign and its per-battle Oaths ──
    oath_stats = {"Deed": L.rank([d for d, _ in DEEDS], order=1), "Foe": L.rank([f for f, _ in FOES], order=2), "Passion": L.rank([p for p, _ in PASSIONS], order=3),
                  "Condition": L.rank([c for c, _ in CONDITIONS], order=4), "Completed": L.flag(order=5)}
    oath_rules = {"oathDone": L.rule([L.mod(["{self}", "designation"], " ✓", append="")], [L.ev_stat("Completed", "✓")])}
    oath_text = OATH_TEXT + "\n\n**Deeds:**\n" + "\n".join(f"- {d} {t}" for d, t in DEEDS) + "\n\n**Foes:**\n" + "\n".join(f"- {d} {t}" for d, t in FOES) + \
        "\n\n**Passions:**\n" + "\n".join(f"- {d} {t}" for d, t in PASSIONS) + "\n\n**Conditions:**\n" + "\n".join(f"- {d} {t}" for d, t in CONDITIONS)
    L.ensure_class(b, "Oath of Crusade", {"aspects": {"Visibility": "always", "Describe": True}, "stats": oath_stats, "templateClass": ""}, replace=True)
    L.class_rules(b, "Oath of Crusade", oath_rules)
    L.put_asset(b, "Oath of Crusade§Oath of Crusade", {"text": oath_text}, keep_text=False)
    rn, rp, rtext = C.single_req(3)
    key = C.campaign(b, "Honouring the Creed", C.intro_of("Honouring the Creed"), [{"name": "Oaths of Crusade", "text": "Create your oath from a Deed, a Foe and optionally a Passion and a Condition (see the Oaths of Crusade below)."}],
                     (rn, rp, rtext), extra_text=OATH_TEXT)
    a = L.catalog(b)[key]
    a["allowed"]["items"].append("Oath of Crusade§Oath of Crusade")
    a["rules"] = {"Three oaths at most: one per battle of the campaign.": L.error_rule([L.ev(["{self}", "tally", "Oath of Crusade"], mx=3)])}
    cz.note(f"agendas new {new}; requisitions {len(reqs)}; badges 3; Relic Fragments tracker; Reclaimed Relics {len(relics)}; Champion's Virtues 6 (Emperor’s Champion only); Honouring the Creed + Oath of Crusade")
