"""Thousand Sons Crusade (10e codex, as carried on the 11e site): Brotherhood of Sorcerers (nine Great Cults, Lore and
Arcana points, Diabolic Rituals to Aelementus / Esoterist / Magister Templi), Boons of Tzeentch, Scintillating Legions.
Source: Wahapedia crus11_thousand-sons. The BSData import had collapsed the 27 cult rewards into three names."""
import re
SLUG, ED, FACTION = "thousand-sons", "11", "Thousand Sons"
LISTS = dict(agendas=True, requisitions=True, badges=True)

BOONS = ["Crystalline Body", "Warp Strider", "Forewarned by Fate", "Flesh Sigils", "Flame-wreathed", "Raptorial Talons", "Immaterial Edge", "Temporal Distortion", "Aura of Illusion"]
TIERS = ["Aelementus", "Esoterist", "Magister Templi"]
CULTS = ["Cult of Mutation", "Cult of Prophecy", "Cult of Time", "Cult of Scheming", "Cult of Magic", "Cult of Knowledge", "Cult of Change", "Cult of Duplicity", "Cult of Manipulation"]


def cult_rewards(sec):
    """per cult: flavour line, then (TIER, lore, arcana, 'REWARD', 'Name (kind…): text') ×3"""
    out = {}
    for cult in CULTS:
        lines = [l.strip() for l in sec.block(cult) if l.strip() and not l.startswith("|")]
        rows, i = [], 0
        while i < len(lines):
            if lines[i].upper() in [t.upper() for t in TIERS] and i + 4 < len(lines):
                tier = TIERS[[t.upper() for t in TIERS].index(lines[i].upper())]
                lore, arcana = lines[i + 1], lines[i + 2]
                m = re.match(r"^(.+?) \((Instant|Battle Honour[^)]*)\):\s*(.*)$", lines[i + 4])
                if m:
                    rows.append({"tier": tier, "lore": int(lore), "arcana": int(arcana), "name": m.group(1).strip(), "kind": m.group(2), "text": m.group(3).strip()})
                i += 5
            else:
                i += 1
        out[cult] = rows
    return out


