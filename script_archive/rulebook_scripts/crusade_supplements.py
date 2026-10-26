"""Campaign supplement content into the core book: campaign Agendas (Armageddon's five plus its eighteen Tactical
Agendas, Nachmund Gauntlet's five) in the Mission Record lists with a rule that asks for the matching campaign;
Crusade Blessings of each campaign, Armageddon's Hellscapes and per-alliance Narrative Goals and Nachmund's phase
Strategic Goals as Ability§ texts the Campaign asset gains for its Mission (and Alliance). Source: the Wahapedia 10e
pages in WAHA_CRUSADE_TXT (default ~/websites/datasources/wahapedia_crusade_2026-10-26/txt). Dry run unless --apply."""
import os, re, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crusade_lib as L
import crusade_waha as Wh
APPLY = "--apply" in sys.argv
D = Path(os.environ.get("WAHA_CRUSADE_TXT") or Path.home() / "websites/datasources/wahapedia_crusade_2026-10-26/txt")
core = "Warhammer_40k_11e"
T = L.taxonomy(core)
import json
before = json.dumps(L.load(core), sort_keys=True)
sec = {n: Wh.Section(n, lines=(D / f"rules10_{n}.txt").read_text(encoding="utf-8").split("\n")) for n in ("tyrannic-war", "pariah-nexus", "armageddon", "nachmund-gauntlet")}
MISSION = {"tyrannic-war": "Tyrannic War", "pariah-nexus": "Pariah Nexus", "armageddon": "Armageddon", "nachmund-gauntlet": "Nachmund Gauntlet"}


def entries(s, title, *, drop_tables=True):
    """named entries with '(Action)' sub-entries folded into the entry before them"""
    out = []
    for e in s.named(title):
        nm = e["name"]
        if drop_tables and re.match(r"^Table [A-Z]", nm, re.I):
            continue
        if nm.lower().endswith("(action)") and out:
            out[-1]["text"] += f"\n\n**{nm}:** " + e["text"]
            continue
        out.append(e)
    return out


def ability_text(title, intro, items):
    body = "\n\n".join(f"**{it['name']}.** {it['text']}" for it in items)
    return (intro + "\n\n" if intro else "") + body


camp_rules = {}


def campaign_ability(name, text, mission, alliance=None):
    L.ability(core, name, text)
    evals = [L.ev_stat("Mission", mission)]
    if alliance:
        evals.append(L.ev_stat("Alliance", alliance))
    camp_rules["campaignText" + re.sub(r"\W", "", name)] = L.rule([L.add(["{self}", "traits"], f"Ability§{name}")], evals,
                                                                   note="campaign reference text for the selected Mission")


# ── agendas: Armageddon (core + Tactical) and Nachmund ──
agendas = {}
arm = entries(sec["armageddon"], "Agendas") + entries(sec["armageddon"], "Tactical Agendas")
agendas["Armageddon"] = [e for e in arm if e["text"]]
nach = [e for e in entries(sec["nachmund-gauntlet"], "Agendas") if e["text"]]
for e in nach:
    if e["name"] == "Strategic Dominance":
        e["name"] = "Strategic Dominance (Nachmund)"
agendas["Nachmund Gauntlet"] = nach
mr = T["Mission Record"]["stats"]
start = 200
for camp, items in agendas.items():
    key = f"{camp} Agenda"
    for stat in ("Agenda 1", "Agenda 2"):
        ranks = mr[stat]["ranks"]
        for i, e in enumerate(items):
            ranks[e["name"]] = {"order": start + i, "tracking": {key: 1}}
    # the agenda needs its campaign: pass when none of these agendas is picked OR the campaign is active
    T["Mission Record"].setdefault("rules", {})[f"{camp} Agendas need the {camp} campaign."] = L.rule(
        None, [L.ev(["{self}", "tracked", key], mx=0), L.ev_tracked(camp, mn=1)], fail="error", evaluate="OR")
    L.ability(core, f"{camp} Agendas", ability_text(f"{camp} Agendas", "", items))
    camp_rules["campaignText" + re.sub(r"\W", "", camp + "Agendas")] = L.rule([L.add(["{self}", "traits"], f"Ability§{camp} Agendas")], [L.ev_stat("Mission", camp)])
    start += 100
