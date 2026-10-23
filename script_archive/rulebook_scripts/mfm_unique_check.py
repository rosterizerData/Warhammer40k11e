"""Rz removeSameTagDetachments rules vs the MFM site's UNIQUE tags (one detachment per tag per army). Needs WAHA_DIR and
MFM_SITE_JSON (mfm_site.py output)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waha_lib as W
import os
SITE_JSON = os.environ.get("MFM_SITE_JSON", "/tmp/mfm_site.json")   # output of mfm_site.py <out.json>
BOOK = {'adepta-sororitas': 'Adepta_Sororitas', 'adeptus-custodes': 'Adeptus_Custodes', 'adeptus-mechanicus': 'Adeptus_Mechanicus', 'aeldari': 'Aeldari',
        'astra-militarum': 'Astra_Militarum', 'black-templars': 'SM_Black_Templars', 'blood-angels': 'SM_Blood_Angels', 'chaos-daemons': 'Chaos_Daemons',
        'chaos-knights': 'Chaos_Knights', 'chaos-space-marines': 'Chaos_Space_Marines', 'chaos-titan-legions': 'Titanicus_Traitoris', 'dark-angels': 'SM_Dark_Angels',
        'death-guard': 'Death_Guard', 'deathwatch': 'SM_Deathwatch', 'drukhari': 'Drukhari', 'emperors-children': "Emperor's_Children", 'genestealer-cults': 'Genestealer_Cults',
        'grey-knights': 'Grey_Knights', 'imperial-agents': 'Imperial_Agents', 'imperial-knights': 'Imperial_Knights', 'leagues-of-votann': 'Leagues_of_Votann',
        'necrons': 'Necrons', 'orks': 'Orks', 'space-marines': 'Space_Marines', 'space-wolves': 'SM_Space_Wolves', 'tau-empire': "T'au_Empire",
        'thousand-sons': 'Thousand_Sons', 'titan-legions': 'Adeptus_Titanicus', 'tyranids': 'Tyranids', 'world-eaters': 'World_Eaters'}
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))
site = json.load(open(SITE_JSON)); books = W.load_books()
bad = 0
for slug, d in site.items():
    b = BOOK[slug]; res = W.resolved(books, b)
    dets = {norm(k.split('§', 1)[1]): (k, v) for k, v in res.items() if k.startswith('Detachment§')}
    groups = {}
    for sd in d['detachments']:
        if sd['unique']:
            groups.setdefault(sd['unique'], []).append(sd['name'])
    # codex text carries tags the site doesn't print as UNIQUE ("This detachment has the COVENS tag and cannot be taken with another COVENS detachment")
    for sd in d['detachments']:
        k, v = dets.get(norm(sd['name']), (None, None))
        m = v and re.search(r'has the \*\*(.+?)\*\* tag', v.get('text') or '')
        if m and not sd['unique']:
            groups.setdefault(m.group(1).upper(), []).append(sd['name'])
    tagged = {norm(n): tag for tag, ns in groups.items() for n in ns}
    for tag, ns in list(groups.items()):   # a text tag seen on one member: pull in the members whose rules point back
        for n in ns:
            k, v = dets.get(norm(n), (None, None))
            for a in ((v or {}).get('rules') or {}).get('removeSameTagDetachments', {}).get('actions', []):
                o = next((x['name'] for x in d['detachments'] if norm(x['name']) == norm(a['value'])), None)
                if o and o not in ns and norm(o) not in tagged:
                    ns.append(o); tagged[norm(o)] = tag
    for sd in d['detachments']:
        n = norm(sd['name']); k, v = dets.get(n, (None, None))
        if not k:
            continue
        rule = (v.get('rules') or {}).get('removeSameTagDetachments')
        on_page = {norm(x['name']) for x in d['detachments']}
        have = sorted(norm(a['value']) for a in (rule or {}).get('actions', []) if a.get('actionType') == 'remove' and norm(a['value']) in on_page)
        want = sorted(norm(x) for x in groups.get(tagged.get(n), []) if norm(x) != n)
        if not want and have:   # a codex tag only one side's text names: accept a symmetric pair/group
            back = all(n in [norm(a['value']) for a in ((dets.get(o, (None, {}))[1].get('rules') or {}).get('removeSameTagDetachments') or {}).get('actions', [])] for o in have)
            if back:
                continue
        if have != want:
            bad += 1
            print(f"{b}: {k}: tag {tagged.get(n)} | rule removes {have} | site siblings {want}")
print(bad, 'mismatches')
