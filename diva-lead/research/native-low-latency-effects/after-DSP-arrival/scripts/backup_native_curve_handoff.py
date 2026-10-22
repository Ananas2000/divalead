"""Back up validated WaveShaper work and a local-FL handoff under the Git lock."""
from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation');N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects')
base=P/'diva-lead/research/native-low-latency-effects';d=base/'after-DSP-arrival';owner='native-curve-and-local-FL-handoff';pause=R/'auto-backup.pause'
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
  shutil.copyfile(W/'LOCAL_FL_STUDIO_HANDOFF_RU.md',base/'LOCAL_FL_STUDIO_HANDOFF_RU.md')
  scripts=d/'scripts';diag=d/'diagnostics'
  for name in ['native_cpu_slots.py','native_chain.py','search_native_chorus_controls.py','probe_native_expanded_waveshaper.py','profile_supported95_candidate.py','fl_native_extra_effect_host.c','calibrate_native_extra_effects.py','probe_Diva_PW_local_after_curve.py','backup_native_curve_handoff.py']:
   shutil.copyfile(W/name,scripts/name)
  for name in ['NATIVE_CURVE_HANDOFF.json','NATIVE_CHORUS_EXPERIMENT_LEDGER.json']:
   shutil.copyfile(N/name,diag/name)
  for name in ['native-expanded-WaveShaper-screen-01','native-expanded-WaveShaper-fine-screen-01','native-expanded-WaveShaper-joint76-profile-02']:
   out=diag/name;out.mkdir(exist_ok=True)
   for p in (W/name).rglob('*.json'):
    dest=out/p.relative_to(W/name);dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,dest)
   own=N/(name+'-CPU-ownership.json')
   if own.exists():shutil.copyfile(own,out/'CPU-ownership.json')
  shutil.copyfile(W/'profile-expanded-WaveShaper.log',diag/'native-curve-first-cohort-transition-retry.log')
  report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_WaveShaper_grid_and_joint76_profile_complete=True,
   profile=json.loads((W/'native-expanded-WaveShaper-joint76-profile-02/completion.json').read_text()),
   current_publication=json.loads((N/'native-latest-publication.json').read_text()),
   prepared_extra_saturator_host_audio_tested=False,prepared_Diva_PW_screen_executed=False,
   local_PC_attached=False,local_GUI_tools_available=False,cloud_only_observed=True,
   original_reference_match_reached=False)
  (diag/'NATIVE_CURVE_AND_LOCAL_HANDOFF_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
  prefix='''LATEST VERIFIED CURVE CONTINUATION AND LOCAL-PC HANDOFF (2026-10-22). The user installed the Codex app and is preparing a local FL session. This cloud conversation still exposes only Linux /workspace and no computer-control tools/skills; do not claim local GUI access. LOCAL_FL_STUDIO_HANDOFF_RU.md is the concise user-facing context for a local session. The user will specify allowed folders; no local folder scope has been given yet. Do not infer that app installation itself connects this cloud conversation to Windows.

New actual native WaveShaper screens (49 broad cases and50 local cases including controls), followed by a supported95/joint76 EQ profile, found a small robust improvement at c3=0.75,c5=-0.35. Fresh paired six-capture objective~1.69739 vs incumbent~1.70825, SEM~0.000918. The complete FST/WAV/A-B/FL-guide kit was independently re-exported and pushed; read current verification for actual export scores. All twelve native state bytes and zero-depth audio roundtrip; working Chorus remains stochastic. Same audited physical PW-keyfollow Diva source, all281 and12 incoming MIDI events; no new notes or source changes. Original match and complete v83 transfer remain false. The controller was handed off to the fully validated candidate; NATIVE_CURVE_HANDOFF.json records exact identities and idempotent launch.

four_native_slots now waits up to55s for a real four-host cohort because a first profile start observed a legitimate controller prefix/validation transition. No process was suspended by that failed preflight; the subsequent full profile completed and resumed the exact original cohort in finally. Preserve owner identity checks. The Chorus control worker additionally screens coupled positive-cubic/negative-quintic curves; fresh validation remains mandatory.

RESEARCH ONLY, NOT TESTED OR DEPLOYED: fl_native_extra_effect_host.c and NativeChain optional extra_effect_name prepare a16-node experiment with ordinary slot mixing and a supplied extra native effect. calibrate_native_extra_effects.py and probe_Diva_PW_local_after_curve.py were prepared but have not rendered yet. No extra processor is in the12-effect public kit. Production NativeChain default remains the15-node family and is independently covered by the new kit export. No third-party audio plugin has been installed into the deployed chain; free downloadable Windows x64 VST2/VST3 options are now authorized if actually needed and tested.

'''
  prior=(R/'start_skill_current.md').read_text();(R/'start_skill_current.md').write_text(prefix+prior);shutil.copyfile(R/'start_skill_current.md',base/'start_skill_current.md')
  files=sorted(p for p in d.rglob('*') if p.is_file() and p!=d/'SHA256SUMS.txt');(d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n' for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/') for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Save validated WaveShaper improvement and local FL Studio handoff')
  commit=git('rev-parse','HEAD');assert protected()==old;assert git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP')==kit_oid;assert git('rev-parse','HEAD:diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip')==zip_oid
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  checked=[]
  for relative in ['LOCAL_FL_STUDIO_HANDOFF_RU.md','after-DSP-arrival/scripts/native_cpu_slots.py','after-DSP-arrival/diagnostics/NATIVE_CURVE_AND_LOCAL_HANDOFF_VERIFICATION.json']:
   local=base/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/diva-lead/research/native-low-latency-effects/'+relative
   for attempt in range(6):
    try:
     with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
     if data==local.read_bytes():break
    except Exception:
     if attempt==5:raise
    time.sleep(2)
   assert data==local.read_bytes();checked.append(dict(path=relative,SHA256=hashlib.sha256(data).hexdigest(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,main_remote_matches=True,
   all_numbered_release_trees_and_root_ZIPs_unchanged=True,native_kit_and_ZIP_unchanged=True,clean_worktree=True,HTTP_files=checked,original_reference_match_reached=False)
  (N/'native-curve-handoff-publication.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists() and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
