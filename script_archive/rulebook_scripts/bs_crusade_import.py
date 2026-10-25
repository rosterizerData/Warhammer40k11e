"""Fill the faction Crusade blocs from BSData's codex Crusade content (bs_crusade_extract.py output):
Battle Traits, tiered Crusade Relics, Battle Scars and the faction "mechanic" honours (Boons, Archeotech, Chapter Command…)
as Battle Honour§ items, plus the Crusade: Armageddon traits/relics/Mighty Champions in the core book.
Unit-type gates become Tags (any-of) and not-Tags (none-of); each book gets the Unit taxonomy rules that grant those tags
from keywords, mirroring the Necron bloc (allowCanoptekTraits). Items already present by name are left alone.
Dry-run unless --apply. Needs BS_CRUSADE_JSON (extract output) and WAHA_DIR (waha_lib)."""
import json, os, re, sys, unicodedata
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
APPLY = "--apply" in sys.argv
F = json.load(open(os.environ["BS_CRUSADE_JSON"]))
books = W.load_books(); RZ = W.RZ
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).lower().replace("’", "'"))
BOOK = {'Aeldari - Aeldari Library': 'Aeldari', 'Chaos - Chaos Daemons Library': 'Chaos_Daemons', 'Chaos - Chaos Knights Library': 'Chaos_Knights',
        'Chaos - Chaos Space Marines': 'Chaos_Space_Marines', 'Chaos - Death Guard': 'Death_Guard', "Chaos - Emperor's Children": "Emperor's_Children",
        'Chaos - Thousand Sons': 'Thousand_Sons', 'Chaos - World Eaters': 'World_Eaters', 'Genestealer Cults': 'Genestealer_Cults',
        'Imperium - Adepta Sororitas': 'Adepta_Sororitas', 'Imperium - Adeptus Custodes': 'Adeptus_Custodes', 'Imperium - Adeptus Mechanicus': 'Adeptus_Mechanicus',
        'Imperium - Agents of the Imperium': 'Imperial_Agents', 'Imperium - Astra Militarum - Library': 'Astra_Militarum', 'Imperium - Black Templars': 'SM_Black_Templars',
        'Imperium - Grey Knights': 'Grey_Knights', 'Imperium - Imperial Knights - Library': 'Imperial_Knights', 'Imperium - Space Marines': 'Space_Marines',
        'Leagues of Votann': 'Leagues_of_Votann', 'Library - Tyranids': 'Tyranids', 'Necrons': 'Necrons', 'Orks': 'Orks', "T'au Empire": "T'au_Empire"}
SHARED = {'Monster Hunters', 'Striding Behemoths', 'Blackstone Battle Honours', 'Blackstone Crusade Relics', 'Main Rules Battle Scars'}
SUPP = ('Tyrannic War', 'Pariah Nexus', 'Nachmund Gauntlet', 'Armageddon', 'Mighty Champions')
CHAPTER_GROUP = {'Inner Circle Advancement': 'SM_Dark_Angels', 'Angels Ascendant': 'SM_Blood_Angels', 'Lone Wolf Battle Scars': 'SM_Space_Wolves'}
CORE_TAGS = {'Character', 'Infantry', 'Mounted', 'Vehicle', 'Monster'}
TIER = {'Artificer Relics': ('Artificer Relic', None), 'Antiquity Relics': ('Antiquity Relic', 2), 'Legendary Relics': ('Legendary Relic', 3)}
def route(src_book, gates):
    """Aeldari library content splits by faction gate; chapter-specific SM groups go to the chapter books"""
    pos = [c for p, c in gates if p == '+']
    if src_book == 'Aeldari':
        if 'Faction: Drukhari' in pos: return 'Drukhari'
        if 'Faction: Harlequins' in pos: return 'Harlequins'
    return src_book
def tags_for(gates, book):
    anyt, nonet = [], []
    for p, c in gates:
        if c.startswith('Faction: '):
            fac = c[9:]
            if p == '+' and ((book == 'Drukhari' and fac == 'Drukhari') or (book == 'Aeldari' and fac == 'Asuryani') or (book == 'Grey_Knights' and fac == 'Grey Knights') or (book == 'Adeptus_Custodes' and fac == 'Adeptus Custodes') or (book == 'Astra_Militarum' and fac == 'Astra Militarum')):
                continue   # the whole book is that faction
        (anyt if p == '+' else nonet).append(c)
    return anyt, nonet
