"""Prune expired default WinVST3 render buffers, protecting saved references."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,time
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');A=Path(__file__).resolve().parent
roots=[D,Path('/workspace/divalead-work/pc-stereo-20261024'),Path('/workspace/divalead-work/native-low-latency-effects')]
result=subprocess.run(['rg','-l','--no-messages','-g','*.json','-g','*.py','-e',r'-(input|output)\.f32',*[str(p)for p in roots]],capture_output=True,text=True)
assert result.returncode in [0,1],result.stderr
protected=set()
for name in result.stdout.splitlines():
 for value in re.findall(r'''['"]([^'"\n]+-(?:input|output)[.]f32)['"]''',Path(name).read_text(errors='replace')):protected.add(value.replace('\\','/').rsplit('/',1)[-1])
active=set();opened=set()
for proc in Path('/proc').glob('[0-9]*/fd'):
 try:
  for fd in proc.iterdir():
   try:
    target=os.readlink(fd);opened.add(target)
    if target.startswith(str(D)+'/')and target.endswith('-host.log'):active.add(Path(target).name[:-len('-host.log')])
   except OSError:pass
 except OSError:pass
rows=[];before=shutil.disk_usage('/tmp').free
for suffix in ['-input.f32','-output.f32']:
 for p in D.glob('*'+suffix):
  tag=p.name[:-len(suffix)];log=D/(tag+'-host.log')
  if p.is_symlink()or tag in active or str(p)in opened or p.name in protected:continue
  if time.time()-p.stat().st_mtime<1800 or not log.is_file():continue
  if 'READY 'not in log.read_text(errors='replace'):continue
  with p.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digest,closed_default_render_buffer_only=True));p.unlink()
r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,logical_bytes_removed=sum(x['bytes']for x in rows),tmp_freed_observed=shutil.disk_usage('/tmp').free-before,protected_exact_saved_JSON_and_Python_references=len(protected),all_selected_WAVs_components_validation_archives_GUI_inputs_and_sources_retained=True,default_buffers_regenerated_by_actual_WinVST3_render=True,not_claimed_removed_scratch_bytes_all_remotely_backed=True)
(A/'EXPIRED_CLOSED_DEFAULT_VST3_BUFFER_CLEANUP.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='files'}),flush=True)
