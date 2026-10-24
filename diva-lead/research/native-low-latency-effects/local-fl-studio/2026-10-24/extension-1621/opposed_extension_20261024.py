"""Test common/difference coordinates of nearly coincident Side dynamics."""
from joint_dynamic_extension_20261024 import *
def main():
    ps={v['title']:v for v in csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t')}
    xs=[sf.read(S/f'FL26_PRE_ZL_{i:02}.wav',dtype='float32',always_2d=True)[0]for i in range(2)]
    z=WinVST3('opp24');controls=[];trials=[]
    variants=[dict(tag=f'opp{d:+g}',a=d,b=-d,phase=1.)for d in(-6.,-4.,-2.,-1.,1.,2.,4.,6.)]
    variants += [dict(tag='common_phase',a=.5,b=.5,phase=1.01)]
    try:
        for i,x in enumerate(xs):
            z.load(PRIVATE);controls.append(evaluate(z,x,f'EXTOPP_CONTROL_{i}'))
        def apply(v):
            z.load(PRIVATE)
            for band,key in((16,'a'),(17,'b')):
                p=ps[f'Target Gain{band}'];z.text(int(p['id']),f"{float(p['display'])+v[key]:.4f}")
            if v['phase']!=1.:z.text(int(ps['Freq19']['id']),f"{float(ps['Freq19']['display'])*v['phase']:.4f}")
        for v in variants:
            pair=[]
            for i,x in enumerate(xs):
                apply(v);pair.append(evaluate(z,x,f"EXTOPP_{v['tag']}_{i}"))
            row=dict(variant=v,rows=pair,mean_loss=float(np.mean([r['loss']for r in pair])),improvements=[c['loss']-r['loss']for c,r in zip(controls,pair)])
            trials.append(row);print(json.dumps(row),flush=True)
            (E/'OPPOSED_SCREEN.json').write_text(json.dumps(dict(controls=controls,trials=trials,promoted=False),indent=2))
        best=min(trials,key=lambda r:r['mean_loss']);apply(best['variant']);z.save(E/'OPPOSED_CANDIDATE.bin');z.dump(E/'OPPOSED_CANDIDATE610.tsv');embed(E/'OPPOSED_CANDIDATE.bin',E/'OPPOSED_CANDIDATE_FL20.flp')
        (E/'OPPOSED_CANDIDATE.json').write_text(json.dumps(dict(best=best,promoted=False),indent=2))
    finally:
        z.close();(E/'OPPOSED_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':main()
