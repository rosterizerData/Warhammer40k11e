# Orks 11e wargear options (Waha Datasheets_options). See loadouts.py for the format.
import copy

NOB_BOYZ = ["Kustom Choppa + Kombi-skorcha", "Kustom Choppa + Kombi-rokkit", "Kustom Choppa + Kustom Shoota",
            "Power Klaw + Kombi-skorcha", "Power Klaw + Kombi-rokkit", "Power Klaw + Kustom Shoota", "Big Choppa"]
NOBZ = ["Kustom Krumpa + Kustom Shoota", "Kustom Krumpa + Kombi-rokkit", "Kustom Krumpa + Paired Krumpas @paired",
        "Big Skorcha + Kustom Choppa @skorcha", "Kustom Big Shoota + Kustom Choppa @kbs", "Big Choppa @bigchoppa"]
OPT = lambda w: [("-", "-"), ("✓", w)]                       # "can be equipped with 1 X"
UPTO = lambda w, k: [(str(i), " + ".join([w] * i) if i else "-") for i in range(k + 1)]   # "up to k X"


def nob_sizes(nob, boy, sizes):
    """1 Nob per 10 models: numeric Models + modelKey fill the Boys (core rules count included models too);
    a rule ahead of the core model tally (order 30) sets the Nob count for the bigger size"""
    def patch(u, own, res):
        tr = [t for t in u["assets"]["traits"] if (t if isinstance(t, str) else t.get("item")) not in (nob, boy)]
        u["assets"]["traits"] = tr + [nob, {"item": boy, "quantity": sizes[0][0] - sizes[0][1]}]
        st = u["stats"]
        st["Models"] = {"increment": {"value": sizes[1][0] - sizes[0][0]}, "max": sizes[-1][0], "min": sizes[0][0],
                        "value": sizes[0][0], "visibility": "normal"}
        st["modelKey"] = {"value": boy}
        st[boy.split("§")[1]] = {"max": sizes[-1][0] - sizes[-1][1], "min": sizes[0][0] - sizes[0][1], "statType": "numeric",
                                 "tracked": True, "value": 0, "visibility": "hidden"}
        label = ((res.get(nob) or {}).get("aspects") or {}).get("Label") or nob.split("§")[1]   # tallies count by Label
        st.pop(nob.split("§")[1], None)
        st[label] = {"max": sizes[-1][1], "min": sizes[0][1], "statType": "numeric", "tracked": True, "value": 0,
                     "visibility": "hidden"}
        for size, nobs in sizes[1:]:
            u.setdefault("rules", {})[f"{nobs} {label}s at {size} models"] = {
                "actions": [{"actionType": "set", "iterations": 1, "paths": [["{self}", "traits", "item", nob, "quantity"]], "value": nobs}],
                "evals": [{"actionable": True, "not": False, "operator": "AND",
                           "paths": [["{self}", "stats", "Models", "processed", "numeric", "current"]], "value": size}],
                "evaluate": "AND", "failState": "pass", "order": 20}
        return f"Nobs by size {sizes}"
    return patch


