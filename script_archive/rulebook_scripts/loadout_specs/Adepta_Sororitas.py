# Adepta Sororitas 11e wargear options. See loadouts.py for the format.
import json
OPT = lambda w: [("-", "-"), ("✓", w)]


def canoness_tallies(u, own, res):
    """the brazier / null rod rules count the Canoness's chainsword by name; 11e calls it a hallowed chainsword"""
    txt = json.dumps(u.get("rules") or {}, ensure_ascii=False).replace('"tally", "Chainsword"', '"tally", "Hallowed chainsword"')
    u["rules"] = json.loads(txt)
    return "rule tallies → Hallowed chainsword"


SPEC = {
    "Canoness": {"_rename": {"Chainsword": "Hallowed Chainsword"}, "_patch": canoness_tallies},
    "Zephyrim Squad": {"Model§Zephyrim Superior": {"static": ["Power Weapon"], "slots": {
        "Pistol Options": ["Bolt Pistol", "Plasma Pistol"], "Optional Banner": OPT("Sacred Banner")}}},
    "Celestian Sacresants": {
        "Model§Sacresant Superior": {"slots": {
            "Melee Options": ["Hallowed Mace", "Anointed Halberd", "Spear of the Faithful"],
            "Pistol Options": ["Bolt Pistol", "Inferno Pistol", "Ministorum Hand Flamer", "Plasma Pistol"]}},
        "Model§Celestian Sacresant": {"static": ["Bolt Pistol"], "slots": {"Melee Options": ["Hallowed Mace", "Anointed Halberd"]}}},
}
