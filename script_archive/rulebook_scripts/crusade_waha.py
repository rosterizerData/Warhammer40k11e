"""Parse the Wahapedia Crusade sections stored at WAHA_CRUSADE_DIR (default
~/websites/datasources/wahapedia_crusade_2026-10-26/crusade_sections): crus10_<slug>.txt / crus11_<slug>.txt as written by
scratch tools waha_html2txt.py + waha_crusade_sections.py ('## '/'### ' headings carrying ⟦#anchor⟧ ids).

  sec = Section('death-guard', '11')
  sec.outline()                         # [(level, title, start_line)]
  sec.block('Agendas')                  # lines of that heading's block (to the next heading of same or higher level)
  sec.named('Agendas')                  # [{name, flavour, text, cost}] entries headed by an UPPERCASE line
  sec.requisitions(); sec.agendas(); sec.badges()
"""
import os, re
from pathlib import Path

DIR = Path(os.environ.get("WAHA_CRUSADE_DIR") or Path.home() / "websites/datasources/wahapedia_crusade_2026-10-26/crusade_sections")
ANCHOR = re.compile(r"⟦[^⟧]*⟧")
NAME = re.compile(r"^(?P<name>[A-Z0-9][A-Z0-9’'\-\.,!&/\(\)’ ]{2,}?)\s*(?P<cost>\d+(?:-\d+)?RP(?:/\d+RP)?)?$")
NOT_NAMES = {"D6", "D3", "D33", "D66", "REWARD", "EFFECT:", "INGREDIENTS REQUIRED", "CHOOSE ONE", "OR", "BATTLE HONOUR", "AELEMENTUS",
             "ESOTERIST", "MAGISTER TEMPLI", "THREAT", "RANGED WEAPONS", "RANGE", "A", "BS", "S", "AP", "D", "WS", "CONDITION", "WEAPON",
             "TYPE", "MELEE", "AGENDAS", "REQUISITIONS", "BATTLE TRAITS", "CRUSADE RELICS", "CRUSADE BADGES", "PERSONAL GLORY",
             "DARK GOD GLORY", "WARFLEET GLORY", "SAINT POINTS", "MARTYR POINTS", "COMMENDATION POINTS", "LOGISTICS POINTS", "PURGATION POINTS"}
RULES_START = re.compile(r"^(At |Each time|Purchase|If |Add |Select|While |Once |Roll |You can|You cannot|You must|Gain |Improve|Subtract|Until|In (your|the) |After |Before |When |Keep |Use |During|For each|Whilst|Re-roll|Do not|Choose|Change|Double|Halve|\d|\*|•|-|–|\||[A-Z][A-Z’' \-]+ (unit|model|units|models)s? (only|with)|[A-Z][A-Z’' \-]+ only\.)")
RULES_HINT = re.compile(r"(\bD6\b|\bD3\b|\bD33\b|\b2D6\b|\bXP\b|\bRP\b|\bCP\b|\d+\"|\d\+|Crusade (army|force|card|points|Relic|Blessing)|Battle Honour|Battle Trait|Battle Scar|Out of Action|Battle-shock|objective marker|re-roll|Hit roll|Wound roll|saving throw|invulnerable|Feel No Pain|Stratagem|Agenda|Requisition|Supply Limit|Order of Battle|characteristic|Starting Strength|Engagement Range|Strategic Reserves|Command phase|Shooting phase|Fight phase|Movement phase|Charge phase|battle round|deployment zone|No Man’s Land|keyword|this unit|this model|the bearer|your army|your opponent|enemy unit|friendly|the battle\b|that unit|that model)")


def is_rules(par):
    return bool(RULES_START.match(par) or RULES_HINT.search(par))


