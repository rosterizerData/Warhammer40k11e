# Adeptus Mechanicus 11e wargear options. See loadouts.py for the format.
OPT = lambda w: [("-", "-"), ("✓", w)]
SPEC = {
    "Serberys Sulphurhounds": {"_rename": {"Phosphor blast pistol": "Phosphor Pistol"}},
    "Sicarian Ruststalkers": {
        "Model§Sicarian Ruststalker Princep": {"slots": {"Weapon Options": ["Transonic Razor and Chordclaw", "Transonic Blades and Chordclaw"]}},
        "Model§Sicarian Ruststalker": {"slots": {"Weapon Options": ["Transonic Razor and Chordclaw", "Transonic Blades"]}}},
    "Sicarian Infiltrators": {
        "Model§Sicarian Infiltrator Princep": {"slots": {"Loadout Options": ["Stubcarbine + Power Weapon", "Flechette Blaster + Taser Goad"]}},
        "Model§Sicarian Infiltrator": {"slots": {"Loadout Options": ["Stubcarbine + Power Weapon", "Flechette Blaster + Taser Goad"]}}},
    "Archaeopter Stratoraptor": {"_unit": {"keep": [], "static": ["2x Cognis Heavy Stubber", "2x Heavy Phosphor Blaster",
                                                                 "Twin Cognis Lascannon", "Armoured Hull"],
                                           "slots": {"Wargear": ["Command Uplink", "Chaff Launcher"]}}},
    "Skitarii Vanguard": {"Model§Skitarii Vanguard Alpha": {"static": ["Close Combat Weapon"], "slots": {
        "Ranged Options": [("Radium carbine", "Radium Carbine"), ("Mechanicus pistol", "Mechanicus Pistol")],
        "Optional Alpha Combat Weapon": OPT("Alpha Combat Weapon")}}},
    "Tech-priest Dominus": {"_unit": {"static": ["Omnissian Axe"], "slots": {
        "Loadout Option 1": ["Volkite Blaster", "Eradication Ray"], "Loadout Option 2": ["Macrostubber", "Phosphor Serpenta"]}}},
}
