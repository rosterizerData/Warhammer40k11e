# T'au Empire 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# Most battlesuit/drone loadouts already match 11e; drones are wargear, not datasheet weapons.
MISSILE_DRONES = [("0", "-"), ("1", "Missile Drone"), ("2", "2x Missile Drone")]


def skyspear(u, own, res):
    """Tiger Shark: the transport bay rank keeps its ability; the alternative is 2 skyspear missile racks"""
    st = u["stats"]["Transport Bay"]
    st["ranks"] = {"Transport Bay": {"order": 0, "traits": [{"trait": "Ability§Transport Bay"}]},
                   "2 Skyspear Missile Racks": {"order": 1, "traits": [{"trait": "Ranged Weapon§Tiger Shark—Skyspear missile rack"}] * 2}}
    st["value"] = "Transport Bay"
    return "transport bay / 2 skyspear missile racks"


SPEC = {
    "Strike Team": {"_rename": {"Support turret missile system": "Support turret"}},
    "Breacher Team": {"_rename": {"Support turret missile system": "Support turret"}},
    "Kroot Lone-Spear": {"_unit": {"static": ["Kalamandra’s bite"], "slots": {
        "Wargear": ["Kroot long gun + Close combat weapon", "Blast javelin + Hunting javelin"]}}},
    "Krootox Rampagers": {"Model§Krootox Rampager": {"static": ["Kroot pistol and hunting javelins", "Hunting blades", "Rampager fists"]}},
    "Tiger Shark": {"_unit": {"static": ["2x Missile pod", "Armoured hull"], "keep": ["Transport Bay"], "slots": {
        "1st Wargear": ["2x Ion cannon", "2x Swiftstrike burst cannon", "2x Swiftstrike railgun"],
        "2nd Wargear": ["2x Burst cannon", "2x Cyclic ion blaster"],
        "Seeker missile": [(str(i), " + ".join(["Seeker missile"] * i) if i else "-") for i in range(7)]}},
        "_patch": skyspear},
    "Manta": {"_unit": {"static": ["2x Heavy rail cannon", "6x Ion cannon", "2x Long-barrelled burst cannon array", "2x Missile pod",
                                   "10x Seeker missile", "Armoured hull"]}},
    "Shas’o R’alai": {"_unit": {"static": ["Experimental pulse submunitions rifle", "Battlesuit fists"]}},
    "R’varna Battlesuit": {"_unit": {"static": ["2x Pulse submunitions cannon", "Battlesuit fists"], "slots": {"Missile Drones": MISSILE_DRONES}}},
    "Y’vahra Battlesuit": {"_unit": {"drop_stats": ["Missile Drones"], "add_slots": {"Missile Drones": MISSILE_DRONES}}},
    "Tetras": {"Model§Tetra": {"static": ["2x Pulse rifle", "Close combat weapons"]}},
}
