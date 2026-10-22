"""Finite native-DSP branch CPU ownership; resume exact processes in finally."""
from contextlib import contextmanager
from pathlib import Path
import datetime,json,os,signal,subprocess,time
N=Path('/workspace/divalead-work/native-low-latency-effects')
OWNER=N/'NATIVE_FINITE_BRANCH.json'
def identity(pid):
    p=Path('/proc',str(pid))
    try:
        fields=(p/'stat').read_text().split()
        return dict(PID=pid,starttime=fields[21],state=fields[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def same(ident):
    now=identity(ident['PID'])
    return now and now['starttime']==ident['starttime'] and now['cmdline']==ident['cmdline']
@contextmanager
def four_native_slots(work):
    assert not OWNER.exists(),'Inspect the existing native finite branch owner first'
    # The controller briefly has one prefix/validation host between four-worker
    # cohorts. Wait for an actual current cohort before reserving anything.
    deadline=time.monotonic()+55;waited=0
    while True:
        assert not OWNER.exists(),'Another finite branch reserved the workers'
        state=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text());parent=state.get('child');p=identity(parent['PID']) if parent else None
        valid=p and p['starttime']==parent['starttime'] and p['state'] not in ['T','Z'] and any(name in p['cmdline'] for name in ['search_native_original.py','search_native_chorus.py','search_native_chorus_controls.py','search_native_source_chorus.py','search_native_source_LBFGS.py','search_native_joint_EQ_LBFGS.py'])
        children=[]
        if valid:
            children=[identity(int(i)) for i in subprocess.run(['ps','-o','pid=','--ppid',str(p['PID'])],text=True,stdout=subprocess.PIPE,check=False).stdout.split()]
            children=[i for i in children if i and i['state'] not in ['T','Z'] and any(name in i['cmdline'] for name in ['fl_native_fl_graph_host.exe','fl_native_chorus_verified_host.exe','fl_native_source_variants_host.exe','fl_native_common_phase_host.exe'])]
        if valid and len(children)==4 and all(same(i) for i in [p,*children]):break
        assert time.monotonic()<deadline,'No verified four-host native cohort became available'
        waited+=1;time.sleep(.2)
    held=[];start=time.monotonic()
    def save(phase,**extra):
        data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,work=str(work),suspended_identities=held,finite_actual_native_branch=True,elapsed_seconds=time.monotonic()-start,**extra)
        OWNER.write_text(json.dumps(data,indent=2)+'\n')
    try:
        with OWNER.open('x') as f:json.dump(dict(owner=identity(os.getpid()),phase='reserving',work=str(work)),f)
        for i in [p,*children]:
            assert same(i);os.kill(i['PID'],signal.SIGSTOP);held.append(i)
        until=time.monotonic()+3
        while not all(identity(i['PID'])['state']=='T' for i in held):
            assert time.monotonic()<until;time.sleep(.02)
        save('actual_finite_native_branch_running',numeric_workers=4,cohort_preflight_wait_polls=waited)
        yield state
    finally:
        resumed=[]
        for i in reversed(held):
            if same(i):os.kill(i['PID'],signal.SIGCONT);resumed.append(i['PID'])
        save('finished_exact_native_cohort_resumed',resumed_PIDs=resumed)
        (N/(Path(work).name+'-CPU-ownership.json')).write_bytes(OWNER.read_bytes());OWNER.unlink()
