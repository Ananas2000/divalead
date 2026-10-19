"""Share identical immutable source files of completed historical proofs.

Keep every pathname and byte. A historical file must be copied to an independent
inode before any future in-place edit. Active three-held proofs are excluded.
"""
from pathlib import Path
import datetime, hashlib, json, os, shutil, time

ROOT = Path(__file__).resolve().parent
HISTORY = Path('/workspace/divalead-work/all-repository-selection/validated-snapshots')
LEDGER = ROOT / 'historical-source-dedup.json'
entries = json.loads(LEDGER.read_text()) if LEDGER.exists() else []
masters = {}
before = shutil.disk_usage(ROOT).free
changed = logical = 0
for proof in sorted(HISTORY.iterdir()):
    if not proof.is_dir() or not (proof / 'validation.json').is_file():
        continue
    for path in sorted((proof / 'analysis').rglob('*')):
        if path.suffix not in {'.py', '.c', '.h', '.json', '.tsv'}:
            continue
        if path.is_symlink() or not path.is_file():
            continue
        st = path.stat()
        if time.time() - max(st.st_mtime, st.st_ctime) < 1800:
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
        assert st.st_dev == master.stat().st_dev
        assert content == master.read_bytes()
        temporary = path.with_name(path.name + '.historical-source-dedup-tmp')
        assert not temporary.exists()
        os.link(master, temporary)
        os.replace(temporary, path)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        entries.append(dict(path=str(path), immutable_master=str(master), SHA256=digest,
                            bytes=len(content), all_paths_and_bytes_preserved=True,
                            copy_to_independent_inode_before_any_in_place_edit=True))
        changed += 1
        logical += len(content)
    # Save after each completed proof; no global storage-keeper ledger changes.
    temp = LEDGER.with_suffix('.tmp')
    temp.write_text(json.dumps(entries, indent=2) + '\n')
    temp.replace(LEDGER)
report = dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              paths_shared=changed, logical_duplicate_bytes=logical,
              actual_free_before=before, actual_free_after=shutil.disk_usage(ROOT).free,
              all_paths_and_SHA_preserved=True, active_three_held_tree_excluded=True)
(ROOT / 'historical-source-dedup-last.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
