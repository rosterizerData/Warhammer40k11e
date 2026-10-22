# Deathwatch 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
OPT = lambda w: [("-", "-"), ("✓", w)]
TERM = ["Storm Bolter + Power Fist", "Storm Bolter + Chainfist", "Storm Bolter + Power Weapon", "Thunder Hammer + U:Storm Shield",
        "Twin Lightning Claws"]
SPEC = {
    "Corvus Blackstar": {"_unit": {"static": ["Armoured Hull", "Auspex Array"], "slots": {
        "Rocket Options": ["2x Blackstar Rocket Launcher", "2x Stormstrike Missile Launcher"],
        "Cannon Options": ["Twin Assault Cannon", "Twin Lascannon"], "Hurricane bolter": OPT("Hurricane Bolter")}}},
    "Deathwatch Terminator Squad": {
        "Model§Deathwatch Terminator Sergeant": {"slots": {"Unique Loadouts": TERM}},
        "Model§Deathwatch Terminator": {"slots": {"Loadout": TERM + [
            "Assault Cannon + Power Fist @heavy", "Cyclone Missile Launcher + Storm Bolter + Power Fist @heavy",
            "Heavy Flamer + Power Fist @heavy", "Plasma Cannon + Power Fist @heavy"]},
            "drop_rules": ["Unique loadouts can not take other options"]}},
    "Spectrus Kill Team": {
        "Model§Kill Team Infiltrator": {"static": ["Bolt Pistol", "Ceramite Fists"], "slots": {
            "Wargear": ["Deathwatch Marksman Bolt Carbine", "Helix Gauntlet @wargear"]}},
        "Model§Kill Team Infiltrator with bolt sniper rifle": {"static": ["Bolt Pistol", "Ceramite Fists"], "slots": {
            "Ranged Option": ["Bolt Sniper Rifle", "Las Fusil", "Instigator Bolt Carbine"]}},
        "Model§Kill Team Infiltrator with combat knife": {"static": ["Special-issue Bolt Pistol"], "slots": {
            "Loadout Options": ["Combat Knife", "Deathwatch Bolt Carbine + Ceramite Fists"]}},
        "Model§Kill Team Infiltrator with occulus bolt carbine": {"static": ["Bolt Pistol", "Deathwatch Occulus Bolt Carbine", "Paired Combat Blades"]},
        "_drop_rules": ["Maximum 1 Sniper can have a Bolt Carbine"]},
    "Fortis Kill Team": {
        "Model§Kill Team Sergeant": {"static": ["Bolt Pistol"], "slots": {
            "Primary": ["Deathwatch Bolt Rifle", "Deathwatch Bolt Rifle + Grenade Launcher @gl", "Chainsword", "Hand Flamer",
                        "Plasma Pistol", "Power Weapon"],
            "Secondary": ["Knives and Fists", "Chainsword", "Power Fist", "Power Weapon", "Thunder Hammer"]}},
        "Model§Kill Team Intercessor": {"static": ["Bolt Pistol", "Knives and Fists"], "slots": {
            "Ranged Options": ["Deathwatch Bolt Rifle", "Deathwatch Bolt Rifle + Grenade Launcher @gl"]}},
        "Model§Kill Team Intercessor with heavy bolt pistol": {"static": ["Heavy Bolt Pistol", "Chainsword"]},
        "Model§Kill Team Intercessor with plasma incinerator": {"static": ["Plasma Incinerator", "Knives and Fists"], "slots": {
            "Pistol Options": ["Bolt Pistol", "Plasma Pistol @pp"]}},
        "Model§Kill Team Intercessor with pyreblaster": {"static": ["Bolt Pistol", "Knives and Fists", "Pyreblaster"]},
        "Model§Kill Team Intercessor with superfrag rocket launcher": {"static": ["Bolt Pistol", "Knives and Fists", "Castellan Launcher"],
            "slots": {"Loadout": ["Superfrag Rocket Launcher", "Superkrak Rocket Launcher", "Vengor Launcher @vengor"]}},
        "_drop_rules": ["1 in 5 Astartes grenade launcher", "Only one plasma pistol incinerator", "Only one Vengor launcher"],
        "_limits": [("gl", "1in5", "Maximum 1 Grenade Launcher for every 5 models"), ("pp", 1, "Only 1 Plasma Pistol"),
                    ("vengor", 1, "Only 1 Vengor Launcher")]},
    "Indomitor Kill Team": {
        "Model§Kill Team Heavy Intercessor": {"static": ["Ceramite Fists"], "slots": {
            "Ranged Options": ["Deathwatch Heavy Bolt Rifle", "Deathwatch Heavy Bolter @hb"]}},
        "Model§Kill Team Heavy Intercessor with melta rifle": {"static": ["Bolt Pistol", "Ceramite Fists"], "slots": {
            "Ranged Options": ["Melta Rifle", "Multi-melta @mm"]}},
        "Model§Kill Team Heavy Intercessor with power fist": {"static": ["Twin Power Fists"], "slots": {
            "Ranged Options": ["Flamestorm Gauntlets", "Auto Boltstorm Gauntlets + Fragstorm Grenade Launcher"]}},
        "_drop_rules": ["1 in 5 models can have a heavy bolter", "Maximum 1 Multi-melta",   # + the 10e jump-pack variant's tallies
                        "appliedw/jumpTally", "applyMissingw/jumps", "applyMorew/jumps", "truew/jumpTally"],
        "_limits": [("hb", "1in5", "Maximum 1 Deathwatch Heavy Bolter for every 5 models"), ("mm", 1, "Only 1 Multi-melta")]},
    "Talonstrike Kill Team": {
        "Model§Kill Team Sergeant with Jump Pack": {"slots": {
            "Primary": ["Heavy Bolt Pistol", "Hand Flamer", "Plasma Pistol"], "Secondary": ["Chainsword", "Power Fist", "Power Weapon"]}},
        "Model§Kill Team Intercessor with Jump Pack": {"static": ["Chainsword"], "slots": {"Loadout": ["Heavy Bolt Pistol", "Plasma Pistol @pp"]}},
        "Model§Kill Team Heavy Intercessor with Jump Pack": {"static": ["Ceramite Fists"], "slots": {"Primary": ["Assault Bolters", "Plasma Exterminators"]}},
        "_limits": [("pp", "1in5", "Maximum 1 Plasma Pistol for every 5 models")]},
    "Decimus Kill Team": {
        "Model§Kill Team Sergeant (Decimus)": {"static": ["Plasma Pistol", "Power Weapon"]},
        "Model§Deathwatch Veteran w/ Heavy thunder hammer (Decimus)": {"static": ["Bolt Pistol"], "slots": {
            "Ranged Weapon": ["Heavy Thunder Hammer", "Power Weapon + Storm Shield @shield"]}},
        "Model§Deathwatch Veteran w/ Marksman bolt carbine (Decimus)": {"static": ["Special-issue Bolt Pistol", "Knives and Fists",
                                                                             "Deathwatch Marksman Bolt Carbine"]},
        "Model§Deathwatch Veteran w/ Stalker bolt rifle (Decimus)": {"static": ["Bolt Pistol", "Knives and Fists"], "slots": {
            "Ranged Weapon": ["Stalker Bolt Rifle", "Plasma Incinerator @pi"]}},
        "Model§Deathwatch Veteran w/ Xenophase blade (Decimus)": {"static": ["Special-issue Bolt Pistol", "Xenophase Blade"]},
        "Model§Gravis Veteran (Decimus)": {"static": ["Bolt Pistol", "Knives and Fists"], "slots": {
            "Loadout": ["Infernus Heavy Bolter", "Frag Cannon @gv", "Hellstorm Bolt Rifle + Grenade Launcher @gv"]}},
        "_limits": [("shield", "1in5", "Maximum 1 Power Weapon and Storm Shield for every 5 models"),
                    ("pi", "1in5", "Maximum 1 Plasma Incinerator for every 5 models"),
                    ("gv", "1in5", "Maximum 1 Frag Cannon or Hellstorm Bolt Rifle for every 5 models")]},
    "Deathwatch Veterans": {
        "Model§Watch Sergeant": {"slots": {"Ranged": ["Boltgun", "Combi-weapon"], "Melee": ["Power Weapon", "Xenophase Blade"]}},
        "Model§Deathwatch Veteran": {"slots": {"Loadout Options": [
            "Boltgun + Power Weapon", "Stalker-pattern Boltgun + Knives and Fists @stalker", "Infernus Heavy Bolter + Knives and Fists @ihb",
            "Deathwatch Shotgun + Knives and Fists @shotgun=0.5", "Heavy Thunder Hammer @hth=0.5", "Frag Cannon + Knives and Fists @frag",
            "Black Shield Blades @bsb", "Boltgun + Storm Shield @shield=0.5", "Power Weapon + Storm Shield @shield=0.5"]}},
        "_drop_rules": ["1 in 5 Frag cannon", "1 in 5 Infernus heavy bolter", "1 in 5 Stalker-pattern boltgun", "2 in 5 Astartes shield",
                        "2 in 5 Deathwatch shotgun", "2 in 5 Deathwatch thunder hammer", "One Black shield blade"],
        "_limits": [("stalker", "1in5", "Maximum 1 Stalker-pattern Boltgun for every 5 models"),
                    ("ihb", "1in5", "Maximum 1 Infernus Heavy Bolter for every 5 models"),
                    ("shotgun", "1in5", "Up to 2 Deathwatch Shotguns for every 5 models"),
                    ("hth", "1in5", "Up to 2 Heavy Thunder Hammers for every 5 models"),
                    ("frag", "1in5", "Maximum 1 Frag Cannon for every 5 models"),
                    ("bsb", 1, "Only 1 Black Shield Blades"),
                    ("shield", "1in5", "Up to 2 Storm Shields for every 5 models")]},
}
