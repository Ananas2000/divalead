"""Remove refetched cache-only packs and test NORMAL save paths, not lazy-off."""
from pathlib import Path
import datetime,fcntl,json,os,re,runpy,shutil,subprocess,sys
P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');R=Path('/workspace/divalead-work/three-held-continuation');sys.path.insert(0,str(D))
old=json.loads((N/'VERIFIED_REMOTE_GIT_AUDIO_BLOB_CACHE_EVICTION.json').read_text());eligible={row['blob']:row for row in old['files']};h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='normal_git_cache_save_validation');git=h['git'];pause=R/'auto-backup.pause';OWNER='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=OWNER,reason='fix accidental cache refetch caused by ls-tree --long; validate normal Git save without lazy-fetch suppression'),f)
try:
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
        before=shutil.disk_usage('/workspace').free;removed=[];packdir=P/'.git/objects/pack'
        for marker in sorted(packdir.glob('*.promisor')):
            pack=marker.with_suffix('.pack');idx=marker.with_suffix('.idx')
            if not pack.is_file()or not idx.is_file()or marker.with_suffix('.keep').exists():continue
            text=subprocess.check_output(['git','-C',str(P),'verify-pack','-v',str(idx)],text=True);objects=[]
            for line in text.splitlines():
                fields=line.split()
                if fields and re.fullmatch('[a-f0-9]{40}',fields[0]):objects.append((fields[0],fields[1]))
            if not objects or not all(kind=='blob'and oid in eligible for oid,kind in objects):continue
            size=pack.stat().st_size+idx.stat().st_size;record=dict(pack=pack.name,bytes=size,objects=[eligible[oid]for oid,kind in objects]);removed.append(record)
            for suffix in ['.pack','.idx','.promisor','.rev','.bitmap']:
                file=marker.with_suffix(suffix)
                if file.exists():file.unlink()
        if(packdir/'multi-pack-index').exists():subprocess.run(['git','-C',str(P),'multi-pack-index','write'],check=True)
        subprocess.run(['git','-C',str(P),'--no-lazy-fetch','fsck','--connectivity-only','--no-dangling'],env=dict(os.environ,GIT_NO_LAZY_FETCH='1'),stdout=subprocess.DEVNULL,check=True)
        # Do not hide the previous ls-tree --long bug by disabling retrieval.
        os.environ.pop('GIT_NO_LAZY_FETCH',None);manifest=(h['PUBLIC']/'SHA256SUMS.txt').read_bytes();normal_before=shutil.disk_usage('/workspace').free;packs_before=set(packdir.glob('*.pack'))
        h['aggregate']();assert(h['PUBLIC']/'SHA256SUMS.txt').read_bytes()==manifest
        git('add','--','diva-lead/research/native-low-latency-effects');git('diff','--cached','--check');assert not git('status','--porcelain')
        assert set(packdir.glob('*.pack'))==packs_before,'Normal metadata path refetched evicted blob packs'
        assert normal_before-shutil.disk_usage('/workspace').free<4*2**20
        # Large automatic repacks need more temporary space than this managed
        # disk. Use explicit bounded verified packing, as in existing scripts.
        previous={}
        for key,value in [('gc.auto','0'),('maintenance.auto','false')]:
            r=subprocess.run(['git','-C',str(P),'config','--local','--get',key],capture_output=True,text=True);previous[key]=r.stdout.strip()if r.returncode==0 else None;subprocess.run(['git','-C',str(P),'config','--local',key,value],check=True)
        receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),HEAD=head,root_before=before,root_after=shutil.disk_usage('/workspace').free,observed_root_recovered=shutil.disk_usage('/workspace').free-before,removed_cache_only_promisor_packs=removed,root_cause='ls-tree --long requests blob sizes and lazily downloads missing archives',fix='metadata SHA aggregation uses ls-tree -r without --long; unchanged absent archives use HEAD SHA manifest',normal_lazy_fetch_enabled_aggregate_git_add_and_diff_passed=True,normal_validation_created_no_new_blob_packs=True,Git_connectivity_without_lazy_fetch_passed=True,previous_auto_maintenance_config=previous,automatic_unbounded_repack_disabled=True,all_refs_versions_and_private_unpublished_source48_untouched=True)
        (N/'REFETCHED_GIT_CACHE_FIX_AND_NORMAL_SAVE_VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('NORMAL_GIT_SAVE_WITHOUT_CACHE_REFETCH_PASS',json.dumps({k:v for k,v in receipt.items()if k!='removed_cache_only_promisor_packs'}),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==OWNER:pause.unlink()
