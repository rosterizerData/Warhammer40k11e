"""Grey Knights Crusade (10e codex, as carried on the 11e site): Visions from the Augurium, Chaos Incursions, Gifts of the
Prescient. Source: Wahapedia crus11_grey-knights. Gifts were imported from BSData as Crusade Honour§ without their costs."""
import re
SLUG, ED, FACTION = "grey-knights", "11", "Grey Knights"
LISTS = dict(agendas=True, requisitions=True, badges=True)

VISIONS = ["Sanctify Site", "Purge and Cleanse", "Rites of Exorcism"] + [f"Vision {i}" for i in range(4, 10)]
RANK_XP = {"Battle-ready": 0, "Blooded": 6, "Battle-hardened": 16, "Heroic": 31, "Legendary": 51}
TEXT = ("**Visions from the Augurium.** At the start of the Select Agendas step, if there are any GREY KNIGHTS CHARACTER units in your Crusade army, consult the Prognosticars: roll a D33 on the Augurium Vision tracker (a 3×3 grid) and set that Vision to **Malefic** "
        "(two Visions if none are Malefic or four or more are Sanctic; a Sanctic Vision rolled turns Malefic; a Malefic one is re-rolled). Grey Knights Agendas can turn one Vision **Sanctic** after each battle. "
        "The nine Visions below are the grid; the codex tracker card gives the six names this book lacks — rename them.\n\n"
        "**Chaos Incursion.** At the Update Order of Battle step, if any row, column or diagonal of three Visions is Malefic, an Incursion begins: tick Incursion, roll a D3 and add the number of Malefic Visions for your Banishment total, and collect Banishment points from Agendas, Requisitions and Battle Honours "
        "(no consulting, no Vision changes meanwhile). When Banishment points reach the total, the Incursion ends: gain 1 Purgation point per Sanctic Vision plus 1 for each full Sanctic row or column, reset Banishment points and the grid to clear.\n\n"
        "**Gifts of the Prescient.** After an Incursion ends, spend Purgation points on Gifts for GREY KNIGHTS CHARACTERS (each unique, each with a minimum rank; a model may hold 1 at Battle-ready or Blooded, 2 at Battle-hardened or Heroic, 3 at Legendary). "
        "Purgation points unspent when you next consult the Prognosticars are lost.")


def gifts_from_text(sec):
    lines = [l for l in sec.block("Gifts of the Prescient") if l.strip()]
    out, i = {}, 0
    while i < len(lines):
        nm = sec.is_name(lines[i])
        if nm and i + 1 < len(lines) and re.fullmatch(r"\d", lines[i + 1].strip()):
            j, body = i + 2, []
            while j < len(lines) and not (sec.is_name(lines[j]) and j + 1 < len(lines) and re.fullmatch(r"\d", lines[j + 1].strip())):
                body.append(lines[j].strip())
                j += 1
            rk = re.search(r"Model with the ([\w-]+) rank", " ".join(body))
            out[nm[0]] = (int(lines[i + 1]), rk.group(1) if rk else "Battle-ready")
            i = j
        else:
            i += 1
    return out


