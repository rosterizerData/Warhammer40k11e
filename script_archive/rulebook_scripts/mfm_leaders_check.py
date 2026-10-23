"""Unit `allowed.items` (which Characters may attach) vs the MFM site's LEADER:/SUPPORT: lists, per faction page,
on the resolved view of that faction's book. Needs WAHA_DIR (waha_lib) and MFM_SITE_JSON (mfm_site.py output)."""
import json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
SITE_JSON = os.environ.get("MFM_SITE_JSON", "/tmp/mfm_site.json")
BOOK = {'adepta-sororitas': 'Adepta_Sororitas', 'adeptus-custodes': 'Adeptus_Custodes', 'adeptus-mechanicus': 'Adeptus_Mechanicus', 'aeldari': 'Aeldari',
        'astra-militarum': 'Astra_Militarum', 'black-templars': 'SM_Black_Templars', 'blood-angels': 'SM_Blood_Angels', 'chaos-daemons': 'Chaos_Daemons',
        'chaos-knights': 'Chaos_Knights', 'chaos-space-marines': 'Chaos_Space_Marines', 'chaos-titan-legions': 'Titanicus_Traitoris', 'dark-angels': 'SM_Dark_Angels',
        'death-guard': 'Death_Guard', 'deathwatch': 'SM_Deathwatch', 'drukhari': 'Drukhari', 'emperors-children': "Emperor's_Children", 'genestealer-cults': 'Genestealer_Cults',
        'grey-knights': 'Grey_Knights', 'imperial-agents': 'Imperial_Agents', 'imperial-knights': 'Imperial_Knights', 'leagues-of-votann': 'Leagues_of_Votann',
        'necrons': 'Necrons', 'orks': 'Orks', 'space-marines': 'Space_Marines', 'space-wolves': 'SM_Space_Wolves', 'tau-empire': "T'au_Empire",
        'thousand-sons': 'Thousand_Sons', 'titan-legions': 'Adeptus_Titanicus', 'tyranids': 'Tyranids', 'world-eaters': 'World_Eaters'}
SUFFIX = re.compile(r'\s*\((agents|legends|old|on foot|new)\)\s*$', re.I)   # book-variant suffixes on Rz keys
norm = lambda s: re.sub(r'[^a-z0-9]', '', SUFFIX.sub('', s).lower().replace('’', "'").replace('‑', '-'))
site = json.load(open(SITE_JSON)); books = W.load_books()
tot = defaultdict(int)
for slug, d in site.items():
    b = BOOK[slug]; res = W.resolved(books, b)
    by_name = defaultdict(list)
    for k in sorted(res, key=lambda k: bool(SUFFIX.search(k.split('§', 1)[1]))):   # plain names before variant copies
        v = res[k]
        cls, _, name = k.partition('§')
        if cls not in ('Model', 'Weapon', 'Ranged Weapon', 'Melee Weapon', 'Wargear', 'Ability', 'Enhancement', 'Stratagem', 'Detachment'):
            by_name[norm(name)].append(k)
    on_page = {norm(u['name']) for u in d['units']}
    leaders = {norm(u['name']) for u in d['units'] if u.get('leaderTo') or u.get('supportTo')}
    # attachers are usually Character§ but a few are units (Warlock Conclave / Skyrunners): any catalog key the site names as a leader
    chars = {norm(k.split('§', 1)[1]) for k in res if k.startswith('Character§') or norm(k.split('§', 1)[1]) in leaders}
    expected = defaultdict(set)   # unit -> characters the site says may attach (leader or support)
    for u in d['units']:
        for t in u.get('leaderTo', []) + u.get('supportTo', []):
            expected[norm(t)].add(norm(u['name']))
    lines = []
    for un, exp in sorted(expected.items()):
        if un not in on_page:
            tot['led_unit_off_page'] += 1; continue   # Legends targets the site still names: the old lists stay
        keys = [k for k in by_name.get(un, []) if not k.startswith('Character§')] or by_name.get(un, [])
        if not keys:
            tot['unit_not_found'] += 1; lines.append(f"  unit not in book: {un} (led by {sorted(exp)})"); continue
        k = keys[0]; v = res[k]
        allowed = {norm(x.split('§', 1)[1]) for x in ((v.get('allowed') or {}).get('items') or []) if not x.startswith('Model§')}
        missing = sorted(c for c in exp - allowed if c in chars)
        absent = sorted(c for c in exp - allowed if c not in chars)
        extra = sorted(c for c in allowed - exp if c in on_page and (c in leaders or ('Character§' + c) in {norm(k) and 'Character§' + norm(k.split('§', 1)[1]) for k in res if k.startswith('Character§')}))
        own = k in (books[b].get('rulebook') or books[b])['assetCatalog'] if isinstance(books[b], dict) else True
        if missing: tot['missing'] += len(missing); lines.append(f"  {k}: MISSING {missing}" + ('' if own else ' (hub-defined)'))
        if absent: tot['char_absent'] += len(absent); lines.append(f"  {k}: character not in book {absent}")
        if extra: tot['extra'] += len(extra); lines.append(f"  {k}: EXTRA {extra}" + ('' if own else ' (hub-defined)'))
    print(f"== {b}: {len(expected)} led units checked" + (f", {len(lines)} findings" if lines else ", clean"))
    for l in lines: print(l)
print(dict(tot))
