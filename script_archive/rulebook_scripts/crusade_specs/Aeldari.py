"""Aeldari Crusade (10e codex, as carried on the 11e site): Guiding Fate (Threat, three Threads of Fate), the Aeldari
Paths. Source: Wahapedia crus11_aeldari. Also removes the twelve Drukhari district abilities the BSData import filed here."""
SLUG, ED, FACTION = "aeldari", "11", "Asuryani"
LISTS = dict(agendas=True, requisitions=True, badges=True)

PATHS = {"Path of the Seer": ["Footfalls of Fate", "Webway Spar", "Spirit of Eldanesh"],
         "Path of Command": ["Paths of the Pathless", "Strategic Philosopher", "Master Misdirector"],
         "Path of the Warrior": ["Dead-eye Shots", "Khaine's Vengeance", "Tactical Teachings", "Nimble Fighters", "Battlewraiths", "Sunshock Fire Patterns"]}
THREADS = ["Destined Device", "Rising Nemesis", "Humble Beginnings", "Enemy of My Enemy", "Cleanse the Corruption", "Isha’s Bounty"]
STAGES = ["Dawning", "Waning", "Frayed", "Ended well", "Ended badly"]
DISTRICTS = ["Weapon Forge", "Toxin Distillery", "Arena", "Scourge Spire", "Incubi Shrine", "Dock", "Sprawl Slum", "Flesh Market", "Shadow District", "Noble Spire", "Gang Territory", "Raidcraft Workshop"]


def results_text(sec):
    lines = [l.strip() for l in sec.block("Results Stage") if l.strip()]
    out, i = [], 0
    while i < len(lines):
        if lines[i] == "THREAT" and i + 3 < len(lines):
            rng, name = lines[i + 1], lines[i + 2].title()
            j = i + 4   # skip flavour
            body = []
            while j < len(lines) and lines[j] != "THREAT":
                body.append(lines[j])
                j += 1
            out.append(f"**Threat {rng} — {name}:** " + " ".join(body))
            i = j
        else:
            i += 1
    return "\n\n".join(out)


def build(cz):
    L, b, sec = cz.L, cz.book, cz.sec
    cat = L.catalog(b)
    # ── repair: the Drukhari district abilities do not belong here ──
    removed = L.del_assets(b, [f"Crusade Honour§{d} controlled" for d in DISTRICTS])
    # ── the Aeldari Paths: a Path rank on Asuryani units, Path traits as their own class gated by it ──
    for cls in ("Unit", "Character"):
        L.unit_stat(b, cls, "Path", L.rank(list(PATHS), group="Crusade", group_order=11, order=20), show_when=[L.ev_kw("Asuryani", field="Faction")])
        for p in PATHS:
            L.class_rule(b, cls, "crusadeTag" + p.replace(" ", ""), L.rule([L.add(["{self}", "constraints", "any"], p)], [L.NARR, L.ev_stat("Path", p)],
                                                                          note=f"Crusade: a unit on the {p} may take that Path's Battle Traits"))
    for p, names in PATHS.items():
        L.reclass(b, "Crusade Honour§", "Aeldari Path Trait", names)
        for n in names:   # reclass merges lists, so set the Tags outright: the Path tag must be the only one
            key = f"Aeldari Path Trait§{n}"
            if key in cat:
                cat[key]["keywords"] = {"Tags": [p]}
    L.honour_class(b, "Aeldari Path Trait", unique=False, allow_on=("Unit", "Character"), allow_evals=[L.ev_kw("Asuryani", field="Faction")],
                   allow_note="The Aeldari Paths: a unit with a Path keyword (gained through Guiding Fate) may take that Path's Battle Traits instead of others")
    # ── threads of fate: the chosen thread's three stage goals appear as an ability ──
    for t in THREADS:
        stages = sec.named(t)
        txt = "\n\n".join(f"**{s['name']} ({STAGES[i] if i < 3 else ''}):** {s['text']}" for i, s in enumerate(stages[:3]))
        L.ability(b, f"Thread of Fate: {t}", txt)
    thread_rules = {f"thread{i}": L.rule([L.add(["{self}", "traits"], f"Ability§Thread of Fate: {t}")], [L.ev_stat("Thread", t)]) for i, t in enumerate(THREADS)}
    children = [L.child(b, "Thread of Fate", f"Thread of Fate {i}", stats={"Thread": L.rank(THREADS, order=1), "Stage": L.rank(STAGES, value="Dawning", dash=False, order=2)},
                        rules=thread_rules, text="Roll a D6 for each Thread when you begin Guiding Fate (re-roll duplicates): 1 Destined Device, 2 Rising Nemesis, 3 Humble Beginnings, 4 Enemy of My Enemy, 5 Cleanse the Corruption, 6 Isha’s Bounty. "
                        "Each Thread runs Dawning → Waning → Frayed; ending it in a battle (Fulcrum of Fate Agenda) reduces Threat by 3 / 2 / 1 by stage.")
                for i in (1, 2, 3)]
    text = ("**Guiding Fate.** If your Crusade force includes ASURYANI or HARLEQUINS models and is not Guiding Fate, it can begin: set Threat to 1 and generate three Threads of Fate. "
            "At the end of each battle add D3 to Threat (3 if you lost). With the Fulcrum of Fate Agenda you can attempt to end one Thread; success reduces Threat by 3 (Dawning), 2 (Waning) or 1 (Frayed). "
            "If Threat reaches 13 every Thread ends in failure. When all three Threads have ended, apply the results below (if all three failed, Threat becomes at least 13) and your force is no longer Guiding Fate.\n\n" + results_text(sec))
    rules = {"failed": L.rule([L.mod(["{self}", "designation"], " — DISASTER (Threat 13+)", append="")], [L.ev(["{self}", "stats", "Threat", "value"], mn=13)], order=1)}
    L.tracker(b, "Guiding Fate", "Guiding Fate", stats={"Threat": L.num(1, mn=0, mx=13, order=1)}, children=children, text=text, class_rules_=rules)
    cz.note(f"removed {removed} Drukhari district items; Path rank + Aeldari Path Trait class ({sum(len(v) for v in PATHS.values())} traits); Guiding Fate tracker with 3 Thread children and {len(THREADS)} thread abilities")
