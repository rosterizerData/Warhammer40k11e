"""Leader vs Support typing: each attacher's Rz trait (Ability§Leader / Ability§Support) vs the datasheet's core ability in
the Waha export, with the MFM site's LEADER:/SUPPORT: lists as a second opinion. Also inventories the hand-written
two-leader rules. Needs WAHA_DIR and MFM_SITE_JSON. Prints findings; --apply fixes traits in the defining book."""
import csv, json, os, re, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
APPLY = "--apply" in sys.argv
SITE_JSON = os.environ.get("MFM_SITE_JSON", "/tmp/mfm_site.json"); WD = os.environ["WAHA_DIR"]
BOOK = {'adepta-sororitas': 'Adepta_Sororitas', 'adeptus-custodes': 'Adeptus_Custodes', 'adeptus-mechanicus': 'Adeptus_Mechanicus', 'aeldari': 'Aeldari',
        'astra-militarum': 'Astra_Militarum', 'black-templars': 'SM_Black_Templars', 'blood-angels': 'SM_Blood_Angels', 'chaos-daemons': 'Chaos_Daemons',
        'chaos-knights': 'Chaos_Knights', 'chaos-space-marines': 'Chaos_Space_Marines', 'chaos-titan-legions': 'Titanicus_Traitoris', 'dark-angels': 'SM_Dark_Angels',
        'death-guard': 'Death_Guard', 'deathwatch': 'SM_Deathwatch', 'drukhari': 'Drukhari', 'emperors-children': "Emperor's_Children", 'genestealer-cults': 'Genestealer_Cults',
        'grey-knights': 'Grey_Knights', 'imperial-agents': 'Imperial_Agents', 'imperial-knights': 'Imperial_Knights', 'leagues-of-votann': 'Leagues_of_Votann',
        'necrons': 'Necrons', 'orks': 'Orks', 'space-marines': 'Space_Marines', 'space-wolves': 'SM_Space_Wolves', 'tau-empire': "T'au_Empire",
        'thousand-sons': 'Thousand_Sons', 'titan-legions': 'Adeptus_Titanicus', 'tyranids': 'Tyranids', 'world-eaters': 'World_Eaters'}
SUFFIX = re.compile(r'\s*\((agents|legends|old|on foot|new)\)\s*$', re.I)
norm = lambda s: re.sub(r'[^a-z0-9]', '', SUFFIX.sub('', s).lower().replace('’', "'").replace('‑', '-'))
rd = lambda f: list(csv.DictReader(open(f'{WD}/{f}', encoding='utf-8-sig'), delimiter='|'))
ds = {r['id']: r for r in rd('Datasheets.csv')}; abil = {r['id']: r for r in rd('Abilities.csv')}
waha_f = defaultdict(set)   # (faction_id, norm(name)) -> {'Leader','Support'} from the datasheet's core abilities
for r in rd('Datasheets_abilities.csv'):
    if r.get('type') == 'Core':
        a = (abil.get(r.get('ability_id')) or {}).get('name', '').strip()
        if a in ('Leader', 'Support'):
            waha_f[(ds[r['datasheet_id']]['faction_id'], norm(ds[r['datasheet_id']]['name']))].add(a)
FACTION = {norm(r['name']): r['id'] for r in rd('Factions.csv')}   # Waha faction ids by name
site = json.load(open(SITE_JSON)); books = W.load_books(); RZ = W.RZ
RULE = re.compile(r'allow.*leaders?|twoLeaders|Increase leaders|allow3Leaders', re.I)
tot = Counter(); fixes = defaultdict(list); rules = []
def traits(v): return [t.get('trait') or t.get('item') if isinstance(t, dict) else t for t in (v.get('assets') or {}).get('traits', [])]
for slug, d in site.items():
    b = BOOK[slug]; res = W.resolved(books, b); chain = W.chain(books, b) + [b]
    fid = FACTION.get(norm(slug.replace('-', ' ').replace('emperors', "emperor's").replace('tau', "t'au")))
    waha = {n: t for (f, n), t in waha_f.items() if f == fid}
    for (f, n), t in waha_f.items():   # a datasheet another faction shares (allies): fall back to it
        waha.setdefault(n, t)
    sitetype = {}
    for u in d['units']:
        L, S = bool(u.get('leaderTo')), bool(u.get('supportTo'))
        if L or S: sitetype[norm(u['name'])] = {'Leader'} if L and not S else {'Support'} if S and not L else {'Leader', 'Support'}
    NOT_ATTACHER = ('Model', 'Ability', 'Weapon', 'Ranged Weapon', 'Melee Weapon', 'Wargear', 'Enhancement', 'Stratagem', 'Detachment')
    for k, v in res.items():
        cls, _, name = k.partition('§'); n = norm(name)
        if cls in NOT_ATTACHER or n not in sitetype or (SUFFIX.search(name) and not (b == 'Imperial_Agents' and name.endswith('(Agents)'))):
            continue   # only Characters / attaching units the site lists as leaders; no variant copies
        have = {a.split('§', 1)[1] for a in traits(v) if a in ('Ability§Leader', 'Ability§Support')}
        want = waha.get(n) or sitetype[n]
        src = 'waha' if n in waha else 'site'
        if n in waha and waha[n] != sitetype[n] and len(sitetype[n]) == 1:
            tot['waha_vs_site'] += 1; print(f"  note {b} {k}: waha {sorted(waha[n])} vs site {sorted(sitetype[n])}")
        if have != want:
            tot['type_mismatch'] += 1; print(f"{b}: {k}: traits {sorted(have)} should be {sorted(want)} ({src})")
            fixes[k].append((b, chain, have, want))
        for rk in (v.get('rules') or {}):
            if RULE.search(rk): rules.append((b, k, rk))
print(dict(tot)); print(len(rules), 'two-leader rules on these pages:', Counter(r[2] for r in rules))
if APPLY:
    touched = set()
    for k, lst in fixes.items():
        b, chain, have, want = lst[0]
        for bk in chain:   # fix the trait in every book of the chain that defines it (traits merge by union)
            e = books[bk]['rulebook']['assetCatalog'].get(k)
            if not e or 'traits' not in (e.get('assets') or {}): continue
            tr = e['assets']['traits']; names = traits(e)
            for a in ('Ability§Leader', 'Ability§Support'):
                if a in names and a.split('§', 1)[1] not in want:
                    tr[:] = [t for t in tr if (t.get('trait') or t.get('item') if isinstance(t, dict) else t) != a]; touched.add(bk)
            for a in want:
                if 'Ability§' + a not in names and bk == chain[-1] if False else ('Ability§' + a not in names):
                    pass
        # add the wanted ability where the trait list lives (the first book in the chain that has traits for this key)
        for bk in chain:
            e = books[bk]['rulebook']['assetCatalog'].get(k)
            if e and 'traits' in (e.get('assets') or {}):
                names = traits(e)
                for a in want:
                    if 'Ability§' + a not in names:
                        e['assets']['traits'].append({'trait': 'Ability§' + a}); touched.add(bk)
                break
    for bk in touched:
        dd = books[bk]; a, b_, c = dd['revision'].split('.'); dd['revision'] = f'{a}.{b_}.{int(c)+1}'
        open(RZ / f"{bk}.rulebook", "w").write(json.dumps(dd, indent=2, ensure_ascii=False)); print('wrote', bk, dd['revision'])
