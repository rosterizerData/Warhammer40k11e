# Tyranids 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
# Unit-wide choices use the book's convention: a unit rank whose `term` is the weapon key, added to every model by a rule.


def spinemaws(u, own, res):
    st = u["stats"]["Spinemaws"]
    st["ranks"] = {"-": {"order": 0}, "✓": {"order": 1, "term": "Ranged Weapon§Ripper Swarms—Spinemaws"}}
    return "Spinemaws rank carries its weapon (unit-wide choice)"


def harpoon(u, own, res):
    """the 11e toxinjector harpoon's ranged profile keeps the [HARPOONED] ability the 10e toxic harpoons had"""
    a = own["Ranged Weapon§Norn Assimilator—Toxinjector Harpoon"].setdefault("assets", {}).setdefault("traits", [])
    if "Ability§Harpooned" not in a:
        a.append("Ability§Harpooned")
    return "harpooned on the ranged harpoon"


SPEC = {
    "Ripper Swarms": {"_patch": spinemaws},
    "Tyranid Warriors with Melee Bio-weapons": {"_rename": {"Bio-weapons": "Tyranid Warrior claws and talons"}},
    "Tyranid Warriors with Ranged Bio-weapons": {"_rename": {"Bio-weapons": "Tyranid Warrior claws and talons"}},
    "Norn Assimilator": {"_unit": {"static": ["Monstrous scything talons", "R:Toxinjector Harpoon", "M:Toxinjector harpoon"]},
                         "_patch": harpoon},
}
