# Imperium hub 11e wargear options (shared units whose options are the same for every consumer). See loadouts.py.


def drop_hekhtur(u, own, res):
    """11e: Sir Hekhtur is his own datasheet, no longer a model in Canis Rex"""
    tr = (u.get("assets") or {}).get("traits") or []
    if "Model§Sir Hekhtur" not in tr:
        return "already done"
    tr.remove("Model§Sir Hekhtur")
    return "Sir Hekhtur model removed (own datasheet in 11e)"


SPONSON = {"Sponson Weapon": ["-", "Twin Icarus Autocannon", "Stormspear Rocket Pod", "Ironstorm Missile Pod"]}

OPT = lambda w: [("-", "-"), ("✓", w)]

SPEC = {
    "Knight Paladin": {"_unit": {"add_slots": SPONSON}},
    "Knight Errant": {"_unit": {"add_slots": SPONSON}},
    "Knight Warden": {"_unit": {"add_slots": SPONSON}},
    "Knight Gallant": {"_unit": {"add_slots": SPONSON}},
    "Knight Crusader": {"_unit": {"add_slots": SPONSON}},
    "Knight Preceptor": {"_unit": {"add_slots": {**SPONSON, "Pintle Weapon": [
        "Questoris Multi-laser", "Meltagun", "Questoris Heavy Stubber"]}}},
    "Canis Rex": {"Model§Canis Rex": {"static": ["Las-impulsor", "Questoris Multi-laser", "Freedom’s Hand"]}, "_patch": drop_hekhtur},
    "Armiger Helverin": {"_unit": {"static": ["Armoured Feet", "2x Armiger Autocannon"], "slots": {
        "Sponson Weapon": ["Questoris Heavy Stubber", "Meltagun"]}}},
    "Armiger Warglaive": {"_unit": {"static": ["Thermal Spear", "Reaper Chain-cleaver"], "slots": {
        "Sponson Weapon": ["Questoris Heavy Stubber", "Meltagun"]}}},
    # ---- Agents of the Imperium (mirror the Deathwatch book's Veterans / Decimus / Corvus)
    "Corvus Blackstar (Agents)": {"_unit": {"static": ["Armoured Hull"], "slots": {
        "Rocket Options": ["2x Blackstar Rocket Launcher", "2x Stormstrike Missile Launcher"],
        "Cannon Options": ["Twin Assault Cannon", "Twin Lascannon"], "Hurricane bolter": OPT("Hurricane Bolter")}}},
    "Deathwatch Kill Team": {
        "Model§Watch Sergeant (Agents)": {"slots": {"Ranged": ["Boltgun", "Combi-weapon"], "Melee": ["Power Weapon", "Xenophase Blade"]}},
        "Model§Deathwatch Veteran (Agents)": {"slots": {"Loadout Options": [
            "Boltgun + Power Weapon", "Stalker-pattern Boltgun + Knives and Fists @stalker", "Infernus Heavy Bolter + Knives and Fists @ihb",
            "Deathwatch Shotgun + Knives and Fists @shotgun=0.5", "Heavy Thunder Hammer @hth=0.5", "Frag Cannon + Knives and Fists @frag",
            "Black Shield Blades @bsb", "Boltgun + Astartes Shield (Agents) @shield=0.5", "Power Weapon + Astartes Shield (Agents) @shield=0.5"]}},
        "_drop_rules": ["1 in 5 models can have a Frag cannon", "1 in 5 models can have a Infernus heavy bolter",
                        "1 in 5 models can have a Stalker-pattern boltgun", "2 in 5 models can have a shield",
                        "2 in 5 models can have a shotgun", "2 in 5 models can have a thunder hammer", "Only one model can use Black Shield blades",
                        "Up to 2 Astartes Shield (Agents)s for every 5 models"],
        "_limits": [("stalker", "1in5", "Maximum 1 Stalker-pattern Boltgun for every 5 models"),
                    ("ihb", "1in5", "Maximum 1 Infernus Heavy Bolter for every 5 models"),
                    ("shotgun", "1in5", "Up to 2 Deathwatch Shotguns for every 5 models"),
                    ("hth", "1in5", "Up to 2 Heavy Thunder Hammers for every 5 models"),
                    ("frag", "1in5", "Maximum 1 Frag Cannon for every 5 models"),
                    ("bsb", 1, "Only 1 Black Shield Blades"),
                    ("shield", "1in5", "Up to 2 Astartes Shields for every 5 models")]},
    "Aquila Kill Team": {
        "Model§Kill Team Sergeant (Aquila)": {"static": ["Plasma Pistol", "Power Weapon"]},
        "Model§Deathwatch Veteran w/ Heavy thunder hammer (Aquila)": {"static": ["Bolt Pistol"], "slots": {
            "Ranged Weapon": ["Heavy Thunder Hammer", "Power Weapon + Astartes Shield (Agents) @shield"]}},
        "Model§Deathwatch Veteran w/ Marksman bolt carbine (Aquila)": {"static": ["Special-issue Bolt Pistol", "Knives and Fists",
                                                                            "Deathwatch Marksman Bolt Carbine"]},
        "Model§Deathwatch Veteran w/ Stalker bolt rifle (Aquila)": {"static": ["Bolt Pistol", "Knives and Fists"], "slots": {
            "Ranged Weapon": ["Stalker Bolt Rifle", "Plasma Incinerator @pi"]}},
        "Model§Deathwatch Veteran w/ Xenophase blade (Aquila)": {"static": ["Special-issue Bolt Pistol", "Xenophase Blade"]},
        "Model§Gravis Veteran (Aquila)": {"static": ["Bolt Pistol", "Knives and Fists"], "slots": {
            "Loadout": ["Infernus Heavy Bolter", "Frag Cannon @gv", "Hellstorm Bolt Rifle + Grenade Launcher @gv"]}},
        "_drop_rules": ["Maximum 1 Power Weapon and Astartes Shield (Agents) for every 5 models"],
        "_limits": [("shield", "1in5", "Maximum 1 Power Weapon and Astartes Shield for every 5 models"),
                    ("pi", "1in5", "Maximum 1 Plasma Incinerator for every 5 models"),
                    ("gv", "1in5", "Maximum 1 Frag Cannon or Hellstorm Bolt Rifle for every 5 models")]},
}
