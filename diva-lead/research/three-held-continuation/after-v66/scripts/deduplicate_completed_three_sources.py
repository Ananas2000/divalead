"""Share byte-identical completed three-held proof source files, retaining paths."""
from pathlib import Path
import datetime, hashlib, json, os, shutil

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/divalead')
analyses = []
for proof in ROOT.iterdir():
    if proof.is_dir() and proof.name.startswith(('verified-', 'tslop0-verified-', 'drift24-verified-', 'pw5190-verified-')) and (proof / 'validation.json').is_file():
        analyses.append(proof / 'analysis')
for release in (REPO / 'diva-lead').glob('v*-wip'):
    if (release / 'SHA256SUMS.txt').is_file():
        analyses.append(release / 'analysis')
research = REPO / 'diva-lead/research/three-held-continuation'
for report in research.rglob('validation.json'):
    if (report.parent / 'analysis').is_dir() and (report.parent / 'arbitrary-input-verification.json').is_file():
        analyses.append(report.parent / 'analysis')

ledger = ROOT / 'completed-three-source-dedup.json'
entries = json.loads(ledger.read_text()) if ledger.exists() else []
masters = {}
before = shutil.disk_usage(ROOT).free
count = logical = 0
for analysis in sorted(set(analyses)):
    for path in sorted(analysis.rglob('*')):
        if path.suffix not in {'.h', '.c', '.py', '.json', '.tsv'} or path.is_symlink() or not path.is_file():
            continue
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        key = (len(content), digest)
        if key not in masters:
            masters[key] = path
            continue
        master = masters[key]
        if path.samefile(master):
            continue
        assert path.stat().st_dev == master.stat().st_dev and content == master.read_bytes()
        temp = path.with_name(path.name + '.three-source-share-tmp')
        assert not temp.exists()
        os.link(master, temp)
        os.replace(temp, path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        entries.append(dict(path=str(path), immutable_master=str(master), SHA256=digest,
                            bytes=len(content), content_unchanged=True,
                            copy_to_independent_inode_before_any_in_place_edit=True))
        count += 1
        logical += len(content)
    temp = ledger.with_suffix('.tmp')
    temp.write_text(json.dumps(entries, indent=2) + '\n')
    temp.replace(ledger)
result = dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              duplicate_paths_shared=count, logical_duplicate_bytes=logical,
              actual_free_before=before, actual_free_after=shutil.disk_usage(ROOT).free,
              all_paths_and_SHA_preserved=True, unfinished_proofs_excluded=True)
(ROOT / 'completed-three-source-dedup-last.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
