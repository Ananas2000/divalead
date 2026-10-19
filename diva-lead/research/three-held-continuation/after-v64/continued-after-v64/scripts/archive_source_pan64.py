"""Archive all15 completed physical probes losslessly, with per-member hashes."""
from pathlib import Path
import tarfile,json,hashlib,datetime
R=Path(__file__).resolve().parent;source=Path('/tmp/divalead-source-pan64');target=Path('/tmp/divalead-source-pan64-completed.tar.gz')
assert not target.exists();d=json.loads((source/'completed.json').read_text());assert d['trials']==15
files=sorted(p for p in source.rglob('*') if p.is_file());manifest={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with tarfile.open(target,'w:gz',compresslevel=6) as archive:
    for p in files:archive.add(p,arcname='source-pan64/'+str(p.relative_to(source)),recursive=False)
with tarfile.open(target,'r:gz') as archive:
    members=archive.getmembers();assert len(members)==len(files)
    for m in members:
        assert m.isfile() and m.name.startswith('source-pan64/') and '..' not in Path(m.name).parts
        assert hashlib.sha256(archive.extractfile(m).read()).hexdigest()==manifest[m.name.removeprefix('source-pan64/')]
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),trials=15,all_completed_sources_and_renders_and_all281_and_scores_preserved=True,source_notes_per_phrase=3,total_note_on=6,full_archive_member_SHA_verified=True,archive=str(target),archive_SHA256=hashlib.sha256(target.read_bytes()).hexdigest(),archive_bytes=target.stat().st_size,members_SHA256=manifest,screening_only_changed_sources_not_adopted=True,match_reached=False)
(R/'source-pan64-archive.json').write_text(json.dumps(report,indent=2)+'\n');print('ALL15_SOURCE_PAN64_PROBES_LOSSLESS_ARCHIVE_VERIFIED',len(files),target.stat().st_size,flush=True)
