"""Prune derived old aux A/B caches; retain every actual candidate WAV/state."""
from pathlib import Path
import datetime,gzip,hashlib,io,json,os,re,tarfile
ROOT=Path('/workspace/divalead-work/all-repository-selection/archived-historical-AB')
N=Path('/workspace/divalead-work/native-low-latency-effects')
decisions=[];freed=0
open_paths=set()
for proc in Path('/proc').glob('[0-9]*/fd'):
    try:
        for fd in proc.iterdir():
            try:open_paths.add(os.readlink(fd))
            except OSError:pass
    except(OSError,PermissionError):pass
for metadata in sorted(ROOT.glob('*.tar.gz.json')):
    original=json.loads(metadata.read_text())
    assert original['derived_AB_cache_only']and original['all_decompressed_bytes_verified']
    archive=Path(original['archive'])
    if not archive.is_file()or str(archive)in open_paths:continue
    removed=[];kept=[]
    for item in original['files']:
        path=Path(item['original_path']);match=re.search(r'-aux-([0-9]+)-',path.parent.name)
        main=path.parent/'actual-Windows.wav'
        if not main.is_file():main=path.parent/'REFERENCE_EDIT_WIP.wav'
        eligible=bool(match and int(match[1])%10!=0 and path.name.startswith('AB_')and '/validated-snapshots/'in str(path)and main.is_file()and(path.parent/'choice.json').is_file()and(path.parent/'validation.json').is_file())
        if eligible:
            with main.open('rb')as f:mainSHA=hashlib.file_digest(f,'sha256').hexdigest()
            removed.append(dict(item,retained_actual_main_WAV=str(main),retained_actual_main_SHA256=mainSHA,actual_candidate_audio_not_removed=True))
        else:kept.append(item)
    if not removed:continue
    with archive.open('rb')as f:originalSHA=hashlib.file_digest(f,'sha256').hexdigest()
    assert originalSHA==original['archive_SHA256']
    oldsize=archive.stat().st_size;oldmeta=metadata.read_bytes();target=archive.with_suffix('.pruning-partial')
    with tarfile.open(archive)as src:
        for item in original['files']:
            blob=src.extractfile(item['member']).read();assert len(blob)==item['bytes']and hashlib.sha256(blob).hexdigest()==item['SHA256']
        if kept:
            with tarfile.open(target,'w:gz',compresslevel=6)as out:
                for item in kept:
                    blob=src.extractfile(item['member']).read();info=tarfile.TarInfo(item['member']);info.size=len(blob);out.addfile(info,io.BytesIO(blob))
    if kept:
        with tarfile.open(target)as out:
            for item in kept:assert hashlib.sha256(out.extractfile(item['member']).read()).hexdigest()==item['SHA256']
        newsize=target.stat().st_size
        if newsize>=oldsize:target.unlink();continue
        target.replace(archive)
        new=dict(original,files=kept,archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest())
    else:
        archive.unlink();newsize=0
        new=dict(original,files=[],archive_intentionally_removed_all_members_were_derived_auxiliary_AB=True,archive_SHA256=None)
    new['explicitly_pruned_auxiliary_AB_members']=removed
    metadata.write_text(json.dumps(new,indent=2)+'\n')
    decisions.append(dict(metadata=str(metadata),original_metadata=original,original_metadata_SHA256=hashlib.sha256(oldmeta).hexdigest(),original_archive_SHA256=originalSHA,old_archive_bytes=oldsize,new_archive_bytes=newsize,removed_only_derived_old_auxiliary_AB_members=removed,kept_members_bit_exact=True))
    freed+=oldsize-newsize
    print('PRUNED_OBSOLETE_DERIVED_AUX_AB',archive.name,len(removed),oldsize-newsize,flush=True)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),archives_changed=len(decisions),freed_bytes=freed,every_actual_main_candidate_WAV_and_choice_and_validation_retained=True,all_public_versions_ABs_Git_objects_and_current_research_untouched=True,every10th_aux_snapshot_comparison_protected=True,not_claimed_that_deleted_private_aux_AB_bytes_are_remote_backed=True)
(N/'OBSOLETE_PRIVATE_AUX_AB_CACHE_PRUNING_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
(N/'OBSOLETE_PRIVATE_AUX_AB_CACHE_PRUNING_DECISION_PROOFS.json.gz').write_bytes(gzip.compress(json.dumps(decisions).encode(),mtime=0))
print('PRIVATE_AUX_AB_PRUNING_COMPLETE',json.dumps(receipt),flush=True)
