"""Rz detachments vs the official MFM site: DP, roles, enhancements (names, points, Upgrade tag) and which detachments
each roster offers. Needs WAHA_DIR (waha_lib) and MFM_SITE_JSON (mfm_site.py output). Run from anywhere."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
import os
SITE_JSON = os.environ.get("MFM_SITE_JSON", "/tmp/mfm_site.json")   # output of mfm_site.py <out.json>
site = json.load(open(SITE_JSON))
BOOK = {'adepta-sororitas': 'Adepta_Sororitas', 'adeptus-custodes': 'Adeptus_Custodes', 'adeptus-mechanicus': 'Adeptus_Mechanicus', 'aeldari': 'Aeldari',
        'astra-militarum': 'Astra_Militarum', 'black-templars': 'SM_Black_Templars', 'blood-angels': 'SM_Blood_Angels', 'chaos-daemons': 'Chaos_Daemons',
        'chaos-knights': 'Chaos_Knights', 'chaos-space-marines': 'Chaos_Space_Marines', 'chaos-titan-legions': 'Titanicus_Traitoris', 'dark-angels': 'SM_Dark_Angels',
        'death-guard': 'Death_Guard', 'deathwatch': 'SM_Deathwatch', 'drukhari': 'Drukhari', 'emperors-children': "Emperor's_Children", 'genestealer-cults': 'Genestealer_Cults',
        'grey-knights': 'Grey_Knights', 'imperial-agents': 'Imperial_Agents', 'imperial-knights': 'Imperial_Knights', 'leagues-of-votann': 'Leagues_of_Votann',
        'necrons': 'Necrons', 'orks': 'Orks', 'space-marines': 'Space_Marines', 'space-wolves': 'SM_Space_Wolves', 'tau-empire': "T'au_Empire",
        'thousand-sons': 'Thousand_Sons', 'titan-legions': 'Adeptus_Titanicus', 'tyranids': 'Tyranids', 'world-eaters': 'World_Eaters'}
TYPO = {'upgarde': 'upgrade', 'introneural': 'intraneural', 'reletavistic': 'relativistic'}
def norm(s):
    s = re.sub(r'\((aura|psychic|upgrade|upgarde)\)', '', s.lower())
    s = re.sub(r'[^a-z0-9]', '', s.replace('’', "'"))
    for a, b in TYPO.items(): s = s.replace(a, b)
    return s
books = W.load_books()
tot = {'det': 0, 'missing': 0, 'dp': 0, 'role': 0, 'enh_missing': 0, 'enh_pts': 0, 'extra': 0}
for slug, d in site.items():
    b = BOOK[slug]
    if b not in books:
        print('no book', b); continue
    res = W.resolved(books, b)
    dets = {norm(k.split('§', 1)[1]): (k, v) for k, v in res.items() if k.startswith('Detachment§')}
    enhs = {norm(k.split('§', 1)[1]): (k, v) for k, v in res.items() if k.startswith('Enhancement§')}
    # a roster-selectable detachment = a rank of the roster's Detachment stat
    ranks = ((res.get('Roster§Roster') or {}).get('stats') or {}).get('Detachment', {}).get('ranks') or {}
    offered = {norm(t['trait'].split('§', 1)[1]) for r in ranks.values() for t in r.get('traits', []) if t['trait'].startswith('Detachment§')}
    seen = set()
    for sd in d['detachments']:
        tot['det'] += 1; n = norm(sd['name']); seen.add(n)
        if n not in dets:
            tot['missing'] += 1; print(f"{b}: MISSING detachment {sd['name']} ({sd['dp']}DP {sd['roles']}{' UNIQUE ' + sd['unique'] if sd['unique'] else ''})"); continue
        k, v = dets[n]
        dp = ((v.get('stats') or {}).get('Detachment Points') or {}).get('value')
        if dp != sd['dp']:
            tot['dp'] += 1; print(f"{b}: {k}: DP {dp} vs site {sd['dp']}")
        roles = sorted(norm(r) for r in ((v.get('keywords') or {}).get('Role') or []))
        if roles != sorted(norm(r) for r in sd['roles']):
            tot['role'] += 1; print(f"{b}: {k}: roles {((v.get('keywords') or {}).get('Role'))} vs site {sd['roles']}")
        for e in sd['enhancements']:
            en = norm(e['name'])
            if en not in enhs:
                tot['enh_missing'] += 1; print(f"{b}: {k}: MISSING enhancement {e['name']} ({e['points']} pts)"); continue
            ek, ev = enhs[en]
            p = ((ev.get('stats') or {}).get('Points') or {}).get('value')
            if p != e['points']:
                tot['enh_pts'] += 1; print(f"{b}: {ek}: {p} pts vs site {e['points']} (in {sd['name']})")
            up_site = '(upgrade)' in e['name'].lower() or '(upgarde)' in e['name'].lower(); up_rz = 'Upgrade' in ((ev.get('keywords') or {}).get('Tags') or [])
            if up_site != up_rz:
                tot['upgrade'] = tot.get('upgrade', 0) + 1; print(f"{b}: {ek}: Upgrade tag {up_rz} vs site {up_site}")
        site_enh = {norm(e['name']) for e in sd['enhancements']}
        for ek, (ekey, ev) in enhs.items():
            if sd['name'].lower() in [x.lower() for x in ((ev.get('keywords') or {}).get('Keywords') or [])] and ek not in site_enh:
                tot['enh_extra'] = tot.get('enh_extra', 0) + 1; print(f"{b}: {k}: Rz-only enhancement {ekey} (not on the site)")
    for n in sorted(offered - seen):
        tot['extra'] += 1; print(f"{b}: offered but not on the site: {dets.get(n, (n,))[0]}")
print(tot)
