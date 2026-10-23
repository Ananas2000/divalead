"""Prune redundant old rejected-trial training/check WAVs, never variants.
Keep every main selected WAV, all parameters/metadata/states, accepted trials,
all original inputs, current research and every public complete kit.
"""
from pathlib import Path
import datetime,gzip,hashlib,json,os,shutil
N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects');open_paths=set();symlink_targets=set()
for p in Path('/proc').glob('[0-9]*'):
 try:
  for f in(p/'fd').iterdir():
   try:open_paths.add(os.readlink(f))
   except OSError:pass
 except OSError:pass
for r in [W,Path('/tmp/divalead-local-1625'),N]:
 for p in r.rglob('*'):
  if p.is_symlink():
   try:symlink_targets.add(str(p.resolve(strict=True)))
   except FileNotFoundError:pass
before={p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']};removed=[];kept=[];proofs=[]
for p in W.glob('chorus-*/full-validated-candidate.json'):
 try:choice=json.loads(p.read_text());completion=json.loads((p.parent/'completion.json').read_text())
 except (ValueError,FileNotFoundError):continue
 if choice.get('robust_improvement')is not False:continue
 root=p.parent;main=root/'best-with-tail.wav'
 if not main.is_file():kept.append(dict(root=str(root),reason='no separate main WAV; retain whole rejected trial'));continue
 protected={str(main),str(Path(choice.get('recorded_audio','/invalid')).resolve())}
 candidates=[*root.glob('actual-WS-Chorus-prefix-*.wav'),*root.glob('full-fresh-realization-*.wav')]
 if not candidates:continue
 proof=dict(root=str(root),full_validated_candidate=choice,completion=completion,kept_main_WAV_SHA256=hashlib.sha256(main.read_bytes()).hexdigest(),kept_main_WAV=str(main));proofs.append(proof)
 for q in candidates:
  if q.is_symlink()or not q.is_file():continue
  if str(q)in protected|open_paths|symlink_targets:kept.append(dict(path=str(q),reason='main selected/active/symlink target'));continue
  # These generated training/check captures are redundant for an explicitly
  # rejected, completed trial. All candidate source parameters remain intact.
  removed.append(dict(path=str(q),bytes=q.stat().st_size,SHA256=hashlib.sha256(q.read_bytes()).hexdigest(),reason='completed explicitly rejected old trial auxiliary prefix/fresh-check capture; main WAV and all metadata retained'));q.unlink()
blob=json.dumps(proofs).encode();packed=gzip.compress(blob,mtime=0);assert gzip.decompress(packed)==blob;(N/'REJECTED_OLD_AUXILIARY_RENDER_PRUNING_DECISION_PROOFS.json.gz').write_bytes(packed)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),before=before,after={p:shutil.disk_usage(p).free for p in before},removed=removed,kept=kept,protected_all_accepted_trials=True,main_selected_WAV_and_all_metadata_retained_for_every_touched_variant=True,source_inputs_Diva_MIDI_reference_runtime_and_current_research_untouched=True,public_versions_Git_history_untouched=True,policy='Drop only generated auxiliary render redundancy, not old versions. An old random Chorus realization may differ on regeneration; each old variant main WAV remains for audition.')
(N/'REJECTED_OLD_AUXILIARY_RENDER_PRUNING_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(removed_files=len(removed),touched_rejected_trials=len(proofs),before=before,after=receipt['after']),indent=2))
