# Chaos hub: 11e changes common to every book that fields these units. See loadouts.py for the format.
def havocs(u, own, res):
    """default: 2 Havocs with Havoc autocannons, 2 with Havoc lascannons"""
    tr = u["assets"]["traits"]
    if any(isinstance(t, dict) and t.get("stats") for t in tr if (t if isinstance(t, str) else t.get("item")) == "Model§Havoc"):
        return "already split"
    u["assets"]["traits"] = [t for t in tr if (t if isinstance(t, str) else t.get("item")) != "Model§Havoc"] + [
        {"item": "Model§Havoc", "quantity": 2},
        {"item": "Model§Havoc", "quantity": 2, "stats": {"Loadout Options": {"value": "Havoc lascannon"}}}]
    return "default 2 autocannons + 2 lascannons"

SPEC = {
    "Havocs (SL)": {"_patch": havocs},
    "Plague Marines": {"_rename": {"Plague boltgun": "Boltgun", "Plague bolt pistol": "Bolt Pistol"}},
    "Khorne Berzerkers": {"_rename": {"Berzerker chainblade": "Chainblade"}},
    "Terrax-pattern Termite": {"_unit": {"static": ["Termite Drill", "Terrax Melta Cutter"], "slots": {
        "Loadout": ["2x Combi-weapon", "2x Heavy Flamer", "2x Twin Volkite Charger"]}}},
}
