# Blood Angels 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
SPEC = {
    "Commander Dante": {"_rename": {"Perdition": "Perdition Pistol"}},
    "Sanguinary Priest": {"_rename": {"Astartes chainsword": "Chainsword"}},
    "Sanguinary Guard": {"Model§Sanguinary Guard": {"static": ["Encarmine Weapon"], "slots": {
        "Ranged Options": ["Angelus Boltgun", "Inferno Pistol @inferno"]}},
        "_drop_rules": ["Maximum 1 Banner"]},
    "Death Company Marines": {"Model§Death Company Marine": {"slots": {
        "Melee Options": ["Chainsword", "Bolt Rifle + Combat Blade @rifle", "Eviscerator @evisce", "Power Fist @special2",
                          "Power Weapon @special2", "Thunder Hammer @special2"],
        "Ranged Options": ["Heavy Bolt Pistol", "Hand Flamer @special1", "Inferno Pistol @special1", "Plasma Pistol @special1"],
        "Grenade Launcher": [("-", "-"), ("✓", "Grenade Launcher @gl")]}},
        "_limits": [("gl", "1in5", "Maximum 1 Grenade Launcher for every 5 models")],
        "_rules": {"A Grenade Launcher needs a Bolt Rifle": {"evals": [{
            "actionable": True, "equation": {"operator": "T-O", "value": ["{self}", "tracked", "rifle"]}, "max": 0,
            "not": False, "operator": "AND", "paths": [["{self}", "tracked", "gl"]]}], "evaluate": "AND", "failState": "error"}}},
    "Death Company Marines with Jump Packs": {
        "Model§Death Company Marine with Jump Pack": {"slots": {
            "Melee Options": ["Chainsword", "Eviscerator @evis", "Power Fist @fist", "Power Weapon @pw=0.5"],
            "Ranged Options": ["Heavy Bolt Pistol", "Hand Flamer @hf", "Inferno Pistol @inf", "Plasma Pistol @pl=0.5"]},
            "drop_rules": ["NoUnique", "Unique Loadouts can not take other options"]},
        "_drop_rules": ["1 in 5 can have Eviscerators", "1 in 5 can have Unique loadouts", "Only one Power weapon.",
                        "Outside of unique loadouts, 1 in 5 can have Plasma pistols"],
        "_limits": [("evis", "1in5", "Maximum 1 Eviscerator for every 5 models"), ("fist", "1in5", "Maximum 1 Power Fist for every 5 models"),
                    ("pw", "1in5", "Up to 2 Power Weapons for every 5 models"), ("hf", "1in5", "Maximum 1 Hand Flamer for every 5 models"),
                    ("inf", "1in5", "Maximum 1 Inferno Pistol for every 5 models"), ("pl", "1in5", "Up to 2 Plasma Pistols for every 5 models")]},
    "Death Company Captain with Jump Pack": {"_unit": {"slots": {"Loadout": [
        "Heavy Bolt Pistol + Chainsword", "Heavy Bolt Pistol + Power Fist", "Heavy Bolt Pistol + Relic Weapon",
        "Hand Flamer + Chainsword", "Hand Flamer + Power Fist", "Hand Flamer + Relic Weapon",
        "Plasma Pistol + Chainsword", "Plasma Pistol + Power Fist", "Plasma Pistol + Relic Weapon",
        "Thunder Hammer + Relic Shield", "Chainsword + Relic Shield"]}}},
}
