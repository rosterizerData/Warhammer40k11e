"""11e Leader/Support cleanup (2026-10-24). A unit's hidden `Leader` counter is fed by attached characters' Ability§Leader
trait; Support characters carry Ability§Support instead, so the 10e-era rules that raised a unit's Leader max to 2 for
them are dead weight. This removes every rule that sets `stats.Leader.max`, keeps the two the 11e datasheets still
justify (Kroot Carnivores at 20 models, Cato Sicarius when Marneus Calgar is in the army) in rewritten form, types the
Astra Militarum Ministorum Priest as Support (its 11e datasheet core ability), and adds a hidden `Support` counter to
the core Unit so the two attachment kinds are both visible to rules."""
import json, re, glob, sys
from pathlib import Path
RZ = Path(__file__).resolve().parents[2]
touched = {}
def load(b): return json.load(open(RZ / f"{b}.rulebook"))
def save(b, d):
    a, m, p = d["revision"].split("."); d["revision"] = f"{a}.{m}.{int(p)+1}"
    open(RZ / f"{b}.rulebook", "w").write(json.dumps(d, indent=2, ensure_ascii=False)); touched[b] = d["revision"]
LEADER_MAX = re.compile(r'"stats", "Leader", "max"')
removed = []
for p in sorted(glob.glob(str(RZ / "*.rulebook"))):
    b = Path(p).stem; d = load(b); c = d["rulebook"]["assetCatalog"]; dirty = False
    for k, v in c.items():
        rules = v.get("rules") or {}
        for rk in list(rules):
            if not LEADER_MAX.search(json.dumps(rules[rk])):
                continue
            if (b, k) == ("T'au_Empire", "Unit§Kroot Carnivores"):
                del rules[rk]
                rules["Two Leaders at 20 models"] = {"evals": [{"actionable": True, "not": False, "operator": "AND", "paths": [["{self}", "stats", "Models", "value"]], "value": 20}],
                    "actions": [{"actionType": "set", "iterations": 1, "paths": [["{self}", "stats", "Leader", "max"]], "value": 2}], "evaluate": "AND", "failState": "pass",
                    "note": "Bodyguard: at a Starting Strength of 20, up to two (different) Leader units may be attached"}
                dirty = True; continue
            if (b, k) == ("Space_Marines", "Character§Cato Sicarius"):
                del rules[rk]
                rules["Support when Marneus Calgar is in the army"] = {"evals": [{"actionable": True, "min": 1, "not": False, "operator": "AND", "paths": [["{roster}", "tally", "Marneus Calgar"]]}],
                    "actions": [{"actionType": "set", "iterations": 1, "paths": [["{parent}", "stats", "Leader", "max"]], "value": 2}], "evaluate": "AND", "failState": "pass",
                    "note": "Captain of the Honour Guard: his Leader ability becomes Support if the army includes Marneus Calgar"}
                dirty = True; continue
            del rules[rk]; removed.append((b, k, rk)); dirty = True
        if "rules" in v and not v["rules"]:
            del v["rules"]
    if b == "Astra_Militarum":   # 11e datasheet: core ability Support (the MFM site prints the same units under LEADER:)
        tr = c["Character§Ministorum Priest"]["assets"]["traits"]
        for t in tr:
            if (t.get("trait") if isinstance(t, dict) else t) == "Ability§Leader":
                t["trait"] = "Ability§Support"; dirty = True; print("AM Ministorum Priest: Leader -> Support")
    if b == "Warhammer_40k_11e":
        st = d["rulebook"]["assetTaxonomy"]["Unit"]["stats"]
        if "Support" not in st:
            st["Support"] = {"statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}; dirty = True; print("core Unit: Support counter added")
    if dirty: save(b, d)
print(len(removed), "Leader-max rules removed:"); 
from collections import Counter
print(Counter(b for b, _, _ in removed)); print("touched:", touched)
