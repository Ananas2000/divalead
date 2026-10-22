"""Publish the functionally verified missing-/tmp source-fixture recovery."""
from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,time
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation');N=Path('/workspace/divalead-work/native-low-latency-effects');B=Path('/tmp/divalead-local-1625')
base=P/'diva-lead/research/native-low-latency-effects';d=base/'local-fl-studio/cloud-after-1625/2026-10-22';owner='missing-source-fixture-recovery';pause=R/'auto-backup.pause'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    until=time.monotonic()+90
    while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':assert time.monotonic()<until;time.sleep(1)
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected();kits={p.name:git('rev-parse','HEAD:'+p.relative_to(P).as_posix())for p in d.glob('WIP[0-9][0-9]')if p.is_dir()}
        shutil.copyfile(B/'start_corrected_fl20.py',d/'scripts/start_corrected_fl20.py');shutil.copyfile(B/'start_corrected_fl20.py',N/'FL20-corrected/runtime-scripts/start_corrected_fl20.py')
        shutil.copyfile(B/'missing-pad-startup-preflight-check/PROOF.json',d/'proofs/MISSING_TMP_SOURCE_FIXTURE_RECOVERY.json')
        shutil.copyfile(B/'backup_missing_pad_recovery.py',d/'scripts/backup_missing_pad_recovery.py')
        current=R/'start_skill_current.md';s=current.read_text();s='STARTUP FIXTURE RECOVERY VERIFIED: start_corrected_fl20.py now rebuilds ONLY a missing native input WAV under task roots from SHA-verified durable raw/h2p, preserving all320768 float32 stereo frames and exact zero padding. This handles lost /tmp while N/BEST survives. --check-only exercised the actual rebuild without starting any controller/DSP process. Existing live controller remains idempotent.\n\n'+s;current.write_text(s);shutil.copyfile(current,base/'start_skill_current.md')
        guide=d/'WIP09_CONTINUATION_RU.md';guide.write_text(guide.read_text()+'\nЕсли после потери /tmp сохранился BEST, но исчез его native input WAV,\nstart_corrected_fl20.py восстановит только отсутствующий рабочий WAV из\nпроверенного по SHA сырого источника. --check-only проверен на новом\nотсутствующем пути: все320768 стереокадров и нулевой хвост точны, процессы\nне запускались; существующий подбор не затронут.\n',encoding='utf-8')
        files=sorted(p for p in d.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n'for p in files))
        git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        git('commit','-m','Recover missing native source fixture from audited raw before corrected search startup')
        after=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+str((d/name).relative_to(P)))==oid for name,oid in kits.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==after and not git('status','--porcelain')
        (N/'MISSING_SOURCE_RECOVERY_PUBLICATION.json').write_text(json.dumps(dict(commit=after,previous_HEAD=before,all_complete_kits_and_numbered_releases_preserved=True,actual_recovery_without_process_start_verified=True,match_reached=False),indent=2)+'\n');print(after,flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