class Section:
    def __init__(self, slug, ed="11", lines=None):
        self.slug, self.ed = slug, ed
        if lines is None:
            p = DIR / f"crus{ed}_{slug}.txt"
            lines = p.read_text(encoding="utf-8").split("\n")
        self.lines = [ANCHOR.sub("", l).rstrip() for l in lines]
        self.heads = [(len(l) - len(l.lstrip("#")), l.lstrip("#").strip(), i) for i, l in enumerate(self.lines) if l.startswith("#")]

    def outline(self):
        return list(self.heads)

    def block(self, title, nth=0, *, upto=None):
        """body lines under the nth heading whose title matches (case-insensitive, exact or startswith). Ends at the next
        heading of the same or higher level, or at a heading titled `upto` (useful when the section nests oddly)."""
        hits = [h for h in self.heads if h[1].lower() == title.lower()] or [h for h in self.heads if h[1].lower().startswith(title.lower())]
        if len(hits) <= nth:
            return []
        lvl, _, start = hits[nth]
        end = len(self.lines)
        for l2, t2, i2 in self.heads:
            if i2 > start and (l2 <= lvl or (upto and t2.lower() == upto.lower())):
                end = i2
                break
        return self.lines[start + 1:end]

    def blocks_after(self, title, level=2, until=None):
        """headings of `level` that follow the heading `title` (badges are '## Name' after '### Crusade Badges')"""
        hits = [h for h in self.heads if h[1].lower() == title.lower()]
        if not hits:
            return []
        start = hits[0][2]
        out = []
        for k, (lvl, t, i) in enumerate(self.heads):
            if i <= start:
                continue
            if until and t.lower() == until.lower():
                break
            if lvl < level and i > start and t.lower() != title.lower():
                # a higher-level heading ends the run
                if out:
                    break
            if lvl == level:
                nxt = self.heads[k + 1][2] if k + 1 < len(self.heads) else len(self.lines)
                out.append((t, self.lines[i + 1:nxt]))
        return out

    # ── entries ──
    @staticmethod
    def paragraphs(lines):
        """one paragraph per non-empty line: the page converter already breaks blocks onto their own lines, and a
        flavour sentence often sits on the line right before the rules line with no blank between them"""
        return [l.strip() for l in lines if l.strip()]

    @staticmethod
    def is_name(line):
        s = line.strip()
        if not s or s.startswith(("|", "#")) or s in NOT_NAMES:
            return None
        m = NAME.match(s)
        if not m:
            return None
        name = m.group("name").strip()
        if len(name) < 3 or name in NOT_NAMES or not re.search(r"[A-Z]{2}", name):
            return None
        return name, m.group("cost")

    def named(self, title=None, lines=None, nth=0, *, drop_flavour=True, upto=None):
        """entries headed by an uppercase name line. Flavour = first paragraph when it does not read like rules."""
        lines = lines if lines is not None else self.block(title, nth, upto=upto)
        entries, cur = [], None
        for l in lines:
            nm = self.is_name(l)
            if nm:
                if cur:
                    entries.append(cur)
                cur = {"name": nm[0], "cost": nm[1], "lines": []}
            elif cur is not None:
                cur["lines"].append(l)
        if cur:
            entries.append(cur)
        out = []
        for e in entries:
            pars = [p for p in self.paragraphs(e["lines"]) if not p.startswith("|")]
            flavour = ""
            if drop_flavour and pars and not is_rules(pars[0]):
                flavour, pars = pars[0], pars[1:]
            out.append({"name": title_case(e["name"]), "raw_name": e["name"], "cost": e["cost"], "flavour": flavour, "text": "\n\n".join(pars)})
        return out

    def agendas(self, title="Agendas"):
        return [e for e in self.named(title) if e["text"]]

    def requisitions(self, title="Requisitions"):
        out = []
        for e in self.named(title):
            if not e["cost"] or not e["text"]:
                continue
            rp = int(re.match(r"\d+", e["cost"]).group())
            text = e["text"]
            if not re.fullmatch(r"\d+RP", e["cost"]):
                text = f"Cost: {e['cost']}. " + text
            out.append({"name": e["name"], "rp": rp, "cost": e["cost"], "text": text})
        return out

    def badges(self, title="Crusade Badges"):
        out = []
        for name, body in self.blocks_after(title, level=2):
            pars = self.paragraphs(body)
            if len(pars) > 1 and not re.match(r"^(You have|You |At least|One or more|Or:)", pars[0]):
                pars = pars[1:]   # the first paragraph is the badge's flavour text
            out.append({"name": name, "text": "\n".join(pars)})
            if len(out) == 3:
                break
        return out


def title_case(s):
    """UPPERCASE heading → Title Case keeping small words lower and apostrophes intact"""
    small = {"of", "the", "and", "a", "an", "to", "in", "on", "for", "or", "da", "em", "em!", "for"}
    words = s.lower().split(" ")
    out = []
    for i, w in enumerate(words):
        base = w
        if i and base in small:
            out.append(base)
            continue
        out.append(re.sub(r"(^|[\s\-/’'(])([a-z])", lambda m: m.group(1) + m.group(2).upper(), base))
    t = " ".join(out)
    t = re.sub(r"’S\b", "’s", t).replace("'S ", "'s ").replace("’Em", "’Em")
    return t
