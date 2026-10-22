"""Profile two actual Diva KeyFollow sources, then independently compare them.

The current validated source and FX remain installed unless a complete new
physical-source/native-FX branch survives independent selection and holdout.
"""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
STATE=N/'FL20_PHYSICAL_SOURCE_PROFILES.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='conditional-two-physical-Diva-KeyFollow-profiles';PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=str(W)+':'+str(B),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_COORD_MAXPASSES='12',DIVALEAD_COORD_MAXCALLS='4500')

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
                hosts=[identity(int(p))for p in ids];hosts=[h for h in hosts if h and 'fl_native_'in h['cmdline']and '.exe'in h['cmdline']]
                progress=read(root/'search-state.json')if root and(root/'search-state.json').exists()else None
                record(stage,child=identity(child.pid),actual_native_hosts=hosts,numeric_workers_observed=len(hosts),
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
    zipped=B/(label+'_complete_WIP.zip');forecast=64*2**20+2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)
    if shutil.disk_usage('/workspace').free<forecast:run(B/'archive_historical_AB_cache.py',[],B/(label+'-lossless-cache-space.log'),stage='losslessly_archiving_only_historical_AB_cache')
    assert shutil.disk_usage('/workspace').free>=forecast
    (B/('FL20_NATIVE_'+code+'_READY.json')).write_text(json.dumps(dict(kit=str(kit),candidate=str(candidate),ZIP=str(zipped),match_reached=False),indent=2)+'\n')
    publisher=B/('publish_fl20_WIP_'+code+'.py');publisher.write_text((B/'publish_fl20_WIP.py').read_text().replace('06',code))
    run(publisher,[],B/(label+'-Git.log'),stage='backing_up_complete_source_profile_kit')
    return kit/'verification/candidate.json'

def install(candidate):
    run(B/'start_corrected_fl20.py',['--check-only','--seed',candidate],B/'physical-source-profile-startup-preflight.log',stage='checking_source_profile_handoff')
    s=idle();saved=s['controller'];current=identity(saved['PID'])
    assert current and current['starttime']==saved['starttime']and current['cmdline']==saved['cmdline']
    os.kill(saved['PID'],signal.SIGTERM);deadline=time.monotonic()+15
    while identity(saved['PID']):assert time.monotonic()<deadline;time.sleep(.1)
    run(B/'start_corrected_fl20.py',['--seed',candidate],B/'physical-source-profile-controller-handoff.log',stage='installing_validated_physical_source_profile')
    assert read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['phase']=='paused_by_control_or_actual_disk_reserve'

with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Complete current WIP11 curve fit, then independently profile EQ for actual Diva KeyFollow0.5 and1.5 sources. No source change without full original-incumbent holdout.'),f)
control=B/'physical-source-profiles-validated-incumbent.json'
try:
    idle();control.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes());incumbent=read(control)
    assert incumbent.get('waveshaper_curve_format')=='native_monotone_bump_v1'
    assert incumbent['source_manifest']['source_preset_SHA256']==read(B/'fl20-Diva-harmonic-source-03/frozen-native-effects.json')['source_manifest']['source_preset_SHA256']
    proposals=[]
    for value,code in [('0.5','0p5'),('1.5','1p5')]:
        label='FL05_KeyFollow_'+code+'_profile';fixture=B/'fl20-Diva-harmonic-source-03'/('PW-keyfollow-'+value)
        audit=B/('fresh-'+label+'-source-audit')
        run(B/'audit_Diva_profile_source.py',[fixture,label,control],B/('audit-KeyFollow-'+code+'.log'),stage='auditing_real_Diva_h2p_and_actual_VST_chunk')
        manifest=read(audit/'source_manifest.json');root=B/('fl20-KeyFollow-'+code+'-EQ76-profile-01')
        seed=B/('KeyFollow-'+code+'-profile-seed.json')
        proposal=dict(incumbent,source_manifest=manifest,full_fresh_native_validation_pending=True,
                      conditional_source_profile_not_accepted=True,seed_loss_belongs_to_old_source=True)
        seed.write_text(json.dumps(proposal,indent=2)+'\n')
        run(B/'fit_fl20_EQ76_coordinates.py',[seed,root],B/(root.name+'.log'),root)
        durable(audit);durable(root);proposals.append(root/'full-validated-candidate.json')
    comparison=B/'paired-two-physical-source-profiles-01'
    run(B/'compare_supported_native_candidates.py',[comparison,control,*proposals],B/(comparison.name+'.log'),stage='independent12_plus12_original_incumbent_holdout')
    durable(comparison);got=read(comparison/'full-validated-candidate.json')
    accepted=bool(got['robust_improvement']and got['loss']<incumbent['loss'])
    installed=control
    if accepted:installed=publish(comparison/'full-validated-candidate.json');install(installed)
    record('conditional_source_profiles_completed_continuous_matching_resumes',
           physical_source_change_accepted=accepted,independent_result=read(comparison/'completion.json'),
           installed_candidate=str(installed),controller=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['controller'])
except BaseException:
    record('conditional_physical_source_profile_failed_preserve_and_resume',error=traceback.format_exc(),
           original_validated_candidate=str(control));raise
finally:
    if PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
