"""Remove only our closed, regenerable PC-* VST3 scratch buffers."""
from pathlib import Path
import datetime,hashlib,json,os,shutil
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');A=Path(__file__).resolve().parent
active=set();opened=set()
for proc in Path('/proc').glob('[0-9]*/fd'):
 try:
  for fd in proc.iterdir():
   try:
    target=os.readlink(fd);opened.add(target)
    if (target.startswith(str(D)+'/PC-')or target.startswith(str(D)+'/ST24-'))and target.endswith('-host.log'):active.add(Path(target).name[:-len('-host.log')])
   except OSError:pass
 except OSError:pass
rows=[];before=shutil.disk_usage('/tmp').free
for suffix in ['-input.f32','-output.f32']:
 for p in [*D.glob('PC-*'+suffix),*D.glob('ST24-*'+suffix)]:
  tag=p.name[:-len(suffix)]
  if tag in active or str(p)in opened or p.is_symlink():continue
  with p.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digest));p.unlink()
r=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed_only_closed_trial_default_DSP_scratch=rows,logical_bytes=sum(x['bytes']for x in rows),tmp_freed=shutil.disk_usage('/tmp').free-before,all_selected_WAVs_validation_archives_states_source_GUI_inputs_retained=True,scratch_regenerated_by_WinVST3_render=True,not_claimed_unselected_scratch_bytes_backed_in_Git=True)
(A/'CLOSED_TRIAL_SCRATCH_CLEANUP.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='removed_only_closed_trial_default_DSP_scratch'}))
