"""Profile two actual Diva internal Plate2 wet levels, then independently compare them.

The current validated source and FX remain installed unless a complete new
physical-source/native-FX branch survives independent selection and holdout.
"""
from pathlib import Path
import datetime,gzip,json,os,shutil,signal,subprocess,time,traceback

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
STATE=N/'FL20_DETAIL8_INTEGRATION_AND_BACKUP.json';PAUSE=N/'fl20-corrected-search.pause'
OWNER='validated-detail8-curve-integration';PY='/workspace/.venvs/divalead/bin/python'
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
    zipped=B/(label+'_complete_WIP.zip');forecast=64*2**20+2*(zipped.stat().st_size+(kit/'NATIVE_FULL_180BPM_WIP.wav').stat().st_size+800000)
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



owned=False
control=B/'detail8-integration-current-incumbent.json'
try:
    deadline=time.monotonic()+3600
    while True:
        prior=read(N/'FL20_DETAIL8_WS_FINITE_PROFILE.json')
        if prior['phase']=='detail8_curve_screen_complete_not_automatically_adopted':break
        assert 'failed'not in prior['phase'],'Diagnose the guarded detail8 research before integration'
        assert time.monotonic()<deadline;record('waiting_for_independent_actual_detail8_curve_validation',prior_phase=prior['phase'],prior_progress=prior.get('progress'));time.sleep(2)
    if not prior['robust_improvement']:
        record('detail8_not_robust_production_helper_and_candidate_unchanged',completion=prior['completion'])
    else:
        deadline=time.monotonic()+60
        while PAUSE.exists():assert time.monotonic()<deadline;time.sleep(.2)
        with PAUSE.open('x')as f:json.dump(dict(owner=OWNER,reason='Verify supported detail8 replay against real native states and zero-depth audio, compare fresh24+24 to the current incumbent, and publish/replay a complete FL20 kit before adoption.'),f)
        owned=True;idle();control.write_bytes((N/'FL20-corrected/BEST_CANDIDATE.json').read_bytes())
        run(B/'verify_detail8_curve_integration.py',[],B/'detail8-curve-supported-integration.log',stage='checking_prospective_helper_against_actual_saved_DLL_state_and_zero_depth_audio')
        audit=B/'detail8-WS-integration-audit-01';durable(audit)
        comparison=B/'paired-supported-detail8-vs-current-independent24-01'
        run(B/'compare_detail8_supported_proposals24_archived.py',[comparison,control,audit/'supported-old-EQ-proposal.json',audit/'supported-current-EQ-proposal.json'],B/(comparison.name+'.log'),stage='independent24_plus24_supported_detail8_grafts_against_original_current_graph')
        durable(comparison);got=read(comparison/'full-validated-candidate.json');incumbent=read(control)
        accepted=bool(got['robust_improvement']and got['loss']<incumbent['loss'])
        if accepted:
            old=B/'fl20_curve_before_detail8.py';assert not old.exists();shutil.copyfile(B/'fl20_curve.py',old)
            shutil.copyfile(B/'fl20_curve_detail8_supported_proposal.py',B/'fl20_curve.py')
            p=B/'search_fl20_controls.py';text=p.read_text();text=text.replace('validate_curve_candidate,FORMAT,LOCAL_FORMAT','validate_curve_candidate,FORMAT,LOCAL_FORMAT,extended_curve_bytes')
            needle='    c=pool.get()'
            addition="""    if len(case)>5 and case[5]is not None:
        current=dict(current,waveshaper_detail_bump_format=prior['waveshaper_detail_bump_format'],waveshaper_detail_bump_adjustment=list(map(float,case[5])))
"""
            assert text.count(needle)==1;text=text.replace(needle,addition+needle)
            marker="try:\n    for i in range(4):"
            block="""if prior.get('waveshaper_detail_bump_adjustment')is not None:
    detail=np.array(prior['waveshaper_detail_bump_adjustment'])
    for k,step in enumerate([.002,.003,.004,.006,.008,.010,.012,.015]):
        for factor in [-2.,-1.,-.5,.5,1.,2.]:
            changed=detail.copy();changed[k]+=factor*step
            data=extended_curve_bytes(seed,prior['waveshaper_curve_adjustment'],prior.get('waveshaper_local_bump_adjustment'),changed)
            values=np.ndarray(shape=(129,),dtype='<f8',buffer=data,offset=42,strides=(24,))
            if np.min(np.diff(values))>=-1e-10:trials.append((f'WS-detail8-{k}-{factor:g}',seed.copy(),dict(overrides),None,None,changed.tolist()))

"""
            assert text.count(marker)==1;text=text.replace(marker,block+marker);compile(text,str(p),'exec');p.write_text(text)
            for name in ['fl20_curve.py','search_fl20_controls.py']:shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
            installed=publish(comparison/'full-validated-candidate.json');install(installed)
            record('supported_detail8_complete_kit_published_and_actual_ZIP_replayed_continuous_matching_resumes',
                supported_curve_change_accepted=True,installed_candidate=str(installed),independent_result=read(comparison/'completion.json'),
                all12_native_states_and_zero_depth_audio_exact=read(audit/'PROOF.json'),controller=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')['controller'])
        else:
            record('detail8_current_incumbent_holdout_not_robust_no_helper_change_matching_resumes',
                supported_curve_change_accepted=False,independent_result=read(comparison/'completion.json'))
except BaseException:
    record('detail8_integration_failed_preserve_validated_incumbent_and_diagnose',error=traceback.format_exc());raise
finally:
    if owned and PAUSE.exists()and read(PAUSE).get('owner')==OWNER:PAUSE.unlink()
