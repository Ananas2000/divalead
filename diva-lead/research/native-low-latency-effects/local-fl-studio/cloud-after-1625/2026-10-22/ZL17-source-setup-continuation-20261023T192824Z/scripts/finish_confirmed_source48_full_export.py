"""Finish the positive fixed48 result after repairing its Git packaging.

The incumbent component must still be exactly the one used for the completed
48 pairs. Do not repeat the fixed test or silently overwrite a newer incumbent.
"""
from pathlib import Path
import datetime,json,os,runpy,subprocess,traceback
import numpy as np
from native_chain import NativeChain
from fl20_curve import apply_candidate
D=Path(__file__).resolve().parent;B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');ROOT=D/'ZL-Diva-OscMix6p5-recovered-full-export-01';ROOT.mkdir(exist_ok=False)
OWNER='Diva-OscMix6p5-positive48-backup-and-export-recovery-20261023';PY='/workspace/.venvs/divalead/bin/python';STOPS=[N/'zl-continuation.stop',N/'zl-useful-full-backup.stop'];STATE=N/'SOURCE48_RECOVERED_FULL_EXPORT_STATE.json'
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal
features=FeaturesOriginal();env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{B}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):return json.loads(Path(p).read_text())
def alive(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,owner=OWNER,only_three_held_notes=True,source_change='Only Diva OscMix6.3 to6.5; other280 parameters/ARP/ADSR/12MIDI exact',reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw);q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def job(name,args):
 record('actual_native_base_and_full_kit_export',script=name)
 with(ROOT/(name+'.log')).open('w')as log:subprocess.run([PY,'-B',str(D/name),*args],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
def resume():
 for p in STOPS:
  if p.exists()and read(p).get('owner')==OWNER:p.unlink()
 result={}
 for name,extra,statefile in [('continue_ZL_matching.py',[],'FL20_ZL_CONTINUOUS_CONTROLLER.json'),('watch_ZL_useful_complete_backups.py',['--watch'],'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')]:
  state=read(N/statefile);pid=state.get('PID',state.get('owner',{}).get('PID'))
  if pid and alive(pid)and os.fsencode(str(D/name))in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0'):continue
  with(N/('SOURCE48_RECOVERED_'+name+'.log')).open('ab')as log:p=subprocess.Popen([PY,'-B',str(D/name),*extra],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  result[name]=p.pid
 return result
try:
 assert all(read(p)['owner']==OWNER for p in STOPS);assert not alive(read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')['owner']['PID']);assert not alive(read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json')['PID']);assert read(N/'SOURCE48_SPLIT_BACKUP_RECOVERY.json')['all96_WAVs_byte_exact_in_3_HTTP_verified_parts']
 proof_root=D/'ZL-Diva-source-OscMix6p5-independent48-adoption-01';summary=read(proof_root/'completion.json');assert summary['robust_improvement']and summary['predeclared_independent_pairs']==48
 prior=read(D/'ZL-continuous65/BEST_CANDIDATE.json');assert Path(prior['native_ZL_component_state']).read_bytes()==(proof_root/'CANDIDATE_COMPONENT.bin').read_bytes();source=read(D/'Diva-tone-actual-current-ZL-rebase02-01/AUDITED_SOURCE_MANIFEST.json');seed=dict(prior['native_base'],source_manifest=source)
 record('confirmed_same_incumbent_as_completed_positive48_measure_new_native_only_mean')
 native=NativeChain(source['native_input'],'source48-recovered-new-native-measurement',fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
 try:
  apply_candidate(native,np.array(seed['x']),seed)
  for key,value in seed['chorus_overrides'].items():native.set(3,int(key),int(value))
  losses=[]
  for rep in range(6):raw,_=native.render();r=features.residual(raw[:288000]);losses.append(float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025)
 finally:native.close()
 seed.update(loss=float(np.mean(losses)),full_fresh_native_realizations=6,full_fresh_native_validation_pending=False)
 proposal=dict(prior,native_base=seed,loss=summary['candidate_mean'],native_ZL_component_state=str(proof_root/'CANDIDATE_COMPONENT.bin'),recorded_audio=str(proof_root/'SELECTED_COMBINED_WIP.wav'),source_tone_changed_since_ZL16=True,source_change_vs_ZL16='Only OSC: OscMix6.3 to6.5; other280 and12MIDI exact',source_fixed48_confirmation=str(proof_root/'completion.json'),native_parameters_changed_from_previous_public_kit=False,source_changed_accepted_only_after_full_export_pending=True)
 proposed=ROOT/'PROPOSED_COMBINED_CANDIDATE.json';proposed.write_text(json.dumps(proposal,indent=2)+'\n');(ROOT/'NATIVE_ONLY_NEW_SOURCE_SIX_REALIZATIONS.json').write_text(json.dumps(dict(losses=losses,mean=float(np.mean(losses))),indent=2)+'\n')
 base=B/'FL20_NATIVE_ZL_REBASED_03';ready=base.with_name(base.name+'-COMBINED_CANDIDATE_READY.json');job('prepare_native_base_for_combined_ZL.py',['--candidate',str(proposed),'--destination',str(base)]);job('package_verified_native_base.py',['--ready',str(ready)])
 shared=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='finish_positive48_full_kit');code=f"{max(int(p.name[-2:])for p in shared['PUBLIC'].glob('ZL-WIP[0-9][0-9]'))+1:02}";record('actual_complete_export_and_independent_ZIP_replay',code=code,native_base=str(base));shared['build'](code,candidate=str(ready))
 kit=B/f'FL20_ZL_{code}_WIP';report=read(kit/'verification/ZL_FULL_VERIFICATION.json');proof=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');assert report['mean_original_objective']<summary['current_control_mean']-.0005;assert proof['six_fresh_whole_chain_mean']<summary['current_control_mean']-.0005;shared['publish'](code)
 choice=read(ready);choice.update(source_changed_accepted_only_after_full_export_pending=False,accepted_full_public_kit='ZL'+code,independent_full_ZIP_replay_mean=proof['six_fresh_whole_chain_mean']);tmp=D/'ZL-continuous65/BEST_CANDIDATE.partial';tmp.write_text(json.dumps(choice,indent=2)+'\n');tmp.replace(D/'ZL-continuous65/BEST_CANDIDATE.json')
 receipt=dict(public_kit='ZL'+code,native_base=str(base),source_OscMix='6.3 to6.5',positive_fixed48_control_mean=summary['current_control_mean'],positive_fixed48_candidate_mean=summary['candidate_mean'],fixed48_SEM=summary['paired_difference_SEM'],full_export_mean=report['mean_original_objective'],ZIP_replay_mean=proof['six_fresh_whole_chain_mean'],all_other280_parameters_and12_MIDI_unchanged=True,all12_native_state_bytes_exact=len(proof['all12_native_saved_states_exact'])==12,whole_native_ZL_zero_depth_error=proof['whole_native_plus_ZL_zero_depth_max_abs_error'],reference_match_reached=False,actual_FL_GUI_validation_pending=True)
 (ROOT/'ADOPTED_ONLY_AFTER_FULL_EXPORT_AND_GIT.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'SOURCE48_NEW_DIVA_FULL_KIT_ADOPTION.json').write_text(json.dumps(receipt,indent=2)+'\n');record('positive48_source_adopted_after_full_kit_push_and_replay',result=receipt);print('CONFIRMED_SOURCE48_NEW_FULL_KIT_ADOPTED',json.dumps(receipt),flush=True)
except BaseException:
 record('failed_preserve_prior_main_and_complete_kits',error=traceback.format_exc());raise
finally:
 if all(p.exists()and read(p).get('owner')==OWNER for p in STOPS):
  restarted=resume();(N/'SOURCE48_RECOVERED_MATCHER_AND_BACKUP_RESTART.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PIDs=restarted,best_mean=read(D/'ZL-continuous65/BEST_CANDIDATE.json')['loss'],reference_match_reached=False),indent=2)+'\n');print('ACTUAL_MATCHER_AND_FULL_BACKUP_RESTARTED',json.dumps(restarted),flush=True)
