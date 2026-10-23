"""Bounded maintenance of verified duplicate archives and dead host scratch only."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,subprocess,time

B=Path('/tmp/divalead-local-1625');W=Path('/tmp/divalead-native-effects')
N=Path('/workspace/divalead-work/native-low-latency-effects')
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),removed=[],archived=False,
            scope='Only duplicate verified archive staging and inactive overwritten NativeChain output WAV buffers',
            source_models_releases_and_recorded_validation_audio_preserved=True)

if shutil.disk_usage('/workspace').free<144*2**20 and not(R/'auto-backup.pause').exists():
    with(R/'auto-backup-Git.lock').open('a')as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:pass
        else:
            clean=not subprocess.check_output(['git','-C',str(P),'status','--porcelain'],text=True).strip()
            if clean:
                result=subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(B/'archive_historical_AB_cache.py')],
                    text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
                report.update(archived=result.returncode==0,archive_status=result.stdout[-1600:])

if shutil.disk_usage('/tmp').free<768*2**20:
    canonical=Path('/workspace/divalead-work/all-repository-selection/archived-historical-AB')
    for p in sorted(B.glob('historical-AB-*.tar.gz')):
        target=canonical/p.name;receipt=canonical/(p.name+'.json')
        if not target.is_file()or not receipt.is_file():continue
        d=json.loads(receipt.read_text());digest=hashlib.sha256(p.read_bytes()).hexdigest()
        assert d['all_decompressed_bytes_verified']and digest==d['archive_SHA256']==hashlib.sha256(target.read_bytes()).hexdigest()
        report['removed'].append(dict(path=str(p),bytes=p.stat().st_size,SHA256=digest,canonical_archive=str(target)))
        p.unlink()

if shutil.disk_usage('/tmp').free<768*2**20:
    protected=set();scan_errors=[]
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,list):
            for x in v:yield from strings(x)
        elif isinstance(v,dict):
            for x in v.values():yield from strings(x)
    for root in [B,N,P/'diva-lead/research/native-low-latency-effects',W]:
        for p in root.rglob('*.json*'):
            if not p.is_file()or p.suffix not in ['.json','.gz']:continue
            if any(s in p.name.upper()for s in ['CLEANUP','DRYRUN','ARCHIVING','DEDUPLICATION','NATIVE_HOST_SCRATCH_MAINTENANCE']):continue
            try:
                data=gzip.decompress(p.read_bytes())if p.name.endswith('.json.gz')else p.read_bytes()
                for s in strings(json.loads(data)):
                    if s.startswith('Z:\\'):s=s[2:].replace('\\','/')
                    if s.startswith('/')and s.endswith('.wav'):protected.add(s)
            except (OSError,ValueError,EOFError)as e:scan_errors.append(dict(path=str(p),error=str(e)))
    # A concurrently written JSON must be retried next cohort, never ignored.
    if not scan_errors:
        active=[]
        for p in Path('/proc').iterdir():
            if not p.name.isdigit():continue
            try:
                if(p/'stat').read_text().split()[2]!='Z':active.append((p/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace'))
            except (FileNotFoundError,ProcessLookupError):pass
        count=0
        for p in sorted(W.glob('*-render.wav'),key=lambda p:p.stat().st_mtime_ns):
            if count>=200 or shutil.disk_usage('/tmp').free>=1000*2**20:break
            log=p.with_name(p.name[:-len('-render.wav')]+'-host.log');stem=p.name[:-len('-render.wav')]
            if str(p)in protected or not log.is_file()or any(stem in argv for argv in active):continue
            st=p.stat()
            if time.time()-st.st_mtime<600 or st.st_size!=2566188:continue
            digest=hashlib.sha256(p.read_bytes()).hexdigest();now=p.stat()
            assert now.st_ino==st.st_ino and now.st_mtime_ns==st.st_mtime_ns and now.st_size==st.st_size
            report['removed'].append(dict(path=str(p),bytes=st.st_size,SHA256=digest,reason='Inactive overwritten host buffer; no JSON audio reference'))
            p.unlink();count+=1
    report.update(protected_audio_paths=len(protected),scan_errors=scan_errors)

report.update(root_free_MiB=shutil.disk_usage('/workspace').free/2**20,tmp_free_MiB=shutil.disk_usage('/tmp').free/2**20)
if report['removed']or report['archived']or report.get('scan_errors'):
    dest=N/('NATIVE_HOST_SCRATCH_MAINTENANCE_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='removed'},ensure_ascii=False))
