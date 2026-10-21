"""Keep native source, accepted vectors and compact actual-proof ledger durable."""
from pathlib import Path
import datetime,hashlib,json,shutil
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead');dest=N/'after-DSP-arrival/scripts';dest.mkdir(parents=True,exist_ok=True)
for path in W.iterdir():
 if path.is_file() and (path.suffix in ['.py','.c'] or path.name in ['staged-plugin-manifest.json','Fruity_WaveShaper_x64-default-state.bin']):shutil.copyfile(path,dest/path.name)
files=sorted(p for p in dest.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt');(dest/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
ledger=[]
for root in sorted(W.iterdir()):
 if root.is_dir() and (root/'completion.json').is_file():
  row=dict(experiment=root.name,completion=json.loads((root/'completion.json').read_text()))
  if (root/'full-validated-candidate.json').is_file():
   choice=json.loads((root/'full-validated-candidate.json').read_text());row.update(mean_loss=choice['loss'],realization_std=choice.get('realization_standard_deviation'),accepted_robust_fresh_improvement=choice.get('robust_improvement'),candidate_SHA256=hashlib.sha256((root/'full-validated-candidate.json').read_bytes()).hexdigest())
  ledger.append(row)
  out=N/'native-compact-proof-ledger'/root.name;out.mkdir(parents=True,exist_ok=True)
  for filename in ['completion.json','full-validated-candidate.json','paired-fresh-control.json','heldout-prefix-validation.json']:
   if (root/filename).is_file():shutil.copyfile(root/filename,out/filename)
phase=W/'native-Diva-static-phase-screen-01';out=N/'native-Diva-static-phase-screen-01';out.mkdir(exist_ok=True)
for path in phase.rglob('*'):
 if path.is_file() and path.suffix in ['.json','.tsv','.h2p','.log']:
  target=out/path.relative_to(phase);target.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(path,target)
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_DSP_only=True,original_audio_never_used_as_candidate_audio=True,only_three_held_notes=True,original_reference_match_reached=False,experiments=ledger)
(N/'NATIVE_CHORUS_EXPERIMENT_LEDGER.json').write_text(json.dumps(report,indent=2)+'\n')
state=json.loads((N/'NATIVE_SEARCH_CONTROLLER.json').read_text());pub=json.loads((N/'native-latest-publication.json').read_text())
(N/'NATIVE_HANDOFF_CURRENT.json').write_text(json.dumps(dict(UTC=report['UTC'],controller_state=state,latest_publication=pub,actual_native_DLL_audio=True,mode='Chorus_EQ_native_low_latency',source_preserved='v83_Great_THREE_HELD',v83_transfer_complete=False,reference_match_reached=False,old_Finish_fits_not_started=True,private_DLLs_not_distributed=True),indent=2)+'\n')
if state.get('best_candidate'):shutil.copyfile(state['best_candidate'],N/'NATIVE_LIVE_CANDIDATE_AT_HANDOFF.json')
print('NATIVE_DURABLE_SOURCE_AND_PROOF_LEDGER_SAVED',len(files),len(ledger))
