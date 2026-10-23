# Space Marines 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# Units whose 10e structure already matches 11e only get `_rename` (weapon keys + rank labels → the 11e assets).
OPT = lambda w: [("-", "-"), ("✓", w)]
CF = {"Close combat weapon": "Ceramite Fists"}

SPEC = {
    # ---------------------------------------------------------------- characters
    "Apothecary Biologis": {"_rename": {"Close combat weapon": "Servo-armature"}},
    "Apothecary": {"_unit": {"static": ["Absolvor Bolt Pistol", "M:Reductor Pistol", "Servo-armature"]}},
    "Ancient": {"_unit": {"static": ["Bolt Pistol", "Ceramite Fists"], "slots": {"Loadout": ["Bolt Rifle", "Power Weapon"]}}},
    "Bladeguard Ancient": {"_rename": {"Close combat weapon": "Relics of Battle"}},
    "Ancient in Terminator Armour": {"_unit": {"static": ["Master-crafted Power Weapon", "Storm Bolter"]},
                                     "_drop_rules": ["nonstandardPrimary", "standardPrimary"]},
    "Captain": {"_unit": {"slots": {
        "Ranged Options": ["Heavy Bolt Pistol + Master-crafted Bolter", "Neo-volkite Pistol", "Plasma Pistol",
                           "Heavy Bolt Pistol + Relic Shield @shield"],
        "Melee Options": ["Master-crafted Power Weapon", "Power Fist @fist"]}},
        "_drop_rules": ["allowRelicShield", "allowSecondary", "disallowSecondary"],
        "_rules": {"A Relic Shield keeps the Master-crafted Power Weapon": {"evals": [
            {"actionable": True, "max": 0, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "shield"]]},
            {"actionable": True, "max": 0, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "fist"]]}],
            "evaluate": "OR", "failState": "error"}}},
    "Captain with Jump Pack": {"_unit": {"slots": {"Loadout": [
        "Heavy Bolt Pistol + Chainsword", "Heavy Bolt Pistol + Power Fist", "Heavy Bolt Pistol + Relic Weapon",
        "Hand Flamer + Chainsword", "Hand Flamer + Power Fist", "Hand Flamer + Relic Weapon",
        "Plasma Pistol + Chainsword", "Plasma Pistol + Power Fist", "Plasma Pistol + Relic Weapon",
        "Thunder Hammer + Relic Shield", "Chainsword + Relic Shield"]}},
        "_drop_rules": ["chain&shield", "disallowTwoRelicWeapon", "hammer", "noHammerorChain"]},
    "Captain in Terminator Armour": {"_unit": {"slots": {
        "Melee": ["Relic Weapon", "Relic Fist"], "Ranged": ["Storm Bolter", "Combi-weapon"]}}},
    "Captain in Gravis Armour": {"_unit": {"slots": {"Loadout": [
        "Master-crafted Heavy Bolt Rifle + Master-crafted Power Weapon",
        "R:Boltstorm Gauntlet + M:Boltstorm Gauntlet + Relic Blade",
        "R:Boltstorm Gauntlet + M:Boltstorm Gauntlet + Relic Chainsword",
        "R:Boltstorm Gauntlet + M:Boltstorm Gauntlet + Relic Power Fist"]}}},
    "Captain on Bike": {"_unit": {"static": ["Twin Bolt Rifle"], "slots": {
        "Ranged": ["Heavy Bolt Pistol", "Plasma Pistol"], "Melee": ["Master-crafted Power Weapon", "Thunder Hammer"]}},
        "_drop_rules": ["disallowTwoRelicWeapon", "noTwinClaws", "twinClaws"]},
    "Chaplain with Jump Pack": {"_unit": {"static": ["Absolvor Bolt Pistol", "Crozius Arcanum"]}},
    "Librarian in Terminator Armour": {"_unit": {"static": ["Force Weapon", "Smite", "Storm Bolter"]}},
    "Lieutenant": {"_unit": {"slots": {
        "Melee": ["Ceramite Fists", "Master-crafted Power Weapon", "Power Fist"],
        "Ranged": ["Bolt Pistol + Master-crafted Bolter", "Bolt Pistol + Master-crafted Power Weapon", "Bolt Pistol + Plasma Pistol",
                   "Bolt Pistol + Power Fist", "Heavy Bolt Pistol + Master-crafted Bolter", "Heavy Bolt Pistol + Master-crafted Power Weapon",
                   "Heavy Bolt Pistol + Plasma Pistol", "Heavy Bolt Pistol + Power Fist",
                   "Neo-volkite Pistol + Master-crafted Power Weapon", "Neo-volkite Pistol + Master-crafted Power Weapon + Storm Shield"]}},
        "_drop_rules": ["disallowTwoStormShield", "noVolkite", "volkite"]},
    "Lieutenant in Phobos Armour": {"_unit": {"static": ["Monomolecular Combat Blades"], "slots": {
        "Ranged": ["Special-issue Bolt Pistol", "Master-crafted Bolt Carbine"]}}},
    "Techmarine": {"_unit": {"static": ["Forge Bolter", "Grav-pistol", "Omnissian Power Axe and Servo-arm"]}},
    "Kayvaan Shrike": {"_rename": {"The Raven’s Talons": "Raven’s Talons"}},
    "Kor’sarro Khan": {"_unit": {"static": ["Anzuq", "Bolt Pistol", "Moonfang"]}},
    "Suboden Khan": {"_rename": {"Power weapon": "Power Sword"}},
    # ---------------------------------------------------------------- infantry
    "Bladeguard Veteran Squad": {"_rename": {"Master-crafted power weapon": "Master-crafted Power Sword"}},
    "Terminator Assault Squad": {
        "Model§Assault Terminator Sergeant": {"slots": {"Loadout": ["Twin Lightning Claws", "Thunder Hammer + U:Storm Shield"]}},
        "Model§Assault Terminator": {"slots": {"Loadout": ["Twin Lightning Claws", "Thunder Hammer + U:Storm Shield"]}}},
    "Inceptor Squad": {"_rename": CF},
    "Infernus Squad": {"_rename": CF},
    "Infiltrator Squad": {"_rename": CF, "Model§Infiltrator": {"drop_ranks": {"Wargear": ["Infiltrator comms array"]}},
                          "_drop_rules": ["Maximum 1 Infiltrator comms array."]},
    "Heavy Intercessor Squad": {"_rename": CF},
    "Hellblaster Squad": {"_rename": CF},
    "Eliminator Squad": {"_rename": CF},
    "Eradicator Squad with melta rifles": {"_rename": CF},
    "Desolation Squad": {"_rename": CF},
    "Aggressor Squad": {"_rename": {"Power fist": "Twin Power Fists"}},
    "Assault Intercessor Squad": {"_rename": {"Astartes chainsword": "Chainsword"}},
    "Assault Intercessors with Jump Packs": {"_rename": {"Astartes chainsword": "Chainsword"}},
    "Intercessor Squad": {"_rename": {"Astartes chainsword": "Chainsword", "Astartes grenade launcher": "Grenade Launcher",
                                      "Close combat weapon": "Knives and Fists"},
                          "Model§Intercessor Sergeant": {"drop_stats": ["Grenade launcher", "NadeLauncher", "bolt"],
                                                         "drop_rules": ["Astartes grenade launcher requires Bolt rifle"]}},
    "Incursor Squad": {"Model§Incursor": {"drop_stats": ["Haywire mine"]},
                       "_drop_stats": ["Haywire"], "_drop_rules": ["applyHaywireMine", "Maximum 1 haywire mine."]},
    "Scout Squad": {
        "Model§Scout Sergeant": {"static": ["Bolt Pistol"], "slots": {
            "Ranged": ["Boltgun", "Shotgun"], "Melee": ["Combat Knife", "Chainsword"]}, "drop_stats": ["pistol"]},
        "Model§Scout": {"static": ["Bolt Pistol", "Combat Knife"], "slots": {
            "Loadout": ["Boltgun", "Shotgun", "Sniper Rifle @sniper", "Heavy Bolter @heavy", "Missile Launcher @heavy"]}},
        "_drop_rules": ["1 in 5 can have a sniper rifle", "1 in 5 can have a special weapon"],
        "_limits": [("sniper", "1in5", "Maximum 1 Sniper Rifle for every 5 models"),
                    ("heavy", "1in5", "Maximum 1 Heavy Bolter or Missile Launcher for every 5 models")]},
    "Scout Bike Squad": {"_rename": {"Astartes shotgun": "Shotgun", "Astartes grenade launcher": "Grenade Launcher",
                                     "Astartes chainsword": "Chainsword"}},
    "Sternguard Veteran Squad": {
        "Model§Sternguard Veteran Sergeant": {"static": ["Artificer Firearm", "Bolt Pistol"], "slots": {
            "Melee": ["Chainsword", "Power Fist", "Power Weapon"]}},
        "Model§Sternguard Veteran": {"static": ["Bolt Pistol", "Ceramite Fists"], "slots": {
            "Loadout": ["Artificer Firearm", "Heavy Bolter @special", "Pyrecannon @special"]}},
        "_drop_rules": ["1 in 5 can have a special weapon."],
        "_limits": [("special", "1in5", "Maximum 1 Heavy Bolter or Pyrecannon for every 5 models")]},
    "Vanguard Veteran Squad with Jump Packs": {
        "Model§Vanguard Veteran Sergeant with Jump Pack": {"slots": {
            "Melee": ["Relic Blade", "Power Fist", "Thunder Hammer"],
            "Loadout": ["Heavy Bolt Pistol", "Plasma Pistol", "Combat Shield"]}},
        "Model§Vanguard Veteran with Jump Pack": {"static": ["Master-crafted Power Weapon"], "slots": {
            "Loadout": ["Heavy Bolt Pistol", "Plasma Pistol @plasma=0.5", "Combat Shield"]}},
        "_limits": [("plasma", "1in5", "Up to 2 Plasma Pistols for every 5 models")]},
    "Company Heroes": {"_rename": {"Bolt Pistol": "Master-crafted Bolt Pistol", "Bolt Rifle": "Master-crafted Bolt Rifle",
                                   "Close combat weapon": "Combat Knife"}},
    "Wardens of Ultramar": {
        "Model§Ancient Gadriel": {"static": ["Bolt Rifle", "Ceramite Fists"]},
        "Model§Veteran Sergeant Metaurus": {"static": ["Heavy Bolt Pistol", "Master-crafted Power Weapon"]},
        "Model§Gaius Silva": {"static": ["Archeotech Laspistol", "Power Weapon"]},
        "Model§Lucia Vestha": {"static": ["Archeotech Laspistol", "Ultramarian Combat Weapons"]},
        "_patch": lambda u, own, res: _strip_wargear(own, ["Model§Veteran Sergeant Metaurus", "Model§Gaius Silva"],
                                                       ["Wargear§Storm Shield", "Wargear§Refractor Field"])},
    "Outrider Squad": {
        "Model§Outrider Sergeant": {"static": ["Twin Bolt Rifle"], "slots": {
            "Melee": ["Chainsword", "Power Weapon", "Thunder Hammer"], "Ranged": ["Heavy Bolt Pistol", "Plasma Pistol @plasma"]}},
        "Model§Outrider": {"static": ["Chainsword", "Twin Bolt Rifle"], "slots": {"Ranged": ["Heavy Bolt Pistol", "Plasma Pistol @plasma"]}},
        "_drop_stats": ["Invader ATVs"],
        "_limits": [("plasma", "1in3", "Maximum 1 Plasma Pistol for every 3 models")]},
    "Reiver Squad": {
        "Model§Reiver Sergeant": {"static": ["Bolt Carbine", "Monomolecular Combat Knife", "Special-issue Bolt Pistol"],
                                  "drop_rules": ["noKnife"]},
        "Model§Reiver": {"static": ["Bolt Carbine", "Monomolecular Combat Knife", "Special-issue Bolt Pistol"]},
        "_unit": {"slots": {"Grav-chutes": OPT("Reiver Grav-chute"), "Grapnel Launchers": OPT("Grapnel Launcher")}}},
    "Invader ATVs": {"_rename": {"Close combat weapon": "Armoured Impact"}},
    # ---------------------------------------------------------------- vehicles
    "Firestrike Servo-turrets": {"_rename": {"Close combat weapon": "Hovering Bulk"}},
    "Ballistus Dreadnought": {"_rename": {"Twin storm bolter": "Storm Bolters"}},
    "Brutalis Dreadnought": {"_rename": {"Brutalis bolt rifles": "Bolt Rifles"}},
    "Invictor Tactical Warsuit": {"_rename": {"Twin ironhail heavy stubber": "Ironhail Heavy Stubbers"}},
    "Redemptor Dreadnought": {"_rename": {"Twin fragstorm grenade launcher": "Fragstorm Grenade Launchers",
                                          "Twin storm bolter": "Storm Bolters"}},
    "Repulsor": {"_rename": {"Repulsor defensive array": "Defensive Array"}},
    "Rapier Carrier": {"_rename": {"Close combat weapon": "Armoured Hull"}},
    "Land Raider Excelsior": {"_unit": {"static": ["Armoured Tracks", "2x Godhammer Lascannon", "Grav-cannon"], "slots": {
        "Multi-melta": OPT("Multi-melta"), "Hunter-killer missile": OPT("Hunter-killer Missile"),
        "Storm bolter": OPT("Storm Bolter"), "Combi-weapon": OPT("Combi-weapon")}}},
    "Dreadnought": {"_unit": {"slots": {
        "Loadout 1": ["Assault Cannon", "Heavy Plasma Cannon", "Multi-melta", "Twin Lascannon"],
        "Loadout 2": ["Dreadnought Fist + Storm Bolter", "Dreadnought Fist + Heavy Flamer", "Missile Launcher + Crushing Feet"]}}},
    "Venerable Dreadnought": {"_unit": {"static": ["Armoured Feet"], "slots": {
        "Loadout 1": ["Assault Cannon", "Dreadnought Inferno Cannon", "Heavy Plasma Cannon", "Multi-melta", "Twin Autocannon",
                      "Twin Heavy Bolter", "Twin Heavy Flamer", "Twin Lascannon"],
        "Loadout 2": ["Dreadnought Fist + Storm Bolter", "Dreadnought Fist + Heavy Flamer", "Missile Launcher", "Twin Autocannon"]}}},
    "Storm Speeder Hammerstrike": {"_unit": {"static": ["Armoured Impact", "Hammerstrike Missile Launcher",
                                                        "Krakstorm Grenade Launchers", "Melta Destroyer"]}},
    "Storm Speeder Hailstrike": {"_unit": {"static": ["Armoured Impact", "Fragstorm Grenade Launchers",
                                                      "Ironhail Heavy Stubber Array", "Onslaught Gatling Cannon"]}},
    "Storm Speeder Thunderstrike": {"_unit": {"static": ["Armoured Impact", "Stormfury Missile Launcher",
                                                         "Thunderstrike Icarus Rocket Pod", "Thunderstrike Las-talon"]}},
    "Gladiator Reaper": {"_unit": {"static": ["Armoured Hull", "Defensive Array", "Twin Heavy Onslaught Gatling Cannon"]}},
    "Gladiator Valiant": {"_unit": {"static": ["Armoured Hull", "Defensive Array", "2x Multi-melta", "Twin Las-talon"]}},
    "Gladiator Lancer": {"_unit": {"static": ["Armoured Hull", "Defensive Array", "Laser Destroyer"]}},
    "Terrax-pattern Termite": {"_unit": {"static": ["Termite Drill", "Terrax Melta Cutter"], "slots": {
        "Loadout": ["2x Combi-weapon", "2x Heavy Flamer", "2x Twin Volkite Charger"]}}},
    "Impulsor": {"_unit": {"static": ["Armoured Hull"], "slots": {
        "Loadout": ["Storm Bolters", "Fragstorm Grenade Launchers"],
        "Upgrade": ["-", "Bellicatus Missile Array", "Orbital Comms Array", "Ironhail Skytalon Array", "Shield Dome"],
        "Heavy stubber": OPT("Ironhail Heavy Stubber")}}},
    "Repulsor Executioner": {"_unit": {"static": ["Armoured Hull", "Defensive Array", "Heavy Onslaught Gatling Cannon", "Twin Heavy Bolter"],
                                       "slots": {"Main gun": ["Heavy Laser Destroyer", "Macro Plasma Incinerator"]}}},
    "Land Speeder": {"_unit": {"static": ["Armoured Impact", "Multi-melta", "Stormfury Missile Launcher"], "slots": {
        "Loadout": ["Onslaught Gatling Cannon", "Pyrecannon"]}}},
    "Sicaran": {"_unit": {"static": ["Armoured Tracks", "Heavy Bolter"], "slots": {
        "Main gun": ["Herakles-pattern Autocannon", "Arcus Multi-launcher", "Omega Plasma Array", "Punisher Rotary Cannon",
                     "Venator Neutron Laser"],
        "Hunter-killer missile": OPT("Hunter-killer Missile"),
        "Loadout": ["-", "2x Heavy Bolter", "2x Lascannon"], "Storm Bolter": OPT("Storm Bolter")}}},
    "Victrix Honour Guard": {"_patch": lambda u, own, res: _victrix(u)},
    "Predator Annihilator": {"_unit": {"static": ["Armoured Tracks", "Predator Twin Lascannon"], "slots": {
        "Loadout": ["2x Lascannon", "2x Heavy Bolter"], "Hunter-killer": OPT("Hunter-killer Missile"), "Storm bolter": OPT("Storm Bolter")}}},
    "Predator Destructor": {"_unit": {"static": ["Armoured Tracks", "Predator Autocannon"], "slots": {
        "Loadout": ["2x Lascannon", "2x Heavy Bolter"], "Hunter-killer": OPT("Hunter-killer Missile"), "Storm bolter": OPT("Storm Bolter")}}},
    "Stormraven Gunship": {"_unit": {"static": ["Armoured Hull", "2x Stormstrike Missile Launcher"], "slots": {
        "Hurricane bolters": [("0", "-"), ("1", "Hurricane Bolter"), ("2", "2x Hurricane Bolter")],
        "Loadout 1": ["Twin Assault Cannon", "Twin Heavy Plasma Cannon", "Twin Lascannon"],
        "Loadout 2": ["Typhoon Missile Launcher", "Twin Heavy Bolter", "Twin Multi-melta"]}}},
    "Thunderhawk Gunship": {"_unit": {"static": ["Armoured Hull", "2x Lascannon", "4x Twin Heavy Bolter", "Hellstrike Missile Battery"], "slots": {
        "Loadout 1": ["Thunderhawk Heavy Cannon", "Turbo-laser Destructor"]}},
        "_patch": lambda u, own, res: _cluster_bombs(u, own)},

}