def to_multi(model, cost2):
    """single-model asset → unit of 1–2 models (Warbuggies pattern); model stats + weapons move to a Model§"""
    def patch(u, own, res):
        mk = f"Model§{model}"
        if mk in own:
            return "already split"
        st = u["stats"]
        m = {"stats": {s: st.pop(s) for s in ("Ld", "M", "OC", "Sv", "T", "W") if s in st}}
        tr = u["assets"]["traits"]
        m["assets"] = {"traits": [t for t in tr if (t if isinstance(t, str) else t.get("item")).split("§")[0].endswith("Weapon")]}
        u["assets"]["traits"] = [t for t in tr if t not in m["assets"]["traits"]] + [{"item": mk, "quantity": 1}]
        own[mk] = m
        u.pop("aspects", None)
        u.setdefault("allowed", {}).setdefault("items", []).append(mk)
        st.update({"model1stTally": {"value": 1}, "model2ndCost": {"value": cost2}, "model2ndTally": {"value": 2},
                   "modelKey": {"value": mk}, "Models": {"increment": {"value": 1}, "max": 2, "min": 1, "value": 1, "visibility": "normal"},
                   model: {"max": 2, "min": 1, "statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}})
        return f"split into {mk} x1–2"
    return patch


def gretchin(u, own, res):
    """11e: 10–20 Gretchin, the Runtherd is its own datasheet"""
    if "Runtherds" not in u["stats"]:
        return "already done"
    u.pop("removed", None)   # it stripped the core Models stat + model-count rules for the old Runtherd tallies
    u["assets"]["traits"] = [t for t in u["assets"]["traits"] if t not in ("Model§Runtherd", "Ability§Runtherd")]
    for r in ["appliedGretchinTally", "appliedRuntherdTally", "applyMissingGretchins", "applyMissingRuntherds",
              "applyMoreGretchins", "applyMoreRuntherds", "trueGretchinTally", "trueRuntherdTally"]:
        u["rules"].pop(r)
    st = u["stats"]
    st.pop("Runtherds"); st.pop("Gretchins")
    st.update({"model1stTally": {"value": 10}, "model2ndTally": {"value": 20}, "modelKey": {"value": "Model§Gretchin"},
               "Models": {"increment": {"value": 10}, "max": 20, "min": 10, "value": 10, "visibility": "normal"},
               "Gretchin": {"max": 20, "min": 10, "statType": "numeric", "tracked": True, "value": 0, "visibility": "hidden"}})
    return "Runtherd model/ability and its tally rules removed; standard Models 10–20"


def ghaz(u, own, res):
    if "Model§Makari" not in u["assets"]["traits"]:
        return "already done"
    u["assets"]["traits"].remove("Model§Makari")
    return "Makari model removed (11e: part of his ability)"


def battlewagon(u, own, res):
    for t in u["assets"]["traits"]:
        if isinstance(t, dict) and t.get("item") == "Ability§Transport":
            t["text"] = ("\n\nThis model has a transport capacity of 22 Orks Infantry models. Each Mega Armour/Jump Pack model "
                         "takes up the space of 2 models. Each Ghazghkull Thraka model takes up the space of 4 models.")
    return "transport text → 11e"


def beast_snaggas(u, own, res):
    a = u["rules"]["applyThumpGun"]["actions"][1]["value"]["stats"]["Loadout Options"]
    a["value"] = "Choppa, Slugga & Thump Gun"
    return nob_sizes("Model§Beast Snagga Nob", "Model§Beast Snagga Boy", [(10, 1), (20, 2)])(u, own, res)


KILL_TANK_GUN = ["-", "Kannon @rollagun @kannon", "Lobba @rollagun @lobba", "Zzap Gun @rollagun"]

SPEC = {
    # ---- characters
    "Warboss": {"_unit": {"slots": {
        "Melee Options": ["Kustom Choppa", "Power Klaw"],
        "Ranged Options": ["Kustom Shoota", "Kombi-rokkit", "Kombi-skorcha"]}}},
    "Warboss on Warbike": {"_unit": {"static": ["Dual Dakkagun"], "slots": {
        "Melee Option": ["Killsaw", "Big Choppa", "Power Klaw"]}}},
    "Weirdboy": {"_unit": {"static": ["Power Vomit", "Copper Staff"]}},
    "Big Mek in Mega Armour": {"_unit": {"static": ["Power Klaw"], "slots": {
        "Ranged Options": ["Kustom Shoota", "Killsaw", "Kombi-weapon", "Kustom Mega-blasta"],
        "Optional Wargear": ["-", "Tellyport Blasta", "Kustom Force Field"]}}},
    "Ghazghkull Thraka": {"Model§Ghazghkull Thraka – Epic Hero": {"static": ["Adamantine ’Eadbutt", "Gork’s Klaw", "Mork’s Roar"]},
                          "_patch": ghaz},
    "Boss Snikrot": {"_unit": {"static": ["Mork’s Teef", "Slugga"]}},
    "Mek": {"_unit": {"static": ["Kustom Mega-slugga", "Mek’s Toolz"]}},
    "Painboy": {"_unit": {"static": ["Dok’s Toolz", "’Urty Syringe"]}},
    "Big Mek with Shokk Attack Gun": {"_unit": {"static": ["Big Mek’s Toolz", "Shokk Attack Gun"]}},
    "Deffkilla Wartrike": {"_unit": {"static": ["Boomstikks", "R:Snagga Klaw", "M:Snagga Klaw", "M:Killa Jet"]}},
    "Beastboss": {"_unit": {"static": ["Shoota", "Beast Snagga Klaw and Beastchoppa"]}},
    "Painboss": {"_unit": {"static": ["Beast Snagga Klaw"]}},
    "Bannernob": {"_unit": {"static": ["Kustom Choppa", "Shoota"]}},
    "Bigboss": {"_unit": {"static": ["Big Choppa", "Slugga"]}},
    "Nazdreg": {"_unit": {"static": ["R:Kustom Blasta X", "M:Kustom Blasta X", "Moonchewa"]}},
    # ---- infantry
    "Boyz": {
        "Model§Boss Nob - Boy": {"slots": {"Loadout Options": NOB_BOYZ}},
        "Model§Boy": {"static": ["Choppa", "Slugga"], "slots": {
            "Ranged Options": ["Shoota", "Big Shoota @bigshoota", "Rokkit Launcha @rokkit", "Burna @burna"]}},
        "_drop_rules": ["Maximum 1 Special weapon for every 10 models"],
        "_limits": [("bigshoota", "1in10", "Maximum 1 Big Shoota for every 10 models"),
                    ("rokkit", "1in10", "Maximum 1 Rokkit Launcha for every 10 models"),
                    ("burna", "1in10", "Maximum 1 Burna for every 10 models")],
        "_patch": nob_sizes("Model§Boss Nob - Boy", "Model§Boy", [(10, 1), (20, 2)])},
    "Gretchin": {"Model§Gretchin": {"static": ["Grot Blasta", "Scavenged Shivs"]}, "_patch": gretchin},
    "Burna Boyz": {"Model§Burna Boy": {"static": ["Burna", "Cuttin' Flames"]}},
    "Lootas": {
        "Model§Spanner": {"static": ["Gun Stock and Fists"], "slots": {
            "Ranged Options": ["Big Shoota", "Kustom Mega-blasta", "Rokkit Launcha"]}},   # shared with Burna Boyz
        "Model§Loota": {"static": ["Deffgun", "Gun Stock and Fists"]}},
    "Tankbustas": {
        "Model§Boss Nob - Tankbusta": {"static": ["Choppa"], "slots": {
            "Loadout": ["2x Rokkit Pistol", "Rokkit Pistol + Smash Hammer"]}},
        "Model§Tankbusta": {"static": ["Gitstikka"], "slots": {
            "Loadout Options": ["Busta Rokkit Launcha", "2x Busta Rokkit Launcha @extra", "Busta Rokkit Launcha + Pulsa Rokkit @extra"]}},
        "_drop_rules": ["Only 1 model can carry 2 rokkit launchas", "Only 1 model can carry a pulsa rokkit"],
        "_limits": [("extra", 1, "Only 1 model can take an extra Busta Rokkit Launcha or a Pulsa Rokkit")]},
    "Nobz": {
        "Model§Boss Nob - Nob": {"slots": {"Loadout Options": NOBZ}},
        "Model§Nob": {"slots": {"Loadout Options": NOBZ}},
        "_drop_stats": ["Ammo Runts"],
        "_drop_rules": ["Maximum 1 Ammo Runt for every 5 models"],
        "_limits": [("skorcha", "1in5", "Maximum 1 Big Skorcha for every 5 models"),
                    ("kbs", "1in5", "Maximum 1 Kustom Big Shoota for every 5 models"),
                    ("bigchoppa", "1in5", "Maximum 1 Big Choppa for every 5 models"),
                    ("paired", "1in5", "Maximum 1 Paired Krumpas for every 5 models")]},
    "Meganobz": {"Model§Meganob": {"slots": {"Loadout Options": [
        "Kustom Shoota + Power Klaw", "Kombi-weapon + Power Klaw", "Kustom Shoota + Killsaw", "Kombi-weapon + Killsaw",
        "Twin Killsaws"]}}},
    "Kommandos": {
        "Model§Boss Nob - Kommando": {"static": ["Slugga"], "slots": {"Loadout Options": ["Choppa", "Big Choppa", "Power Klaw"]}},
        "Model§Kommando": {"slots": {"Loadout Options": [
            "Choppa + Slugga", "Choppa + Slugga + Burna @burna", "Choppa + Slugga + Rokkit Launcha @rokkit",
            "Breacha Ram + Slugga @ram", "Choppa + Slugga + Kustom Shoota @kshoota"]}},
        "_drop_stats": ["Bomb Squig", "Distraction Grot"],
        "_drop_rules": ["Maximum 1 Breach Ram", "Maximum 1 Burna", "Maximum 1 Rokkit launcha", "Maximum 2 Speshul shootas"],
        "_limits": [("burna", 1, "Maximum 1 Burna"), ("rokkit", 1, "Maximum 1 Rokkit Launcha"),
                    ("ram", 1, "Maximum 1 Breacha Ram"), ("kshoota", 2, "Maximum 2 Kustom Shootas")]},
    "Stormboyz": {"Model§Boss Nob - Stormboy": {"static": ["Slugga"], "slots": {"Melee Options": ["Kustom Choppa", "Power Klaw"]}}},
    "Flash Gitz": {"_drop_stats": ["Ammo Runt"]},
    "Breaka Boyz": {
        "Model§Boss Nob - Breaka Boy": {"static": ["Choppa", "Rokkit Pistol"], "slots": {"Loadout": ["Smash Hammer", "Rokkit Pistol"]}},
        "Model§Breaka Boy": {"slots": {"Loadout Options": ["Smash Hammer", "Knucklebustas @knuckle", "Tankhammer @tank"]}}},
    "Beast Snagga Boyz": {
        "Model§Beast Snagga Nob": {"static": ["Power Snappa", "Slugga"]},
        "Model§Beast Snagga Boy": {"slots": {"Loadout Options": [
            ("Slugga & Choppa", "Slugga + Choppa"), ("Choppa, Slugga & Thump Gun", "Choppa + Slugga + Thump Gun @special")]}},
        "_patch": beast_snaggas},
    "Squighog Boyz": {
        "Model§Nob on Smasha Squig": {"static": ["Big Choppa", "Slugga", "Squig’s Jaws"]},
        "Model§Squighog Boy": {"static": ["Saddlegit’s Shiv", "Squig’s Jaws", "W:Stikka"]},
        "_drop_stats": ["Bomb Squigs"], "_drop_rules": ["Maximum 1 Squig for every 4 models"]},
    # ---- vehicles / walkers / bikes
    "Trukk": {"_unit": {"static": ["Spiked Ram"], "slots": {
        "Ranged Options": ["Dual Big Shoota", "Rokkit Launcha"],
        "Melee Options": ["-", "Buzzsaw", "Grabbin’ Klaw"]}}},
    "Deffkoptas": {"Model§Deffkopta": {"static": ["Choppa", "Slugga", "Spinnin’ Blades"], "slots": {
        "Rocket Options": [("Rokkit Launcha", "Rokkit Launcha"), ("Kustom mega-blasta", "Kustom Mega-blasta @special")]}}},
    "Dakkajet": {"_unit": {"static": ["Armoured Impact", "2x Dual Supa-shoota"], "slots": {"Dual Supa-shoota": OPT("Dual Supa-shoota")}}},
    "Burna-bommer": {"_unit": {"static": ["Armoured Impact", "Dual Big Shoota", "Dual Supa Shoota"], "slots": {
        "Skorcha Missile Rack": OPT("Skorcha Missile Rack")}}},
    "Blitza-bommer": {"_unit": {"static": ["Armoured Impact", "Big Shoota", "Dual Supa-shoota"]}},
    "Wazbom Blastajet": {"_unit": {"static": ["Armoured Impact", "Smasha Gun"], "slots": {
        "Cannon Options": ["Dual Wazbom Mega-kannon", "Dual Tellyport Mega-blasta"],
        "Blastajet Force Field": OPT("Blastajet Force Field"),
        "Dual Supa-shoota": OPT("Dual Supa-shoota")}}},
    "Warbikers": {
        "Model§Boss Nob on Warbike": {"static": ["Kustom Choppa", "Dual Kombi-rokkit"]},
        "Model§Warbiker": {"static": ["Choppa", "Dual Dakkagun"]}},
    "Warbuggies": {"Model§Warbuggy": {"static": ["Extra Dakka", "Spiked Ram"], "slots": {"Ranged Options": ["Mek Speshul", "Rivet Kannon"]}}},
    "Mek Gunz": {"Model§Mek Gun": {"static": ["Scavenged Shivs"], "slots": {
        "Gun Options": ["Smasha Gun", "Bubblechukka", "Kustom Mega-kannon", "Traktor Kannon"]}}},
    "Battlewagon": {"_unit": {"static": ["Crushin’ Bulk"], "slots": {
        "Wreckin’ Ball": OPT("Wreckin’ Ball"), "Grabbin’ Klaw": OPT("Grabbin’ Klaw"), "# of Big Shootas": UPTO("Big Shoota", 4)}},
        "_drop_rules": ["applyArdCase"], "_patch": battlewagon},
    "Deff Dread": {"_unit": {"static": ["Dread Klaws"], "slots": {
        "Big Shoota": ["Big Shoota", "Extra Klaw", "Kustom Mega-blasta", "Rokkit Launcha"],
        "Skorcha": ["Skorcha", "Extra Klaw", "Big Shoota", "Kustom Mega-blasta", "Rokkit Launcha"]}},
        "_drop_rules": ["Klaws"]},
    "Killa Kans": {"Model§Killa Kan": {"static": ["Kan Blasta", "Kan Klaw"]}},
    "Morkanaut": {"_unit": {"static": ["2x Dual Big Shoota", "Klaw of Mork", "Kustom Mega-blasta", "Kustom Mega-zappa", "2x Rokkit Launcha"]}},
    "Gorkanaut": {"_unit": {"static": ["Deffstorm Mega-shoota", "2x Dual Big Shoota", "Klaw of Gork", "2x Rokkit Launcha", "Skorcha"]}},
    "Stompa": {"_unit": {"static": ["5x Big Shoota", "Deffkannon and Supa-rokkits", "Mega-choppa", "Skorcha", "Supa-gatler"]}},
    "Grot Tanks": {"Model§Grot Tank": {"static": ["Ramshackle Hull"], "slots": {
        "Loadout 1": ["Grot Tank Shoota", "Grotzooka", "Kustom Mega-blasta", "Rokkit Launcha", "Skorcha"],
        "Loadout 2": ["-", "Grot Tank Shoota @special", "Grotzooka @special", "Kustom Mega-blasta @special",
                      "Rokkit Launcha @special", "Skorcha @special"]}}},
    "Grot Mega-tank": {"_unit": {"static": ["Armoured Hull", "Mega-tank Weapons"], "slots": {
        "Loadout 1": ["Dual Grotzooka", "Dual Big Shoota", "Dual Kustom Mega-blasta", "Dual Rokkit Launcha", "Dual Skorcha"],
        "Loadout 2": ["Dual Big Shoota", "Dual Grotzooka", "Dual Kustom Mega-blasta", "Dual Rokkit Launcha", "Dual Skorcha"]}}},
    "Lifta Wagon": {"_unit": {"static": ["Crushin' Bulk", "Lifta-droppa"], "slots": {
        "Grabbin’ klaw": OPT("Grabbin’ Klaw"),
        "Ranged Options": ["-", "Big Shoota + Rokkit Launcha", "2x Big Shoota", "2x Rokkit Launcha"],
        "Wreckin’ ball": OPT("Wreckin’ Ball")}}},
    "Big Trakk": {"_unit": {"static": ["Armoured Hull", "2x Big Shoota"], "slots": {"Kannon": ["-", "Kannon", "Supa-kannon"]}}},
    "Kill Tank": {"_unit": {"slots": {
        "Dual Big Shoota": ["Dual Big Shoota", "Rokkit Launcha", "Skorcha"],
        "Skorcha": ["Skorcha", "Dual Big Shoota", "Rokkit Launcha"],
        "Main Armament": ["Tank Kannon + Crushin' Bulk", "Deff Rolla @rolla=3"],
        "Deff Rolla Weapon 1": KILL_TANK_GUN, "Deff Rolla Weapon 2": KILL_TANK_GUN, "Deff Rolla Weapon 3": KILL_TANK_GUN,
        "Deff Rolla Big Shootas": [(str(i), (" + ".join(["Big Shoota"] * i) + f" @rollabs={i}") if i else "-") for i in range(6)]}},
        "_rules": {
            "A Deff Rolla takes exactly three of Kannon, Lobba and Zzap Gun": {"evals": [{
                "actionable": True, "equation": {"operator": "T-O", "value": ["{self}", "tracked", "rolla"]}, "max": 0, "min": 0,
                "not": False, "operator": "AND", "paths": [["{self}", "tracked", "rollagun"]]}], "evaluate": "AND", "failState": "error"},
            "At most 1 Kannon and 1 Lobba with the Deff Rolla": {"evals": [
                {"actionable": True, "max": 1, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "kannon"]]},
                {"actionable": True, "max": 1, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "lobba"]]}],
                "evaluate": "AND", "failState": "error"},
            "Big Shootas need a Deff Rolla": {"evals": [
                {"actionable": True, "max": 0, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "rollabs"]]},
                {"actionable": True, "min": 1, "not": False, "operator": "AND", "paths": [["{self}", "tracked", "rolla"]]}],
                "evaluate": "OR", "failState": "error"}}},
    "Gargantuan Squiggoth": {"_unit": {"static": ["Huge Tusks"], "slots": {
        "Kannon": ["Kannon", "Supa-kannon"], "Extra Kannon": ["-", "Kannon", "Supa-kannon"]}}},
    "Big’ed Bossbunka": {"_unit": {"static": ["Gaze of Gork"], "slots": {
        "Big Shootas": [("1", "Big Shoota"), ("2", "2x Big Shoota"), ("3", "3x Big Shoota")]}}},
    "Big Mek Dakkarig": {"_unit": {"static": ["Blitzkannon", "Multi-busta Launcha", "Stompy Feet"]}},
    "Wartrakks": {"Model§Wartrakk": {"static": ["Kustom Choppa", "Kustom Shoota", "Multi-busta Launcha"]}, "_patch": to_multi("Wartrakk", 130)},
    "Rukkatrukk Squigbuggies": {"_patch": to_multi("Rukkatrukk Squigbuggy", 160)},
    "Gunwagon": {"_unit": {"static": ["Crushin’ Bulk"], "slots": {
        "Kannon": ["Kannon", "Killkannon", "Zzap Gun"],
        "Wreckin’ Ball": OPT("Wreckin’ Ball"), "Grabbin’ Klaw": OPT("Grabbin’ Klaw"), "Lobba": OPT("Lobba"),
        "# of Big Shootas": UPTO("Big Shoota", 4)}}},
}