plan = defaultdict(lambda: {'assets': {}, 'anytags': set(), 'nonetags': set()}); notext = []
stats = Counter(); skipped = []
SM_FAMILY = {'Space_Marines', 'SM_Black_Templars', 'SM_Blood_Angels', 'SM_Dark_Angels', 'SM_Deathwatch', 'SM_Space_Wolves'}
def add_asset(book, key, asset, anyt=(), nonet=()):
    cat = books[book]['rulebook']['assetCatalog']
    cls, _, name = key.partition('§')
    if any(k.startswith(cls + '§') and norm(k.split('§', 1)[1]) == norm(name) for k in cat) or key in plan[book]['assets']:
        stats['already'] += 1; return
    if not asset.get('text'): stats['no text'] += 1; notext.append((book, key)); return
    if not asset.get('keywords', {}).get('Tags'):   # no unit gate: any unit of the book's faction (its Faction keyword sits in every unit's constraints)
        fac = ((books[book]['rulebook']['assetCatalog'].get('Roster§Roster') or {}).get('stats', {}).get('Faction', {}).get('value')) or {'Harlequins': 'Harlequins', 'Space_Marines': 'Adeptus Astartes'}.get(book)
        if fac: asset.setdefault('keywords', {})['Tags'] = [fac]
    plan[book]['assets'][key] = asset; stats[cls] += 1
    plan[book]['anytags'].update(anyt); plan[book]['nonetags'].update(nonet)
for src, fac in F.items():
    book0 = BOOK.get(src)
    if not book0: continue
    for it in fac['traits']:
        book = route(book0, it['gates']); anyt, nonet = tags_for(it['gates'], book)
        a = {'keywords': {'Tags': anyt + ['not' + c.replace(' ', '') for c in nonet]}, 'text': it['text']}
        add_asset(book, 'Battle Trait§' + it['name'], a, anyt, nonet)
    for tier, items in fac['relics'].items():
        tag, pts = TIER.get(tier, (None, None))
        if not tag:
            for it in items:
                book = route(book0, it['gates']); anyt, nonet = tags_for(it['gates'], book)
                add_asset(book, 'Crusade Honour§' + it['name'], {'keywords': {'Keywords': [tier], 'Tags': anyt + ['not' + c.replace(' ', '') for c in nonet]}, 'text': it['text']}, anyt, nonet)
            continue
        for it in items:
            book = route(book0, it['gates']); anyt, nonet = tags_for(it['gates'], book)
            a = {'keywords': {'Tags': [tag]}, 'text': it['text']}
            if pts: a['stats'] = {'Crusade Pts': {'value': pts}}
            if book == 'Harlequins' and 'Faction: Harlequins' not in anyt: anyt = anyt + ['Faction: Harlequins']   # the hub is visible to Aeldari and Drukhari rosters
            if anyt or nonet:   # relic-specific gate as an error rule (tier tag must stay the only allow-tag)
                evals = [{'actionable': True, 'contains': True, 'not': False, 'operator': 'AND', 'paths': [['{parent}', 'keywords', 'Faction' if c.startswith('Faction: ') else 'Keywords']], 'value': c.replace('Faction: ', '')} for c in anyt]
                evals += [{'actionable': True, 'contains': True, 'not': True, 'operator': 'AND', 'paths': [['{parent}', 'keywords', 'Keywords']], 'value': c} for c in nonet]
                a['rules'] = {(' or '.join(c.replace('Faction: ', '') for c in anyt) or 'This') + (' only' if anyt else '') + (' (not ' + ', '.join(nonet) + ')' if nonet else '') + '.': {'evals': evals, 'evaluate': 'OR' if len(anyt) > 1 and not nonet else 'AND', 'failState': 'error'}}
            add_asset(book, 'Crusade Relic§' + it['name'], a)
    for it in fac['scars']:
        book = route(book0, it['gates']); anyt, nonet = tags_for(it['gates'], book)
        a = {'keywords': {'Tags': anyt + ['not' + c.replace(' ', '') for c in nonet]}, 'text': it['text']}
        add_asset(book, 'Battle Scar§' + it['name'], a, anyt, nonet)
    for grp, items in fac['honours'].items():
        if grp in SHARED or grp.startswith(SUPP): continue
        for it in items:
            book = CHAPTER_GROUP.get(grp) or route(book0, it['gates']); anyt, nonet = tags_for(it['gates'], book)
            cls = 'Battle Scar' if 'Scar' in grp else 'Crusade Honour'
            a = {'keywords': {'Keywords': [grp], 'Tags': anyt + ['not' + c.replace(' ', '') for c in nonet]}, 'text': it['text']}
            cp = it['costs'].get('Crusade Points')
            if cp not in (None, 1, '1', 1.0): a['stats'] = {'Crusade Pts': {'value': int(float(cp))}}
            add_asset(book, f'{cls}§' + it['name'], a, anyt, nonet)
