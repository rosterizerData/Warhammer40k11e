# Death Guard 11e wargear options. See loadouts.py for the format.
import importlib.util as _u, pathlib as _p
_c = _u.module_from_spec(_s := _u.spec_from_file_location("cc", _p.Path(__file__).with_name("_chaos_common.py"))); _s.loader.exec_module(_c)
OPT = lambda w: [("-", "-"), ("✓", w)]
PREDATOR = lambda main: {"_unit": {"static": ["Armoured Tracks", main], "slots": {
    "Loadout 1": ["-", "2x Lascannon", "2x Heavy Bolter"], "Loadout 2": ["-", "Combi-weapon", "Combi-bolter"],
    "Havoc Launcher": OPT("Havoc Launcher")}}}
SPEC = {
    "Blightlord Terminators": {"_rename": {"Plague combi-bolter": "Combi-bolter"}},
    "Icon Bearer": {"_rename": {"Plague boltgun": "Boltgun"}},
    "Malignant Plaguecaster": {"_rename": {"Plague bolt pistol": "Bolt Pistol"}},
    "Plague Surgeon": {"_rename": {"Plague bolt pistol": "Bolt Pistol"}},
    "Lord of Contagion": {"_unit": {"static": ["Manreaper"]}},
    "Lord of Virulence": {"_unit": {"static": ["Twin Plague Spewer", "Power Fist"]}},
    "Miasmic Malignifier": {"_unit": {"static": ["Miasmic Gouts"]}},
    "Mortarion": {"_rename": {"The Lantern": "Lantern"}},
    "Typhus": {"_unit": {"static": ["Lakrimae"]}},
    "Death Guard Possessed": {"Model§Possessed Champion": {"drop_stats": ["Chaos Icon"]},
                              "Model§Possessed": {"drop_stats": ["Chaos Icon"]}},
    "Rapier Carrier": {"_rename": {"Close combat weapon": "Armoured Hull"}},
    "Chaos Rhino": {"_unit": {"static": ["Armoured Tracks"], "slots": {
        "Loadout Options 1": ["-", "Combi-bolter", "Combi-weapon"],
        "Loadout Options 2": ["Combi-bolter", ("Havoc launcher", "Havoc Launcher"), ("Combi-bolter & Havoc Launcher", "Combi-bolter + Havoc Launcher")]}}},
    "Chaos Land Raider": {"_unit": {"static": ["2x Soulshatter Lascannon", "Twin Heavy Bolter", "Armoured Tracks"], "slots": {
        "Loadout Options": ["-", "Combi-bolter", "Combi-weapon"], "Havoc Launcher": OPT("Havoc Launcher")}}},
    "Chaos Predator Annihilator": PREDATOR("Predator Twin Lascannon"),
    "Chaos Predator Destructor": PREDATOR("Predator Autocannon"),
    "Helbrute": {"_unit": {"static": ["Close combat weapon"], "slots": {
        "Loadout 1": ["Multi-melta", "Plasma Cannon", "Twin Autocannon", "Twin Lascannon", "Twin Heavy Bolter", "Helbrute Fist @hbfist"],
        "Loadout 2": ["Helbrute Fist @hbfist", "Missile Launcher", "Helbrute Hammer", "Power Scourge"],
        "1 per Helbrute fist": [("-", "-"), ("1 Combi-bolter", "Combi-bolter @special"), ("2 Combi-bolters", "2x Combi-bolter @special=2"),
                                ("1 Heavy flamer", "Heavy Flamer @special"), ("2 Heavy flamers", "2x Heavy Flamer @special=2"),
                                ("Heavy flamer & Combi-bolter", "Heavy Flamer + Combi-bolter @special=2")]}}},
    "Terrax-pattern Termite": _c.TERMITE,
    "Kratos": _c.KRATOS,
}
