"""Scoped recoverable checkpoint of current accepted DSP and storage cleanup."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,struct,subprocess,time,xml.etree.ElementTree as ET
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
prefix=(D/'watch_ZL_useful_complete_backups.py').read_text().split("if __name__=='__main__':")[0]
exec(compile(prefix,'ZL-backup-helpers','exec'),globals())
OWNER_MANUAL='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
deadline=time.monotonic()+45
while pause.exists():
 assert time.monotonic()<deadline,'Other writer remains active; preserve current checkout';time.sleep(.2)
with pause.open('x')as f:json.dump(dict(owner=OWNER_MANUAL,PID=os.getpid(),reason='recoverable current 69-param DSP and verified obsolete staging cleanup'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');old=protected();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=PUBLIC/('current-69param-and-storage-'+stamp);dest.mkdir();scripts=dest/'scripts';scripts.mkdir()
  best=read(D/'ZL-continuous65/BEST_CANDIDATE.json');component=Path(best['native_ZL_component_state']);completion=read(component.parent/'completion.json');assert completion['robust_improvement'];copy_evidence(component.parent,dest/'accepted-private-best',True)
  (dest/'BEST_CANDIDATE_COMPONENT_AUTHORITATIVE.json').write_text(json.dumps(best,indent=2)+'\n')
  data=component.read_bytes();xml=ET.fromstring(data[8:8+struct.unpack_from('<I',data,4)[0]]);physical={p.attrib['id']:float(p.attrib['value'])for p in xml.find('Para')};(dest/'REAL_COMPONENT_XML_PHYSICAL_VALUES.json').write_text(json.dumps(physical,indent=2)+'\n')
  if not list(PUBLIC.glob('ZL*-validated-continuation/LR-current-control-merge')):copy_evidence(D/'ZL-confirmed-extra-allpass-LR-merge-01',dest/'LR-current-control-merge',True)
  for name in ['OLD_ZL_EXPANDED_STAGES_REMOTE_VERIFIED_EVICTION.json','ZL_FULL_BACKUP_WATCHER_START.json','LEGACY_IDLE_CONTROLLERS_RETIRED_FOR_CURRENT_ZL_MATCHING.json','ZL_POST_EXTRA_ALLPASS_LR_MERGE_RESTART.json']:
   p=N/name;b=p.read_bytes()
   if len(b)>150000:(dest/(name+'.gz')).write_bytes(gzip.compress(b,mtime=0))
   else:shutil.copyfile(p,dest/name)
  for name in ['continue_ZL_matching.py','watch_ZL_useful_complete_backups.py','freeze_ZL_export_input.py','merge_confirmed_ZL_extra_allpass_LR.py','study_ZL_extra_allpass_LR.py','backup_current_ZL_research_and_cleanup.py']:
   compile((D/name).read_text(),name,'exec');shutil.copyfile(D/name,scripts/name)
  shutil.copyfile(N/'evict_verified_old_ZL_expanded_stages.py',scripts/'evict_verified_old_ZL_expanded_stages.py')
  main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');watcher=read(N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json');latest=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json')
  assert alive(main['owner']['PID'])and alive(watcher['PID'])
  (dest/'ACTUAL_MAIN_AND_FULL_BACKUP_WATCHER_SNAPSHOT.json').write_text(json.dumps(dict(main=main,backup_watcher=watcher),indent=2)+'\n')
  receipts=[('REMOTE_BACKED_LOCAL_RELEASE_OMISSIONS_20261023.json','before_free_bytes','after_free_bytes'),('REMOTE_BACKED_TMP_COPIES_REMOVED_20261023.json','before_free_bytes','after_free_bytes'),('REMOTE_BACKED_HISTORICAL_WORK_CLEANUP.json','before','after'),('OLD_ZL_EXPANDED_STAGES_REMOTE_VERIFIED_EVICTION.json','before','after')]
  freed=0
  for name,a,b in receipts:
   r=read(N/name);freed+=sum(r[b][p]-r[a][p]for p in ['/workspace','/tmp'])
  storage={p:shutil.disk_usage(p).free for p in ['/workspace','/tmp']};o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),observed_total_cleanup_net_freed_bytes=freed,observed_GB=freed/1e9,observed_GiB=freed/2**30,current_free_bytes=storage,retained_cross_volume_archives_not_counted_as_total_freed=True,reference_match_reached=False)
  (dest/'STORAGE_MEASUREMENTS.json').write_text(json.dumps(o,indent=2)+'\n')
  latestcode=latest['full_kit'][-2:]
  guide=f'''# Продолжение:69параметров и место, {stamp}

Полного совпадения с оригиналом пока нет. Актуальный полный опубликованный
комплект на момент этой записи — [ZL{latestcode}](ZL{latestcode}_CONTINUATION_RU.md).
[ZIP с FLP/WAV/Diva/MIDI/17FST/инструкцией](ZL-WIP{latestcode}/Diva_ZL_{latestcode}_WIP_complete_WIP.zip).
В этом отдельном checkpoint сохранён ещё более свежий принятый частный WIP,
mean{best['loss']:.9f}: реальный компонент, выбранный WAV, JSON результатов и
lossless-архив всех12проверочных WAV. Это checkpoint исследования, не новый
полный FLP. Физические значения извлечены из реального componentXML;
унаследованные старые массивы BESTJSON могут быть устаревшими.

Три внешние ноты41→37→36 на фразу, две фразы, прежний внутренний ARP Diva.
Источник и12nativeFX не менялись. В ZL12staticPeak+4AllPass+4dynamicPeak,
OutputGain:69настраиваемых физических параметров. Частное добавление последней
MidAllPass повторно проверено против актуального контроля: парные6
1.452662023→1.452132597, SEM0.000036365; actualPDC0, impulsefirst0,
оба новых coldinstance совпали побитно, componentresave точен. Данные и все
12WAV этого сравнения также сохранены здесь или в priorvalidatedcontinuation.

Основной поиск расширен: перед каждым coordinate-sweep проверяются48совместных
вариантов нескольких полос. Это помогает проверять сочетания, которые не даёт
подбор по одному параметру. Дальше прежние2heldouts,6freshpaired и критерий
robust>max(.0005,3SEM). Полный original-reference критерий не изменён. WAV
реально обрабатывается официальным WindowsVST3 и настоящими штатными DLL FL.
Ни новых subjectiveaudition, ни GUIFL20экспорта здесь не заявляется.

На момент snapshot реальный numericPID{main['owner']['PID']},
phase={main['phase']}; backupwatcherPID{watcher['PID']}. Сам snapshot не доказывает,
что они работают позже: проверять actualPID/starttime/cmdline. Основной процесс
сохраняет все принятые состояния и WAV; отдельный testedwatcher делает полные
комплекты при полезном улучшении, проверяет render/parser/ZIPreplay и пушит их.
Legacy oldnative/oldFinish контроллеры завершены, не запускать их параллельно.

По сумме фактических измерений четырёх операций освобождено около
**{freed/1e9:.2f}GB ({freed/2**30:.2f}GiB)**. Часть уже заняли новые результаты.
Отдельный перенос~1GiB сохранённых архивов между разделами в эту сумму не входит.
Версии GitHub/история/все полные kits сохранены. После прежних проверок удалены
20лишних expanded/checkZIP путей ZL01–07: каждый файл проверен по реальному
полному remoteZIP. ZL01 replay с отличавшимся TSV оставлен. Последний ZL08,
новые kits, BASEFL20_NATIVE17, исходник, референс и активные файлы сохранены.

Для восстановления старого целого комплекта получите ZIP по remotecommit и
remote_ZIP_git_path из журнала, распакуйте в НОВУЮ папку. Checkout старых
номерных WAV/rootZIP выгружен со skip-worktree, восстановление одного пути:
`git restore --ignore-skip-worktree-bits -- точный/путь`.
Сведения о первой очистке: [ZL05](ZL05_CONTINUATION_RU.md). Не восстанавливать
все старые аудиокопии одновременно — это снова займёт рабочий диск.

[Официальный ZL Equalizer2 1.4.1 Windowsx64](https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi)
выбран за бесплатный VST3, динамический Mid/Side EQ и нулевую добавленную
буферную задержку проверенного MinimumPhase/lookahead0 режима. Плагин на
реальных рендерах улучшил исходный критерий; это не доказательство100%совпадения.
'''
  (PUBLIC/'CURRENT_69PARAM_AND_STORAGE_RU.md').write_text(guide,encoding='utf-8');(dest/'README_RU.md').write_text(guide,encoding='utf-8')
  p=PUBLIC/'README_RU.md';p.write_text('[Текущее продолжение69params, совместный поиск, место и восстановление](CURRENT_69PARAM_AND_STORAGE_RU.md).\n\n'+p.read_text(),encoding='utf-8')
  header=f'''BEGIN_CURRENT_69PARAM_COUPLED_SEARCH_AND_STORAGE
LATEST COMPLETE PUBLIC KIT ZL{latestcode}; newer private accepted mean{best['loss']:.9f} backed in current-69param-and-storage-{stamp}/accepted-private-best with actualcomponent/selectedWAV/all12validationWAVarchive. Read CURRENT_69PARAM_AND_STORAGE_RU.md first. CurrentactualmainPID{main['owner']['PID']} andfullkitwatcherPID{watcher['PID']} snapshots only; verify actualprocess/starttime/state. MAIN69params now12staticPeak+4AllPass+4dynamicPeak+OutputGain; directoryZL-continuous65 name historical. Joint48one-to-three-band proposals precede every scalarcoordinate sweep; same frozeninput/unchangedoriginalobjective/2heldouts/paired6/robust>.0005or3SEM andcoldstateproof policy unchanged. ComponentXML authoritative over inherited stalearrays; actual610readbacks required on export. Source and12nativeFX andexactthreeheldnoteARP unchanged. Last separateMidAP at~3182Hz/Q3.52 mergedafterfreshpaired6 gain1.452662023->1.452132597; PDC0/impulse0/statebytesexact/twonewcoldinstancesbitexact. No exactmatch, subjectiveaudition, newFLGUIexport orASIOlatencyclaim.

Alllegacyoldstocknumeric/watcher/FinishGitpublisher are retired withactualidentitychecked idlehandoff; don'tresume them. MainactualD/continue_ZL_matching.py, N/FL20_ZL_CONTINUOUS_CONTROLLER.json; backupD/watch_ZL_useful_complete_backups.py --watch, N/ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json. Both alive at thissnapshot, not a permanencepromise. Main finitecohort guards root64MiB/tmp112MiB; fullkitbackup guard192/180MiB. Userauthorizes persistentwork/fullbackups/FL20internetFX andoldlocalcopyeviction, no pertrialquestions. Source01..07 staging/checkZIP omissions additional20paths verifiedagainstremoteZIP, ZL01mismatchedTSVreplay preserved, latest08+ andbuilderbase17 kept. Totalobservedcleanup~{freed/1e9:.2f}GB excludes1GiBcrossvolumerelocation. AllGitversions/history/fulltreeOIDs preserved; skippedoldcheckoutrestoreindividualwithgitrestoreignore-skip-worktree-bits, privateoldkitrestoreexactremoteZIP perreceipt. AggregateSHA includes omittedPUBLIC04ZIPviaGitblob. Savedoldonboardingdraft remainsunpublished andnotblocker.
END_CURRENT_69PARAM_COUPLED_SEARCH_AND_STORAGE

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md')
  aggregate();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Back up current 69-parameter coupled ZL search, full private WAV validation and verified old stage eviction');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
  for rel in ['CURRENT_69PARAM_AND_STORAGE_RU.md',dest.relative_to(PUBLIC).as_posix()+'/accepted-private-best/'+component.name]:
   p=PUBLIC/rel
   with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix(),timeout=40)as response:b=response.read()
   assert b==p.read_bytes()
  receipt=dict(commit=commit,previous_HEAD=before,all_old_full_kit_tree_OIDs_preserved=True,private_best_mean=best['loss'],latest_complete_kit=latest['full_kit'],observed_cleanup_net_freed_bytes=freed,actual_main_PID=main['owner']['PID'],actual_backup_watcher_PID=watcher['PID'],reference_match_reached=False)
  (N/'CURRENT_69PARAM_AND_STORAGE_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER_MANUAL:pause.unlink()
