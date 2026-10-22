# Space Wolves 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
SPEC = {
    "Logan Grimnar": {"_rename": {"The Axe Morkai": "Axe Morkai"}},
    "Ulrik the Slayer": {"_rename": {"Artificer crozius": "Artificer Crozius Arcanum"}},
    "Murderfang": {"_rename": {"The Murderclaws": "Murderclaws"}},
    "Blood Claws": {"_rename": {"Astartes chainsword": "Chainsword"}},
    "Grey Hunters": {"_rename": {"Astartes chainsword": "Chainsword"},
                     "Model§Grey Hunter Pack Leader": {"static": ["Bolt Carbine"], "slots": {
                         "Melee Options": ["Chainsword", "Power Fist", "Power Weapon"], "Ranged Options": ["Bolt Pistol", "Plasma Pistol"]}}},
    "Thunderwolf Cavalry": {
        "Model§Thunderwolf Cavalry Pack Leader": {"static": ["Teeth and Claws", "Wolf Guard Weapon"], "slots": {
            "Pistol Options": ["Bolt Pistol", "Plasma Pistol @plasma", "Boltgun + Storm Shield"]}},
        "Model§Thunderwolf Cavalry": {"static": ["Teeth and Claws", "Wolf Guard Weapon"], "slots": {
            "Pistol Options": ["Bolt Pistol", "Plasma Pistol @plasma", "Boltgun + Storm Shield"]}}},
    "Venerable Dreadnought (SW)": {"_unit": {"drop_ranks": {"Cannon Options": ["Twin lascannon"]}}},
    "Wolf Guard Battle Leader": {"_unit": {"slots": {
        "Loadout Options 1": ["Master-crafted Power Weapon", "Thunder Hammer"],
        "Loadout Options 2": ["Plasma Pistol", "Storm Shield - Battle Leader"]}}},
    "Wolf Guard Headtakers": {"Model§Wolf Guard Headtaker": {"static": ["Heavy Bolt Pistol"], "slots": {
        "Loadout Options": ["Paired Master-crafted Power Weapons", "Master-crafted Power Weapon + Storm Shield - Headtakers"]}}},
    "Wulfen with Storm Shields": {"Model§Wulfen with Storm Shield": {"static": ["Thunder Hammer"], "slots": {
        "Wargear Options": ["Stormfrag Auto-launcher", "Death Totem"]}}},
    "Wolf Scouts": {
        "Model§Wolf Scout": {"slots": {
            "Loadout Options": ["Plasma Pistol + Combat Knife @pp", "Bolt Pistol @swap", "Runic Stave @swap", "Thunderclap @swap",
                                "Instigator Bolt Carbine + Combat Knife @inst", "Plasma Gun + Combat Knife @pg"],
            "Haywire Mine": [("-", "-"), ("✓", "Haywire Mine @hm")]}},
        "Model§Wolf Scout Pack Leader": {"add_slots": {"Haywire Mine": [("-", "-"), ("✓", "Haywire Mine @hm")]}},
        "_drop_rules": ["Only one model can have a Haywire mine", "Only one model can have a plasma gun",
                        "Only one model can have a Runic Stave", "1 in 12 can have an Instigator Bolt Carbine"],
        "_limits": [("swap", 1, "Only 1 Wolf Scout can take a Bolt Pistol, Runic Stave or Thunderclap"),
                    ("inst", "1in12", "Maximum 1 Instigator Bolt Carbine for every 12 models"),
                    ("hm", 1, "Only 1 model can take a Haywire Mine"), ("pg", 1, "Only 1 Wolf Scout can take a Plasma Gun")]},
}
