# Chaos Space Marines 11e wargear options. See loadouts.py for the format.
import importlib.util as _u, pathlib as _p
_c = _u.module_from_spec(_s := _u.spec_from_file_location("cc", _p.Path(__file__).with_name("_chaos_common.py"))); _s.loader.exec_module(_c)
def havocs(u, own, res):
    """default: 2 Havocs with Havoc autocannons, 2 with Havoc lascannons"""
    tr = u["assets"]["traits"]
    if any(isinstance(t, dict) and t.get("stats") for t in tr if (t if isinstance(t, str) else t.get("item")) == "Model§Havoc"):
        return "already split"
    u["assets"]["traits"] = [t for t in tr if (t if isinstance(t, str) else t.get("item")) != "Model§Havoc"] + [
        {"item": "Model§Havoc", "quantity": 2},
        {"item": "Model§Havoc", "quantity": 2, "stats": {"Loadout Options": {"value": "Havoc lascannon"}}}]
    return "default 2 autocannons + 2 lascannons"

SPEC = {
    "Havocs": {"_patch": havocs},
    "Chaos Lord on Juggernaut": {"_unit": {"static": ["Close combat weapon", "Bladed horn"], "keep": ["Loadout 1", "Loadout 2"]},
                                 "_rename": {"Plasma pistol – supercharge": "Plasma pistol"}},
    "Decimator": {"_unit": {"static": ["Armoured Feet"], "keep": ["Loadout 1", "Loadout 2", "Unique Loadout"]}},
    "Rapier Carrier": {"_rename": {"Close combat weapon": "Armoured Hull"}},
    "Cultist Mob with firearms": {"_rename": {"Cultist firearm": "Autogun", "Cultist grenade launcher": "Grenade launcher"}},
    "Terrax-pattern Termite": _c.TERMITE,
    "Kratos": _c.KRATOS,
}
