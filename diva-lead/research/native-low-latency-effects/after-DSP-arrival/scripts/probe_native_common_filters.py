"""Finite stock-EQ cutoff search, keeping exactly four active numeric workers.

Temporarily yields the current native fitting cohort's CPU slots, then resumes
the same PID/start-time identities in finally. No Wine service is stopped.
"""
from pathlib import Path
import concurrent.futures,datetime,json,os,queue,signal,threading,time,subprocess
import numpy as np
import soundfile as sf
from native_chain import NativeChain,W
from apply_native_candidate import apply
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(W/'common-filter-isolated-assessment')
from native_original_objective import FeaturesOriginal
from native_features import target

N=Path('/workspace/divalead-work/native-low-latency-effects')
ROOT=W/'common-native-filter-grid-02';ROOT.mkdir(exist_ok=False)
OWNER=N/'NATIVE_FINITE_BRANCH.json';statefile=N/'NATIVE_SEARCH_CONTROLLER.json'
assert not OWNER.exists(),'Another finite native branch needs inspection'
def ident(pid):
    p=Path('/proc',str(pid))
    try:
        fields=(p/'stat').read_text().split()
        return dict(PID=pid,starttime=fields[21],state=fields[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def same(a):
    b=ident(a['PID']);return b and b['starttime']==a['starttime'] and b['cmdline']==a['cmdline']
def write(phase,**extra):
    OWNER.write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=ident(os.getpid()),phase=phase,finite_actual_native_branch=True,work=str(ROOT),**extra),indent=2)+'\n')

cohort=json.loads(statefile.read_text());parent=cohort['child'];actual=ident(parent['PID'])
assert actual and actual['starttime']==parent['starttime'] and 'search_native_original.py' in actual['cmdline']
assert actual['state']!='T'
children=[ident(int(v)) for v in subprocess.check_output(['ps','-o','pid=','--ppid',str(parent['PID'])],text=True).split()]
children=[v for v in children if v and 'fl_native_fl_graph_host.exe' in v['cmdline']]
assert len(children)==4 and all(v['state']!='T' for v in children)
held=[];clients=[];executor=None;start=time.monotonic()
features=FeaturesOriginal(target);pool=queue.Queue();rows=[];mutex=threading.Lock();best=float('inf')
base=json.loads((Path(cohort['search_root'])/'best.json').read_text());x=np.array(base['x']);assert len(x)==86
(ROOT/'frozen-parent-candidate.json').write_text(json.dumps(base,indent=2)+'\n')
try:
    write('reserving_native_CPU_slots',suspended_identities=[actual,*children])
    for p in [actual,*children]:
        assert same(p);os.kill(p['PID'],signal.SIGSTOP);held.append(p)
    deadline=time.monotonic()+3
    while not all(ident(p['PID'])['state']=='T' for p in held):
        assert time.monotonic()<deadline;time.sleep(.02)
    write('actual_common_filter_grid_running',suspended_identities=held,numeric_workers=4)
    for i in range(4):
        c=NativeChain(W/'native-frozen-source-with-tail.wav',f'common-grid-{i}',fl_graph=True);clients.append(c);pool.put(c)
    def eval_case(spec):
        global best
        c=pool.get()
        try:
            apply(c,x)
            for n in [1,2]:c.bypass(n,True)
            if spec is not None:
                c.bypass(1,False)
                for b in range(7):c.set(1,b,0);c.set(1,21+b,0);c.set(1,28+b,0)
                c.set(1,35,0);c.set(1,27,1)
                c.set(1,13,int(round(np.log(spec['Hz']/20)/np.log(1000)*65536)))
                c.set(1,20,int(round(spec['width']*65536)));c.set(1,34,spec['order'])
            y,status=c.render();r=features.residual(y[:len(target)]);loss=float(r@r)+float(np.sum(x[:28]**2))*.00000025
            row=dict(spec=spec,loss=loss,original_reference_assessment=features.local.last,native_status=status,peak=float(abs(y).max()),elapsed_seconds=time.monotonic()-start,native_DLL_audio=True,only_three_held_notes=True,declared_effect_PDC_frames=0,match_reached=False)
            with mutex:
                rows.append(row)
                if loss<best:
                    best=loss;point=dict(row,x=x.tolist(),common_filters=spec,strict_waveform_match=False,original_reference_match_reached=False)
                    (ROOT/'best.json').write_text(json.dumps(point,indent=2)+'\n');sf.write(ROOT/'best-with-tail.wav',y,48000,subtype='FLOAT')
                    print('COMMON_NATIVE_FILTER_BEST',loss,spec,flush=True)
            return row
        finally:pool.put(c)
    baseline=eval_case(None);(ROOT/'baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    specs=[dict(Hz=f,width=w,order=o) for f in [5000,6500,8000,10000,12500,16000,20000] for w in [.3,.5,.7,1.] for o in [-3,-1,0,1,2,3]]
    executor=concurrent.futures.ThreadPoolExecutor(4);list(executor.map(eval_case,specs))
    (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    (ROOT/'completion.json').write_text(json.dumps(dict(cases=len(rows),elapsed_seconds=time.monotonic()-start,baseline_loss=baseline['loss'],best_loss=best,match_reached=False),indent=2)+'\n')
finally:
    if executor:executor.shutdown(wait=True)
    for c in clients:c.close()
    resumed=[]
    for p in list(reversed(held)):
        if same(p):os.kill(p['PID'],signal.SIGCONT);resumed.append(p['PID'])
    write('completed_native_cohort_resumed',resumed_PIDs=resumed,elapsed_seconds=time.monotonic()-start)
    shutil_dest=N/'COMMON_NATIVE_FILTER_GRID_OWNER_LAST.json'
    shutil_dest.write_bytes(OWNER.read_bytes());OWNER.unlink()
print('FINITE_NATIVE_FILTER_GRID_COMPLETE_AND_COHORT_RESUMED',flush=True)
