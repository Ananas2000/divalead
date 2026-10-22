"""Losslessly archive only old v53-derived comparison A/B cache WAVs.

All actual lead renders, reference edits, models, scores, presets and numbered
releases remain at their paths. Every removed derived AB byte is recoverable.
"""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tarfile
R=Path('/workspace/divalead-work/all-repository-selection');P=Path('/workspace/divalead')
N=Path('/workspace/divalead-work/native-low-latency-effects');B=Path('/tmp/divalead-local-1625')
out=R/'archived-historical-AB';out.mkdir(exist_ok=True)
files=[]
for d in (R/'validated-snapshots').iterdir():
    if not d.is_dir()or '-53-'not in d.name or any(x in d.name for x in ['current','recovered']):continue
    if not(d/'validation.json').is_file():continue
    for p in d.glob('AB_*.wav'):
        if p.is_file()and not p.is_symlink()and p.stat().st_nlink==1:files.append(p)
files.sort(key=lambda p:(p.stat().st_mtime_ns,str(p)));files=files[:80]
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
head=git('rev-parse','HEAD');before=shutil.disk_usage('/workspace').free;batches=[]
for index in range(0,len(files),4):
    selected=files[index:index+4];name=f'historical-AB-{os.getpid()}-{index//4:03}.tar.gz';tmp=B/name
    records=[]
    for p in selected:
        st=p.stat();records.append(dict(original_path=str(p),member=str(p.relative_to(R/'validated-snapshots')),
            bytes=st.st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),mtime_ns=st.st_mtime_ns))
    with tarfile.open(tmp,'w:gz',compresslevel=6)as archive:
        for p,row in zip(selected,records):archive.add(p,arcname=row['member'],recursive=False)
    with tarfile.open(tmp,'r:gz')as archive:
        assert len(archive.getmembers())==len(records)
        for r in records:assert hashlib.sha256(archive.extractfile(r['member']).read()).hexdigest()==r['SHA256']
    assert tmp.stat().st_size+32*2**20<shutil.disk_usage('/workspace').free
    target=out/name;assert not target.exists();shutil.copyfile(tmp,target)
    assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(tmp.read_bytes()).digest()
    with tarfile.open(target,'r:gz')as archive:
        for r in records:assert hashlib.sha256(archive.extractfile(r['member']).read()).hexdigest()==r['SHA256']
    receipt=dict(archive=str(target),archive_SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),
        derived_AB_cache_only=True,all_decompressed_bytes_verified=True,files=records)
    (out/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    for r in records:
        p=Path(r['original_path']);st=p.stat()
        assert st.st_nlink==1 and st.st_mtime_ns==r['mtime_ns'] and st.st_size==r['bytes']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA256'];p.unlink()
    batches.append(receipt)
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD_unchanged=head,
    scope='Only derived AB_*.wav in completed non-current v53-derived validation cache folders',
    original_audio_models_reference_edits_numbered_releases_and_presets_preserved=True,
    all_decompressed_SHA256_verified=True,archived_AB_files=len(files),actual_free_bytes_before=before,
    actual_free_bytes_after=shutil.disk_usage('/workspace').free,batches=batches)
(N/'HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='batches'}),flush=True)
