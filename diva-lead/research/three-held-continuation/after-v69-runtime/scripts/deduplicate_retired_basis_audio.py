"""Share byte-identical frozen inputs in retired numerical rounds; retain every path."""
from pathlib import Path
import datetime,hashlib,json,os,shutil

R=Path(__file__).resolve().parent
LEGACY={'continuation','phase-continuation','joint-phase-continuation','drift24-continuation','balance-power-continuation'}
RETIRED={'continue_three.py','continue_three_joint_phase.py','continue_three_balance_power.py','continue_phase18.py','continue_drift24.py'}
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        cmd=(proc/'cmdline').read_bytes().split(b'\0')
        state=(proc/'stat').read_text().rsplit(')',1)[1].split()[0]
        if state!='Z':assert not any(str(R/name).encode() in cmd for name in RETIRED),'A legacy controller is still live'
    except (FileNotFoundError,ProcessLookupError):pass

audit=json.loads((R/'retired-basis-exact-copy-audit.json').read_text())
assert audit['only_retired_numeric_basis_copies']
before=shutil.disk_usage(R).free;rows=[]
for row in audit['entries']:
    p=Path(row['path']);master=Path(row['master']);parts=p.relative_to(R).parts
    assert parts[0] in LEGACY and 'basis' in parts and p.suffix=='.wav'
    assert p.is_file() and master.is_file() and not p.is_symlink() and not master.is_symlink()
    assert p.stat().st_dev==master.stat().st_dev
    data=p.read_bytes();assert data==master.read_bytes() and hashlib.sha256(data).hexdigest()==row['SHA256']
    if p.samefile(master):continue
    temp=p.with_name(p.name+'.retired-input-share-tmp');assert not temp.exists()
    os.link(master,temp);os.replace(temp,p)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256']
    rows.append(dict(**row,content_unchanged=True,copy_to_independent_inode_before_edit=True))
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),shared_paths=len(rows),
    actual_free_before=before,actual_free_after=shutil.disk_usage(R).free,
    original_audio_bytes_paths_and_SHA_preserved=True,current_source_and_WAVs_not_modified=True,
    only_retired_numeric_basis_copies=True,entries=rows)
(R/'retired-basis-exact-copy-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='entries'}),flush=True)
