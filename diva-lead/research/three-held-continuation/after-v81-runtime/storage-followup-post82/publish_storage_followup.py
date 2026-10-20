from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path('/workspace/divalead-work/three-held-continuation');P=Path('/workspace/divalead');O=P/'diva-lead/research/three-held-continuation/after-v81-runtime/storage-followup-post82';pause=R/'auto-backup.pause';owner='post82-selective-cache-receipt'
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=P,text=True).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not O.exists()
receipt=json.loads((R/'post82-obsolete-cache-cleanup.json').read_text());assert len(receipt['actions'])==30 and receipt['all_numbered_releases_and_current_three_held_proofs_preserved']
while True:
 try:fd=os.open(pause,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except FileExistsError:time.sleep(2);continue
 with os.fdopen(fd,'w') as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
 break
try:
 for _ in range(120):
  status=json.loads((R/'auto-backup-state.json').read_text())
  if status['phase']=='paused_for_manual_Git_work':break
  time.sleep(1)
 else:raise RuntimeError(status)
 with (R/'auto-backup-Git.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
  protected={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
  protected.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
  O.mkdir()
  for name in ['prune_post82_obsolete_caches.py','post82-obsolete-cache-cleanup.json','post82-obsolete-cache-cleanup-plan.json','post81-runtime-public-verification.json','post81-runtime-config-readback-complete.json']:
   shutil.copyfile(R/name,O/name);assert sha(R/name)==sha(O/name)
  shutil.copyfile(__file__,O/'publish_storage_followup.py')
  (O/'README_RU.md').write_text('''# Дополнительная выборочная очистка после v82

Удалены только генерируемые WAV/SO/DLL/EXE ещё 30 худших оставшихся старых шестнадцатинотных кэшей из диапазона ошибки [0,85; 0,86). Это ограниченная выборка: другие кэши и все их модели, исходники, метрики и validation.json сохранены. Ни один номерной комплект или ZIP, исходный референс и текущие трёхнотные доказательства не удалены. План перечисляет каждый удалённый файл с SHA256; контрольные хэши важных результатов проверены до и после.

Измеренный прирост свободного места — 163713024 байта. Обычные резервы расчёта и публикации не снижены. Не восстанавливать намеренно удалённые генерируемые кэши без необходимости. Подбор продолжен на трёх удерживаемых нотах; полного совпадения пока нет.

Также сохранены подтверждение публикации всех 46 новых физических проб и точное чтение сохранённой конфигурации запуска, ревизия 87. Это не означает публикации снимка среды или проверки восстановления в новой задаче; Save/Publish выполняется через настройки среды. Текущий подбор и автоматические бэкапы работают независимо.
''')
  target=str(O.relative_to(P));git('add','--',target);assert all(n.startswith(target+'/') for n in git('diff','--cached','--name-only').splitlines());git('diff','--cached','--check');git('commit','-m','Record bounded cleanup of 30 obsolete caches and verified current environment startup')
  assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in protected.items())
  commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
  files=[]
  for name in ['README_RU.md','post82-obsolete-cache-cleanup.json','post81-runtime-config-readback-complete.json']:
   data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes();files.append(name)
  assert not git('status','--porcelain')
  (R/'post82-storage-followup-public-verification.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_and_HTTP_byte_exact=True,HTTP_files=files,all_numbered_releases_and_ZIPs_unchanged=True,match_reached=False),indent=2)+'\n');print('SELECTIVE_STORAGE_RECEIPTS_AND_CONFIGURATION_READBACK_PUBLIC',commit,flush=True)
finally:
 if pause.exists() and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
