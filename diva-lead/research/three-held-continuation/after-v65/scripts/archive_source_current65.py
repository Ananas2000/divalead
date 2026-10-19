"""Losslessly archive all32 actual Diva source probes and newer-Finish rescores."""
from pathlib import Path
import hashlib, io, json, tarfile

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/tmp/divalead-source-current65')
RESCORED = Path('/tmp/divalead-source-current65-b11')
DEST = Path('/tmp/divalead-source-current65-archives')
DEST.mkdir(exist_ok=False)
assert json.loads((SOURCE / 'completed.json').read_text())['trials'] == 32
assert len(json.loads((ROOT / 'source-current65-rescore.json').read_text())['trials']) == 32
archives = []
for start in range(0, 32, 8):
    files = []
    for index in range(start, start + 8):
        folder = SOURCE / ('trial-' + format(index, '03d'))
        files.extend((p, 'actual-Diva/' + str(p.relative_to(SOURCE))) for p in sorted(folder.rglob('*')) if p.is_file())
        path = RESCORED / ('trial-' + format(index, '03d') + '.wav')
        files.append((path, 'newer-Finish/' + path.name))
    if start == 0:
        files.extend((p, 'actual-Diva/' + p.name) for p in [SOURCE/'history.json', SOURCE/'completed.json'])
        files.append((ROOT/'source-current65-rescore.json', 'newer-Finish/scores-summary.json'))
    archive = DEST / ('source-current65-trials-' + format(start, '02d') + '-' + format(start+7, '02d') + '.tar.gz')
    expected = {}
    with tarfile.open(archive, 'w:gz', compresslevel=6) as tar:
        for path, name in files:
            content = path.read_bytes()
            expected[name] = hashlib.sha256(content).hexdigest()
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(content))
    with tarfile.open(archive) as tar:
        assert set(tar.getnames()) == set(expected)
        for member in tar:
            assert hashlib.sha256(tar.extractfile(member).read()).hexdigest() == expected[member.name]
    assert archive.stat().st_size < 50_000_000
    archives.append(dict(file=archive.name, bytes=archive.stat().st_size,
                         SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                         all_members_decompressed_SHA_verified=True, members=expected))
report = dict(actual_Diva_source_trials=32, newer_Finish_rescores=32,
              physical_source_variants_accepted=False, all_cases_preserved_losslessly=True,
              three_held_notes_per_phrase=3, total_note_on_per_render=6, match_reached=False,
              archives=archives)
(DEST / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(archives=len(archives), total_bytes=sum(a['bytes'] for a in archives),
                     actual_Diva_trials=32, all_members_SHA_verified=True)), flush=True)
