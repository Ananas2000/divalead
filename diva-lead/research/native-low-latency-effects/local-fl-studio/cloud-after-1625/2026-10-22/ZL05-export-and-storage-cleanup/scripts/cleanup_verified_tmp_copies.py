from pathlib import Path
import hashlib,json,os,shutil,subprocess,datetime
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects')
plan=json.loads((N/'TMP_REMOTE_BACKED_DUPLICATE_PLAN.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=P,text=True).split()[0]==head
protected=set()
for root in ['/workspace/divalead-work/native-low-latency-effects','/tmp/divalead-local-1625','/tmp/divalead-native-effects']:
 for p in Path(root).rglob('*'):
  if p.is_symlink():
   try:protected.add(str(p.resolve(strict=True)))
   except FileNotFoundError:pass
for proc in Path('/proc').glob('[0-9]*'):
 try:
  for p in (proc/'fd').iterdir():
   try:protected.add(os.readlink(p))
   except OSError:pass
 except (PermissionError,FileNotFoundError):pass
before={x:shutil.disk_usage(x).free for x in ['/workspace','/tmp']};removed=[];kept=[]
for row in plan:
 p=Path(row['local'])
 if str(p)in protected:kept.append(row);continue
 if not p.is_file()or p.is_symlink():continue
 size=p.stat().st_size;h=hashlib.sha1(f'blob {size}\0'.encode()+p.read_bytes()).hexdigest();assert h==row['blob']
 p.unlink();removed.append(row)
receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),verified_remote_commit=head,before_free_bytes=before,after_free_bytes={x:shutil.disk_usage(x).free for x in before},removed=removed,protected_open_or_symlink_target=kept,restore='git show '+head+':<git_path> > <local_path>',policy='Only exact blob matches already in remote HEAD; active inputs and symlink targets excluded.')
(N/'REMOTE_BACKED_TMP_COPIES_REMOVED_20261023.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(removed=len(removed),protected=len(kept),before=before,after=receipt['after_free_bytes']),indent=2))
