"""Screen actual ZL on a captured FL26 prefix. Proposals require fresh validation."""
from experiment_20261024 import *
def main():
    x,sr=sf.read(S/'FL26_PRE_ZL_00.wav',dtype='float32',always_2d=True);assert sr==48000
    z=WinVST3('gui24');rows=[]
    try:
        for name,p in [('public',V/'ZL_component.bin'),('confirmed',PRIVATE)]:
            z.load(p);row=evaluate(z,x,'GUI_PREFIX_'+name);rows.append(row);print(json.dumps(row),flush=True)
        z.load(PRIVATE);z.dump(S/'ZL23_CONFIRMED_ALL610.tsv');z.save(S/'ZL23_CONFIRMED_RESAVED.bin')
        (S/'GUI_PREFIX_BASELINES.json').write_text(json.dumps(rows,indent=2))
        params=list(csv.DictReader((S/'ZL23_CONFIRMED_ALL610.tsv').open(),delimiter='\t'))
        bytitle={v['title']:v for v in params}
        screen=[]
        # Narrow differential screen around opposite-signed upper-band residuals.
        # One captured input is only a screen; this cannot promote a new best.
        for band in (4,5,10,11):
            p=bytitle[f'Gain{band}'];base=float(p['display'])
            for delta in (-.6,-.3,.3,.6):
                z.load(PRIVATE);z.text(int(p['id']),f'{base+delta:.2f}')
                row=evaluate(z,x,f'GUI_SCREEN_g{band}_{delta:+.1f}');row['change']=dict(title=p['title'],id=int(p['id']),before=base,after=base+delta)
                screen.append(row);print(json.dumps(row),flush=True)
                (S/'GUI_SINGLE_PREFIX_SCREEN.json').write_text(json.dumps(screen,indent=2))
        best=min(screen,key=lambda v:v['loss']);z.load(PRIVATE);z.text(best['change']['id'],f"{best['change']['after']:.2f}");z.save(S/'GUI_SCREEN_ONLY_PROPOSAL.bin');z.dump(S/'GUI_SCREEN_ONLY_PROPOSAL610.tsv')
        (S/'GUI_SCREEN_ONLY_PROPOSAL.json').write_text(json.dumps(dict(best=best,confirmed_baseline=rows[1],promoted=False,reason='Single captured input; needs fresh paired and held-out FL renders'),indent=2))
    finally:
        z.close();(S/'GUI_PREFIX_ZL_HOST.log').write_text('\n'.join(str(v)for v in z.transcript),encoding='utf-8')
if __name__=='__main__':main()
