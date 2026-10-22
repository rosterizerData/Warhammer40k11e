# Black Templars 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# BT's own Impulsor / Gladiator / Repulsor datasheets add a Multi-melta: overrides of the Space Marines units.
OPT = lambda w: [("-", "-"), ("✓", w)]
MM = {"Multi-melta": OPT("Multi-melta")}
SPEC = {
    "Impulsor": {"_unit": {"static": ["Armoured Hull"], "slots": {
        "Loadout": ["Storm Bolters", "Fragstorm Grenade Launchers"],
        "Heavy stubber": ["-", "Ironhail Heavy Stubber", "Multi-melta"],
        "Upgrade": ["-", "Bellicatus Missile Array", "Orbital Comms Array", "Shield Dome"]}}},
    "Gladiator Lancer": {"_unit": {"add_slots": MM}},
    "Gladiator Valiant": {"_unit": {"add_slots": MM}},
    "Gladiator Reaper": {"_unit": {"add_slots": MM}},
    "Repulsor": {"_unit": {"add_slots": MM}},
    "Repulsor Executioner": {"_unit": {"add_slots": MM}},
    "Castellan": {"_unit": {"slots": {"Melee Option": ["Master-crafted Power Weapon", "Chainsword"],
                                      "Ranged Option": ["Combi-weapon", "Heavy Bolt Pistol"]}}},
    "Execrator": {"_unit": {"static": ["Crozius Arcanum"], "slots": {"Loadout": [
        "Absolvor Bolt Pistol", "Hand Flamer", "Absolvor Bolt Pistol + Master-crafted Power Weapon"]}}},
    "Sword Brethren Squad": {
        "Model§Primaris Sword Brother - Sword Brethren": {"slots": {
            "Melee Options": [("Chainsword", "Chainsword"), ("Master-crafted Power Weapon", "Master-crafted Power Weapon"),
                              ("Thunder Hammer", "Thunder Hammer @th"), ("Twin lightning claws", "Twin Lightning Claws @claw")],
            "Pistol Options": ["Heavy Bolt Pistol", "Hand Flamer @hf=0.5", "Plasma Pistol @pl", "-"]}},
        "_drop_rules": ["1 in 5 models can have a Plasma pistol", "1 in 5 models can have a Thunder hammer",
                        "1 in 5 models can have Twin lightning claws", "2 in 5 models can have a Pyre pistol"],
        "_limits": [("th", "1in4", "Maximum 1 Thunder Hammer for every 4 models"),
                    ("claw", "1in4", "Maximum 1 Twin Lightning Claws for every 4 models"),
                    ("pl", "1in4", "Maximum 1 Plasma Pistol for every 4 models"),
                    ("hf", "1in4", "Up to 2 Hand Flamers for every 4 models")]},
    "Crusader Squad": {
        "Model§Sword Brother": {"static": ["Master-crafted Power Weapon"], "slots": {"Pistol Option": ["Heavy Bolt Pistol", "Hand Flamer"]}},
        "Model§Initiate": {"static": ["Bolt Pistol", "Close combat weapon"], "slots": {"Loadout Options": [
            "Bolt Rifle", "Heavy Bolt Pistol + Initiate Chainsword", "Heavy Bolt Pistol + Power Fist @special=0.5", "Pyreblaster @special=0.5"]}},
        "Model§Neophyte": {"slots": {"Loadout Options": ["Bolt Pistol + Neophyte Chainsword", "Shotgun + Combat Knife"]}},
        "_drop_rules": ["2 in 10 models can have a Power fist or Pyreblaster"],
        "_limits": [("special", "1in10", "Up to 2 Power Fists or Pyreblasters for every 10 models")]},
}
