# Harlequins hub (Aeldari / Drukhari / Corsairs) 11e wargear options. See loadouts.py for the format.
# Shared Corsair and Harlequin models live here; the Aeldari and Drukhari books wire them into their units.
import json
from pathlib import Path

CD_GUNS = ["Twin Shuriken Catapult", "Dark Lance", "Dissonance Cannon", "Scatter Laser", "Shuriken Cannon", "Splinter Cannon"]


def reaver_weapons_to_hub(u, own, res):
    """Reaver Band weapons the hub models use but only the Aeldari book defined: move them here so Drukhari sees them"""
    ael = json.load(open(Path(__file__).resolve().parents[3] / "Aeldari.rulebook"))["rulebook"]["assetCatalog"]
    moved = [k for k in ael if k.split("§")[0].endswith("Weapon") and k.split("§", 1)[1].startswith("Corsair Reaver Band—") and k not in own]
    for k in moved:
        own[k] = ael[k]; res[k] = ael[k]
    return f"copied {moved} from Aeldari" if moved else "weapons already in the hub"


SPEC = {
    "Troupe": {"_rename": {"Aeldari power sword": "Power sword"}},
    "Corsair Cloud Dancer Band": {
        "Model§Corsair Cloud Dancers": {"static": ["Brace of Pistols", "Close combat weapon"], "slots": {"Ranged Loadout": CD_GUNS}},
        "Model§Cloud Dancer Felarch": {"static": ["Brace of Pistols", "Close combat weapon"], "slots": {
            "Ranged Loadout": CD_GUNS, "Melee Options": ["-", "Dissonance Pistol", "Void Sabre"]}}},
    "Corsair Reaver Band": {
        "Model§Corsair Reavers": {"drop_ranks": {"Loadout": ["Shardcarbine", "Shuriken catapult"]}},
        "Model§Corsair Reaver Felarch": {"drop_ranks": {"Loadout": ["Shardcarbine", "Shuriken catapult"]}},
        "_patch": reaver_weapons_to_hub},
}
