"""Verify standard on-demand Git blob retrieval before evicting public cache."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil,subprocess,zlib
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');R=Path('/workspace/divalead-work/three-held-continuation')
ROOT=D/'Git-promisor-audio-cache-probe-20261024';ROOT.mkdir(exist_ok=False)
env=dict(os.environ,GIT_NO_LAZY_FETCH='1')
def git(*args,**kw):return subprocess.check_output(['git','-C',str(P),*args],**kw)
pause=R/'auto-backup.pause';OWNER='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=OWNER,reason='verify standard partial-clone lazy retrieval of public audio cache; no refs or worktree changes'),f)
keys=['core.repositoryformatversion','extensions.partialClone','remote.origin.promisor','remote.origin.partialclonefilter'];old={}
for key in keys:
    result=subprocess.run(['git','-C',str(P),'config','--local','--get',key],capture_output=True,text=True)
    old[key]=result.stdout.rstrip('\n')if result.returncode==0 else None
changed=False;backup=None;loose=None
try:
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain',text=True)
        head=git('rev-parse','HEAD',text=True).strip();assert git('ls-remote','origin','refs/heads/main',text=True).split()[0]==head
        candidates=[]
        for line in git('ls-tree','-rl','HEAD','--','diva-lead/research/native-low-latency-effects',text=True).splitlines():
            info,path=line.split('\t',1);a=info.split();f=P/'.git/objects'/a[2][:2]/a[2][2:]
            if a[1]=='blob'and int(a[3])>=20*2**20 and path.endswith('WAVs.tar.gz')and not(P/path).exists()and f.is_file():candidates.append((f.stat().st_size,a[2],path))
        size,oid,relative=min(candidates);loose=P/'.git/objects'/oid[:2]/oid[2:];backup=ROOT/'probe-original-loose-object.zlib';shutil.copyfile(loose,backup)
        original=zlib.decompress(backup.read_bytes());assert hashlib.sha1(original).hexdigest()==oid;header,data=original.split(b'\0',1);assert header==b'blob '+str(len(data)).encode();rawSHA=hashlib.sha256(data).hexdigest()
        # A promisor pack of every PUBLIC reachable commit/tree marks only
        # remote-backed objects promised. Unpublished local archive refs remain.
        structural=[line.split()[0]for line in git('rev-list','--objects','--filter=blob:none',head,text=True).splitlines()]
        inp='\n'.join(structural)+'\n';types=git('cat-file','--batch-check=%(objecttype) %(objectsize)',input=inp,text=True)
        assert all(line.split()[0]in ['commit','tree','tag']for line in types.splitlines())
        pack=ROOT/'public-structural.pack';idx=ROOT/'public-structural.idx'
        with pack.open('wb')as out:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--threads=2','--window=24','--depth=40'],input=inp.encode(),stdout=out,check=True)
        packid=git('index-pack','-o',str(idx),str(pack),text=True).strip();assert re.fullmatch('[a-f0-9]{40}',packid)
        subprocess.run(['git','-C',str(P),'verify-pack',str(idx)],check=True)
        for f,suffix in [(pack,'pack'),(idx,'idx')]:
            target=P/'.git/objects/pack'/f'pack-{packid}.{suffix}'
            if target.exists():assert target.read_bytes()==f.read_bytes()
            else:shutil.copyfile(f,target)
        (P/'.git/objects/pack'/f'pack-{packid}.promisor').write_text('Verified published origin/main '+head+'\n')
        for key,value in [('core.repositoryformatversion','1'),('extensions.partialClone','origin'),('remote.origin.promisor','true'),('remote.origin.partialclonefilter','blob:none')]:subprocess.run(['git','-C',str(P),'config','--local',key,value],check=True)
        changed=True
        loose.unlink()
        missing=subprocess.run(['git','-C',str(P),'--no-lazy-fetch','cat-file','-e',oid],env=env,capture_output=True)
        assert missing.returncode!=0,'Probe object had another local copy; no lazy test established'
        subprocess.run(['git','-C',str(P),'--no-lazy-fetch','fsck','--connectivity-only','--no-dangling'],env=env,stdout=subprocess.DEVNULL,check=True)
        # This must perform the real authenticated fetch, not use the saved copy.
        retrieved=git('cat-file','blob',oid,timeout=120)
        assert len(retrieved)==len(data)and hashlib.sha256(retrieved).hexdigest()==rawSHA
        subprocess.run(['git','-C',str(P),'--no-lazy-fetch','fsck','--connectivity-only','--no-dangling'],env=env,stdout=subprocess.DEVNULL,check=True)
        assert git('rev-parse','HEAD',text=True).strip()==head and not git('status','--porcelain',text=True)
        receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),public_HEAD=head,probe_path=relative,probe_blob=oid,probe_content_SHA256=rawSHA,actual_missing_blob_fetched_on_demand_and_exact=True,Git_no_lazy_fetch_connectivity_before_and_after_passed=True,public_structural_promisor_pack=packid,public_structural_objects=len(structural),public_structural_pack_bytes=pack.stat().st_size,all_local_refs_and_unpublished_objects_untouched=True,previous_selected_Git_config=old,standard_partial_clone_remote='origin')
        (N/'VERIFIED_GIT_PROMISOR_AUDIO_CACHE_PROBE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('VERIFIED_ACTUAL_LAZY_GIT_BLOB_FETCH',json.dumps(receipt),flush=True)
        backup.unlink();pack.unlink();idx.unlink()
except BaseException:
    # Restore the original bytes before removing partial-clone metadata if any
    # supported retrieval/verification step fails. No remote refs are changed.
    if backup is not None and backup.exists()and loose is not None:loose.parent.mkdir(exist_ok=True);shutil.copyfile(backup,loose)
    if changed:
        for key,value in old.items():
            if value is None:subprocess.run(['git','-C',str(P),'config','--local','--unset-all',key],check=False)
            else:subprocess.run(['git','-C',str(P),'config','--local',key,value],check=True)
    raise
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==OWNER:pause.unlink()
