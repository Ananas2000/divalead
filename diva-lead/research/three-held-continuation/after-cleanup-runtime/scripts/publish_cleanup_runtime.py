"""Freeze running-work support and hold Git stable through exact config readback."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');ROOT=P/'diva-lead/research/three-held-continuation';O=ROOT/'after-cleanup-runtime';PAUSE=R/'auto-backup.pause';OWNER='publish-selective-cleanup-runtime'
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0',*a],cwd=P,text=True).strip()
while True:
 try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except FileExistsError:time.sleep(2);continue
 with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
 break
for _ in range(90):
 state=json.loads((R/'auto-backup-state.json').read_text())
 if state['phase']=='paused_for_manual_Git_work':break
 time.sleep(1)
else:raise RuntimeError(state)
with (R/'auto-backup-Git.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
 O.mkdir(exist_ok=False);(O/'scripts').mkdir();(O/'diagnostics').mkdir()
 scripts=['fit_three_hf_cleaner100.py','run_cleaner_hf100.py','probe_cleaner_offharmonic_hf.py','probe_cleaner_coupled_hf.py','refine_cleaner_coupled_hf.py','auto_backup_three.py','start_three_services.py','prepare_next_full_v72.py','build_three_v72.py','write_v72_docs.py','finalize_v72.py','verify_zip_windows_v72.py','run_full_v72_build.py','publish_full_v72.py','publish_cleanup_runtime.py']
 for name in scripts:shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
 for name in ['selective-cleanup-public-verification.json','selective-temp-copy-cleanup.json','selective-cleanup-config-save-readback.json','after-cleanup-residual-band-diagnostic.json','cleaner-offharmonic-hf-grid-result.json','cleaner-coupled-hf-grid-result.json','cleaner-coupled-optimization-result.json','public-v70-verification.json','public-v71-verification.json','cleaner-hf100-state.json','v72-preparation-controller-state.json']:
  shutil.copyfile(R/name,O/'diagnostics'/name)
 shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md')
 rows=[]
 for role,first in [('main',6),('phase',34),('balance',5)]:
  for run in sorted((R/('pw5190-live-'+role)).glob('round-*')):
   if int(run.name.split('-')[1])<first:continue
   d=dict(role=role,round=run.name,completed_decision=json.loads((run/'decision.json').read_text()) if (run/'decision.json').exists() else None)
   rows.append(d)
   if d['completed_decision'] and d['completed_decision'].get('full_proof_completed') is False:
    target=R/('pw5190-verified-live-'+role+'-'+run.name.removeprefix('round-'));dest=O/'rejected-models'/target.name;dest.mkdir(parents=True)
    for f in [target/'analysis/spectral_model.json',target/'scores/actual-three.json',run/'decision.json',run/'validation.log']:
     if f.exists():shutil.copyfile(f,dest/f.name)
 write(O/'rounds-at-snapshot.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rounds=rows,in_progress_is_not_completed=True,match_reached=False))
 (O/'README_RU.md').write_text('''# Продолжение после выборочной очистки

Все номерные комплекты сохранены. Очистка освободила922431488байт на основном диске и5182283776байт на временном. История Git не переписывалась. Полные v70/v71 прошли свежую Diva, независимые проверки и фактическую DLL из чистого ZIP; публикации проверены по HTTP.

Подбор после публикаций продолжается. Текущий лучший WAV и полный DLL-комплект выбираются соответствующими CURRENT JSON, они могут различаться. Снимки состояний в diagnostics фиксируют момент записи, не обещают сохранение процессов после публикации среды. Непроверенные и отвергнутые точки не объявляются готовыми.

Отдельная конечная проба cleaner-HF100 временно использует1 вычислительный слот фазового процесса, с более строгим пределом шумового остатка. Она возобновляет только свой точно проверенный родительский процесс. Обычный суммарный бюджет2+1+1 сохранён. Подробные актуальные инструкции — start_skill_current.md. Всё ещё только три удерживаемые ноты; MistaTowa исключён. Совпадение звука не достигнуто.
''')
 target=str(O.relative_to(P));git('add','--',target);assert all(x.startswith(target+'/') for x in git('diff','--cached','--name-only').splitlines());git('diff','--cached','--check');git('commit','-m','Preserve ongoing three-held matching, selective cleanup receipts and cleaner HF research runtime')
 assert all(x.startswith(target+'/') for x in git('diff',before,'HEAD','--name-only').splitlines())
 head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
 for name in ['README_RU.md','start_skill_current.md','scripts/run_cleaner_hf100.py']:
  data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes()
 assert not git('status','--porcelain');write(R/'cleanup-runtime-public-verification.json',dict(commit=head,remote_exact=True,HTTP_bytes_exact=True,numbered_releases_unchanged=True,match_reached=False))
 write(R/'cleanup-runtime-ready-for-config.json',dict(commit=head,lock_held=True,owner=OWNER));print('RUNTIME_PUSHED_AND_HTTP_VERIFIED_READY_FOR_CONFIG',head,flush=True)
 until=time.monotonic()+180
 while time.monotonic()<until and not (R/'cleanup-runtime-config-readback-complete.json').exists():time.sleep(2)
 assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink();print('RUNTIME_GIT_LOCK_AND_PAUSE_RELEASED',flush=True)
