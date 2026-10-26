"""Adeptus Mechanicus Crusade (10e codex, as carried on the 11e site): The Search for Archeotech — Archeotech Parts,
Archeotech Treasures on Tech-Priests (one weapon, one force field, one techno-arcana each), Legendary Archeotech.
Source: Wahapedia crus11_adeptus-mechanicus. The 21 BSData Crusade Honour§ items become Archeotech Treasure§ /
Legendary Archeotech flags on the tracker."""
SLUG, ED, FACTION = "adeptus-mechanicus", "11", "Adeptus Mechanicus"
LISTS = dict(agendas=True, requisitions=True, badges=True)

WEAPONS = {  # name: (Range, A, BS, S, AP, D, [abilities])
    "Electro-fire Implants": (12, "D6+3", 3, 4, 0, 1, ["Ability§Assault", {"item": "Ability§Anti-", "stats": {"keyword": {"value": "infantry"}, "x": {"value": "4+"}}}, "Ability§Torrent"]),
    "Neural Jammer": (18, 4, 3, 4, -2, 1, ["Ability§Devastating Wounds", "Ability§Pistol", "Ability§Precision"]),
    "Nanoshard Projector": (12, 3, 3, 5, -1, 2, ["Ability§Lethal Hits", "Ability§Pistol"]),
    "Arc Annulus": (12, 2, 3, 7, -1, 2, [{"item": "Ability§Anti-", "stats": {"keyword": {"value": "vehicle"}, "x": {"value": "3+"}}}, "Ability§Pistol"]),
    "Electro-fused Vambraces": (12, 6, 3, 3, -1, 1, ["Ability§Pistol", {"item": "Ability§Sustained Hits", "stats": {"x": {"value": "2"}}}]),
    "Digital Cannon": (24, 2, 3, 6, -1, 3, []),
}
FORCE_FIELDS = ["Void Shell", "Arc Implants", "Time Sink", "Conversion Eradicator", "Inverse Power Feeds", "Technodermis"]
TECHNO_ARCANA = ["Hagioscope", "Exo-gauntlet", "Ferrosanctic Orrery", "Obscuroptikon", "Tri-dimensional Covenant", "Hypercircuit"]
LEGENDARY = {
    "The Doom of Thorantus": "Once per battle, at the end of your Movement phase, select one enemy VEHICLE unit within 18\" of and visible to the bearer. Until the start of your next Movement phase, subtract 2 from the Attacks characteristic of ranged weapons equipped by models in that unit, and each time that unit ends a Normal, Advance, Fall Back or Charge move, it suffers D6 mortal wounds.",
    "Syntaxik Charger": "The bearer gains the Syntaxik Charger for the battle: 24\", A 8, BS 3+, S 3, AP 0, D 1, [ANTI-INFANTRY 2+], [DEVASTATING WOUNDS], One Shot (the bearer can only shoot with this weapon once per battle), Sonic Devastation (in your Shooting phase, after this model has shot, select one enemy unit hit by one or more of those attacks made with this weapon; until the start of your next turn, worsen the Weapon Skill characteristic of melee weapons equipped by models in that unit by 1).",
    "Augur of the First Reclamation": "Add 2 to the bearer’s Objective Control characteristic, and at the end of your Command phase, if the bearer is within range of an objective marker that is not in your deployment zone, you gain 1CP. In addition, at the end of the battle, if the bearer was in your Crusade army and you won that battle, roll one D6: on a 4+, your Crusade force acquires one Archeotech Part.",
}
TRACKER_TEXT = (
    "**The Search for Archeotech.** Each time you win a battle, roll one D6: on a 5+ your Crusade force acquires one Archeotech Part — choose a Power Source or roll one D6 for its type (1–2 Weapon Part, 3–4 Force Field Part, 5–6 Techno-arcana Part). "
    "The **Assemble Archeotech** Requisition spends one Power Source plus one other Part to add an Archeotech Treasure of that type (roll one D6 on its table, or spend one more Power Source to re-roll once) to the collection of one TECH-PRIEST (not an EPIC HERO); the treasure is a Battle Honour worth 1 Crusade point. "
    "When mustering, each TECH-PRIEST can field up to one archeotech weapon, one force field and one techno-arcana from its collection (leave the ones it does not field off its card for that battle).\n\n"
    "**Legendary Archeotech.** Before a battle, just before selecting Agendas, you can either Collect Location Data (at the end of the battle gain 1 Location Data instead of any Archeotech Part) or Scan for Legendary Archeotech (roll one D6 and add your Location Data: on 10+ the scan succeeds and you can select the Claim Legendary Archeotech Agenda; otherwise lose 1 Location Data). "
    "Claim Legendary Archeotech: your opponent places a Legendary Archeotech marker in their deployment zone (more than 3\" from edges and 6\" from objectives); if an ADEPTUS MECHANICUS CHARACTER from your Crusade army controls it at the end of the battle, add one piece of Legendary Archeotech (roll one D6: 1–2 The Doom of Thorantus, 3–4 Syntaxik Charger, 5–6 Augur of the First Reclamation, re-rolling duplicates) and tick it below; whether or not you succeed, reduce your Location Data by 10 (to a minimum of 0); an enemy CHARACTER that controls the marker gains 3XP. "
    "Bring one piece into a battle with the **Auto-Sermon of Deployment** Requisition.")


