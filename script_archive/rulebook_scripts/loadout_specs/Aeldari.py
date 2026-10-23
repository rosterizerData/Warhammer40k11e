# Aeldari 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# Exarch / platform loadouts are driven by unit-level ranks + model rules already; only renames and fixes here.
import json
from pathlib import Path


def current_corsair(u, own, res):
    """MFM lists this unit for Aeldari: not Legends here"""
    kw = u.setdefault("keywords", {})
    kw["Source"] = ["10th Edition Codex"]
    return "Source → 10th Edition Codex (listed in MFM)"


def drop_hub_copies(u, own, res):
    hub = json.load(open(Path(__file__).resolve().parents[3] / "Harlequins.rulebook"))["rulebook"]["assetCatalog"]
    gone = [k for k in list(own) if k.split("§", 1)[-1].startswith("Corsair Reaver Band—") and k in hub and own[k] == hub[k]]
    for k in gone:
        del own[k]
    return current_corsair(u, own, res) + (f"; removed duplicates of hub weapons {gone}" if gone else "")


def dragon_knights(u, own, res):
    """11e: 1 Dragon Knight Leader + 2–5 Dragon Knights (3 or 6 models); stats and weapons move to a Model§"""
    mk = "Model§Dragon Knight"
    if mk in own:
        return "already split"
    st = u["stats"]
    m = {"stats": {s: st.pop(s) for s in ("Ld", "M", "OC", "Sv", "T", "W") if s in st}}
    tr = u["assets"]["traits"]
    m["assets"] = {"traits": [t for t in tr if isinstance(t, str) and "Weapon§" in t] + ["Melee Weapon§Dragon Knights—Laser Lance"]}
    u["assets"]["traits"] = [t for t in tr if not (isinstance(t, str) and "Weapon§" in t)] + [{"item": mk, "quantity": 3}]
    own[mk] = m
    u.pop("aspects", None)
    u.setdefault("allowed", {}).setdefault("items", []).append(mk)
    st.update({"model1stTally": {"value": 3}, "model2ndCost": {"value": 190}, "model2ndTally": {"value": 6},
               "modelKey": {"value": mk}, "Models": {"increment": {"value": 3}, "max": 6, "min": 3, "value": 3, "visibility": "normal"},
               "Dragon Knight": {"max": 6, "min": 3, "statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}})
    return "split into Model§Dragon Knight x3–6"


SPEC = {
    "Autarch Skyrunner": {"_unit": {"static": ["Close combat weapon", "Twin Shuriken Catapult"], "slots": {
        "Main": ["W:Laser Lance", "Dragon Fusion Gun", "Banshee Blade"]}}},
    "Avatar of Khaine": {"_unit": {"static": ["R:The Wailing Doom", "M:The Wailing Doom"]}},
    "Storm Guardians": {"_rename": {"Guardian combat weapon": "Close combat weapon", "Guardian fusion gun": "Fusion gun"}},
    "Rangers": {"_rename": {"Ranger long rifle": "Long rifle"}},
    "Shroud Runners": {"_rename": {"Ranger long rifle": "Long rifle"}},
    "Prince Yriel": {"_rename": {"The Eye of Wrath": "Eye of Wrath", "The Spear of Twilight": "Spear of Twilight"}},
    "Ynnari Venom": {"_unit": {"static": ["Splinter Cannon", "Bladevanes"], "slots": {"Cannon Options": ["Twin Splinter Rifle", "Splinter Cannon"]}}},
    "Dragon Knights": {"_patch": dragon_knights},   # also gives the model its melee Laser Lance profile
    "Corsair Cloud Dancer Band": {"_patch": current_corsair},
    "Corsair Reaver Band": {"_patch": drop_hub_copies},
}