# tag-granting rules per book (Unit taxonomy), mirroring Necrons.allowCanoptekTraits
def kw_eval(tag, book):
    if tag.startswith('Faction: ') and book in SM_FAMILY:
        return {'actionable': True, 'not': False, 'operator': 'AND', 'paths': [['{roster}', 'stats', 'Chapter', 'value']], 'value': tag[9:]}
    return {'actionable': True, 'contains': True, 'not': False, 'operator': 'AND', 'paths': [['{self}', 'keywords', 'Faction' if tag.startswith('Faction: ') else 'Keywords']], 'value': tag.replace('Faction: ', '')}
NARR = {'actionable': True, 'not': False, 'operator': 'AND', 'paths': [['{roster}', 'stats', 'Play', 'value']], 'value': 'Narrative'}
def grant_rule(tag, book):
    return {'actions': [{'actionType': 'add', 'iterations': 1, 'paths': [['{self}', 'constraints', 'any']], 'value': tag}], 'evals': [NARR, kw_eval(tag, book)], 'evaluate': 'AND', 'failState': 'pass',
            'note': 'Crusade: units with this keyword may take the Battle Honours tagged with it'}
def block_rule(tag, book):
    return {'actions': [{'actionType': 'add', 'iterations': 1, 'paths': [['{self}', 'constraints', 'none']], 'value': 'not' + tag.replace(' ', '')}], 'evals': [NARR, kw_eval(tag, book)], 'evaluate': 'AND', 'failState': 'pass',
            'note': 'Crusade: units with this keyword cannot take the Battle Honours tagged not-this'}
for book, p in plan.items():
    p['rules'] = {}
    have = set(((books[book]['rulebook'].get('assetTaxonomy') or {}).get('Unit') or {}).get('rules') or {})
    for t in sorted(p['anytags'] - CORE_TAGS):
        rn = 'crusadeTag' + re.sub(r'\W', '', t)
        if rn not in have: p['rules'][rn] = grant_rule(t, book)
    for t in sorted(p['nonetags'] - CORE_TAGS):
        rn = 'crusadeNot' + re.sub(r'\W', '', t)
        if rn not in have: p['rules'][rn] = block_rule(t, book)
# core: generic exclusion tags + a Battle Honour allowance (the mechanic honours are Battle Honour§ items)
core = books['Warhammer_40k_11e']['rulebook']; U = core['assetTaxonomy']['Unit']['rules']
core_new = {}
for t in ('Character', 'Infantry', 'Mounted', 'Vehicle', 'Monster'):
    if 'crusadeNot' + t not in U: core_new['crusadeNot' + t] = block_rule(t, 'Warhammer_40k_11e')
if 'allowCrusadeHonours' not in U:   # a class of its own: an allowance on 'Battle Honour' would admit every honour class templated on it
    r = json.loads(json.dumps(U['allowTraits'])); r['actions'][0]['value'] = 'Crusade Honour'; core_new['allowCrusadeHonours'] = r
    T = core['assetTaxonomy']; T.setdefault('Crusade Honour', {'aspects': {'Lock Qty': True}, 'keywords': {'Tags': [], 'Keywords': []}, 'templateClass': 'Battle Honour'})
# Crusade: Armageddon (10e, May 2025): traits, tiered relics and the Mighty Champions, gated by a Campaign mission flag like Tyrannic War
ARM = {'assets': {}, 'tax': {}}
src = F['Chaos - Death Guard']
for it in src['honours'].get('Armageddon Battle Traits', []):
    anyt = [c for p, c in it['gates'] if p == '+']; nonet = [c for p, c in it['gates'] if p == '-']
    ARM['assets']['Armageddon Trait§' + it['name']] = {'keywords': {'Tags': anyt + ['not' + c.replace(' ', '') for c in nonet]}, 'text': it['text']}
