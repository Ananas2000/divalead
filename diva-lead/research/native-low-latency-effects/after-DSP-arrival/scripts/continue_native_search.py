"""Continue actual stock-DLL matching and publish proved WIP improvements.

Only one controller, four numeric workers. Never starts the old Finish fit.
Uses existing platform Git authentication; never reads or logs credentials.
"""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,sys,time,traceback
import numpy as np
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
R=Path('/workspace/divalead-work/three-held-continuation');P=Path('/workspace/divalead')
PY=Path('/workspace/.venvs/divalead/bin/python');STATE=N/'NATIVE_SEARCH_CONTROLLER.json'
STOP=N/'native-search.stop';PAUSE=N/'native-search.pause'
lock=(N/'native-search-controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def read(p):return json.loads(Path(p).read_text())
def identity(pid):
    try:
        fields=Path(f'/proc/{pid}/stat').read_text().split()
        if fields[2]=='Z':return None
        return dict(PID=pid,starttime=fields[21],cmdline=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None
def state(phase,**fields):
    data=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller=identity(os.getpid()),phase=phase,only_three_held_notes=True,native_DLL_audio=True,numeric_workers=4,old_Finish_controllers_not_started=True,match_reached=False,**fields)
    tmp=STATE.with_suffix('.partial');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(STATE)
def run(script,args,log,extra=None):
    e=env.copy();e.update(extra or {})
    with Path(log).open('w') as f:
        subprocess.run([str(PY),'-B',str(W/script),*map(str,args)],env=e,stdout=f,stderr=f,check=True)
def publish(candidate,generation):
    kit=W/f'native-complete-generation-{generation:04d}'
    run('export_native_checkpoint.py',[candidate,kit],W/f'native-export-{generation}.log')
    run('verify_fst_with_pyflp.py',[kit],W/f'native-FST-{generation}.log')
    run('complete_native_checkpoint.py',[kit],W/f'native-guide-{generation}.log')
    run('verify_native_latency_blocks.py',[candidate,kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],W/f'native-latency-{generation}.log')
    run('assess_native_reference.py',[kit/'verification/NATIVE_WITH_TAIL_WIP.wav'],W/f'native-reference-{generation}.log')
    shutil.copyfile(W/'reference-assessment/COMPARISON.json',kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json')
    proof=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json');assert proof['repeat_max_abs_error']<=2e-7
    actual=read(kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json')[-1]
    expected=read(candidate)['original_reference_assessment'];assert abs(actual['tone_score']-expected['tone_score'])<2e-5
    while (R/'auto-backup.pause').exists() or subprocess.check_output(['git','-C',str(P),'status','--porcelain'],text=True).strip():
        if STOP.exists():return False
        state('waiting_for_clean_manual_Git_boundary',generation=generation,candidate=str(candidate));time.sleep(5)
    run('publish_native_progress.py',[kit],W/f'native-publication-{generation}.log')
    return True

try:
    assert read(R/'native-effects-priority.json')['active']
    source=P/'diva-lead/v83-wip/Diva_SOURCE_FROZEN_48k.wav'
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    assert source_hash=='7a852ee05341c77708faced2e554c3f45080a691b5f001322221ec5cd9bf027e'
    current=W/'direct-original-stock-fit';adopt=int(sys.argv[1]) if len(sys.argv)>1 else None
    known=identity(adopt) if adopt else None
    if adopt:
        assert known and str(W/'search_native_original.py') in known['cmdline']
        while identity(adopt)==known:
            if STOP.exists():state('stopped_by_control_file_without_killing_adopted_job');raise SystemExit(0)
            state('adopted_native_search_running',child=known,search_root=str(current),progress=read(current/'search-state.json') if (current/'search-state.json').exists() else None)
            time.sleep(10)
    best=read(current/'best.json');best_path=current/'best.json';published_loss=None
    previous=W/'native-publication-candidate.json'
    if previous.exists():published_loss=read(previous)['loss']
    generation=0
    while not STOP.exists():
        while PAUSE.exists() or shutil.disk_usage('/workspace').free<64*1024**2 or shutil.disk_usage('/tmp').free<512*1024**2:
            if STOP.exists():break
            state('paused_by_control_file_or_actual_disk_limit',root_free_MiB=shutil.disk_usage('/workspace').free/1024**2,tmp_free_MiB=shutil.disk_usage('/tmp').free/1024**2);time.sleep(10)
        if STOP.exists():break
        assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
        saved=N/'NATIVE_BEST_CANDIDATE.json';saved.write_text(json.dumps(best,indent=2)+'\n')
        if published_loss is None or best['loss']<published_loss*.99:
            state('verifying_native_checkpoint_for_Git',generation=generation,candidate=str(best_path),loss=best['loss'])
            if publish(best_path,generation):published_loss=best['loss']
        generation+=1;current=W/f'original-stock-generation-{generation:04d}'
        if current.exists():raise RuntimeError('Refusing to overwrite an existing native search generation')
        seed=W/f'native-generation-{generation:04d}-seed.json';row=json.loads(json.dumps(best))
        # Small alternate starts explore the stock topology; best vectors stay immutable.
        if generation%3==0:
            rng=np.random.default_rng(83000+generation);x=np.array(row['x']);x[:28]=np.clip(x[:28]+rng.normal(0,.15,28),-18,18);row['x']=x.tolist()
        seed.write_text(json.dumps(row,indent=2)+'\n')
        e=env.copy();e['DIVALEAD_NATIVE_SEARCH_ROOT']=str(current)
        log=(W/f'original-stock-generation-{generation:04d}.log').open('w')
        child=subprocess.Popen([str(PY),'-B',str(W/'search_native_original.py'),str(seed)],env=e,stdout=log,stderr=log)
        while child.poll() is None:
            state('native_original_reference_search_running',generation=generation,child=identity(child.pid),search_root=str(current),best_loss=best['loss'],progress=read(current/'search-state.json') if (current/'search-state.json').exists() else None)
            if STOP.exists():child.terminate();child.wait(timeout=30);break
            time.sleep(10)
        log.close()
        if STOP.exists():break
        assert child.returncode==0
        got=read(current/'best.json')
        if got['loss']<best['loss']:best=got;best_path=current/'best.json'
    state('stopped_by_control_file',best_candidate=str(best_path),best_loss=best['loss'])
except Exception:
    state('failed_preserve_files_and_diagnose',error=traceback.format_exc());raise
