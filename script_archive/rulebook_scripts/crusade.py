"""Build a faction's Crusade mini-game into its book from crusade_specs/<Book>.py.

  python3 crusade.py <Book> [--apply] [--no-lists] [--no-build]

A spec module defines:
  SLUG, ED          – Wahapedia section (crusade_waha.Section)
  FACTION           – keyword used for Agenda tracking ("<FACTION> Agenda") and default tags
  LISTS             – dict(agendas=True, requisitions=True, badges=True); REQ_SKIP, REQ_RP overrides
  build(cz)         – the bespoke part (tracker, stats, honour classes, rules); cz is a Context
Dry-run prints what would change; --apply writes the book and bumps its revision. Re-runs are idempotent.
"""
import importlib.util, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import crusade_lib as L
import crusade_waha as Wh

book = sys.argv[1]
APPLY = "--apply" in sys.argv
DO_LISTS = "--no-lists" not in sys.argv
DO_BUILD = "--no-build" not in sys.argv
spec_path = Path(__file__).parent / "crusade_specs" / f"{book}.py"
sp = importlib.util.spec_from_file_location("spec", spec_path)
spec = importlib.util.module_from_spec(sp)
sp.loader.exec_module(spec)


class Context:
    def __init__(self):
        self.book = book
        self.L = L
        self.sec = Wh.Section(spec.SLUG, getattr(spec, "ED", "11")) if getattr(spec, "SLUG", None) else None
        self.faction = getattr(spec, "FACTION", None) or L.faction_value(book)
        self.log = []

    def note(self, msg):
        self.log.append(msg)


cz = Context()
before = json.dumps(L.load(book), sort_keys=True)
lists = getattr(spec, "LISTS", {"agendas": True, "requisitions": True, "badges": True})
if DO_LISTS and cz.sec:
    if lists.get("agendas"):
        ag = [a["name"] for a in cz.sec.agendas()] + list(getattr(spec, "EXTRA_AGENDAS", []))
        L.agendas(book, ag, cz.faction)
        cz.note(f"agendas ({len(ag)}): " + "; ".join(ag))
    if lists.get("requisitions"):
        rq = [r for r in cz.sec.requisitions() if r["name"] not in getattr(spec, "REQ_SKIP", ())]
        for r in rq:
            r["rp"] = getattr(spec, "REQ_RP", {}).get(r["name"], r["rp"])
        L.requisitions(book, rq)
        cz.note(f"requisitions ({len(rq)}): " + "; ".join(f"{r['name']} {r['cost']}" for r in rq))
    if lists.get("badges"):
        bd = cz.sec.badges()
        L.badges(book, bd)
        cz.note(f"badges ({len(bd)}): " + "; ".join(b["name"] for b in bd))
if DO_BUILD and hasattr(spec, "build"):
    spec.build(cz)
after = json.dumps(L.load(book), sort_keys=True)
for m in cz.log:
    print("-", m)
print(f"{book}: {'changed' if before != after else 'no change'}")
if APPLY and before != after:
    print("written, revision", L.save(book))
elif before != after:
    print("dry run (use --apply)")
