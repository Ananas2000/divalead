"""Native Diva oscillator/filter refinement of the three-held-note ARP source."""
from pathlib import Path
import sys,copy,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
seed=json.loads((m.ROOT/'arp-refinement/best-three-arp/selection.json').read_text())
m.ROOT=m.ROOT/'arp-timbre';m.ROOT.mkdir(exist_ok=False)
m.common.WORK=m.ROOT;(m.ROOT/'scores').mkdir()
m.write(m.ROOT/'frozen-seed.json',seed)
m.evaluate('sixteen',label='exact v57 control')
current=m.evaluate('three-arp',seed['fields'],roots=seed['root_velocities'],label='best held-note envelope source')
for field,values in [('OSC:OscMix',[3,4.5,6.5,8]),('OSC:PW',[50.5,51.25,52.25,53]),('VCF1:Res',[10,11,13,14]),('VCF1:KeyScl',[4,6,10,12]),('OSC:Tune2',[23.98,24,24.04,24.06]),('main:CcOp',[115,123,127])]:
    origin=copy.deepcopy(current);choices=[current]
    for value in values:
        f=copy.deepcopy(origin['fields']);f[field]=value
        choices.append(m.evaluate('three-arp',f,roots=origin['root_velocities'],label=field+'='+str(value)))
    current=min(choices,key=lambda r:r['score'])
    print('COORDINATE',field,current['score'],flush=True)
m.write(m.ROOT/'completed.json',dict(best=current,trials=len(m.history),match_reached=False))
print('COMPLETED',current['score'],flush=True)
