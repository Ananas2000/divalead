"""Small real-plugin screen; two FL26 captures, no promotion without fresh pairs."""
from experiment_20261024 import *
def main():
    inputs=[sf.read(S/f'FL26_PRE_ZL_{i:02}.wav',dtype='float32',always_2d=True)[0]for i in range(2)]
    p={v['title']:v for v in csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t')}
    z=WinVST3('dyn24');rows=[];controls=[]
    try:
        for i,x in enumerate(inputs):
            for label,c in [('public',V/'ZL_component.bin'),('confirmed',PRIVATE)]:
                z.load(c);r=evaluate(z,x,f'DYNAMIC_CONTROL_{label}_{i}');controls.append(r)
        for b in (14,15,16,17,20,21):
            row=p[f'Target Gain{b}'];base=float(row['display'])
            for delta in (-1.,1.):
                z.load(PRIVATE);z.text(int(row['id']),f'{base+delta:.2f}')
                r=evaluate(z,inputs[0],f'DYNAMIC_SCREEN_b{b}_{delta:+.0f}');r['change']=dict(id=int(row['id']),title=row['title'],before=base,after=base+delta);rows.append(r)
                print(json.dumps(r),flush=True)
                (S/'DYNAMIC_SCREEN.json').write_text(json.dumps(dict(controls=controls,trials=rows,promoted=False),indent=2))
        eligible=[r for r in rows if r['loss']<controls[1]['loss']-.0003]
        for r in eligible:
            z.load(PRIVATE);z.text(r['change']['id'],f"{r['change']['after']:.2f}")
            hold=evaluate(z,inputs[1],r['label']+'_HOLDOUT');r['heldout']=hold;r['heldout_improvement']=controls[3]['loss']-hold['loss']
            if r['heldout_improvement']>.0005:
                z.save(S/(r['label']+'_UNCONFIRMED.bin'));z.dump(S/(r['label']+'_UNCONFIRMED610.tsv'))
        (S/'DYNAMIC_SCREEN.json').write_text(json.dumps(dict(controls=controls,trials=rows,promoted=False,reason='Only two GUI captures; new acceptance still requires paired6 and cold2'),indent=2))
        print(json.dumps(dict(eligible=len(eligible),best=min(rows,key=lambda r:r['loss']),promoted=False)),flush=True)
    finally:
        z.close();(S/'DYNAMIC_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':main()
