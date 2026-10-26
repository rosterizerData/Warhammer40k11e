"""Crusade: Nachmund Gauntlet (10e, 2024) into the core book, beside Armageddon: a Campaign Mission rank, Nachmund Traits
(gated like the Armageddon ones), tiered Nachmund Relics, the seven Nachmund Mighty Champion abilities (their own items,
each campaign's champions gated to its mission), and the campaign alliances. Traits/relics/champions come from the BSData
extract (BS_CRUSADE_JSON, gates included); alliance and badge text from the Wahapedia page. Dry run unless --apply."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crusade_lib as L
APPLY = "--apply" in sys.argv
F = json.load(open(os.environ["BS_CRUSADE_JSON"]))
lib = F["Aeldari - Aeldari Library"]["honours"]
core = "Warhammer_40k_11e"
T = L.taxonomy(core); C = L.catalog(core)
before = json.dumps(L.load(core), sort_keys=True)
TIER = {"Artificer Relics": ("Artificer Relic", None), "Antiquity Relics": ("Antiquity Relic", 2), "Legendary Relics": ("Legendary Relic", 3)}

# classes mirror the Armageddon ones
T["Nachmund Trait"] = json.loads(json.dumps(T["Armageddon Trait"]))
T["Nachmund Relic"] = json.loads(json.dumps(T["Armageddon Relic"]))
# campaign mission + alliances
mr = T["Campaign"]["stats"]["Mission"]["ranks"]
mr.setdefault("Nachmund Gauntlet", {"order": 4, "tracking": {"Nachmund Gauntlet": 1}})
al = T["Campaign"]["stats"]["Alliance"]["ranks"]
for i, a in enumerate(["Gatebreakers", "Desecrators", "Marauders", "Guardians", "Despoilers"]):
    al.setdefault(a, {"order": 7 + i})
# allowances
U = T["Unit"]["rules"]; Ch = T["Character"]["rules"]
r = json.loads(json.dumps(U["allowArmageddonTraits"])); r["actions"][0]["value"] = "Nachmund Trait"; r["evals"][0]["paths"] = [["{roster}", "tracked", "Nachmund Gauntlet"]]
U["allowNachmundTraits"] = r
r = json.loads(json.dumps(Ch["allowArmageddonRelics"])); r["actions"][0]["value"] = "Nachmund Relic"; r["evals"][0]["paths"] = [["{roster}", "tracked", "Nachmund Gauntlet"]]
Ch["allowNachmundRelics"] = r
r = json.loads(json.dumps(Ch["allowMightyChampion"])); r["evals"][0]["paths"] = [["{roster}", "tracked", "Nachmund Gauntlet"]]
r["note"] = "Crusade: Nachmund Gauntlet — the Campaign Master gives each named character one Mighty Champion ability"
Ch["allowMightyChampionNachmund"] = r
# traits and relics
n_tr = n_rel = n_ch = 0
for it in lib.get("Nachmund Gauntlet Battle Traits", []):
    if not it["text"]:
        continue
    anyt = [c for p, c in it["gates"] if p == "+"]; nonet = [c for p, c in it["gates"] if p == "-"]
    C[f"Nachmund Trait§{it['name']}"] = {"keywords": {"Tags": anyt + ["not" + c.replace(" ", "") for c in nonet]}, "text": it["text"]}
    n_tr += 1
for it in lib.get("Nachmund Gauntlet Crusade Relics", []):
    if not it["text"]:
        continue
    tag, pts = TIER.get(it["path"][-1], ("Artificer Relic", None))
    a = {"keywords": {"Tags": [tag]}, "text": it["text"]}
    if pts:
        a["stats"] = {"Crusade Pts": {"value": pts}}
    anyt = [c for p, c in it["gates"] if p == "+"]
    if anyt:
        a["rules"] = {" or ".join(anyt) + " only.": L.error_rule([L.ev_kw(c, who="{parent}") for c in anyt], evaluate="OR" if len(anyt) > 1 else "AND")}
    C[f"Nachmund Relic§{it['name']}"] = a
    n_rel += 1
# champions: the existing seven are Armageddon's; gate them, and add the Nachmund seven
for k in [k for k in C if k.startswith("Mighty Champion§") and "(Nachmund" not in k]:
    C[k].setdefault("rules", {})["Crusade: Armageddon only."] = L.error_rule([L.ev_tracked("Armageddon", mn=1)])
for it in lib.get("Mighty Champions", []):
    if it["path"] and it["path"][-1] == "Nachmund Gauntlet Crusade Abilities" and it["text"]:
        C[f"Mighty Champion§{it['name']} (Nachmund Gauntlet)"] = {"keywords": {"Tags": ["Character"]}, "text": re.sub(r"\^\^", "", it["text"]).replace("\n- ", "\n• "),
                                                                "rules": {"Crusade: Nachmund Gauntlet only.": L.error_rule([L.ev_tracked("Nachmund Gauntlet", mn=1)])}}
        n_ch += 1
print(f"Nachmund: traits {n_tr}, relics {n_rel}, champions {n_ch}; mission rank + 5 alliance ranks; 3 allowance rules")
after = json.dumps(L.load(core), sort_keys=True)
if APPLY and before != after:
    print("written, revision", L.save(core))
elif before != after:
    print("dry run (use --apply)")
else:
    print("no change")
