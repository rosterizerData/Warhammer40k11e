# Necrons 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
def staff_of_light(u, own, res):
    """the Overlord's staff of light parent listed a Geomancer tremorglaive as its melee profile"""
    own["Weapon§Overlord—Staff of light"]["assets"]["traits"] = ["Melee Weapon§Overlord—Staff of light", "Ranged Weapon§Overlord—Staff of light"]
    return "staff of light profiles fixed"


SPEC = {
    "Overlord": {"_unit": {"keep": ["Resurrection Orb"], "slots": {"Melee": [
        ("Tachyon arrow and Overlord’s blade", "Tachyon arrow + Overlord’s blade"), ("Staff of light", "W:Staff of light"), "Voidscythe"]}},
        "_patch": staff_of_light},
    "C’tan Shard of the Void Dragon": {"_unit": {"static": ["Voltaic storm", "Canoptek tail blades", "W:Spear of the Void Dragon",
                                                         "R:Spear of the Void Dragon"]}},
    "Tesseract Vault": {"_unit": {"static": ["4x Tesla spheres", "Armoured bulk", "Antimatter Meteor", "Cosmic Fire", "Time’s Arrow"]}},
    "Canoptek Tomb Stalker": {"_rename": {"Tomb Stalker’s claws": "Tomb Stalker claws"}},
    "Canoptek Tomb Sentinel": {"_rename": {"Tomb Sentinel’s claws": "Tomb Sentinel claws"}},
    "The Silent King": {"_rename": {"Scythe of Dust": "Weapons of the Final Triarch", "Close combat weapon": "Armoured bulk"}},
}
