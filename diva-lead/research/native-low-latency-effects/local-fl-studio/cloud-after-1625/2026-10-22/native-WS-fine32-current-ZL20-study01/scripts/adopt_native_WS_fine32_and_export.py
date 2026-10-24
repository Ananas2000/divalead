"""Adopt positive fixed nativeEQ12 pairs only after supported full21 replay/push."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
import numpy as np
from fl20_curve import native_dsp_settings_SHA256
D=Path(__file__).resolve().parent;B=D.parent
N=Path('/workspace/divalead-work/native-low-latency-effects')
STUDY=D/'ZL-native-WS-fine32-current-ZL20-01'
ROOT=D/'ZL-native-WS-fine32-supported-adoption-01';ROOT.mkdir(exist_ok=False)
OWNER='native-WS-fine32-finite-refit-20261024'
PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{B}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):return json.loads(Path(p).read_text())
def dead(pid):
    try:return Path(f'/proc/{pid}/stat').read_text().split()[2]=='Z'
    except FileNotFoundError:return True
def job(name,args):
    with(ROOT/(name+'.log')).open('w')as log:subprocess.run([PY,'-B',str(D/name),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
for stop in ['zl-continuation.stop','zl-useful-full-backup.stop']:assert read(N/stop)['owner']==OWNER
assert dead(read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID'])
summary=read(STUDY/'completion.json');assert summary['robust_improvement']and len(summary['captures'])==12
prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');proposal=read(STUDY/'CANDIDATE_COMBINED_RESEARCH_ONLY.json');initial=read(STUDY/'PRIOR_COMBINED_CANDIDATE.json')
assert Path(prior['native_ZL_component_state']).read_bytes()==(STUDY/'UNCHANGED_ZL_COMPONENT.bin').read_bytes()
assert native_dsp_settings_SHA256(prior['native_base']['x'],prior['native_base'])==native_dsp_settings_SHA256(initial['native_base']['x'],initial['native_base'])
assert prior['native_base']['source_manifest']['source_preset_SHA256']==proposal['native_base']['source_manifest']['source_preset_SHA256']
helpers=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='native_WS_fine32_adoption_helpers')
# Recoverable duplicate proof copies are safe to evict before a new export.
pause=helpers['R']/'auto-backup.pause';cleanup='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as stream:json.dump(dict(owner=cleanup,PID=os.getpid(),reason='evict exact already-pushed finite EQ04 proof duplicates before supported export'),stream)
try:
    with(helpers['R']/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);git=helpers['git'];assert not git('status','--porcelain')
        public=helpers['PUBLIC']/'native-WS-fine32-current-ZL20-study01/TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz';relative=public.relative_to(helpers['P']).as_posix();blob=subprocess.check_output(['git','-C',str(helpers['P']),'show','origin/main:'+relative]);digest=hashlib.sha256(blob).hexdigest();evicted=[]
        if public.exists():
            assert public.read_bytes()==blob;git('update-index','--skip-worktree','--',relative);public.unlink();evicted.append(str(public))
        private=STUDY/'TWELVE_FRESH_CONTROL_CANDIDATE_WAVs.tar.gz'
        if private.exists():assert private.read_bytes()==blob;private.unlink();evicted.append(str(private))
        (ROOT/'EXACT_REMOTE_PROOF_DUPLICATES_EVICTED.json').write_text(json.dumps(dict(paths=evicted,retained_public_Git_path=relative,SHA256=digest,all_audio_bytes_preserved=True,selected_WAV_and_all_states_untouched=True),indent=2)+'\n')
finally:
    if pause.exists()and read(pause).get('owner')==cleanup:pause.unlink()
assert shutil.disk_usage('/workspace').free>=128*2**20,'Preserve128MiB before verified nativebase/fullkit export'
assert shutil.disk_usage('/tmp').free>=180*2**20,'Preserve180MiB before verified nativebase/fullkit export'
base=B/'FL20_NATIVE_ZL_REBASED_05';ready=base.with_name(base.name+'-COMBINED_CANDIDATE_READY.json')
job('prepare_native_base_for_combined_ZL.py',['--candidate',str(STUDY/'CANDIDATE_COMBINED_RESEARCH_ONLY.json'),'--destination',str(base)])
job('package_verified_native_base.py',['--ready',str(ready)])
code=f"{max(int(p.name[-2:])for p in helpers['PUBLIC'].glob('ZL-WIP[0-9][0-9]'))+1:02}"
helpers['build'](code,candidate=str(ready))
kit=B/f'FL20_ZL_{code}_WIP';report=read(kit/'verification/ZL_FULL_VERIFICATION.json');replay=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json')
assert report['mean_original_objective']<summary['current_control_mean']-.0005
assert replay['six_fresh_whole_chain_mean']<summary['current_control_mean']-.0005
helpers['publish'](code)
choice=read(ready);choice.update(accepted_full_public_kit='ZL'+code,native_WS_fine32_adopted_after_full_export_and_Git=True,independent_full_ZIP_replay_mean=replay['six_fresh_whole_chain_mean'])
temp=D/'ZL-continuous65/BEST_CANDIDATE.partial';temp.write_text(json.dumps(choice,indent=2)+'\n');temp.replace(D/'ZL-continuous65/BEST_CANDIDATE.json')
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),public_kit='ZL'+code,native_base=str(base),source_Diva_and_all12_MIDI_unchanged=True,paired12_control_mean=summary['current_control_mean'],paired12_candidate_mean=summary['candidate_mean'],paired12_SEM=summary['paired_difference_SEM'],full_export_mean=report['mean_original_objective'],independent_ZIP_mean=replay['six_fresh_whole_chain_mean'],only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True)
(ROOT/'ADOPTED_ONLY_AFTER_FULL_SUPPORTED_ZIP_AND_PUSH.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'NATIVE_WS_FINE32_FULL_KIT_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ACTUAL_NATIVE_WS_FINE32_FULL_KIT_ADOPTED',json.dumps(receipt),flush=True)
