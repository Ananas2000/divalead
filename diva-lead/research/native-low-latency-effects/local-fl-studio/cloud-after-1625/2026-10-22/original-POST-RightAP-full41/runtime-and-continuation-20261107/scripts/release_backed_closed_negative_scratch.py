"""Release only known owned throwaway buffers of remotely archived negative studies."""
from pathlib import Path
import datetime,hashlib,json,os,shutil
J=Path(__file__).resolve().parent;O=J.parent/'stereo-refinement-20261025';D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');W=Path('/tmp/divalead-native-effects')
groups=[
    ('Delta29-620-',J/'original-native12-delta29-current620-negative-20261107_COMPLETE_PUBLICATION.json'),
    ('DifferentialShelf-620-',J/'original-native12-differential-shelves620-121models-negative-20261107_COMPLETE_PUBLICATION.json'),
    ('DivaToneAxes620-',J/'original-Diva-TuneSlop-PWMdepth-Drift-current620-negative-20261107_COMPLETE_PUBLICATION.json'),
    ('Common109NativeGain11-',O/'original-native12-common109-native-globalgain11-NEW12-stereo-failed-20261104_PUBLICATION.json'),
    ('Common109Stereo18-',O/'original-native12-common109-native-stereo18-bank16-screen-negative-20261104_PUBLICATION.json')]
opened=[]
for proc in Path('/proc').glob('[0-9]*'):
    try:
        if(proc/'stat').read_text().split()[2]=='Z':continue
        for fd in(proc/'fd').iterdir():
            try:opened.append(os.readlink(fd))
            except(FileNotFoundError,PermissionError,ProcessLookupError):pass
    except(FileNotFoundError,PermissionError,ProcessLookupError):pass
rows=[]
for prefix,receipt_path in groups:
    receipt=json.loads(receipt_path.read_text());assert receipt.get('all_original_members_remote_verified')or receipt.get('all_retained_study_files_and_WAVs_remote_Git_verified')
    assert not any(Path(target).name.startswith(prefix)and target.endswith('-host.log')for target in opened),'A matching actual host log is still open'
    files=[p for p in D.glob(prefix+'*.f32')if p.name.endswith(('-input.f32','-output.f32'))]+list(W.glob(prefix+'*-render.wav'))
    for f in files:
        assert str(f)not in opened
        rows.append(dict(path=str(f),bytes=f.stat().st_size,SHA256=hashlib.sha256(f.read_bytes()).hexdigest(),verified_closed_study_receipt=str(receipt_path),only_owned_default_overwritten_render_buffer=True))
(J/'OWN_CLOSED_SCRATCH_RELEASE_PLAN.json').write_text(json.dumps(rows,indent=2)+'\n');before=shutil.disk_usage('/workspace').free
for row in rows:
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];p.unlink()
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,root_actual_bytes_released=shutil.disk_usage('/workspace').free-before,all_archived_WAVs_and_components_source_BEST_and_private_plugins_kept=True,no_running_host_files_deleted=True,no_accepted_kit_touched=True)
(J/'OWN_CLOSED_NEGATIVE_SCRATCH_RELEASE.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='rows'}),flush=True)