# ── Crusade Blessings per campaign (plus the faction blessings where the page has them) ──
for slug, mission in MISSION.items():
    s = sec[slug]
    bl = s.named("Crusade Blessings")
    intro = next((l for l in s.block("Crusade Blessings") if l.startswith("An Underdog")), "")
    table = "Number of Blessings by difference in Crusade points: 0–4 none, 5–9 one, 10–14 two, 15–19 three, 20+ four."
    fac = []
    agenda_names = {e["name"] for e in s.named("Agendas")} | {e["name"] for e in s.named("Tactical Agendas")} | {e["name"] for e in s.named("Strategic Footing Agendas")}
    for e in s.named("Faction Crusade Blessings"):
        if e["name"] in agenda_names:
            break
        if e["name"].endswith(" Only") or e["name"].startswith("Excluding"):
            # the page puts the keyword restriction on its own line between the name and the text
            if fac:
                fac[-1]["text"] = f"({e['raw_name'].title()}) " + (e["text"] or e["flavour"])
            continue
        fac.append(e)
    items = [e for e in bl if e["text"]] + [e for e in fac if e["text"]]
    if items:
        campaign_ability(f"Crusade Blessings — {mission}", ability_text("", intro + "\n\n" + table, items), mission)
# ── Armageddon: Hellscapes and the alliance Narrative Goals ──
a = sec["armageddon"]
hells = []
for h in ("Folded Space", "Fractured Realm", "Fading Reality", "Scattered Coordinates", "Staggered Time", "Banishing Rifts", "Gravitic Nexus", "Endless Nightmare"):
    lines = [l for l in a.block(h) if l.strip() and not l.startswith("|")]
    hells.append({"name": h, "text": "\n".join(lines[:6])})
intro = " ".join(l for l in a.block("Hellscapes") if l.strip())[:600]
campaign_ability("Armageddon — Hellscapes", ability_text("", intro, hells) + "\n\n**Anomalies** (Empyric Anomaly 10, Warp Surge Anomaly 11) and the Warp Events/Warp counters rules are on the Armageddon pages.", "Armageddon")
GOALS = {"Gatebreakers": ["Stabilising the Front", "Reclaim the Lost Hives", "Strengthen the Imperator Line", "Raze the Monoliths", "Light in the Dark", "Shatter the Red Angel’s Gate"],
         "Desecrators": ["Planetfall", "Vile Rituals", "Corrupt the Fire Wastes", "Feed the Storm", "The Dark Gods Demand", "Warp Made Manifest"],
         "Marauders": ["Drawn to the Fight", "Forgotten Relics", "Escalation", "Decapitation", "Bloodied but Unbowed", "Endless War"]}
for alliance, goals in GOALS.items():
    items = []
    for g in goals:
        lines = [l for l in a.block(g) if l.strip() and not l.startswith("|")]
        items.append({"name": g, "text": "\n".join(lines)})
    campaign_ability(f"Armageddon — {alliance} narrative goals", ability_text("", "Four campaign phases; each phase your alliance attempts one narrative goal. Success and failure each point to the next goal.", items), "Armageddon", alliance)
# ── Nachmund: strategic goals by phase ──
n = sec["nachmund-gauntlet"]
items = []
for ph in ("Phase 1", "Phase 2", "Phase 3"):
    lines = [l for l in n.block(ph) if l.strip() and not l.startswith("|")]
    items.append({"name": ph, "text": "\n".join(lines)})
campaign_ability("Nachmund Gauntlet — strategic goals", ability_text("", "Three phases; each alliance (Guardians, Despoilers, Marauders) has a strategic goal per phase, resolved with Strategic Asset Points at the four Sangua Terra strategic sites.", items), "Nachmund Gauntlet")
T["Campaign"].setdefault("rules", {}).update(camp_rules)
print(f"agendas: Armageddon {len(agendas['Armageddon'])}, Nachmund {len(agendas['Nachmund Gauntlet'])}; campaign abilities: {len(camp_rules)}")
after = json.dumps(L.load(core), sort_keys=True)
if APPLY and before != after:
    print("written, revision", L.save(core))
elif before != after:
    print("dry run (use --apply)")
else:
    print("no change")
