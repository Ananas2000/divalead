"""Only expired closed host INPUT buffers; never source/output/preset data."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,time
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');N=Path('/workspace/divalead-work/native-low-latency-effects');active=set();open_paths=set()
for proc in Path('/proc').glob('[0-9]*/fd'):
    try:
        for fd in proc.iterdir():
            try:
                target=os.readlink(fd);open_paths.add(target)
                if target.startswith(str(D)+'/')and target.endswith('-host.log'):active.add(Path(target).name[:-len('-host.log')])
            except OSError:pass
    except(OSError,PermissionError):pass
literal=set()
for script in D.glob('*.py'):
    literal.update(re.findall(r"['\"]([^'\"\n]+-input[.]f32)['\"]",script.read_text()))
before=shutil.disk_usage('/tmp').free;rows=[]
for p in sorted(D.glob('*-input.f32')):
    tag=p.name[:-len('-input.f32')];log=D/(tag+'-host.log')
    if p.is_symlink()or not p.is_file()or tag in active or str(p)in open_paths or p.name in literal:continue
    if time.time()-p.stat().st_mtime<1800 or not log.is_file():continue
    with log.open(errors='replace')as f:prefix=f.read(4096)
    if'READY 'not in prefix:continue
    with p.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digest,host_tag=tag,closed_expired_input_only=True));p.unlink()
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,logical_bytes_removed=sum(r['bytes']for r in rows),observed_tmp_recovered=shutil.disk_usage('/tmp').free-before,all_output_WAVs_and_all_source_fixtures_and_presets_untouched=True,active_host_tags_protected=sorted(active),literal_input_fixtures_protected=True,regeneration='WinVST3.render writes its default input buffer from the new actual native render before processing; no input buffer is used as a deliverable or selected output',not_claimed_old_stochastic_scratch_bytes_are_remote_backed=True)
(N/'EXPIRED_CLOSED_VST3_INPUT_SCRATCH_CLEANUP_20261024.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CLOSED_EXPIRED_INPUT_SCRATCH_ONLY_REMOVED',json.dumps({k:v for k,v in receipt.items()if k not in ['files','active_host_tags_protected']}),flush=True)
