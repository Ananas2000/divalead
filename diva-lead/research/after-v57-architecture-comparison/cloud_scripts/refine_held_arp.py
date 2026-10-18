"""Extend the promising internal-Diva ARP source, still exactly 3 held notes."""
from pathlib import Path
import sys, copy, json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
seed=json.loads((m.ROOT/'best-three-arp/selection.json').read_text())
m.ROOT=m.ROOT/'arp-refinement';m.ROOT.mkdir(exist_ok=False)
m.common.WORK=m.ROOT;(m.ROOT/'scores').mkdir()
m.write(m.ROOT/'frozen-seed.json',seed)
m.evaluate('sixteen',label='v57 exact screening control')
current=m.evaluate('three-arp',seed['fields'],roots=seed['root_velocities'],label='frozen best first ARP search')
for field,values in [('VCA1:ModDpt',[-72,-68,-64,-60,-50,-40,-20,0]),('ENV1:Atk',[14,16,18,20]),('ENV1:Dec',[7,7.5,8.5,9,9.5]),('ENV1:Sus',[80,88,96,100]),('ENV1:Vel',[10,20,40,60,100]),('VCA1:Vol',[47,49,52,54])]:
    origin=copy.deepcopy(current);choices=[current]
    for value in values:
        fields=copy.deepcopy(origin['fields']);fields[field]=value
        choices.append(m.evaluate('three-arp',fields,roots=origin['root_velocities'],label=field+'='+str(value)))
    current=min(choices,key=lambda r:r['score'])
    print('COORDINATE',field,current['score'],flush=True)
for i in range(3):
    origin=copy.deepcopy(current);choices=[current]
    for delta in [-6,-3,3,6]:
        roots=list(origin['root_velocities']);roots[i]+=delta
        choices.append(m.evaluate('three-arp',origin['fields'],roots=roots,label='root velocity '+str((i,delta))))
    current=min(choices,key=lambda r:r['score'])
m.write(m.ROOT/'completed.json',dict(best=current,trials=len(m.history),match_reached=False))
print('COMPLETED',current['score'],flush=True)
