"""BSData 11e catalogues (BSDATA_DIR, the wh40k-11e JSON files) -> per-faction Crusade content with unit-type gating (from 'hidden if notInstanceOf <category>' modifiers)."""
import json, glob, re, sys
from collections import Counter, defaultdict
index={}
def idx(o):
    if isinstance(o, dict):
        if o.get('id') and o.get('name'): index[o['id']]=o
        for v in o.values(): idx(v)
    elif isinstance(o, list):
        for v in o: idx(v)
import os; BS=os.environ.get("BSDATA_DIR", "."); files=sorted(glob.glob(os.path.join(BS, "*.json")))
for f in files: idx(json.load(open(f)))
def res(o):
    if o.get('targetId') and o['targetId'] in index:
        t=dict(index[o['targetId']])
        for k in ('modifiers','constraints','costs'):
            if o.get(k): t[k]=(t.get(k) or [])+o[k]
        return t
    return o
def text(o):
    for r in (o.get('rules') or []):
        if r.get('description'): return re.sub(r'\s+',' ',r['description']).strip()
    for p in (o.get('profiles') or []):
        for ch in (p.get('characteristics') or []):
            t=ch.get('$text') or ch.get('value') or ''
            if t: return re.sub(r'\s+',' ',t).strip()
    for il in (o.get('infoLinks') or []):
        t=index.get(il.get('targetId'))
        if t: return text(t)
    return ''
def gates(o):
    """[(polarity, category)] from modifiers that hide the entry: 'hidden if notInstanceOf X' -> ('+',X); 'hidden if instanceOf X' -> ('-',X)"""
    out=[]
    for m in (o.get('modifiers') or []):
        if not (m.get('type')=='set' and m.get('field')=='hidden' and str(m.get('value')).lower()=='true'): continue
        conds=list(m.get('conditions') or [])
        for cg in (m.get('conditionGroups') or []): conds+= [dict(c, _grp=cg.get('type')) for c in (cg.get('conditions') or [])]
        for c in conds:
            cat=index.get(c.get('childId'),{}).get('name') or c.get('childId')
            if c.get('type')=='notInstanceOf': out.append(('+',cat))
            elif c.get('type')=='instanceOf': out.append(('-',cat))
    return out
def kids(o): return [res(k) for key in ('selectionEntryGroups','selectionEntries','entryLinks') for k in (o.get(key) or [])]
def find(o, pred, out):
    if isinstance(o, dict):
        if pred(o): out.append(o)
        for v in o.values(): find(v, pred, out)
    elif isinstance(o, list):
        for v in o: find(v, pred, out)
def leaf_items(g, path=()):
    for k in kids(g):
        ch=kids(k)
        if ch: yield from leaf_items(k, path+(k.get('name') or '',))
        else: yield path, k
out={}
for f in files:
    d=json.load(open(f)); fac={'traits':[], 'relics':defaultdict(list), 'scars':[], 'honours':defaultdict(list), 'group_text':{}}
    seen=set()
    def add(kind, path, k, extra=None):
        key=(kind, k.get('name'))
        if key in seen: return
        seen.add(key)
        item={'name':k.get('name'),'text':text(k),'gates':gates(k),'costs':{c.get('name'):c.get('value') for c in (k.get('costs') or []) if str(c.get('value')) not in ('0','0.0','None')},'path':list(path)}
        if kind=='traits': fac['traits'].append(item)
        elif kind=='scars': fac['scars'].append(item)
        elif kind=='relics': fac['relics'][extra].append(item)
        else: fac['honours'][extra].append(item)
    for grp,kind in (('Codex Battle Traits','traits'),('Codex Battle Scars','scars'),('Codex Crusade Relics','relics')):
        gs=[]; find(d, lambda o: o.get('name')==grp, gs)
        for g in gs:
            for path,k in leaf_items(g):
                if kind=='relics': add(kind, path, k, extra=(path[-1] if path else '?'))
                else: add(kind, path, k)
    # faction mechanic groups: named groups under Crusade that are not the shared ones
    SHARED={'Battle Tallies','Battle Honours','Weapon Modifications','Battle Traits','Crusade Relics','Tyrannic War Battle Honours','Pariah Nexus Blackstone Upgrades','Experience Points','Legendary Veterans','Battle Scars','Codex Battle Traits','Codex Crusade Relics','Codex Battle Scars','Core Battle Traits','Core Crusade Relics','Core Battle Scars'}
    cr=[]; find(d, lambda o: o.get('name')=='Crusade' and (o.get('selectionEntryGroups') or o.get('selectionEntries')), cr)
    def walk_groups(g, path=()):
        for k in kids(g):
            nm=k.get('name') or ''
            ch=kids(k)
            if ch and nm not in SHARED and not re.search(r'^(Core|Codex) ', nm) and nm not in ('Antiquity Relics','Legendary Relics','Artificer Relics'):
                gt=text(k)
                if gt: fac['group_text'][nm]=gt
                for p2,leaf in leaf_items(k, (nm,)): add('honours', p2, leaf, extra=p2[0])
            elif ch: walk_groups(k, path+(nm,))
    for g in cr: walk_groups(g)
    if fac['traits'] or fac['relics'] or fac['scars'] or fac['honours']:
        out[os.path.basename(f)[:-5]]={'traits':fac['traits'],'relics':dict(fac['relics']),'scars':fac['scars'],'honours':{k:v for k,v in fac['honours'].items()},'group_text':fac['group_text']}
json.dump(out, open(sys.argv[1],'w'), ensure_ascii=False, indent=1)
cats=Counter()
for f,fac in out.items():
    for it in fac['traits']+fac['scars']+[x for v in fac['honours'].values() for x in v]: cats.update(g for g in it['gates'])
    print(f"{f:42} traits {len(fac['traits']):2} relics {sum(len(v) for v in fac['relics'].values()):2} {dict((k[:3],len(v)) for k,v in fac['relics'].items())} scars {len(fac['scars'])} honours {dict((k[:22],len(v)) for k,v in fac['honours'].items())}")
print('\ngate categories:', cats.most_common(40))