def build(cz):
    L, b = cz.L, cz.book
    ts = [L.ev_kw("Thousand Sons", field="Faction")]
    # ── Boons of Tzeentch: Characters (not Daemon Princes), three per model ──
    L.reclass(b, "Crusade Honour§", "Boon of Tzeentch", BOONS)
    L.honour_class(b, "Boon of Tzeentch", unique=False, allow_on=("Character",), allow_evals=[L.ev_kw("Daemon Prince", not_=True)],
                   allow_note="Boons of Tzeentch: THOUSAND SONS CHARACTER models (not DAEMON PRINCES) may take a Boon of Tzeentch instead of another Battle Honour; a duplicate D33 roll means Spawndom",
                   cap=3, cap_text="No model can have more than three Boons of Tzeentch.")
    # ── the collapsed rewards go; the 27 come back under their own names ──
    L.del_assets(b, ["Crusade Honour§Aelementus", "Crusade Honour§Esoterist", "Crusade Honour§Magister Templi"])
    rewards = cult_rewards(cz.sec)
    # ── per-Character cult card: Great Cult, Lore, Arcana, Cult Rank ──
    show = ts + [L.ev_kw("Epic Hero", not_=True)]
    L.unit_stat(b, "Character", "Great Cult", L.rank(CULTS, group="Crusade", group_order=11, order=20), show_when=show)
    L.unit_stat(b, "Character", "Lore Points", L.num(0, mn=0, mx=99, group="Crusade", group_order=11, order=21), show_when=show, show_rule="crusadeShowLorePoints")
    L.unit_stat(b, "Character", "Arcana Points", L.num(0, mn=0, mx=99, group="Crusade", group_order=11, order=22), show_when=show, show_rule="crusadeShowArcanaPoints")
    L.unit_stat(b, "Character", "Cult Rank", L.rank({t: {"number": i + 1} for i, t in enumerate(TIERS)}, group="Crusade", group_order=11, order=23), show_when=show, show_rule="crusadeShowCultRank")
    L.class_rule(b, "Character", "Tzaangor Shamans can never progress further than Aelementus.",
                 L.rule(None, [L.ev_stat("Play", "Narrative", who="{roster}", not_=True), L.ev_kw("Tzaangor Shaman", not_=True), L.ev(L.rankvalue("Cult Rank"), mx=1)],
                        fail="error", evaluate="OR", note="only checked in Narrative play (stored stat values survive a switch to Matched play)"))
    # ── Great Cult Battle Honours: gated on the Character's cult and rank ──
    L.honour_class(b, "Great Cult Battle Honour", unique=False, allow_on=("Character",), allow_evals=ts + [L.ev_stat("Great Cult", "-", not_=True)],
                   allow_note="Great Cult Battle Honours: the reward of a Diabolic Ritual rank in the Character's Great Cult (deduct the Lore and Arcana points and pay the 1RP Diabolic Ritual Requisition)",
                   cap=3, cap_text="A Character can hold at most one Great Cult Battle Honour per rank (three in all).")
    items, table = [], []
    for cult, rows in rewards.items():
        for r in rows:
            cost = f"{r['lore']} Lore / {r['arcana']} Arcana"
            table.append(f"{cult} — {r['tier']} ({cost}): {r['name']}" + (" (Instant)" if r["kind"] == "Instant" else ""))
            if r["kind"] == "Instant":
                continue
            tier_n = TIERS.index(r["tier"]) + 1
            items.append({"name": r["name"], "tags": [FACTION], "keywords": [cult, r["tier"]],
                          "text": f"*{cult}, {r['tier']} ({cost}).* " + (f"[{r['kind']}] " if r["kind"] != "Battle Honour" else "") + r["text"],
                          "rules": {f"{cult} only.": L.error_rule([L.ev_stat("Great Cult", cult, who="{parent}")]),
                                    f"Needs the {r['tier']} rank.": L.error_rule([L.ev(L.rankvalue("Cult Rank", "{parent}"), mn=tier_n)])}})
    L.honours(b, "Great Cult Battle Honour", items, keep_text=False)
    instants = "\n".join("• " + t for t in table)
    text = ("**Brotherhood of Sorcerers.** Each THOUSAND SONS CHARACTER (not EPIC HEROES) belongs to one of the nine Great Cults (set it on the Character's card) and gains Lore points and Arcana points from Agendas "
            "and from the Plots and Schemes test. After a battle, if a Character has the Lore and Arcana points for the next rank in its cult, it can perform a Diabolic Ritual (Requisition, 1RP; 2RP until your next battle "
            "after a failed Plots and Schemes test): deduct the points, raise its Cult Rank and take the reward — Instant rewards apply at once, Battle Honour rewards are the Great Cult Battle Honours (replace a non-cult honour "
            "if the Character is at its cap). TZAANGOR SHAMANS stop at Aelementus. EPIC HEROES hoard their points for bragging rights only.\n\n"
            "**Plots and Schemes:** at the end of the Determine Victor step your WARLORD takes a Leadership test: −1 with units from 2–3 Great Cults in the army, −2 for 4–6, −3 for 7–9; +1 with another unit of the WARLORD's cult; +1 if you won. "
            "Passed: your WARLORD gains 1 Lore and 1 Arcana point, or another CHARACTER gains one of either. Failed: Diabolic Ritual costs 2RP until the end of your next battle.\n\n"
            "**Ritual costs and rewards (Lore / Arcana):**\n" + instants + "\n\n"
            "**Scintillating Legions:** with the Changehost of Deceit Detachment, SCINTILLATING LEGIONS units from your Order of Battle can join your Crusade army; they never gain Experience points or Battle Honours and automatically pass Out of Action tests.")
    L.tracker(b, "Brotherhood of Sorcerers", "Brotherhood of Sorcerers", text=text)
    L.class_rule(b, "Unit", "noCrusadeXpScintillatingLegions",
                 L.rule([L.set_(["{self}", "stats", "Experience", "visibility"], "hidden"), L.set_(["{self}", "stats", "Battle Honour", "max"], 0)],
                        [L.NARR, L.ev_kw("Scintillating Legions", field="Faction")],
                        note="Crusade: SCINTILLATING LEGIONS units never gain Experience points or Battle Honours and automatically pass Out of Action tests"))
    n_inst = sum(1 for rows in rewards.values() for r in rows if r["kind"] == "Instant")
    cz.note(f"Boons of Tzeentch reclassed; cult card stats; Great Cult Battle Honours {len(items)} (+{n_inst} instant rewards as text) from {len(rewards)} cults; Brotherhood reference; Scintillating Legions no-XP")
