import json, sys
d=json.load(open(sys.argv[1])); print(f"===== {sys.argv[1].split('/')[-1]}")
cur=lambda v: v['current'] if v.get('current') is not None else v.get('value')
print('ROSTER:', {k:cur(v) for k,v in d['stats'].items() if k in ('Points','Crusade Pts','Requisition Pts','Blackstone Frg.')}, '| tracked:', {k:v for k,v in (d['tracked'] or {}).items() if k in ('Tyrannic War','Pariah Nexus','Supply Limit','Supply Used','Campaign Points','Battles Won')})
KEEP=('Experience','Rank','Battle Honour','Crusade Pts','Supply Limit','Supply Used','Mission','Alliance','Battle Tally','Campaign Points','RP','RP Reward','Upgrade Path','Blackstone Fragments','D','Result tyrannic','Result Pariah','Agenda 1')
def walk(a, depth=0, div=''):
    st={k:cur(v) for k,v in a['stats'].items() if k in KEEP and cur(v) not in (None,0,'-')}
    if 'Battle Honour' in a['stats'] and a['stats']['Battle Honour'].get('max') is not None: st['BH max']=a['stats']['Battle Honour']['max']
    errs=[e for e in a['errors'] if e.startswith('error')]
    print('  '*depth+f"{div}{a['item']}{' x'+str(a['quantity']) if a.get('quantity') and a['quantity']>1 else ''} {st}{'  !! '+' | '.join(errs) if errs else ''}")
    for t in a['traits']:
        if not t['item'].startswith(('Ranged Weapon§','Melee Weapon§','Wargear§','Ability§','Model§','Stratagem','Detachment§')) or t['included']: walk(t, depth+1, '~')
    for c in a['included']:
        if not c['item'].startswith('Model§'): walk(c, depth+1, '')
walk(d)
