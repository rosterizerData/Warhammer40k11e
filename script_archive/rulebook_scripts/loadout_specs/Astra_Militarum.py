# Astra Militarum 11e wargear options. See loadouts.py for the format.
# Ministorum Priest / Tech-Priest Enginseer: hub units whose AM loadouts come from this book's overrides.
OPT = lambda w: [("-", "-"), ("✓", w)]
ML = {"Militarum multi-laser": "Multi-laser"}
SPEC = {
    "Sabre Weapons Battery": {"Model§Sabre Gun Platforms": {"static": ["Close Combat Weapon"], "slots": {
        "Loadout": ["Twin Heavy Bolter", "Defence Searchlight", "Twin Autocannon", "Twin Heavy Stubber", "Twin Lascannon"]}}},
    "Valkyrie": {"_rename": ML},
    "Armoured Sentinels": {"_rename": ML},
    "Scout Sentinels": {"_rename": ML},
    "Chimera": {"_unit": {"static": ["Armoured Tracks", "Lasgun Array"], "slots": {
        "Main Weapon": ["Multi-laser", "Heavy Bolter", "Heavy Flamer"], "Hull Weapon": ["Heavy Bolter", "Heavy Flamer"],
        "Pintle Weapon": ["-", "Heavy Stubber", "Storm Bolter"], "Hunter-Killer": OPT("Hunter-killer Missile")}}},
    "Leman Russ Commander": {"_rename": {"Militarum plasma cannon": "Plasma Cannon"}},
    "Hippogriff AFV": {"_rename": {"Heavy Lascannon": "Lascannon"}},
    "Cadian Shock Troops": {"_rename": {"Drum-fed autogun": "Sergeant’s Autogun"}},
    "Cadian Castellan": {"_unit": {"slots": {
        "Melee Weapon": ["Chainsword", "Boltgun + Close Combat Weapon", "Power Fist", "Power Weapon"],
        "Ranged Weapon": ["Laspistol", "Bolt Pistol", "Plasma Pistol"]}}},
    "Banehammer": {"_unit": {"static": ["Armoured Tracks", "2x Lascannon", "Tremor Cannon", "Twin Heavy Bolter"], "slots": {
        "Sponson Weapons 1": ["2x Twin Heavy Flamer", "2x Twin Heavy Bolter"],
        "Sponson Weapons 2": ["-", "2x Twin Heavy Flamer + 2x Lascannon", "2x Twin Heavy Bolter + 2x Lascannon"]}}},
    "Provisionally Prepared": {"_rename": {"Close combat weapon": "Close Combat Weapons"}},
    "Ministorum Priest": {"_rename": {"Zealot's vindicator": "W:Zealot’s vindictor"}},
    "Tech-Priest Enginseer": {"_rename": {"Archeotech pistol": "Mechanicus Pistol"}},
    "Ciaphas Cain": {"_unit": {"static": ["Chainsword and Gun But", "Laspistols", "Meltagun"]}},
}
