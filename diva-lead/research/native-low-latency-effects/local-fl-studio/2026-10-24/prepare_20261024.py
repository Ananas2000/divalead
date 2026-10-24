"""Restore the current upstream ZL23 kit into an isolated local session."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP23/Diva_ZL_23_WIP_complete_WIP.zip'
expected='67c01afa22a2f6f357e7699969e2b5b725ceaf292e8975501cbcf0bd243e3fe1'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
session=ROOT/'sessions/2026-10-24';session.mkdir(exist_ok=True)
dest=session/'ZL23_upstream';assert not dest.exists(),'Already prepared; inspect existing session'
dest.mkdir()
with zipfile.ZipFile(source)as z:
    for info in z.infolist():
        p=(dest/info.filename).resolve();assert p.is_relative_to(dest.resolve())
        if info.is_dir():p.mkdir(parents=True,exist_ok=True)
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
files=sorted(p for p in dest.rglob('*')if p.is_file())
report=dict(upstream_commit='05150a2a8e990b65e0c58c00cfc487689e34bde5',kit_sha256=expected,files=[dict(path=p.relative_to(dest).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in files],actual_FL_GUI_validation_pending=True,match_reached=False)
(session/'UPSTREAM_RESTORE.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(files=len(files),flp=[str(p)for p in files if p.suffix=='.flp'],top=[p.relative_to(dest).as_posix()for p in files][:45])))
