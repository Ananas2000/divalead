"""Fresh 16-note Diva dynamics, respecting the existing eleven guards and crest."""
from pathlib import Path
import sys,copy,json,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_architectures as m
from search_global_guards import ORIGINAL53_LIMITS
m.ROOT=m.ROOT/'sixteen-refinement';m.ROOT.mkdir(exist_ok=False)
m.common.WORK=m.ROOT;(m.ROOT/'scores').mkdir()
original=json.loads((m.P/'ranking.json').read_text())['results'][0]['metrics']
baseline=m.evaluate('sixteen',label='exact published v57')
eligible_best=baseline
def feasible(r):return r['crest_RMS_dB']<=m.CAP and all(r['metrics'][k]<=original[k]*v for k,v in ORIGINAL53_LIMITS.items())
def trial(timing,label):
    global eligible_best
    r=m.evaluate('sixteen',timing=timing,label=label)
    r['fixed_original11_and_crest_passed']=bool(feasible(r))
    if feasible(r) and r['score']<eligible_best['score']-1e-10:
        eligible_best=copy.deepcopy(r)
        dest=m.ROOT/'best-feasible';dest.mkdir(exist_ok=True)
        shutil.copyfile(m.ROOT/'current-source.wav',dest/'raw-Diva.wav')
        shutil.copyfile(m.ROOT/'current-edit.wav',dest/'REFERENCE_EDIT_WIP.wav')
        shutil.copyfile(Path(r['case'])/'source.h2p',dest/'source.h2p')
        shutil.copyfile(Path(r['case'])/'all281.tsv',dest/'all281.tsv')
        m.write(dest/'selection.json',r)
        print('NEW_FEASIBLE_BEST',r['score'],label,flush=True)
    return r

# Opposite octave-level errors in the two repeats require separate changes.
for first,second in [(-1,1),(-2,1),(-1,2),(-2,2),(0,1),(-1,0)]:
    t=copy.deepcopy(m.TIMING);t['velocities'][5]+=first;t['second_velocities'][5]+=second
    trial(t,'C# octave velocities '+str((first,second)))
current=eligible_best
for field,index in [('velocities',3),('velocities',4),('velocities',5),('second_velocities',5),('second_velocities',3),('velocities',0),('second_velocities',7),('velocities',7),('velocities',2),('second_velocities',2)]:
    origin=copy.deepcopy(current);choices=[current]
    for delta in [-1,1]:
        t=copy.deepcopy(origin['timing']);t[field][index]+=delta
        choices.append(trial(t,'individual '+str((field,index,delta))))
    current=min([r for r in choices if feasible(r)],key=lambda r:r['score'])
# Shortening/lengthening corresponding release gates is tested independently.
for index in [1,2,5,7]:
    origin=copy.deepcopy(current);choices=[current]
    for delta in [-.002,.002]:
        t=copy.deepcopy(origin['timing'])
        for field in ['gates','second_gates']:t[field][index]+=delta
        choices.append(trial(t,'paired gate '+str((index,delta))))
    current=min([r for r in choices if feasible(r)],key=lambda r:r['score'])
m.write(m.ROOT/'completed.json',dict(best_feasible=eligible_best,trials=len(m.history),baseline=baseline,match_reached=False))
print('COMPLETED',eligible_best['score'],flush=True)
