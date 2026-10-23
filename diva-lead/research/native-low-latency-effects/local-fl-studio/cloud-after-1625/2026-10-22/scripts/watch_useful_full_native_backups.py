"""Profile two actual Diva internal Plate2 wet levels, then independently compare them.

The current validated source and FX remain installed unless a complete new
physical-source/native-FX branch survives independent selection and holdout.
"""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
STATE=N/'FL20_USEFUL_FULL_BACKUP_WATCHER.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='useful-proved-full-native-backups-without-stopping-matching';PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_COORD_MAXPASSES='8',DIVALEAD_COORD_MAXCALLS='3000')

def read(p):
    for attempt in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)

def identity(pid):
    try:
        p=Path('/proc')/str(pid);s=(p/'stat').read_text().split()
        if s[2]=='Z':return None
        return dict(PID=pid,starttime=s[21],state=s[2],cmdline=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode())
    except FileNotFoundError:return None

def record(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),
             phase=phase,only_three_held_notes=True,actual_FL_GUI_export_pending=True,
             original_reference_match_reached=False,**extra)
    p=STATE.with_suffix('.partial');p.write_text(json.dumps(obj,indent=2)+'\n');p.replace(STATE)

def idle():
    deadline=time.monotonic()+1800
    while True:
        s=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');saved=s['controller'];now=identity(saved['PID'])
        assert now and now['starttime']==saved['starttime']and now['cmdline']==saved['cmdline']
        if s['phase']=='paused_by_control_or_actual_disk_reserve':return s
        assert time.monotonic()<deadline,'Current finite cohort did not reach the owned idle boundary'
        record('waiting_for_current_complete_fit_and_fresh_checks',prior_progress=s.get('progress'));time.sleep(5)

def run(script,args,log,root=None,stage='actual_physical_source_profile_running'):
    with Path(log).open('w')as f:
        child=subprocess.Popen([PY,'-B',str(script),*map(str,args)],stdout=f,stderr=f,env=env)
        try:
            while child.poll()is None:
                ids=subprocess.run(['ps','-o','pid=','--ppid',str(child.pid)],text=True,stdout=subprocess.PIPE,check=False).stdout.split()
                all_children=[identity(int(p))for p in ids];hosts=[h for h in all_children if h and 'fl_native_'in h['cmdline']and '.exe'in h['cmdline']];diva_hosts=[h for h in all_children if h and 'diva_performance_history.exe'in h['cmdline']]
                progress=read(root/'search-state.json')if root and(root/'search-state.json').exists()else None
                record(stage,child=identity(child.pid),actual_native_hosts=hosts,actual_Diva_hosts=diva_hosts,numeric_workers_observed=len(hosts),
                       root=str(root)if root else None,script=str(script),progress=progress,log=str(log));time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)

def durable(root):
    target=N/'FL20-corrected/completed'/root.name;target.mkdir(parents=True,exist_ok=True)
    for p in root.glob('*.json'):
        data=p.read_bytes()
        if len(data)>200000:
            packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data
            (target/(p.name+'.gz')).write_bytes(packed)
        else:shutil.copyfile(p,target/p.name)

