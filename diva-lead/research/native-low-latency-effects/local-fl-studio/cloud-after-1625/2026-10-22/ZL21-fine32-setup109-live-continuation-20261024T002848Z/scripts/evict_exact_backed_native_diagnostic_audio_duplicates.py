"""Keep diagnosis metadata/states; offload exact archived private WAV copies."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');N=Path('/workspace/divalead-work/native-low-latency-effects');P=Path('/workspace/divalead')
publication=json.loads((N/'ZL20_NATIVE_DIAGNOSTICS_SETUP_CONTINUATION_PUBLICATION.json').read_text());manifest=json.loads((D/'ZL20-native-state-controls-proof-archive-01/FILE_MANIFEST_AND_ARCHIVE_SHA256.json').read_text());relative=publication['public_path']+'/lossless-actual-native-diagnostics/'+manifest['archive'];archive=D/'ZL20-native-state-controls-proof-archive-01'/manifest['archive']
blob=subprocess.check_output(['git','-C',str(P),'show',publication['commit']+':'+relative]);assert hashlib.sha256(blob).hexdigest()==manifest['archive_SHA256']and blob==archive.read_bytes()
open_paths=set()
for root in Path('/proc').glob('[0-9]*/fd'):
    try:
        for fd in root.iterdir():
            try:open_paths.add(os.readlink(fd))
            except OSError:pass
    except(OSError,PermissionError):pass
before=shutil.disk_usage('/tmp').free;removed=[]
for row in manifest['files']:
    p=D/row['name'];assert p.resolve().is_relative_to(D)
    if p.suffix not in ['.wav','.f32','.zip']or not p.is_file()or str(p)in open_paths:continue
    assert not p.is_symlink()
    with p.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['SHA256']
    removed.append(dict(path=str(p),SHA256=row['SHA256'],bytes=row['bytes'],archive_member=row['name']));p.unlink()
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),freed_bytes=sum(r['bytes']for r in removed),observed_tmp_free_change=shutil.disk_usage('/tmp').free-before,files=removed,archive_commit=publication['commit'],archive_public_path=relative,archive_SHA256=manifest['archive_SHA256'],all_original_diagnostic_file_bytes_retained_in_lossless_Git_backed_archive=True,all_metadata_states_code_and_current_user_kits_untouched=True,restore_steps=['git -C /workspace/divalead show '+publication['commit']+':'+relative+' > /tmp/native-diagnostics.tar.xz','tar -xJf /tmp/native-diagnostics.tar.xz -C '+str(D)+' CHOSEN_ARCHIVE_MEMBER'])
(N/'EXACT_GIT_BACKED_NATIVE_DIAGNOSTIC_AUDIO_DUPLICATE_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in ['files','restore_steps']}),flush=True)
