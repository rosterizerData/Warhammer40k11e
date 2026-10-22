# Thousand Sons 11e wargear options. See loadouts.py for the format.
import importlib.util as _u, pathlib as _p
_c = _u.module_from_spec(_s := _u.spec_from_file_location("cc", _p.Path(__file__).with_name("_chaos_common.py"))); _s.loader.exec_module(_c)
OPT = lambda w: [("-", "-"), ("✓", w)]
PREDATOR = lambda main: {"_unit": {"static": ["Armoured Tracks", main], "slots": {
    "Sponsons": ["-", "2x Lascannon", "2x Inferno Heavy Bolter"], "Additional": ["-", "Inferno Combi-bolter", "Inferno Combi-weapon"],
    "Havoc launcher": OPT("Havoc Launcher")}}}
SPEC = {
    "Sorcerer in Terminator Armour": {"_rename": {"Coruscating Flames": "Gaze of Hate"}},
    "Tzaangor Shaman": {"_rename": {"Shaman’s stave": "Force Stave"}},
    "Rapier Carrier": {"_rename": {"Close combat weapon": "Armoured Hull"}},
    "Chaos Predator Annihilator": PREDATOR("Predator Twin Lascannon"),
    "Chaos Predator Destructor": PREDATOR("Predator Autocannon"),
    "Chaos Rhino": {"_unit": {"static": ["Armoured Tracks"], "slots": {
        "Additional": ["-", "Inferno Combi-bolter", "Inferno Combi-weapon"],
        "Havoc launcher": ["Inferno Combi-bolter", "Havoc Launcher", "Inferno Combi-bolter + Havoc Launcher"]}}},
    "Defiler": {"_unit": {"static": ["Shearing Claws"], "keep": ["Loadout 1", "Loadout 3", "Loadout 4"], "slots": {
        "Loadout 2": ["2x Excruciator Cannon", "2x Pyraflux Magma Cutters"]}}},
    "Terrax-pattern Termite": _c.TERMITE,
    "Kratos": _c.KRATOS,
}
