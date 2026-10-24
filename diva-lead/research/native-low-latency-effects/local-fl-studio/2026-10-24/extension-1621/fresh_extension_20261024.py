"""Frozen-candidate paired evaluation on six new GUI prefixes and two cold reloads."""
from joint_dynamic_extension_20261024 import *
import argparse
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=8);args=ap.parse_args();rows=[]
    for i in range(args.count):
        inp=E/f'FRESH_{i:02}.wav'
        if not inp.exists():break
        out=E/f'FRESH_PAIR_{i:02}.json'
        if out.exists():rows.append(json.loads(out.read_text()));continue
        x,sr=sf.read(inp,dtype='float32',always_2d=True);assert sr==48000 and len(x)>192000 and np.isfinite(x).all()
        z=WinVST3(f'fresh{i:02}');pair={}
        try:
            order=[('control',PRIVATE),('candidate',E/'OPPOSED_CANDIDATE.bin')]
            if i%2:order.reverse()
            for tag,c in order:
                z.load(c);pair[tag]=evaluate(z,x,f'FRESHPAIR_{i:02}_{tag}')
        finally:z.close()
        row=dict(index=i,kind='cold_GUI_reload'if i>=6 else'fresh_GUI_render',input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),frames=len(x),pair=pair,improvement=pair['control']['loss']-pair['candidate']['loss'])
        out.write_text(json.dumps(row,indent=2));rows.append(row);print(json.dumps(row),flush=True)
    fresh=[r['improvement']for r in rows[:6]];cold=[r['improvement']for r in rows[6:8]]
    mean=float(np.mean(fresh))if fresh else None;sem=float(np.std(fresh,ddof=1)/np.sqrt(len(fresh)))if len(fresh)>1 else None
    threshold=max(.0005,3*sem)if sem is not None else None
    accepted=len(rows)==8 and len(set(r['input_sha256']for r in rows))==8 and mean>threshold and min(cold)>0
    report=dict(pairs=len(rows),fresh6_improvements=fresh,cold2_improvements=cold,fresh_mean_improvement=mean,fresh_SEM=sem,required_improvement=threshold,accepted=accepted,source='Actual FL26 native-only GUI exports; candidate frozen before this cohort',candidate_only_changes=['Target Gain16 +0.5dB','Target Gain17 +0.5dB','Mid AllPass19 frequency +1%'])
    (E/'FRESH_SUMMARY.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':main()
