"""Apply mfm_leaders_check findings: remove attachers the MFM site doesn't list from unit `allowed.items` (in every book of
the chain that lists them — allowed merges by union) and add the ones it lists but the book lacks (own-book override).
Needs WAHA_DIR and MFM_SITE_JSON. Dry-run unless --apply."""
import json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
APPLY = "--apply" in sys.argv
BOOK = {'adepta-sororitas': 'Adepta_Sororitas', 'adeptus-custodes': 'Adeptus_Custodes', 'adeptus-mechanicus': 'Adeptus_Mechanicus', 'aeldari': 'Aeldari',
        'astra-militarum': 'Astra_Militarum', 'black-templars': 'SM_Black_Templars', 'blood-angels': 'SM_Blood_Angels', 'chaos-daemons': 'Chaos_Daemons',
        'chaos-knights': 'Chaos_Knights', 'chaos-space-marines': 'Chaos_Space_Marines', 'chaos-titan-legions': 'Titanicus_Traitoris', 'dark-angels': 'SM_Dark_Angels',
        'death-guard': 'Death_Guard', 'deathwatch': 'SM_Deathwatch', 'drukhari': 'Drukhari', 'emperors-children': "Emperor's_Children", 'genestealer-cults': 'Genestealer_Cults',
        'grey-knights': 'Grey_Knights', 'imperial-agents': 'Imperial_Agents', 'imperial-knights': 'Imperial_Knights', 'leagues-of-votann': 'Leagues_of_Votann',
        'necrons': 'Necrons', 'orks': 'Orks', 'space-marines': 'Space_Marines', 'space-wolves': 'SM_Space_Wolves', 'tau-empire': "T'au_Empire",
        'thousand-sons': 'Thousand_Sons', 'titan-legions': 'Adeptus_Titanicus', 'tyranids': 'Tyranids', 'world-eaters': 'World_Eaters'}
SITE_JSON = os.environ.get("MFM_SITE_JSON", "/tmp/mfm_site.json")
SUFFIX = re.compile(r'\s*\((agents|legends|old|on foot|new)\)\s*$', re.I)   # book-variant suffixes on Rz keys
norm = lambda s: re.sub(r'[^a-z0-9]', '', SUFFIX.sub('', s).lower().replace('’', "'").replace('‑', '-'))
site = json.load(open(SITE_JSON)); books = W.load_books(); RZ = W.RZ
changed = defaultdict(list)
for slug, d in site.items():
    b = BOOK[slug]; res = W.resolved(books, b); chain = W.chain(books, b) + [b]
    on_page = {norm(u['name']) for u in d['units']}
    leaders = {norm(u['name']) for u in d['units'] if u.get('leaderTo') or u.get('supportTo')}
    keyof = {}
    ordered = sorted(res, key=lambda k: bool(SUFFIX.search(k.split('§', 1)[1])))   # plain names first, variants fall back
    for k in ordered:
        n = norm(k.split('§', 1)[1])
        if k.startswith('Character§') or n in leaders:
            keyof.setdefault(n, k)
    expected = defaultdict(set)
    for u in d['units']:
        for t in u.get('leaderTo', []) + u.get('supportTo', []):
            expected[norm(t)].add(norm(u['name']))
    units = {}
    for k in ordered:
        cls, _, name = k.partition('§')
        if cls not in ('Model', 'Weapon', 'Ranged Weapon', 'Melee Weapon', 'Wargear', 'Ability', 'Enhancement', 'Stratagem', 'Detachment', 'Character'):
            units.setdefault(norm(name), k)
    for un, exp in sorted(expected.items()):
        if un not in on_page or un not in units:
            continue
        k = units[un]
        if SUFFIX.search(k.split('§', 1)[1]):
            continue   # only a variant copy exists here (Legends duplicate): leave it
        allowed = {norm(x.split('§', 1)[1]): x for x in ((res[k].get('allowed') or {}).get('items') or []) if not x.startswith('Model§')}
        missing = [c for c in exp - set(allowed) if c in keyof]
        extra = [allowed[c] for c in set(allowed) - exp if c in on_page and (c in leaders or allowed[c].startswith('Character§'))]
        for x in extra:   # remove from every book in the chain whose entry lists it
            for bk in chain:
                e = books[bk]['rulebook']['assetCatalog'].get(k) or {}
                items = (e.get('allowed') or {}).get('items') or []
                if x in items:
                    items.remove(x); changed[bk].append(f"{k}: - {x}")
        if missing:
            e = books[b]['rulebook']['assetCatalog'].setdefault(k, {})
            items = e.setdefault('allowed', {}).setdefault('items', [])
            for c in missing:
                if keyof[c] not in items:
                    items.append(keyof[c]); changed[b].append(f"{k}: + {keyof[c]}")
for bk, lines in changed.items():
    print(f"== {bk} ({len(lines)})"); print("\n".join("   " + l for l in lines))
if APPLY:
    for bk in changed:
        d = books[bk]; a, b_, c = d['revision'].split('.'); d['revision'] = f'{a}.{b_}.{int(c)+1}'
        open(RZ / f"{bk}.rulebook", "w").write(json.dumps(d, indent=2, ensure_ascii=False)); print("wrote", bk, d['revision'])
