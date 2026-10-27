"""Release only closed rejected WAVs already SHA-verified in ordinary Git archives."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
H=Path(__file__).resolve().parent;O=H.parent/'stereo-refinement-20261025';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='closed_rejected_audio_cache_recovery');P,N,C,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
roots=['RELATIVE_AIR_PRIMARY_JOINT_RETRY2','LARGER_POST_TRIM_PRIMARY_COADAPT','RELATIVE_AIR_PRIMARY_POST_MARGIN','PRIMARY_RELATIVE_AIR_DYNAMICS','RELATIVE_AIR_UPPER_SHELF_VERIFIED']
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='release only closed rejected byte-verified archived WAV copies'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise TimeoutError('Publisher remains live')
  time.sleep(.5)
try:
 with(C/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();commit=git('rev-parse','origin/main');assert git('rev-parse','HEAD')==commit
  manifests=[]
  for m in PUBLIC.glob('original-*/ARCHIVE_MEMBER_SHA256.json'):
   try:
    rows=json.loads(m.read_text());index={r['name']:r for r in rows};receipts=list(O.glob(m.parent.name+'_PUBLICATION.json'))+list(H.glob(m.parent.name+'_PUBLICATION.json'))
    if receipts and json.loads(receipts[0].read_text()).get('all_retained_study_files_and_WAVs_remote_Git_verified'):manifests.append((m,index,receipts[0]))
   except (KeyError,TypeError,json.JSONDecodeError):continue
  opened=set()
  for p in Path('/proc').glob('[0-9]*/fd/*'):
   try:opened.add(p.resolve())
   except (OSError,RuntimeError):pass
  best=(H.parent/'pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json').read_text();released=[];proofs=[];before=shutil.disk_usage('/workspace').free
  for dirname in roots:
   r=H/dirname;completion=json.loads((r/'completion.json').read_text());assert completion['robust_improvement']is False and completion['not_adopted']is True
   wavs=list(r.rglob('*.wav'));digests={p:hashlib.sha256(p.read_bytes()).hexdigest()for p in wavs}
   matches=[]
   for m,index,receipt in manifests:
    ok=[p for p in wavs if p.relative_to(r).as_posix()in index and index[p.relative_to(r).as_posix()]['SHA256']==digests[p]]
    if ok:matches.append((len(ok),m,index,receipt,ok))
   if not matches:continue
   _,m,index,receipt,ok=max(matches,key=lambda x:x[0]);url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+m.relative_to(P).as_posix();assert h['read_public_bytes'](url)==m.read_bytes()
   archive_manifests=list(m.parent.glob('*ARCHIVE_MANIFEST.json'));assert len(archive_manifests)==1
   archive=json.loads(archive_manifests[0].read_text());assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+archive_manifests[0].relative_to(P).as_posix())==archive_manifests[0].read_bytes()
   for part in archive['parts']:assert git('rev-parse',commit+':'+part['path'])==part['OID']
   proofs.append(dict(root=str(r),public_manifest=str(m.relative_to(P)),verified_prior_receipt=str(receipt),current_remote_parts=archive['parts']))
   for p in ok:
    assert p.resolve()not in opened and str(p)not in best and hashlib.sha256(p.read_bytes()).hexdigest()==digests[p];released.append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digests[p],archive_member=p.relative_to(r).as_posix(),public_archive=m.parent.relative_to(P).as_posix()));p.unlink()
  result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),remote_commit=commit,root_free_before=before,root_free_after=shutil.disk_usage('/workspace').free,bytes_released=sum(x['bytes']for x in released),closed_rejected_roots_only=True,current36_first0_source_presets_states_reference_all_preserved=True,proofs=proofs,released=released);(H/'VERIFIED_FIVE_CLOSED_NEGATIVE_AUDIO_RELEASE_20261027.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['released','proofs']}),flush=True)
finally:
 if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
