"""Bounded phase sensitivity around the accepted Mid all-pass near 3kHz."""
from joint_dynamic_extension_20261024 import *
def main():
    params={v['title']:v for v in csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t')}
    xs=[sf.read(S/f'FL26_PRE_ZL_{i:02}.wav',dtype='float32',always_2d=True)[0]for i in range(2)]
    z=WinVST3('phase24');controls=[];trials=[]
    try:
        for i,x in enumerate(xs):
            z.load(PRIVATE);controls.append(evaluate(z,x,f'EXTPHASE_CONTROL_{i}'))
        for title,multipliers in [('Freq19',(.98,.99,1.01,1.02)),('Q19',(.9,1.1))]:
            p=params[title];before=float(p['display'])
            for mul in multipliers:
                pair=[]
                for i,x in enumerate(xs):
                    z.load(PRIVATE);z.text(int(p['id']),f'{before*mul:.4f}')
                    pair.append(evaluate(z,x,f'EXTPHASE_{title}_{mul:g}_{i}'))
                row=dict(title=title,id=int(p['id']),before=before,after=before*mul,rows=pair,mean_loss=float(np.mean([r['loss']for r in pair])),improvements=[c['loss']-r['loss']for c,r in zip(controls,pair)])
                trials.append(row);print(json.dumps(row),flush=True)
                (E/'PHASE_SCREEN.json').write_text(json.dumps(dict(controls=controls,trials=trials,promoted=False),indent=2))
        best=min(trials,key=lambda r:r['mean_loss']);z.load(PRIVATE);z.text(best['id'],f"{best['after']:.4f}");z.save(E/'PHASE_CANDIDATE.bin');z.dump(E/'PHASE_CANDIDATE610.tsv');embed(E/'PHASE_CANDIDATE.bin',E/'PHASE_CANDIDATE_FL20.flp')
        # Actual bypassed component for independent future FL GUI capture.
        z.load(PRIVATE);z.set(1652125811,1)
        y,status=z.render(xs[0],R);error=float(abs(y-xs[0]).max());assert error<1e-7,error
        z.save(E/'CAPTURE_BYPASS.bin');embed(E/'CAPTURE_BYPASS.bin',E/'CAPTURE_NATIVE_ONLY.flp')
        (E/'CAPTURE_BYPASS_PROOF.json').write_text(json.dumps(dict(status=status,max_error=error,bypass_param=1652125811),indent=2))
    finally:
        z.close();(E/'PHASE_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':main()
