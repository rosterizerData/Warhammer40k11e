# Adeptus Custodes 11e wargear options. See loadouts.py for the format.
OPT = lambda w: [("-", "-"), ("✓", w)]
def _size(lo, hi, drop=(), counts=()):
    """MFM 1.6 brackets (= the 11e codex sizes): a numeric Models stat clamped to the priced sizes, plus the unit's
    hidden per-model count stats (`counts`) that the core tally rules check against"""
    def patch(u, own, res):
        m = u["stats"].setdefault("Models", {"dynamic": True, "group": "Loadout", "groupOrder": 2, "statOrder": 1, "statType": "numeric", "tracked": True, "visibility": "normal"})
        m.update({"min": lo, "max": hi, "value": max(lo, min(hi, m.get("value") or lo))})
        if lo == hi:
            m.pop("increment", None)
        for c in counts:
            u["stats"][c].update({"min": lo, "max": hi})
        for r in drop:
            u.get("rules", {}).pop(r, None)
        return f"Models {lo}–{hi}" + (f", dropped {list(drop)}" if drop else "")
    return patch


SPEC = {
    "Venatari with Kinetic Destroyers": {"_patch": _size(3, 3)},
    "Custodian Wardens": {"_patch": _size(2, 3, counts=("Custodian Warden",))},
    "Venerable Contemptor Dreadnought": {"_rename": {"Contemptor combat weapon": "Contemptor Fist"}},
    "Trajann Valoris": {"_unit": {"static": ["W:Eagle’s Scream", "M:Watcher’s Axe"]}},
    "Shield-captain": {"_unit": {"slots": {"Spear Options": [
        "W:Pyrithite Spear + Praesidium Shield", "Eternity-pattern Paragon Blade + Praesidium Shield", "W:Castellan Axe", "W:Guardian Spear"]}}},
    "Shield-captain on Dawneagle Jetbike": {"_unit": {"static": ["Interceptor Lance"], "slots": {
        "Ranged Options": ["Salvo Launcher", "Hurricane Bolter"]}}},
    "Allarus Custodians": {"_patch": _size(2, 3, counts=("Allarus Custodian",)), "Model§Allarus Custodian": {"static": ["Balistus Grenade Launcher"], "slots": {
        "Spear Options": ["W:Guardian Spear", "W:Castellan Axe"], "Vexilla": OPT("Vexilla @vexilla")}},
        "_drop_stats": ["Vexilla"], "_drop_rules": ["applyVexilla", "Maximum 1 Vexilla"],
        "_limits": [("vexilla", 1, "Maximum 1 Vexilla")]},
    "Vertus Praetors": {"Model§Vertus Praetor": {"static": ["Interceptor Lance"], "slots": {
        "Ranged Options": ["Salvo Launcher", "Hurricane Bolter"]}}},
    "Contemptor-Achillus Dreadnought": {"_unit": {"static": ["R:Dreadspear", "M:Dreadspear"], "slots": {
        "Loadout": ["2x Lastrum Storm Bolter", "2x Adrathic Combi-destructor", "2x Twin Infernus Incinerator"]}}},
    "Caladius Grav-tank": {"_unit": {"static": ["Armoured Hull", "Iliastus Accelerator Cannon"], "slots": {
        "Loadout Options": ["Twin Lastrum Bolt Cannon", "Twin Neutronium Cascade Projectors"]}}},
    "Coronus Grav-carrier": {"_unit": {"static": ["Armoured Hull", "Twin Arachnus Blaze Cannon"], "slots": {
        "Loadout Options": ["Twin Lastrum Bolt Cannon", "Twin Neutronium Cascade Projectors"]}}},
    "Caladius Annihilator Grav-Tank": {"_unit": {"static": ["Armoured Hull", "Arachnus Blaze Carronade"], "slots": {
        "Loadout Options": ["Twin Lastrum Bolt Cannon", "Twin Neutronium Cascade Projectors"]}}},
    "Pallas Grav-attack": {"_unit": {"static": ["Armoured Hull"], "slots": {
        "Loadout Options": ["Twin Arachnus Blaze Cannon", "Twin Iliastus Accelerator Fusil"]}}},
    "Telemon Heavy Dreadnought": {"_unit": {"static": ["Spiculus Bolt Launcher"], "slots": {"Loadout": [
        "Dual Caestus Fists + 2x Twin Neutronium Cascade Projectors",
        "Adrathic Desolator + Caestus Fist + Twin Neutronium Cascade Projectors",
        "Arachnus Storm Cannon + Caestus Fist + Twin Neutronium Cascade Projectors",
        "Caestus Fist + Iliastus Accelerator Culverin + Twin Neutronium Cascade Projectors"]}},
        "_drop_rules": ["moreAttackif2Caestus"]},
    "Contemptor-Galatus Dreadnought": {"_unit": {"static": ["R:Warblade", "M:Warblade"]}},
    "Knight-centura": {"_unit": {"slots": {"Loadout Options": [
        "Executioner Greatblade", "Master-crafted Boltgun + Gun Stock", "Master-crafted Flamer + Gun Stock"]}}},
    "Custodian Guard Sodality with Adrasite Spears": {
        "Model§Custodian Guard with Adrasite and Pyrithite Spear": {"static": ["W:Adrasite Spear"]}},
    "Custodian Guard Sodality": {"_patch": _size(3, 3, ("costForFinalModel",), ("Custodian Guard",)), "Model§Custodian Guard": {"static": ["W:Guardian Spear"], "slots": {"Vexilla": OPT("Vexilla @vexilla")}},
        "_drop_stats": ["Vexilla"], "_drop_rules": ["applyVexilla", "Maximum 1 Vexilla"],
        "_limits": [("vexilla", 1, "Maximum 1 Vexilla")]},
    "Custodian Guard Sodality with Pyrithite Spears": {"_unit": {"static": ["R:Pyrithite Spear", "M:Pyrithite Spear"]}},
    "Sentinel Guard Sodality": {"_patch": _size(3, 3), "_unit": {"static": ["R:Sentinel Blade", "M:Sentinel Blade", "U:Praesidium Shield"],
                                          "slots": {"Vexilla": OPT("Vexilla")}}},
    "Prosecutor Squad": {"_rename": {"Close combat weapon": "Gun Stock"}},
    "Witchseeker Squad": {"_rename": {"Close combat weapon": "Gun Stock", "Witchseeker flamer": "Flamer"}},
    "Venatari with Verutum Lances": {"_patch": _size(3, 3), "Model§Venatari Custodian": {"static": ["R:Verutum Lance", "M:Verutum Lance"]}},
    "Aquilon Terminators with Solarite Power Gauntlets": {"_patch": _size(3, 3), "Model§Aquilon Custodian": {"static": [
        "Adrathic Combi-destructor", "Solarite Power Gauntlet"]}},
    "Aquilon Terminators with Solarite Power Talons": {"_patch": _size(3, 3), "_unit": {"static": ["Solarite Power Talon"], "slots": {
        "Ranged Options": ["Lastrum Storm Bolter", "Infernus Firepike"]}}},
    "Gyrfalcon Jetbike Sodality": {"_patch": _size(2, 2), "_unit": {"static": ["Solarite Power Lance"], "slots": {
        "Ranged Options": ["Lastrum Bolt Cannon", "Adrathic Devastator", "Arachnus Volley Cannon", "Twin Corvae Las-pulser"]}}},
}

# Legends sodalities: the MFM 1.6 Legends entries price 3 models
for _n, _p in {"Custodian Guard Sodality with Adrasite Spears": _size(3, 3, counts=("Custodian Guard with Adrasite and Pyrithite Spear",)),
               "Sagittarum Custodians Sodality": _size(3, 3, counts=("Sagittarum Custodian",))}.items():
    SPEC.setdefault(_n, {})["_patch"] = _p