def build(cz):
    L, b = cz.L, cz.book
    cat = L.catalog(b)
    # ── Archeotech Treasures: own class on TECH-PRIESTS (not Epic Heroes), one of each type per model ──
    L.reclass(b, "Crusade Honour§", "Archeotech Treasure", list(WEAPONS) + FORCE_FIELDS + TECHNO_ARCANA, patch={"keywords": {"Tags": []}})
    for n in WEAPONS:
        cat[f"Archeotech Treasure§{n}"]["keywords"]["Keywords"] = ["Archeotech Weapon"]
    for n in FORCE_FIELDS:
        cat[f"Archeotech Treasure§{n}"]["keywords"]["Keywords"] = ["Archeotech Force Field"]
    for n in TECHNO_ARCANA:
        cat[f"Archeotech Treasure§{n}"]["keywords"]["Keywords"] = ["Archeotech Techno-arcana"]
    L.honour_class(b, "Archeotech Treasure", unique=False, allow_on=("Character",),
                   allow_evals=[L.ev_kw("Tech-Priest"), L.ev_kw("Epic Hero", not_=True)],
                   allow_note="Archeotech Treasures: assembled with the Assemble Archeotech Requisition and added to a TECH-PRIEST's collection; each TECH-PRIEST fields up to one archeotech weapon, one force field and one techno-arcana")
    for kind in ("Archeotech Weapon", "Archeotech Force Field", "Archeotech Techno-arcana"):
        L.class_rule(b, "Character", f"One {kind.lower()} per Tech-Priest.", L.error_rule([L.ev(["{self}", "tally", kind], mx=1)]))
    # the six weapons also put a real profile on the model: a Ranged Weapon§ trait added by the treasure
    for n, (rng, a, bs, s, ap, d, abil) in WEAPONS.items():
        wkey = f"Ranged Weapon§Archeotech—{n}"
        L.put_asset(b, wkey, {"aspects": {"Label": n}, "assets": {"traits": abil}, "stats": {"A": {"value": a}, "AP": {"value": ap}, "BS": {"value": bs}, "D": {"value": d}, "Range": {"value": rng}, "S": {"value": s}}}, reuse_key=False)
        t = cat[f"Archeotech Treasure§{n}"]
        abil_txt = ", ".join(("[" + (x if isinstance(x, str) else x["item"]).split("§")[1].upper().rstrip("-") + ((" " + x["stats"]["keyword"]["value"].upper() + " " + x["stats"]["x"]["value"]) if not isinstance(x, str) and "keyword" in x["stats"] else (" " + x["stats"]["x"]["value"]) if not isinstance(x, str) else "") + "]") for x in abil)
        t["text"] = f"The bearer is equipped with the {n}: {rng}\", A {a}, BS {bs}+, S {s}, AP {ap}, D {d}" + (f", {abil_txt}" if abil_txt else "") + ". Archeotech weapons cannot be upgraded by Weapon Modifications."
        t["rules"] = {"addWeapon": L.rule([L.add(["{parent}", "traits"], wkey)], [], note="the archeotech weapon profile joins the bearer's weapons")}
    # ── tracker: parts, location data, legendary archeotech ──
    stats = {"Power Source": L.num(0, mn=0, mx=20, order=1, label="Power Sources", group="Archeotech Parts", group_order=1),
             "Weapon Part": L.num(0, mn=0, mx=20, order=2, label="Weapon Parts", group="Archeotech Parts", group_order=1),
             "Force Field Part": L.num(0, mn=0, mx=20, order=3, label="Force Field Parts", group="Archeotech Parts", group_order=1),
             "Techno-arcana Part": L.num(0, mn=0, mx=20, order=4, label="Techno-arcana Parts", group="Archeotech Parts", group_order=1),
             "Location Data": L.num(0, mn=0, mx=20, order=5, group="Legendary Archeotech", group_order=2)}
    rules = {}
    for i, (n, txt) in enumerate(LEGENDARY.items()):
        stats[n] = L.flag(tracking={"Legendary Archeotech": 1}, order=6 + i, group="Legendary Archeotech", group_order=2)
        L.ability(b, n, txt)
        rules[f"legendary{i}"] = L.rule([L.add(["{self}", "traits"], f"Ability§{n}")], [L.ev_stat(n, "✓")])
    L.del_assets(b, [f"Crusade Honour§{n}" for n in LEGENDARY])
    L.tracker(b, "Archeotech", "The Search for Archeotech", stats=stats, text=TRACKER_TEXT, class_rules_=rules)
    # the 10e carry-over badges were spelt "Archaeotech" and had no text; the section's "Archeotech" badges replace them
    L.del_assets(b, [k for k in list(cat) if k.startswith("Crusade Badge§Archaeotech")])
    oob = L.taxonomy(b).get("Order of Battle", {}).get("allowed", {}).get("items", [])
    oob[:] = [k for k in oob if not k.startswith("Crusade Badge§Archaeotech")]
    cz.note("18 treasures reclassed (6 weapons with Ranged Weapon§ profiles added by rule); tracker with 4 part counters, Location Data and 3 Legendary Archeotech flags")
