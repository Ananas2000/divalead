"""Back up the current proved native best after the conditional source holdout."""
from pathlib import Path
import datetime,json,os,shutil,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects');P=Path('/workspace/divalead')
N=Path('/workspace/divalead-work/native-low-latency-effects');PAUSE=N/'fl20-corrected-search.pause'
STATE=N/'FL20_POST_RESEARCH_BEST_BACKUP.json';OWNER='full-proven-best-backup-after-post-LR-independent-holdout'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
owned=False

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

def state(phase,**extra):
    obj=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=identity(os.getpid()),phase=phase,
             only_three_held_notes=True,actual_FL_GUI_export_pending=True,reference_match_reached=False,**extra)
    t=STATE.with_suffix('.partial');t.write_text(json.dumps(obj,indent=2)+'\n');t.replace(STATE)

def run(script,args,log):
    with Path(log).open('w')as out:
        child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(script),*map(str,args)],env=env,stdout=out,stderr=out)
        try:
            while child.poll()is None:
                state('actual_best_full_kit_export_validation_or_publication',child=identity(child.pid),script=str(script),log=str(log));time.sleep(5)
            assert child.returncode==0,(str(script),child.returncode,str(log))
        finally:
            if child.poll()is None:child.send_signal(signal.SIGINT);child.wait(timeout=60)

try:
    deadline=time.monotonic()+3600
    while True:
        finite=read(N/'FL20_POST_LR_CURRENT_COMPARISON_FINITE.json')
        if finite['phase']=='post_LR_vs_current_independent24_complete_matching_resumes':break
        assert 'failed'not in finite['phase'],'Diagnose the finite source job before taking its owned pause'
        now=identity(finite['owner']['PID']);assert now and now['starttime']==finite['owner']['starttime']
        assert time.monotonic()<deadline;state('waiting_for_actual_post_LR_vs_current_holdout',prior_phase=finite['phase']);time.sleep(2)
    deadline=time.monotonic()+60
    while PAUSE.exists():assert time.monotonic()<deadline;time.sleep(.2)
    with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Make a complete verified backup of the current improved native best, then resume numeric matching'),f)
    owned=True;deadline=time.monotonic()+1800
    while read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase']!='paused_by_control_or_actual_disk_reserve':
        assert time.monotonic()<deadline;state('waiting_for_an_observed_completed_numeric_cohort');time.sleep(5)
    restored13=B/'corrected-restoration-WIP13-local4-check'
    if not(restored13/'actual-DLL-restoration-check/PROOF.json').exists():
        run(restored13/'verify_corrected_restoration.py',[restored13],B/'WIP13-actual-restoration-check.log')
    public=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
    published=[read(p)['mean_original_objective']for p in public.glob('WIP[0-9][0-9]/verification/NATIVE_PRESET_VERIFICATION.json')]
    candidate=N/'FL20-corrected/BEST_CANDIDATE.json';best=read(candidate)
    assert best['full_fresh_native_realizations']>=6 and not best.get('full_fresh_native_validation_pending',False)
    if best['loss']>=min(published)-.002:
        state('current_full_public_kit_already_covers_the_useful_improvement',best_loss=best['loss'],last_published=min(published))
    else:
        number=max(int(p.name[3:])for p in public.glob('WIP[0-9][0-9]')if p.is_dir())+1
        code=f'{number:02}';label='Diva_NATIVE_'+code+'_WIP';kit=B/('FL20_NATIVE_'+code+'_WIP')
        frozen=B/(label+'-proven-best-seed.json');frozen.write_bytes(candidate.read_bytes())
        run(B/'export_fl20_checkpoint.py',[frozen,kit],B/(label+'-export.log'))
        proof=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json')
        assert proof['mean_original_objective']<min(published)-.0015,'Independent export did not retain a useful improvement'
        run(W/'verify_fst_with_pyflp.py',[kit],B/(label+'-parse.log'))
        run(B/'verify_fl20_latency.py',[kit/'verification/candidate.json',kit/'verification/NATIVE_LATENCY_AND_BLOCKS.json'],B/(label+'-latency.log'))
        run(B/'finalize_fl20_kit.py',[kit,label],B/(label+'-finalize.log'))
        zipped=B/(label+'_complete_WIP.zip');forecast=64*2**20+2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)
        if shutil.disk_usage('/workspace').free<forecast:run(B/'archive_historical_AB_cache.py',[],B/(label+'-lossless-cache-space.log'))
        assert shutil.disk_usage('/workspace').free>=forecast
        (B/('FL20_NATIVE_'+code+'_READY.json')).write_text(json.dumps(dict(kit=str(kit),candidate=str(frozen),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
        publisher=B/('publish_fl20_WIP_'+code+'.py');publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
        run(publisher,[],B/(label+'-Git.log'))
        destination=B/('corrected-restoration-WIP'+code+'-actual-check')
        run(B/'restore_corrected_workspace.py',['--checkpoint','WIP'+code,'--destination',destination],B/(label+'-restore.log'))
        run(destination/'verify_corrected_restoration.py',[destination],B/(label+'-actual-restoration.log'))
        run(B/'make_direct_reference_AB.py',[kit,B/('listening-Native'+code+'-01'),'NATIVE'+code+'_WIP'],B/(label+'-direct-AB.log'))
        state('best_full_backup_complete_continuous_matching_resumes',published_checkpoint='WIP'+code,
              full_actual_export_mean=proof['mean_original_objective'],full_actual_export_std=proof['std_original_objective'])
except BaseException:
    state('best_backup_failed_preserve_and_resume_matching',error=traceback.format_exc());raise
finally:
    if owned and PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
