"""Separate detector frequency/Q from the main near-coincident Side peaks."""
from joint_dynamic_extension_20261024 import *
def main():
    ps={v['title']:v for v in csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t')}
    xs=[sf.read(S/f'FL26_PRE_ZL_{i:02}.wav',dtype='float32',always_2d=True)[0]for i in range(2)]
    z=WinVST3('det24');trials=[]
    try:
        z.load(PRIVATE);baseline=evaluate(z,xs[0],'EXTDET_CONTROL_0')
        def apply(title,mul):
            z.load(PRIVATE)
            for band in(16,17):
                p=ps[f'{title}{band}'];z.text(int(p['id']),f"{float(p['display'])*mul:.4f}")
        for title,mults in [('Side Freq',(.5,.8,1.2,2.)),('Side Q',(.5,2.))]:
            for mul in mults:
                apply(title,mul);r=evaluate(z,xs[0],f"EXTDET_{title.replace(' ','')}_{mul:g}_0")
                row=dict(title=title,multiplier=mul,row=r,improvement=baseline['loss']-r['loss']);trials.append(row);print(json.dumps(row),flush=True)
                (E/'DETECTOR_SCREEN.json').write_text(json.dumps(dict(baseline=baseline,trials=trials,promoted=False),indent=2))
        best=min(trials,key=lambda r:r['row']['loss'])
        if best['improvement']>.0005:
            z.load(PRIVATE);control=evaluate(z,xs[1],'EXTDET_CONTROL_1');apply(best['title'],best['multiplier']);hold=evaluate(z,xs[1],'EXTDET_BEST_1');best['second_input_control']=control;best['second_input']=hold;best['second_input_improvement']=control['loss']-hold['loss']
        apply(best['title'],best['multiplier']);z.save(E/'DETECTOR_CANDIDATE.bin');z.dump(E/'DETECTOR_CANDIDATE610.tsv');embed(E/'DETECTOR_CANDIDATE.bin',E/'DETECTOR_CANDIDATE_FL20.flp')
        (E/'DETECTOR_SCREEN.json').write_text(json.dumps(dict(baseline=baseline,trials=trials,best=best,promoted=False),indent=2))
    finally:
        z.close();(E/'DETECTOR_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':main()
