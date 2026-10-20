"""Selectively prune only another weak tier of retired sixteen-note generated caches."""
from pathlib import Path
import datetime,hashlib,json,shutil
R=Path(__file__).resolve().parent;C=R.parent/'all-repository-selection/validated-snapshots'
report=R/'post83-obsolete-cache-cleanup.json';assert not report.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=[R/'post80plate68-verified-core147-live-checkpoint-0001/validation.json',R/'source-post80plate68-basis/validation.json',R/'source-post80plate68-basis/Diva_source.wav',R/'baseline/validation.json',R/'source-post74joint-basis/Diva_source.wav',R/'post74joint-verified-live-main-0028-gain/validation.json',Path('/workspace/divalead/diva-lead/v83-wip/SHA256SUMS.txt')]
hashes={str(p):sha(p) for p in protected};actions=[];before=shutil.disk_usage(R).free
def old_score(p):
    d=json.loads(p.read_text());value=d.get('fresh_carrier_score',d.get('score'));return value if isinstance(value,(int,float)) else float('-inf')
for path in sorted(C.glob('*/validation.json'),key=old_score,reverse=True):
    data=json.loads(path.read_text());score=data.get('fresh_carrier_score',data.get('score'))
    if not isinstance(score,(int,float)) or not .85<=score<.86:continue
    removed=[]
    for f in path.parent.rglob('*'):
        if f.is_file() and not f.is_symlink() and f.suffix.lower() in ['.wav','.so','.dll','.exe']:
            assert C.resolve() in f.resolve().parents
            removed.append(dict(path=str(f.relative_to(path.parent)),bytes=f.stat().st_size,SHA256=sha(f)))
    if removed:actions.append(dict(snapshot=path.parent.name,old_sixteen_note_score=score,validation_SHA256=sha(path),generated_only=removed,models_source_and_metrics_preserved=True))
    if len(actions)==20:break
plan=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='User requested only unnecessary worse intermediate caches, preserving numbered releases.',score_tier_inclusive_lower_exclusive_upper=[.85,.86],selected_variant_limit=20,worst_remaining_in_this_tier_only=True,only_old_sixteen_note_generated_cache=True,all_numbered_releases_and_current_three_held_proofs_preserved=True,protected_hashes=hashes,actual_free_before=before,actions=actions)
(R/'post83-obsolete-cache-cleanup-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
for action in actions:
    folder=C/action['snapshot']
    assert sha(folder/'validation.json')==action['validation_SHA256']
    for item in action['generated_only']:
        path=folder/item['path'];assert sha(path)==item['SHA256'];path.unlink()
    assert sha(folder/'validation.json')==action['validation_SHA256']
assert all(sha(Path(p))==digest for p,digest in hashes.items())
plan['actual_free_after']=shutil.disk_usage(R).free;plan['actual_bytes_recovered']=plan['actual_free_after']-before
report.write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(dict(pruned_obsolete_cache_variants=len(actions),actual_bytes_recovered=plan['actual_bytes_recovered'],actual_free_after=plan['actual_free_after'],all_numbered_versions_and_current_proofs_preserved=True)),flush=True)
