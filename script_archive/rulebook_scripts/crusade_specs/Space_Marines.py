"""Space Marines Crusade (10e codex; the 11e codex has no Crusade section): the Oathsworn Campaign / Honour Points /
Chapter Command / Promotion bloc already exists in the book. This spec fills the lists, documents the Honour point gains
and removes the BSData duplicates of the Promotion abilities and the chapter-specific items (rebuilt in the chapter books).
Source: Wahapedia crus10_space-marines (powered by Wahapedia)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _sm_common as C
SLUG, ED, FACTION = "space-marines", "10", "Adeptus Astartes"
LISTS = dict(agendas=False, requisitions=False, badges=False)   # handled below (dedupe against the ranks already in the book)

CHAPTER_COMMAND = ["Master of the Codex", "Master of Combat", "Battlefield Chirurgy", "Selfless Healer", "Wise Orator", "Mantra of Strength",
                   "Liturgy of Resanctification", "Shielded by the Machine God", "Roused to Fury", "Ardent Protectors", "Empyric Castellan",
                   "Psychic Scourge", "Steadfast Example", "Pennant of the Fallen"]
HONOUR_TEXT = ("**Oathsworn Campaigns and Honour points.** An Oathsworn Campaign lasts three battles. Each battle you win earns your Crusade force Honour points by "
               "battle size: Incursion +2, Strike Force +3, Onslaught +5; Bonus Agendas earn more. Record them on the roster's Honour Points counter. When a campaign "
               "ends, spend Honour points on Chapter Command promotions and unit assignments, then reset them to 0 (for every 5 unspent points lost this way, one "
               "unit of your choice gains 1XP).")


def build(cz):
    L, b = cz.L, cz.book
    n = C.NTH[b]
    # lists
    new = C.agendas_dedupe(b, [a["name"] for a in C.SEC.named("Agendas", nth=n) if a["text"]], "Astartes")
    reqs = C.reqs_nth(n)
    keys = []
    for r in reqs:   # Enduring Duty stays campaign-gated (allowEnduringDuty after three battles): never on the Order of Battle list
        key = L.put_asset(b, f"Requisition§{r['name']}", {"stats": {"RP": {"value": r["rp"]}}, "text": r["text"]}, keep_text=True)
        if r["name"] != "Enduring Duty":
            keys.append(key)
    L.allow_items(b, "Order of Battle", keys)
    for bd in C.badges_nth(n):   # the badges are awarded by the Order of Battle rules; only their texts were missing
        L.put_asset(b, f"Crusade Badge§{bd['name']}", {"text": bd["text"]}, keep_text=True)
    # Honour point gains on the three campaign assets
    for k in L.keys_with_prefix(b, "Oathsworn Campaign§"):
        a = L.catalog(b)[k]
        name = k.split("§", 1)[1]
        intro = C.intro_of(name)
        bon = C.bonus({"Unflinching Bulwark": 1, "Precision Strike": 2, "The Forging of Legends": 3}[name])
        a["text"] = HONOUR_TEXT + ("\n\n" + intro if intro else "") + "\n\n**Bonus Agendas:**\n" + "\n".join(f"- **{e['name']}:** {e['text']}" for e in bon)
    # delete the BSData duplicates: Chapter Command honours twin the Promotion Abilities; the chapter families are rebuilt in their books
    cat = L.catalog(b)
    gone = [k for k in list(cat) if k.startswith("Crusade Honour§")]
    L.del_assets(b, gone)
    for rn in ("crusadeTagWolfPriest", "crusadeNotFactionBlackTemplars"):   # grants that only served the deleted items
        L.taxonomy(b)["Unit"].get("rules", {}).pop(rn, None)
    cz.note(f"agendas new {new}; requisitions {len(reqs)} (Enduring Duty campaign-only); badge texts 3; deleted {len(gone)} Crusade Honour§ "
            f"({len(CHAPTER_COMMAND)} Chapter Command twins, 12 Deeds of Making → Space Wolves, 12 Reclaimed Relics → Black Templars)")
