# World Eaters 11e wargear options. See loadouts.py for the format.
import importlib.util as _u, pathlib as _p
_c = _u.module_from_spec(_s := _u.spec_from_file_location("cc", _p.Path(__file__).with_name("_chaos_common.py"))); _s.loader.exec_module(_c)
HELBRUTE_FIST = ["Helbrute Fist @hbfist", ("Helbrute fist with combi-bolter", "Helbrute Fist + Combi-bolter @hbfist"),
                 ("Helbrute fist with heavy flamer", "Helbrute Fist + Heavy Flamer @hbfist")]
SPEC = {
    "Lord Invocatus": {"_rename": {"Juggernaut’s bladed horn": "Bladed horn"}},
    "Lord on Juggernaut": {"_rename": {"Juggernaut’s bladed horn": "Bladed horn"}},
    "Bloodcrushers": {"_rename": {"Juggernaut’s bladed horn": "Bladed horn"}},
    "Maulerfiend": {"_unit": {"static": ["Maulerfiend Fists"], "slots": {"Weapon": ["Lasher Tendrils", ("2 Magma cutters", "2x Magma Cutters")]}}},
    "Rapier Carrier": {"_rename": {"Close combat weapon": "Armoured Hull"}},
    "Chaos Rhino": {"_unit": {"static": ["Armoured Tracks"], "slots": {
        "Additional": ["-", "Combi-bolter", "Combi-weapon"],
        "Havoc launcher": ["Combi-bolter", "Havoc Launcher", "Combi-bolter + Havoc Launcher"]}}},
    "Helbrute": {"_unit": {"static": ["Close combat weapon"], "slots": {
        "Weapon 1": ["Multi-melta", "Plasma Cannon", "Twin Autocannon", "Twin Heavy Bolter", "Twin Lascannon"] + HELBRUTE_FIST,
        "Weapon 2": ["Missile Launcher", "Helbrute Hammer", "Power Scourge"] + HELBRUTE_FIST}}},
    "Terrax-pattern Termite": _c.TERMITE,
    "Kratos": _c.KRATOS,
}