def _strip_wargear(own, models, gear):
    for m in models:
        a = own[m]
        a.setdefault("assets", {})["traits"] = [t for t in a["assets"].get("traits", []) if t not in gear]
    return f"removed {gear} (not 11e wargear)"


def _cluster_bombs(u, own):
    """11e: Thunderhawk cluster bombs are a datasheet ability, not wargear"""
    k = "Ability§Thunderhawk Cluster Bombs"
    own.setdefault(k, {"keywords": {"Keywords": ["Model Ability"]}, "text": "In your Movement phase, when this unit ends a normal/advance move, you can select one enemy unit this unit moved over during that move and roll six D6: for each 3+, that enemy unit suffers 1 mortal wound."})
    tr = u["assets"]["traits"]
    if k not in tr:
        tr.append(k)
    return "cluster bombs as an ability"


def _victrix(u):
    """11e: 1–6 models in all, the Chapter Ancient and Champion included; at least one Honour Guard
    (the unit's own designation is in its tally, so count the characters instead: Models ≥ characters + 1)"""
    u["stats"]["Models"]["min"] = 1
    for s in ("Chapter Ancient", "Chapter Champion"):
        u["stats"][s]["ranks"]["✓"]["tracking"] = {"honourChars": 1}
    u.setdefault("rules", {})["At least 1 Victrix Honour Guard"] = {"evals": [
        {"actionable": True, "equation": {"operator": "T-O", "value": ["{self}", "tracked", "honourChars"]}, "min": 1, "not": False,
         "operator": "AND", "paths": [["{self}", "stats", "Models", "value"]]}],
        "evaluate": "AND", "failState": "error"}
    return "1–6 models including the Ancient and Champion"
