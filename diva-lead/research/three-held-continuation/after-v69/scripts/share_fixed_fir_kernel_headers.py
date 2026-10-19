"""Share the unchanged FIR kernel table, retaining every byte and path."""
from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path(__file__).resolve().parent
MASTER=Path('/workspace/divalead/diva-lead/v67-wip/analysis/fir_kernels.h')
EXPECTED='d941df0d40f40993b39b2b33eae89f92fd9c4ddc4fbd8e822e705d2489f05d93'
original=MASTER.read_bytes();assert hashlib.sha256(original).hexdigest()==EXPECTED
before=shutil.disk_usage(R).free;rows=[]
for p in sorted(R.rglob('fir_kernels.h')):
    if not p.is_file() or p.is_symlink() or p.samefile(MASTER):continue
    data=p.read_bytes()
    assert data==original and hashlib.sha256(data).hexdigest()==EXPECTED,str(p)
    assert p.stat().st_dev==MASTER.stat().st_dev
    temp=p.with_name(p.name+'.fixed-table-share-tmp');assert not temp.exists()
    os.link(MASTER,temp);os.replace(temp,p)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED
    rows.append(dict(path=str(p),immutable_master=str(MASTER),SHA256=EXPECTED,bytes=len(data)))
out=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),shared_paths=len(rows),
    actual_free_before=before,actual_free_after=shutil.disk_usage(R).free,entries=rows,
    all_original_paths_bytes_and_SHA_preserved=True,only_fixed_FIR_table=True,
    live_scripts_models_DSP_parameters_or_audio_not_edited=True,
    copy_to_independent_inode_before_any_future_table_change=True)
(R/'fixed-fir-kernel-sharing.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='entries'}),flush=True)
