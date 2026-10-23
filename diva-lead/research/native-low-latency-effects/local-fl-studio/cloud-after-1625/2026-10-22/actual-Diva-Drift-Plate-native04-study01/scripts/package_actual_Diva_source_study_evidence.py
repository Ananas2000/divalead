"""Gather all real source-case audits and selected/cold audio into a research kit."""
from pathlib import Path
import argparse,gzip,hashlib,io,json,tarfile
p=argparse.ArgumentParser();p.add_argument('--study',required=True);a=p.parse_args()
root=Path(a.study)
rows=json.loads(gzip.decompress((root/'ALL_TRAINING_RESULTS.json.gz').read_bytes()))
assert json.loads((root/'completion.json').read_text())['training_cases']==len(rows)
archive=root/f'ALL{len(rows)}_ACTUAL_DIVA_PRESETS_CHUNKS_AND_281_MIDI_AUDITS.tar.gz'
assert not archive.exists()
manifest=[]
with tarfile.open(archive,'w:gz',compresslevel=6)as tar:
    for row in rows:
        assert row['all281_audited']and row['all12_MIDI_events_exact']
        folder=Path(row['source_audio']).parent
        for f in [Path(row['source_preset']),Path(row['source_VST_chunk']),folder/'all281.tsv',folder/'Diva.log',folder.parent/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json']:
            blob=f.read_bytes();name=row['label']+'/'+f.name;info=tarfile.TarInfo(name);info.size=len(blob);tar.addfile(info,io.BytesIO(blob));manifest.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
with tarfile.open(archive)as tar:
    for row in manifest:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
(root/'ALL_CASES_AUDIT_ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
selected=json.loads((root/'SELECTED_SOURCE_RESEARCH_ONLY.json').read_text())
dest=root/'actual-source';dest.mkdir();src=Path(selected['source_audio']).parent
for source in [Path(selected['source_preset']),Path(selected['source_VST_chunk']),Path(selected['source_audio']),root/'selected-source-cold-chunk-replay/Diva_source.wav']:
    name='cold-chunk-source.wav'if source.parent.name=='selected-source-cold-chunk-replay'else source.name
    (dest/name).write_bytes(source.read_bytes())
for f in [src/'all281.tsv',src/'Diva.log',root/'selected-source-cold-chunk-replay/all281.tsv',root/'selected-source-cold-chunk-replay/Diva.log']:
    name=('cold-chunk-'if f.parent.name=='selected-source-cold-chunk-replay'else'')+f.name+'.gz'
    blob=f.read_bytes();(dest/name).write_bytes(gzip.compress(blob,mtime=0));assert gzip.decompress((dest/name).read_bytes())==blob
print('ACTUAL_SOURCE_STUDY_ALL_CASE_AUDITS_PACKAGED',len(rows),archive.stat().st_size,flush=True)
