# Shared bits for the Chaos-family specs (imported by path from each spec).
import re


def combi_parent(unit):
    """make `Ranged Weapon§<unit>—Combi-weapon` (stat-less multi-profile parent) from the book's own sub-profiles"""
    def patch(u, own, res):
        key = f"Ranged Weapon§{unit}—Combi-weapon"
        subs = sorted(k for k in own if k.startswith(f"Ranged Weapon§{unit}—Combi-weapon – "))
        if key in own:   # parent already here: make sure it carries every profile the book has
            tr = own[key].setdefault("assets", {}).setdefault("traits", [])
            miss = [k for k in subs if k not in tr]
            tr += miss
            return f"added {miss} to {key}" if miss else "parent complete"
        if key in res or not subs:
            return "parent exists" if key in res else "no sub-profiles"
        own[key] = {"aspects": {"Label": "Combi-weapon"}, "assets": {"traits": subs}, "keywords": {"Tags": ["Multi-weapon"]}}
        return f"created {key} from {len(subs)} profiles (re-run to wire)"
    return patch


TERMITE = {"_unit": {"static": ["Termite Drill", "Terrax Melta Cutter"], "slots": {
    "Loadout": ["2x Combi-weapon", "2x Heavy Flamer", "2x Twin Volkite Charger"]}}, "_patch": combi_parent("Terrax-pattern Termite")}
KRATOS = {"_unit": {"static": ["Autocannon", "Armoured Tracks"], "keep": ["Hull weapons", "Hunter-killer missile", "Main cannon", "Sponson weapons"],
                    "slots": {"Pintle Mount weapon": ["-", "Combi-weapon", ("Havoc launcher", "Havoc Launcher"), ("Heavy bolter", "Heavy Bolter"),
                                               ("Heavy flamer", "Heavy Flamer"), "Multi-melta", ("Twin boltgun", "Twin Boltgun")]}},
          "_patch": lambda u, own, res: _kratos(u, own, res)}


def _kratos(u, own, res):
    """the hub's Pintle Mount weapon sits at statOrder 3; keep it so the override merges without a removal"""
    if "Pintle Mount weapon" in u.get("stats", {}):
        u["stats"]["Pintle Mount weapon"]["statOrder"] = 3
    return combi_parent("Kratos")(u, own, res)