def publish(candidate):
    public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
    number=max(int(p.name[3:])for p in public.glob('WIP[0-9][0-9]')if p.is_dir())+1
    code=f'{number:02}';label='Diva_NATIVE_'+code+'_WIP';kit=B/('FL20_NATIVE_'+code+'_WIP')
    run(B/'export_fl20_checkpoint.py',[candidate,kit],B/(label+'-export.log'),stage='checking_complete_source_profile_kit')
    assert read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')['mean_original_objective']<read(control)['loss']-.001
    run(W/'verify_fst_with_pyflp.py',[kit],B/(label+'-parse.log'),stage='checking_complete_source_profile_kit')
    run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/(label+'-latency.log'),stage='checking_complete_source_profile_kit')
    run(B/'finalize_fl20_kit.py',[kit,label],B/(label+'-finalize.log'),stage='checking_complete_source_profile_kit')
    zipped=B/(label+'_complete_WIP.zip');forecast=144*2**20+2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)
    if shutil.disk_usage('/workspace').free<forecast:run(B/'archive_historical_AB_cache.py',[],B/(label+'-lossless-cache-space.log'),stage='losslessly_archiving_only_historical_AB_cache')
    assert shutil.disk_usage('/workspace').free>=forecast
    (B/('FL20_NATIVE_'+code+'_READY.json')).write_text(json.dumps(dict(kit=str(kit),candidate=str(candidate),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
    publisher=B/('publish_fl20_WIP_'+code+'.py');publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
    run(publisher,[],B/(label+'-Git.log'),stage='backing_up_complete_source_profile_kit')
    restore=B/('corrected-restoration-WIP'+code+'-actual-check')
    run(B/'restore_corrected_workspace.py',['--destination',restore,'--checkpoint','WIP'+code],B/(label+'-restore.log'),stage='restoring_complete_ZIP_into_new_directory')
    run(restore/'verify_corrected_restoration.py',[restore],B/(label+'-actual-replay.log'),stage='checking_restored_actual_native_states_Diva_program_and_fresh_audio')
    run(B/'make_direct_reference_AB.py',[kit,B/('listening-Native'+code+'-01'),'NATIVE'+code+'_WIP'],B/(label+'-direct-AB.log'),stage='making_original_to_new_WIP_AB')
    return kit/'verification/candidate.json'

def install(candidate):
    run(B/'start_corrected_fl20.py',['--check-only','--seed',candidate],B/'physical-source-profile-startup-preflight.log',stage='checking_source_profile_handoff')
    s=idle();saved=s['controller'];current=identity(saved['PID'])
    assert current and current['starttime']==saved['starttime']and current['cmdline']==saved['cmdline']
    os.kill(saved['PID'],signal.SIGTERM);deadline=time.monotonic()+15
    while identity(saved['PID']):assert time.monotonic()<deadline;time.sleep(.1)
    run(B/'start_corrected_fl20.py',['--seed',candidate],B/'physical-source-profile-controller-handoff.log',stage='installing_validated_physical_source_profile')
    assert read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase']=='paused_by_control_or_actual_disk_reserve'



STOP=N/'useful-full-backup-watcher.stop'
public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
iteration=0
try:
    while not STOP.exists()and not(N/'fl20-corrected-search.stop').exists():
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');saved=main['controller'];actual=identity(saved['PID'])
        assert actual and actual['starttime']==saved['starttime']and actual['cmdline']==saved['cmdline'],'The genuine matcher is not alive; preserve and diagnose rather than restarting it'
        best=read(N/'FL20-corrected/BEST_CANDIDATE.json')
        published=[(read(p)['mean_original_objective'],p.parent/'candidate.json')for p in public.glob('WIP[0-9][0-9]/verification/NATIVE_PRESET_VERIFICATION.json')]
        prior_mean,prior_candidate=min(published,key=lambda row:row[0])
        if PAUSE.exists()or best['loss']>=prior_mean-.004:
            record('monitoring_actual_matcher_for_useful_proved_complete_backup',best_loss=best['loss'],current_full_public_mean=prior_mean,
                backup_threshold_absolute=.004,main_controller=actual,main_phase=main['phase'],main_progress=main.get('progress'))
            time.sleep(10);continue
        try:
            with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Finish the current actual cohort; back up a robust useful improvement as full FLP/WAV/Diva/MIDI/FST/FL20 guide/ZIP, restore it and resume matching.'),f)
        except FileExistsError:time.sleep(2);continue
        try:
            idle();best=read(N/'FL20-corrected/BEST_CANDIDATE.json')
            assert best['full_fresh_native_realizations']>=6 and not best.get('full_fresh_native_validation_pending',False)
            if best['loss']<prior_mean-.004:
                iteration+=1;stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                control=B/('useful-backup-'+stamp+'-public-control.json');control.write_bytes(prior_candidate.read_bytes())
                candidate=B/('useful-backup-'+stamp+'-validated-best.json');candidate.write_text(json.dumps(best,indent=2)+'\n')
                exported=publish(candidate)
                record('complete_useful_backup_pushed_actual_ZIP_replayed_preparing_current_handoff',published_candidate=str(exported),best_loss=best['loss'],
                    full_public_mean=read(exported)['loss'],matching_resumes_after_owned_pause=True)
                run(B/'backup_latest_native_continuation.py',[],B/('useful-backup-'+stamp+'-handoff.log'),stage='backing_up_short_AB_current_handoff_and_research_without_modifying_complete_kits')
                record('complete_useful_backup_pushed_and_documented_matching_resumes',published_candidate=str(exported),best_loss=best['loss'],
                    full_public_mean=read(exported)['loss'],only_owned_pause_released=True)
        finally:
            if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
        time.sleep(10)
    record('useful_full_backup_watcher_stopped_by_control_file_no_numeric_worker_interrupted')
except BaseException:
    record('useful_full_backup_watcher_failed_preserve_and_diagnose_matching_not_stopped_by_watcher',error=traceback.format_exc());raise