for it in src['honours'].get('Armageddon Crusade Relics', []):
    tag, pts = TIER.get(it['path'][-1], ('Artificer Relic', None))
    a = {'keywords': {'Tags': [tag]}, 'text': it['text']}
    if pts: a['stats'] = {'Crusade Pts': {'value': pts}}
    ARM['assets']['Armageddon Relic§' + it['name']] = a
for it in F['Aeldari - Aeldari Library']['honours'].get('Mighty Champions', []):
    if it['path'] and it['path'][-1] == 'Armageddon Crusade Abilities' and it['text']: ARM['assets'].setdefault('Mighty Champion§' + it['name'], {'keywords': {'Tags': ['Character']}, 'text': it['text']})
T = core['assetTaxonomy']
ARM['tax'] = {'Armageddon Trait': json.loads(json.dumps(T['Tyrannic Trait'])), 'Armageddon Relic': json.loads(json.dumps(T.get('Tyrannic Relic') or T['Tyrannic Trait'])),
              'Mighty Champion': {'aspects': {'Lock Qty': True, 'Unique': True}, 'keywords': {'Tags': [], 'Keywords': []}, 'templateClass': 'Battle Honour'}}
def retrack(rule, cls):
    r = json.loads(json.dumps(rule).replace('"Tyrannic War"', '"Armageddon"')); r['actions'][0]['value'] = cls; return r
arm_rules = {'Unit': {'allowArmageddonTraits': retrack(U['allowTyrannicTraits'], 'Armageddon Trait')},
             'Character': {'allowArmageddonRelics': retrack(core['assetTaxonomy']['Character']['rules']['allowTyrannicRelics'], 'Armageddon Relic'),
                           'allowMightyChampion': {'actions': [{'actionType': 'add', 'iterations': 1, 'paths': [['{self}', 'allowed', 'classifications']], 'value': 'Mighty Champion'}],
                                                   'evals': [{'actionable': True, 'min': 1, 'not': False, 'operator': 'AND', 'paths': [['{roster}', 'tracked', 'Armageddon']]},
                                                             {'actionable': True, 'contains': True, 'not': False, 'operator': 'AND', 'paths': [['{self}', 'keywords', 'Keywords']], 'value': 'Epic Hero'}],
                                                   'evaluate': 'AND', 'failState': 'pass', 'note': 'Crusade: Armageddon — the Campaign Master gives each named character one Mighty Champion ability'},
                           'One Mighty Champion ability per character.': {'evals': [{'actionable': True, 'max': 1, 'not': False, 'operator': 'AND', 'paths': [['{self}', 'tally', 'Mighty Champion']]}], 'evaluate': 'AND', 'failState': 'error'}}}
print('Armageddon:', Counter(k.split('§')[0] for k in ARM['assets']))
# report
for book, p in sorted(plan.items()):
    c = Counter(k.split('§')[0] for k in p['assets'])
    print(f"{book:22} {dict(c)} | rules: {sorted(p['rules'])}")
print('core rules to add:', sorted(core_new)); print('stats:', dict(stats)); print('skipped:', skipped[:10]); print('no text:', [k for b, k in notext])
if APPLY:
    touched = set()
    for book, p in plan.items():
        d = books[book]; cat = d['rulebook']['assetCatalog']
        for k, a in p['assets'].items(): cat[k] = a
        if p['rules']:
            tax = d['rulebook'].setdefault('assetTaxonomy', {}).setdefault('Unit', {}); tax.setdefault('rules', {}).update(p['rules'])
        touched.add(book)
    if core_new: U.update(core_new); touched.add('Warhammer_40k_11e')
    for k, a in ARM['assets'].items():
        if k not in core['assetCatalog']: core['assetCatalog'][k] = a
    for cls, tax in ARM['tax'].items(): T.setdefault(cls, tax)
    for cls, rules in arm_rules.items():
        for rk, rv in rules.items(): T[cls]['rules'].setdefault(rk, rv)
    mr = T['Campaign']['stats']['Mission']['ranks']; mr.setdefault('Armageddon', {'order': 3, 'tracking': {'Armageddon': 1}})
    touched.add('Warhammer_40k_11e')
    for bk in touched:
        d = books[bk]; a, m, c = d['revision'].split('.'); d['revision'] = f'{a}.{m}.{int(c)+1}'
        open(RZ / f'{bk}.rulebook', 'w').write(json.dumps(d, indent=2, ensure_ascii=False)); print('wrote', bk, d['revision'])
