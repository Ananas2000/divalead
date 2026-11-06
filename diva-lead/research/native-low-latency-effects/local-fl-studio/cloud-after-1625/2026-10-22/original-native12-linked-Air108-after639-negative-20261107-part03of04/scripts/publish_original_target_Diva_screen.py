"""Preserve all21 actual Diva screens and42 WAVs; offload verified archive cache."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,tarfile,zlib
H=Path(__file__).resolve().parent;ROOT=Path('/tmp/divalead-original-target-Diva-tone-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='original_target_Diva_screen_backup')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];s=read(ROOT/'completion.json');assert s['training_cases']==21 and not s['robust_improvement']
archive=H/'ALL21_ACTUAL_DIVA_AND_FULL_RENDER_CASES.tar.gz';members=[]
with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
 for folder in sorted(ROOT.iterdir()):
  if not folder.is_dir()or folder.name=='assessment':continue
  for p in sorted(folder.rglob('*')):
   if p.is_file():
    name=p.relative_to(ROOT).as_posix();tar.add(p,arcname=name,recursive=False);members.append(dict(name=name,bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert sum(Path(row['name']).suffix=='.wav'for row in members)==42
with tarfile.open(archive)as tar:
 for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
(ROOT/'ALL_CASE_ARCHIVE_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve21 fresh actualDiva source screens andall42source/processedWAV, original-onlytarget'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  owned=PUBLIC/'original-target-actual-Diva-tone-study01'
  if owned.exists()and not git('ls-tree','HEAD','--',str(owned.relative_to(P))):shutil.move(str(owned),str(H/'source-publication-pre-split-staging'))
  assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'original-target-actual-Diva-tone-study01'
  if dest.exists():
   assert not git('ls-tree','HEAD','--',str(dest.relative_to(P)));shutil.move(str(dest),str(H/'source-publication-pre-split-staging'))
  dest.mkdir()
  for p in ROOT.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']:shutil.copyfile(p,dest/p.name)
  # Same filesystem hard link avoids an unnecessary large staging copy.
  h['copy_or_split_evidence_file'](archive,dest);scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_actual_Diva_against_original_current_two_ZL.py','publish_original_target_Diva_screen.py']:shutil.copyfile(H/name,scripts/name)
  doc='''# Оригинал — единственная цель:21новый настоящий вариант Diva

Зафиксировано последнее принятое native06+PRIMARYcohort155+POST25.
Три входящие удерживаемые ноты41→37→36 дважды/ARP/ADSR неизменны.
Проверены OscMix,PW,глубинаPWKeyFollow2,cutoff,резонанс,Drift,Platewet,VCAmoddepth.
Для каждого варианта заново запущена присланная Diva, сверены все281параметр
и12incomingMIDIevent. Контрольный новый DivaWAV побайтово равен сохранённому
источнику. Затем настоящие nativeDLL и ДВА официальных ZLVST3 дают4реализации
на вариант; контроль8. Три лучших варианта дополнительно проверены по8реализаций.

Цель — только загруженный Diva_original_lead_reference.wav. Сверены его SHA
иdecodedarray с анализатором. v83/Finish не служат ни целью, ни обработчиком.
Прежние objective/веса/819alignment/порог и допуски не менялись; исправленное
стерео защищено прежними дополнительными guards. Ни одна проба не улучшила
исходный полный критерий относительно контроля. Свежие6/cold2 не запускались,
потому что screen не прошёл. Исходный принятый пресет остаётся прежним.
Это завершённое отвергнутое исследование, не новая версия звука и не совпадение.

Losslessархив сохраняет ВСЕ21полныхcase: исходный реальный DivaWAV и выбранный
полный native+2ZL WAV, h2p,реальныйVSTchunk,281TSV,лог12нот иproofJSON.
Все42WAV и остальные члены провереныSHA256; manifest сохранён отдельно.
Архив не содержит все промежуточные случайные Chorusдубли, только два
обозначенныхWAV на вариант. Регенерируемые worker paddedinputбуферы исключены.
После Gitpush/byteverification архивный cache может быть offloaded; все байты
остаются вGit. Старые fullkits/PCGUI/sourcebases сохранены. GUI FLStudio
не запускался. MistaTowa/подмешивание оригинала не используются.
Следующая гипотеза — реальные zero-PDC фазовые полосы ZL, снова к оригиналу.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  header='''BEGIN_USER_ORIGINAL_ONLY_NORMAL_PROCESSING_20261025
User explicitly clarified: target is ORIGINAL WAV on normal low-latency processing, NOT reconstructingv83/oldFinish. v83is historicaldiagnostic ONLY, never target/fittingtransfer. Existing FeaturesOriginal alreadydirectly targetsoriginal; unchangedobjective/tolerances/fresh6cold2/stereo gates. New21actualDiva source variants withall281and12MIDInotes audited in original-target-actual-Diva-tone-study01, all42source/processedWAVlossless backed; noneimproved originalcriterion, notadopted. Currentbest155/native06/twoZLPOST25/3longnotes/ARP/ADSRpreserved. Current original-target finitephaseowner original-reference-tone-finite-20261025 holds N/zl-stereo-continuation.stop toallownewactualZLphaseexperiment; removeONLYwhenfullyvalidated/adopted-or-rejected andresume actualmain. OldsingleZLstopsremainretired. FullmatchFALSE. NoMista/referenceinsynthesis/pertrialquestions. Preservealloldfullkits/PCGUI/privateoriginalsource48. Current analysis is tooriginal, notproxy-v83.
END_USER_ORIGINAL_ONLY_NORMAL_PROCESSING_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve21 actual Diva original-target tone screens, all42WAVs and user target clarification');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  pubs=[dest/archive.name]if(dest/archive.name).exists()else sorted(dest.glob(archive.name+'.part-*'));remote_parts=[];whole=hashlib.sha256()
  for pub in pubs:
   rel=pub.relative_to(P).as_posix();b=pub.read_bytes();oid=git('rev-parse','HEAD:'+rel);assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==oid;assert subprocess.check_output(['git','-C',str(P),'show',commit+':'+rel])==b
   whole.update(b);remote_parts.append(dict(path=rel,OID=oid,SHA256=hashlib.sha256(b).hexdigest()));git('update-index','--skip-worktree','--',rel);pub.unlink()
  assert whole.hexdigest()==hashlib.sha256(archive.read_bytes()).hexdigest();archive.unlink()
  # Source/selected WAV cache is recoverable from the exact verified archive;
  # retain all metadata and the real unchanged-control WAVs for next experiments.
  freed=0
  for row in members:
   p=ROOT/row['name']
   if p.suffix=='.wav'and not row['name'].startswith('unchanged-control/'):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256'];freed+=p.stat().st_size;p.unlink()
  temp=H/'original-target-public-structural-cache';temp.mkdir();out=temp/'structural.pack';ids=[line.split()[0]for line in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
  with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
  ph=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();dst=P/'.git/objects/pack'/('pack-'+ph);Path(str(dst)+'.promisor').touch()
  for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(dst)+suffix);out.with_suffix(suffix).unlink()
  for item in remote_parts:
   oid=item['OID'];loose=P/'.git/objects'/oid[:2]/oid[2:]
   if loose.exists():
    raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid and hashlib.sha256(raw.split(b'\0',1)[1]).hexdigest()==item['SHA256'];loose.unlink()
  subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),archive_SHA256=whole.hexdigest(),archive_parts=remote_parts,all21_actual_Diva_and42WAVs_Git_verified=True,recoverable_rejected_WAV_cache_bytes_released=freed,original_is_the_only_target=True,accepted=False,reference_match_reached=False)
  (H/'ORIGINAL_TARGET_DIVA_SCREEN_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
