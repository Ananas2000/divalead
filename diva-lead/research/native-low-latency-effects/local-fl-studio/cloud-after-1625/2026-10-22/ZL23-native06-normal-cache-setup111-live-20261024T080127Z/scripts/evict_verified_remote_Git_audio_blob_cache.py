"""Evict only reloadable public audio blobs from a tested Git promisor cache."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,sys,zlib
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');R=Path('/workspace/divalead-work/three-held-continuation')
probe=json.loads((N/'VERIFIED_GIT_PROMISOR_AUDIO_CACHE_PROBE.json').read_text());assert probe['actual_missing_blob_fetched_on_demand_and_exact']
sys.path.insert(0,str(D))
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='verified_promisor_eviction_helpers');git=h['git'];OWNER='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=OWNER,reason='evict only verified public old WAV archives from the standard on-demand Git cache; refs/history preserved'),f)
rows=[]
try:
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');head=git('rev-parse','HEAD');assert head==probe['public_HEAD']and git('ls-remote','origin','refs/heads/main').split()[0]==head
        protected=h['protected']();private_ref=git('rev-parse','refs/archive/unpublished-pre-split-f3ed5c50');before=shutil.disk_usage('/workspace').free
        manifest=(h['PUBLIC']/'SHA256SUMS.txt').read_bytes();cache={line.split('  ',1)[1]:line.split('  ',1)[0]for line in manifest.decode().splitlines()}
        for line in git('ls-tree','-r','HEAD','--',h['PUBLIC'].relative_to(P).as_posix()).splitlines():
            info,relative=line.split('\t',1);a=info.split();path=P/relative;key=path.relative_to(h['PUBLIC']).as_posix();loose=P/'.git/objects'/a[2][:2]/a[2][2:]
            if a[1]!='blob' or not path.name.endswith('WAVs.tar.gz')or path.exists()or not loose.is_file():continue
            if loose.stat().st_size<20*2**20:continue
            if key.startswith(('ZL21-','native-WS-fine32-current-ZL20-study01/')):continue
            raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==a[2];header,blob=raw.split(b'\0',1);assert header==b'blob '+str(len(blob)).encode();digest=hashlib.sha256(blob).hexdigest();assert digest==cache[key]
            row=dict(path=relative,blob=a[2],content_bytes=len(blob),loose_cache_bytes=loose.stat().st_size,SHA256=digest,remote_commit=head,restore='git show '+head+':'+relative+' (fetches on demand)');rows.append(row);loose.unlink();print('EVICTED_RELOADABLE_OLD_PUBLIC_GIT_AUDIO_CACHE',relative,row['loose_cache_bytes'],flush=True)
        subprocess.run(['git','-C',str(P),'--no-lazy-fetch','fsck','--connectivity-only','--no-dangling'],env=dict(os.environ,GIT_NO_LAZY_FETCH='1'),stdout=subprocess.DEVNULL,check=True)
        # This real whole-repository check must not fetch the evicted WAVs.
        os.environ['GIT_NO_LAZY_FETCH']='1';h['aggregate']();assert(h['PUBLIC']/'SHA256SUMS.txt').read_bytes()==manifest
        assert not git('status','--porcelain')and git('rev-parse','HEAD')==head;assert git('rev-parse','refs/archive/unpublished-pre-split-f3ed5c50')==private_ref
        assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in protected.items())
        assert subprocess.check_output(['git','-C',str(P),'--no-lazy-fetch','cat-file','-s','41e9bf7d7adba68226614297644c9661181bff6d'],env=dict(os.environ,GIT_NO_LAZY_FETCH='1'),text=True).strip()=='200289363'
        receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD=head,Git_promisor_cache_enabled_and_real_lazy_fetch_tested=True,removed_only_reloadable_loose_old_public_WAV_archive_blobs=True,files=rows,logical_cache_bytes_evicted=sum(r['loose_cache_bytes']for r in rows),observed_root_free_change=shutil.disk_usage('/workspace').free-before,root_free_after=shutil.disk_usage('/workspace').free,all_refs_history_and_full_kit_tree_OIDs_preserved=True,unpublished_private_original_source48_blob_retained=True,selected_user_kits_and_current_native05_states_untouched=True,Git_no_lazy_fetch_connectivity_passed=True,whole_SHA_manifest_byte_exact_without_refetching=True,local_archive_cache_missing_by_design_not_claimed_all_objects_retained=True)
        (N/'VERIFIED_REMOTE_GIT_AUDIO_BLOB_CACHE_EVICTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('REMOTE_BACKED_GIT_AUDIO_CACHE_EVICTED',json.dumps({k:v for k,v in receipt.items()if k!='files'}),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==OWNER:pause.unlink()
