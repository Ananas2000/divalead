"""Stream bounded packs to /tmp, verify, install, then remove only packed aliases."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,re,shutil,subprocess,time
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');OBJ=REPO/'.git/objects'
TMP=Path('/tmp/divalead-streamed-loose-packs');PAUSE=R/'auto-backup.pause';OWNER='pack-only-new-loose-objects'
def git(*args,**kw):return subprocess.run(['git','-c','gc.auto=0',*args],cwd=REPO,text=True,capture_output=True,check=True,**kw).stdout.strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    temp=p.with_suffix(p.suffix+'.progress-tmp');temp.write_text(json.dumps(x,indent=2)+'\n');temp.replace(p)
assert json.loads(PAUSE.read_text())['owner']==OWNER
assert json.loads((R/'auto-backup-state.json').read_text())['phase']=='paused_for_manual_Git_work'
assert not TMP.exists();TMP.mkdir()
with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    head=git('rev-parse','HEAD');before=shutil.disk_usage(R).free
    oldpacks={str(p):(p.stat().st_size,p.stat().st_mtime_ns,sha(p) if p.suffix=='.idx' else None) for p in (OBJ/'pack').iterdir() if p.is_file()}
    all_loose={}
    for folder in sorted(OBJ.iterdir()):
        if not folder.is_dir() or not re.fullmatch('[0-9a-f]{2}',folder.name):continue
        for p in sorted(folder.iterdir()):
            if re.fullmatch('[0-9a-f]{38}',p.name) and p.is_file():
                st=p.stat();all_loose[folder.name+p.name]=dict(path=str(p),size=st.st_size,ino=st.st_ino,mtime_ns=st.st_mtime_ns,SHA256=sha(p))
    names={}
    for line in git('rev-list','--objects','--all','--unpacked').splitlines():
        parts=line.split(' ',1)
        if len(parts)==2:names[parts[0]]=parts[1]
    # Already compressed large ZIP/tar objects are retained loose; never delete them.
    selected=[oid for oid,row in all_loose.items() if row['size']<8*1024**2]
    selected.sort(key=lambda oid:(Path(names.get(oid,'')).name,all_loose[oid]['size'],oid))
    chunks=[];current=[];size=0
    for oid in selected:
        n=all_loose[oid]['size']
        if current and size+n>96*1024**2:chunks.append(current);current=[];size=0
        current.append(oid);size+=n
    if current:chunks.append(current)
    write(TMP/'original-object-records.json',all_loose);results=[]
    for i,oids in enumerate(chunks):
        content=''.join(oid+(' '+names[oid] if oid in names else '')+'\n' for oid in oids)
        pack=TMP/('chunk-'+str(i)+'.pack');stderr=TMP/('chunk-'+str(i)+'.stderr')
        with pack.open('wb') as out,stderr.open('wb') as err:
            proc=subprocess.run(['git','-c','gc.auto=0','-c','pack.writeReverseIndex=false','pack-objects','--stdout','--delta-base-offset','--threads=1','--window=10','--depth=30'],cwd=REPO,input=content.encode(),stdout=out,stderr=err)
        assert proc.returncode==0,stderr.read_text()
        idx=pack.with_suffix('.idx');packid=git('index-pack','--strict','--index-version=2','-o',str(idx),str(pack)).splitlines()[-1]
        assert re.fullmatch('[0-9a-f]{40}',packid),packid
        verification=git('verify-pack','-v',str(idx));verified={line.split()[0] for line in verification.splitlines() if re.match(r'^[0-9a-f]{40} (commit|tree|blob|tag) ',line)}
        assert verified==set(oids)
        free=shutil.disk_usage(R).free;needed=pack.stat().st_size+idx.stat().st_size
        assert free-needed>128*1024**2,dict(root_free=free,pack_bytes=needed,no_objects_removed_from_this_chunk=True)
        installed=[]
        for source,suffix in [(pack,'.pack'),(idx,'.idx')]:
            dest=OBJ/'pack'/('pack-'+packid+suffix);assert not dest.exists();temp=dest.with_suffix(dest.suffix+'.verified-copy-tmp');assert not temp.exists()
            shutil.copyfile(source,temp);assert sha(source)==sha(temp)
            with temp.open('rb') as stream:os.fsync(stream.fileno())
            os.replace(temp,dest);installed.append(dest)
        git('verify-pack',str(installed[1]))
        for oid in oids:
            row=all_loose[oid];p=Path(row['path']);st=p.stat()
            assert (st.st_size,st.st_ino,st.st_mtime_ns)==(row['size'],row['ino'],row['mtime_ns']) and sha(p)==row['SHA256']
            p.unlink()
        checked=git('cat-file','--batch-check',input='\n'.join(oids)+'\n');assert len(checked.splitlines())==len(oids) and ' missing' not in checked
        result=dict(chunk=i,pack_id=packid,objects=len(oids),pack_bytes=needed,original_loose_bytes=sum(all_loose[oid]['size'] for oid in oids),root_free_after=shutil.disk_usage(R).free,pack_SHA256=sha(installed[0]),index_SHA256=sha(installed[1]))
        results.append(result);write(R/'streamed-loose-packs-progress.json',dict(chunks=results,all_original_objects_retained=True,original_HEAD=head))
        print('VERIFIED_CHUNK_INSTALLED',json.dumps(result),flush=True)
    check=git('cat-file','--batch-check',input='\n'.join(all_loose)+'\n');assert len(check.splitlines())==len(all_loose) and ' missing' not in check
    fsck=git('fsck','--connectivity-only','--no-reflogs');(TMP/'connectivity-fsck.txt').write_text(fsck+'\n')
    for path,record in oldpacks.items():
        p=Path(path);assert (p.stat().st_size,p.stat().st_mtime_ns)==record[:2]
        if record[2]:assert sha(p)==record[2]
    assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
    report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_HEAD_unchanged=head,all_original_objects_retained_and_readable=len(all_loose),objects_packed=len(selected),large_already_compressed_objects_left_loose=len(all_loose)-len(selected),all_old_packs_unchanged=True,no_source_audio_history_or_refs_removed=True,connectivity_fsck_passed=True,root_free_before=before,root_free_after=shutil.disk_usage(R).free,chunks=results,pack_creation_streamed_to_separate_tmp=True)
    write(R/'streamed-loose-packs-result.json',report)
    assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink()
    print('BOUNDED_STREAMED_PACKING_COMPLETE',json.dumps(report),flush=True)