def build(cz):
    L, b = cz.L, cz.book
    gifts = gifts_from_text(cz.sec)
    # ── Gifts of the Prescient: own class, costs, rank gates, caps ──
    L.reclass(b, "Crusade Honour§", "Gift of the Prescient")
    cat = L.catalog(b)
    for k in [k for k in cat if k.startswith("Gift of the Prescient§")]:
        name = k.split("§", 1)[1]
        hit = next((v for n, v in gifts.items() if L.norm(n) == L.norm(name)), None)
        cost, rk = hit if hit else (1, "Battle-ready")
        cat[k].setdefault("stats", {})["Purgation Pts"] = {"value": cost}
        cat[k]["keywords"] = {"Tags": [FACTION], "Keywords": [f"{rk} rank or higher"]}   # the faction Tag satisfies the Character's constraints.any
        not_narr = L.ev(["{roster}", "stats", "Play", "value"], "Narrative", not_=True)
        cat[k]["rules"] = {f"{rk} rank or higher.": L.rule(None, [not_narr, L.ev(["{parent}", "stats", "Experience", "value"], mn=RANK_XP[rk])], fail="error", evaluate="OR")}
        if hit is None:
            cz.note(f"no cost/rank found for {name}")
    L.unique_in_roster(b, [k.split("§", 1)[1] for k in cat if k.startswith("Gift of the Prescient§")])
    L.honour_class(b, "Gift of the Prescient", unique=True, allow_on=("Character",),
                   stats={"Purgation Pts": {"statType": "numeric", "tracked": True, "value": 1, "visibility": "always", "group": "Cost", "groupOrder": -1}},
                   allow_note="Gifts of the Prescient: bought with Purgation points after a Chaos Incursion ends; each is unique and needs a minimum rank")
    not_narr = L.ev(["{roster}", "stats", "Play", "value"], "Narrative", not_=True)
    L.class_rule(b, "Character", "Gifts of the Prescient: one at Battle-ready or Blooded.", L.rule(None, [not_narr, L.ev(["{self}", "tally", "Gift of the Prescient"], mx=1), L.ev(["{self}", "stats", "Experience", "value"], mn=16)], fail="error", evaluate="OR"))
    L.class_rule(b, "Character", "Gifts of the Prescient: two at Battle-hardened or Heroic.", L.rule(None, [not_narr, L.ev(["{self}", "tally", "Gift of the Prescient"], mx=2), L.ev(["{self}", "stats", "Experience", "value"], mn=51)], fail="error", evaluate="OR"))
    L.class_rule(b, "Character", "Gifts of the Prescient: three at most.", L.rule(None, [not_narr, L.ev(["{self}", "tally", "Gift of the Prescient"], mx=3)], fail="error", evaluate="OR"))
    # ── Augurium tracker with nine Vision children ──
    vis_children = []
    for i, v in enumerate(VISIONS):
        vis_children.append(L.child(b, "Augurium Vision", v, stats={"State": L.rank({"Malefic": {"tracking": {"Malefic Vision": 1}}, "Sanctic": {"tracking": {"Sanctic Vision": 1}}}, order=1)}, rename=True,
                                    text=f"Grid position {['top-left','top-centre','top-right','middle-left','centre','middle-right','bottom-left','bottom-centre','bottom-right'][i]}."))
    stats = {"Incursion": L.flag(tracking={"Chaos Incursion": 1}, order=1, label="Chaos Incursion under way"),
             "Banishment total": L.num(0, mn=0, mx=12, order=2),
             "Banishment points": L.num(0, mn=0, mx=12, order=3),
             "Purgation Points": L.num(0, mn=0, mx=30, order=4, label="Purgation points earned", icons=["eye"]),
             "Purgation Pts spent": L.num(0, mn=0, mx=99, dynamic=False, order=5, label="Purgation points spent")}
    rules = {"purgationSpent": L.rule([L.set_(["{self}", "stats", "Purgation Pts spent", "value"], ["{roster}", "tracked", "Purgation Pts"])], [], order=2),
             "Purgation points spent exceed the points earned.": L.rule(None, [L.ev(["{roster}", "tracked", "Purgation Pts"], mx=["{self}", "stats", "Purgation Points", "value"])], fail="error", order=5),
             "banished": L.rule([L.mod(["{self}", "designation"], " — INCURSION ENDED: claim Purgation points", append="")],
                                [L.ev_stat("Incursion", "✓"), L.ev(["{self}", "stats", "Banishment total", "value"], mn=1), L.ev(["{self}", "stats", "Banishment points", "value"], mn=["{self}", "stats", "Banishment total", "value"])], order=5)}
    L.tracker(b, "Augurium", "Augurium Vision Tracker", stats=stats, children=vis_children, text=TEXT, class_rules_=rules)
    cz.note(f"Gifts reclassed with costs/ranks ({len(gifts)} parsed); Augurium tracker with 9 Vision children, Incursion flag, Banishment and Purgation ledger")
