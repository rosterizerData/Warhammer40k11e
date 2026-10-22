# Drukhari 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
import copy, json
from pathlib import Path


def mirror_aeldari(unit):
    """Legends Corsairs here were single game pieces; give them the shared hub models and limits the Aeldari book wires"""
    def patch(u, own, res):
        ael = json.load(open(Path(__file__).resolve().parents[3] / "Aeldari.rulebook"))["rulebook"]["assetCatalog"][f"Unit§{unit}"]
        if (u.get("aspects") or {}).get("Type") == "game piece":
            u["aspects"].pop("Type")
            if not u["aspects"]:
                del u["aspects"]
        for s in ("M", "T", "Sv", "W", "Ld", "OC"):
            u.get("stats", {}).pop(s, None)
        tr = (u.setdefault("assets", {})).get("traits") or []
        tr = [t for t in tr if not (isinstance(t, str) and "Weapon§" in t)]
        models = [t for t in (ael.get("assets") or {}).get("traits") or [] if (t if isinstance(t, str) else t.get("item", "")).startswith("Model§")]
        u["assets"]["traits"] = [t for t in tr if t not in models] + copy.deepcopy(models)
        items = [i for i in (ael.get("allowed") or {}).get("items") or [] if i in res]
        al = u.setdefault("allowed", {}).setdefault("items", [])
        al += [i for i in items if i not in al]
        u["stats"].update({k: copy.deepcopy(v) for k, v in (ael.get("stats") or {}).items() if k != "Points"})
        u.setdefault("rules", {}).update(copy.deepcopy(ael.get("rules") or {}))
        return "uses the shared Corsair models and limits"
    return patch


SPEC = {
    "Drazhar": {"_rename": {"The Executioner’s demiklaives": "Executioner’s demiklaives"}},
    "Wracks": {"_rename": {"Torturer's tool": "Torturer’s tools"}},
    "Raider": {"_rename": {"Bladevanes": "Bladevanes and chainsnares"}},
    "Razorwing Jetfighter": {"_rename": {"Disintegrator": "Disintegrator cannon"}},
    "Scourges with Heavy Weapons": {"_rename": {"Drukhari haywire blaster": "Haywire blaster"}},
    "Talos": {"_rename": {"Twin Drukhari haywire blaster": "Twin haywire blaster"}},
    "Voidraven Bomber": {"_unit": {"static": ["Bladed Wings"], "slots": {
        "Ranged Options": ["2x Void Lance", "2x Dark Scythe"], "Optional Voidraven missiles": [("-", "-"), ("✓", "Voidraven Missiles")]}}},
    "Corsair Voidreavers": {"_patch": mirror_aeldari("Corsair Voidreavers")},
    "Corsair Voidscarred": {"_patch": mirror_aeldari("Corsair Voidscarred")},
    "Corsair Cloud Dancer Band": {"_patch": mirror_aeldari("Corsair Cloud Dancer Band")},
    "Corsair Reaver Band": {"_patch": mirror_aeldari("Corsair Reaver Band")},
    "Corsair Skyreavers": {"_patch": mirror_aeldari("Corsair Skyreavers")},
}
