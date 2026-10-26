"""Archive completed actual studies with bounded staging space, not new presets."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,tarfile,time,zlib
H=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');CH=Path('/tmp/divalead-original-Chorus-phase8-20261025-01');JOINT=Path('/tmp/divalead-original-Diva-joint7-20261025-01');TEMP=Path('/tmp/divalead-completed-study-proof-batches-20261025');TEMP.mkdir(exist_ok=False)
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='completed_actual_native_source_studies');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];cs=read(CH/'completion.json');js=read(JOINT/'completion.json');assert cs['training_cases']==203 and js['training_cases']==35 and not cs['robust_improvement']and not js['robust_improvement']
folders=sorted(p for p in JOINT.iterdir()if p.is_dir()and(p/'ACTUAL_DIVA_AND_FULL_CHAIN_VERIFICATION.json').exists());assert len(folders)==35;archives=[];all_members=[]
for k in range(0,len(folders),8):
 archive=TEMP/f'JOINT_DIVA_CASES_{k:03d}_{min(k+7,len(folders)-1):03d}.tar.gz';members=[]
 with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
  for folder in folders[k:k+8]:
   for p in sorted(folder.rglob('*')):
    if p.is_file():
     name=p.relative_to(JOINT).as_posix();tar.add(p,arcname=name,recursive=False);members.append(dict(name=name,bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest()))
 with tarfile.open(archive)as tar:
  for row in members:assert hashlib.sha256(tar.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 archives.append(dict(local=str(archive),filename=archive.name,bytes=archive.stat().st_size,SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),members=members));all_members+=members
assert sum(Path(row['name']).suffix=='.wav'for row in all_members)==70
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause';deadline=time.monotonic()+240
while True:
 try:
  with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='bounded-space backup completed203native+35actualDiva studies andall70sourceprocessedWAV'),f)
  break
 except FileExistsError:
  if time.monotonic()>deadline:raise
  time.sleep(.25)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-Chorus203-and-Diva-joint35-studies';dest.mkdir();parts=[]
  for root,prefix in [(CH,'CHORUS203'),(JOINT,'DIVA_JOINT35')]:
   for p in root.iterdir():
    if p.is_file()and p.suffix in ['.json','.gz','.bin']:shutil.copyfile(p,dest/(prefix+'_'+p.name))
  scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_native_Chorus_phase8_original.py','original_Diva_joint7_library.py','study_actual_Diva_joint7_original.py','backup_completed_native_and_joint_Diva_studies.py','cleanup_expired_default_native_render_buffers.py']:shutil.copyfile(H/name,scripts/name)
  shutil.copyfile(H/'CLOSED_DEFAULT_NATIVE_RENDER_BUFFER_CLEANUP.json',dest/'CLOSED_DEFAULT_NATIVE_RENDER_BUFFER_CLEANUP.json');shutil.copyfile(H/'direct_original_residual_diagnosis/CURRENT_ORIGINAL_HARMONIC_RESIDUALS.json',dest/'CURRENT_ORIGINAL_HARMONIC_RESIDUALS.json')
  # Stage each verified archive directly from its /tmp path, then retain it as
  # an index-only skip-worktree entry. This avoids a redundant large checkout
  # copy while keeping the exact ordinary Git blob in the pending commit.
  for row in archives:
   path=Path(row['local']);rel=(dest/row['filename']).relative_to(P).as_posix();oid=subprocess.check_output(['git','-C',str(P),'hash-object','-w',str(path)],text=True).strip();b=path.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==oid;git('update-index','--add','--cacheinfo','100644,'+oid+','+rel);git('update-index','--skip-worktree','--',rel);parts.append(dict(path=rel,OID=oid,SHA256=row['SHA256'],bytes=row['bytes'],filename=row['filename']))
  manifest=[{k:v for k,v in row.items()if k!='local'}for row in archives];(dest/'ALL70_WAV_ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
  doc='''# Продолжение к оригиналу:203nativeChorus-пробы и35совместных вариантовDiva

Цель — только загруженный оригинал на штатнойобработке/nativeDLL+дваZL.
v83/Finish не используется как цель/эффект. Три длинные входящие ноты41→37→36
на фразу дважды иARP/ADSR сохранены. Это завершённые исследования, не новаяверсия.

203реальныепробы FruityChorus(7параметров)+sourceStereoShaperphase(1параметр)
в нынешнейцепи: coupledLHS+3прохода,по4nativeреализации; контроль12,лучшиеповторно12.
ТочныеcanonicalWSfine32/EQ/матрица/wetмаршруты иобаZL фиксированы. Свежего
подтверждённого выигрыша нет, измененийнепринято. Числа/настройки сохранены;
это неархив всех случайныхChorusдублей или всехtrialWAV.

35новых настоящих запусков Diva: совместно7тоновыхконтролей(OscMix,PW,
PWKeyFollow2,cutoff,resonance,Tune1/Tune2). Длякаждого281параметр и12MIDIevents
аудированы. Двеновые серии реальных ±finite-differenceисточников дали
физическиеошибкигармоник; boundedlinearLS предложилсовместные правки, затем
онивсерендерились настоящейDiva/native/ZL. Предсказания не использовались
дляпринятия. Контроль12nativeрендеров,каждаяпроба4,4лучшихповторно12.
После перепроверки контрольосталсялучшим; gainsэкрана не подтвердились,
fresh6/cold2/exportне запускались. Ничегоизэтойсерии неприменено.

Архивы сохраняют все35case:35исходныхDivaWAV+35полныхвыбранныхnative/ZLWAV,
всеh2p/actualchunks/281TSV/логи12нот/proofJSON. Все70WAV иостальныечлены
SHAпроверены. Каждаяпорция до8case; manifestуказанотдельно. Большиеархивы
могут быть index-onlyskipworktree/promisorcache, байтыполностью вGit.
Исходныеоценки/веса/819alignment/пороги/стереоguards неизменны. Fine-difference
векторывычислены изнастоящихвыходов, DSPвPython неимитировался.

Диагностикаcurrent26vsoriginal: весомые остаткиH13всреднем−3.09дБ,
H6+2.25дБ,H11+2.70дБ. Нужен баланс обертонов; общийподъёмверханеисправляет
разницу. Всеэтисредние — физическиеметрики, не процентысходства/прослушивание.
КандидатснизкойH24непринимается,если полныйoriginalobjectiveне улучшился.
Current WIP26 невыдаётся заполное совпадение.

Освобождены647741440фактическихбайт/tmp: только закрытые старые default
NativeChain*-render.wavбуферы сзащитойживыхFD/hosttags/2462точныхсохранённых
JSON/Pythonссылок. ВсеselectedstudyWAV/nativepresets/sourcebases/GUI/текущие
fullkits сохранены. ЭтиscratchнеобъявленывсепоGitbacked, онирегeнерируютсяDSP.
GUIFLStudio/субъективноепрослушивание/новаяполнаясборкаэтимизучениемнезаявляются.
Оригиналнедобавляетсявсинтез, MistaTowaнеиспользуется. Основнойпоискиновая
совместнаяsource+FXгипотеза продолжают работать, актуальныживыеконтроллеры.
'''
  (dest/'README_RU.md').write_text(doc);hashes={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()};hashes.update({row['filename']:row['SHA256']for row in parts});(dest/'FILE_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n');h['aggregate']()
  p=PUBLIC/'SHA256SUMS.txt';known={line.split('  ',1)[1]:line.split('  ',1)[0]for line in p.read_text().splitlines()};known.update({str((dest/row['filename']).relative_to(PUBLIC)):row['SHA256']for row in parts});p.write_text(''.join(sha+'  '+name+'\n'for name,sha in sorted(known.items())))
  git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve203 native Chorus trials and35 actual joint Diva variants with all70WAVs');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  for row in parts:
   b=subprocess.check_output(['git','-C',str(P),'show',commit+':'+row['path']]);assert hashlib.sha256(b).hexdigest()==row['SHA256'];assert b==Path(next(x['local']for x in archives if x['filename']==row['filename'])).read_bytes()
  # Metadata graph marks public historical blob cache as fetch-on-demand.
  temp=H/'completed-studies-public-structural-cache';temp.mkdir();out=temp/'structural.pack';ids=[line.split()[0]for line in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
  with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
  ph=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();dst=P/'.git/objects/pack'/('pack-'+ph);Path(str(dst)+'.promisor').touch()
  for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(dst)+suffix);out.with_suffix(suffix).unlink()
  for row in parts:
   oid=row['OID'];loose=P/'.git/objects'/oid[:2]/oid[2:]
   if loose.exists():raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid and hashlib.sha256(raw.split(b'\0',1)[1]).hexdigest()==row['SHA256'];loose.unlink()
  # All raw/selected private source cases remain for now; evict only the
  # verified archive duplicates. Current/selected unbacked audio is untouched.
  for row in archives:Path(row['local']).unlink()
  subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all35_actual_Diva_and70WAVs_Git_byte_verified=True,Chorus203_and_Diva35_not_adopted=True,archive_blobs_on_demand_with_all_refs_retained=True,original_is_the_only_target=True,reference_match_reached=False);(H/'CHORUS203_DIVA35_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
