"""Start corrected search once; an existing verified controller is left alone."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,subprocess,time
B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects')
state=N/'FL20_CORRECTED_SEARCH_CONTROLLER.json'
def identity(pid):
    try:
        f=Path(f'/proc/{pid}/stat').read_text().split()
        if f[2]=='Z':return None
        return dict(PID=pid,starttime=f[21],state=f[2],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
p=argparse.ArgumentParser();p.add_argument('--seed',type=Path)
p.add_argument('--attach-pid',type=int);p.add_argument('--attach-root',type=Path);args=p.parse_args()
if state.exists():
    previous=json.loads(state.read_text()).get('controller')
    now=identity(previous['PID'])if previous else None
    if now and now['starttime']==previous['starttime']and now['cmdline']==previous['cmdline']and 'continue_corrected_fl20.py'in now['cmdline']:
        print(json.dumps(dict(already_running=True,controller=now,no_new_controller_or_numeric_cohort_started=True)));raise SystemExit(0)
assert not(N/'fl20-corrected-search.stop').exists(),'Inspect the corrected stop request; do not remove it automatically'
args.seed=args.seed or(N/'FL20-corrected/BEST_CANDIDATE.json'if(N/'FL20-corrected/BEST_CANDIDATE.json').exists()else B/'restored-candidate.json')
seed=json.loads(args.seed.read_text());assert len(seed['x'])==95 and not seed.get('source_post_EQ')
assert seed.get('full_fresh_native_realizations',0)>=6 and seed.get('source_manifest')
sm=seed['source_manifest'];assert Path(sm['native_input']).is_file()
assert hashlib.sha256(Path(sm['source_audio']).read_bytes()).hexdigest()==sm['source_audio_SHA256']
assert hashlib.sha256(Path(sm['source_preset']).read_bytes()).hexdigest()==sm['source_preset_SHA256']
argv=['/workspace/.venvs/divalead/bin/python','-B',str(B/'continue_corrected_fl20.py'),str(args.seed)]
if args.attach_pid:
    ident=identity(args.attach_pid);assert ident and 'fit_fl20_postEQ_scaled.py'in ident['cmdline']and str(args.attach_root)in ident['cmdline']
    attach=B/'ATTACHED_FINITE_RESEARCH.json';attach.write_text(json.dumps(dict(process=ident,root=str(args.attach_root)),indent=2)+'\n');argv.append(str(attach))
with (B/'continue_corrected_fl20.log').open('a')as log:
    child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,close_fds=True)
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        assert child.poll()is None,'Inspect corrected controller startup log'
        if state.exists()and json.loads(state.read_text()).get('controller',{}).get('PID')==child.pid:break
        time.sleep(.2)
    else:raise RuntimeError('No current startup state from new corrected controller')
print(json.dumps(dict(started=True,controller=identity(child.pid),state=str(state),old_native_controller_not_started=True)))
