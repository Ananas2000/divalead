"""Back up tested source95 runtime recovery and compact proofs, leaving audio kit intact."""
from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation');N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects');base=P/'diva-lead/research/native-low-latency-effects';d=base/'after-DSP-arrival';owner='native-joint76-verified-research-backup';pause=R/'auto-backup.pause'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def protected():return sorted([x for x in git('ls-tree','HEAD:diva-lead').splitlines() if re.search(r'\tv\d+-wip$',x)]+[x for x in git('ls-tree','HEAD').splitlines() if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',x)])
with pause.open('x') as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
 deadline=time.monotonic()+90
 while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
  assert time.monotonic()<deadline;time.sleep(1)
 with (R/'auto-backup-Git.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');before=git('rev-parse','HEAD');old=protected();assert git('ls-remote','origin','refs/heads/main').split()[0]==before
  kit_oid=git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP');zip_oid=git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip')
  scripts=d/'scripts';diag=d/'diagnostics'
  for name in ['native_cpu_slots.py','native_chain.py','continue_native_chorus.py','search_native_joint_EQ_LBFGS.py','check_joint_EQ_actual.py','handoff_joint76_controller.py','refresh_verified_native_kit.py','write_joint76_current_guide.py','probe_native_cross_ms.py','fl_native_cross_ms_host.c','probe_Diva_sync_PW_fine_native.py','profile_Diva_cutoff148.py','complete_native_checkpoint.py','sync_native_durable.py','backup_native_joint76_research.py']:
   shutil.copyfile(W/name,scripts/name)
  for name in ['NATIVE_RESTORED_RUNTIME_AUDIO_CHECK.json','PW_PHASE_FAMILY_HANDOFF.json','DOMINATED_OLD_CANONICAL_LOSSLESS_ARCHIVING.json','COMPLETED_SNAPSHOT_EXACT_AUDIO_SHARING.json','LOSSLESS_AUDIO_GIT_PACKING.json','NATIVE_CHORUS_EXPERIMENT_LEDGER.json','NATIVE_JOINT76_HANDOFF.json','JOINT76_CURRENT_GUIDE_STATE.json','COMPLETED_NATIVE_HOST_SCRATCH_CLEANUP.json']:
   if (N/name).exists():shutil.copyfile(N/name,diag/name)
  folder=diag/'native95-LBFGS-actual-integration-01';folder.mkdir(exist_ok=True)
  for p in (N/'native95-LBFGS-actual-integration-01').glob('*.json'):shutil.copyfile(p,folder/p.name)
  for name in ['native-Diva-sync-PW-fine-screen-01','native-cross-MS-branches-01','native-Diva-cutoff148-profile-01','native-joint76-actual-integration-01']:
   folder=diag/name;folder.mkdir(exist_ok=True)
   for p in (N/name).rglob('*'):
    if p.is_file() and p.suffix in ['.json','.h2p','.gz']:
     dest=folder/p.relative_to(N/name);dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
  shutil.copyfile(R/'start_skill_current.md',base/'start_skill_current.md')
  (diag/'JOINT76_CONTINUATION_VERIFICATION.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tmp_and_old_process_loss_observed=True,actual_six_capture_runtime_recovery_verified=True,fresh_Diva_all281_12events_and_source_audio_verified=True,source95_LBFGS_bounded_actual_integration_passed=True,idempotent_start_no_duplicates_verified_twice=True,GUI_FL_Studio_tested=False,independent_from_scratch_machine_install_not_claimed=True,latest_runtime_state_snapshot=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text()),joint76_actual_check=json.loads((N/'native-joint76-actual-integration-01/ACTUAL_INTEGRATION_PROOF.json').read_text()),rejected_source_and_cross_trials_retained=True,match_reached=False),indent=2)+'\n')
  files=sorted(p for p in d.rglob('*') if p.is_file() and p!=d/'SHA256SUMS.txt');(d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n' for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/') for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Fit native EQ gain, frequency and bandwidth jointly; retain rejected source and cross-routing trials')
  commit=git('rev-parse','HEAD');assert protected()==old;assert git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')==kit_oid;assert git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip')==zip_oid
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  checked=[]
  for relative in ['start_skill_current.md','after-DSP-arrival/scripts/prepare_native_runtime.py','after-DSP-arrival/diagnostics/JOINT76_CONTINUATION_VERIFICATION.json']:
   local=base/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/diva-lead/research/native-low-latency-effects/'+relative
   for attempt in range(6):
    try:
     with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
     if data==local.read_bytes():break
    except Exception:
     if attempt==5:raise
    time.sleep(2)
   assert data==local.read_bytes();checked.append(dict(path=relative,SHA256=hashlib.sha256(data).hexdigest(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,main_remote_matches=True,all_numbered_release_trees_and_root_ZIPs_unchanged=True,native_kit_and_ZIP_unchanged=True,clean_worktree=True,HTTP_files=checked,original_reference_match_reached=False)
  (N/'native-joint76-code-publication.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists() and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
