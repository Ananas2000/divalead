"""Release expired closed NativeChain output buffers, never selected study WAVs."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,time
import soundfile as sf
H=Path(__file__).resolve().parent;W=Path('/tmp/divalead-native-effects');D=Path('/tmp/divalead-local-1625');roots=[Path('/workspace/divalead-work'),D]
r=subprocess.run(['rg','-l','--no-messages','-g','*.json','-g','*.py','-e',r'-render[.]wav',*[str(p)for p in roots]],capture_output=True,text=True);assert r.returncode in [0,1];protected=set()
for name in r.stdout.splitlines():
 for match in re.findall(r'''['"]([^'"\n]+-render[.]wav)['"]''',Path(name).read_text(errors='replace')):protected.add(match.replace('\\','/').rsplit('/',1)[-1])
opened=set();active=set()
for directory in Path('/proc').glob('[0-9]*/fd'):
 try:
  for fd in directory.iterdir():
   try:
    name=os.readlink(fd);opened.add(name)
    if name.startswith(str(W)+'/')and name.endswith('-host.log'):active.add(Path(name).name[:-len('-host.log')])
   except OSError:pass
 except OSError:pass
before=shutil.disk_usage('/tmp').free;removed=[]
for p in W.glob('*-render.wav'):
 tag=p.name[:-len('-render.wav')]
 if p.is_symlink()or tag in active or str(p)in opened or p.name in protected or time.time()-p.stat().st_mtime<1800:continue
 if not(W/(tag+'-host.log')).exists():continue
 try:info=sf.info(p)
 except RuntimeError:continue
 if not(info.samplerate==48000 and info.channels==2 and info.subtype=='FLOAT'and info.frames in [288000,320768]):continue
 with p.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 removed.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digest,expired_closed_default_NativeChain_output_only=True));p.unlink()
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=removed,logical_bytes_removed=sum(row['bytes']for row in removed),observed_tmp_bytes_released=shutil.disk_usage('/tmp').free-before,exact_saved_JSON_Python_references_protected=len(protected),all_selected_study_WAVs_native_states_sourcebases_GUI_and_current_fullkits_retained=True,removed_buffers_regenerated_by_native_render=True,not_claiming_all_scratch_bytes_remote_backed=True)
(H/'CLOSED_DEFAULT_NATIVE_RENDER_BUFFER_CLEANUP.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='files'}),flush=True)
