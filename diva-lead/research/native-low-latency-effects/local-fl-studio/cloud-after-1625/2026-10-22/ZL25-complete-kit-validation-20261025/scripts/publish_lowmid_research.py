"""Back up the completed new Side-phase hypothesis and every retained proof WAV."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,zlib
A=Path(__file__).resolve().parent;ROOT=Path('/tmp/divalead-lowmid-side-phase-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='lowmid25_evidence_backup');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
s=read(ROOT/'completion.json');assert s['robust_improvement'];assert max(read(ROOT/'ACTUAL_COLD_REPLAY_AND_LATENCY_PROOF.json')['two_fresh_cold_actual_two_ZL_instances_replay_max_abs_errors'])==0
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='preserve low-mid stereo improvement, all30 training/validation WAVs and actual cold replay'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'lowmid-Side-phase-after-cohort15-20261025';h['copy_evidence'](ROOT,dest,True);scripts=dest/'scripts';scripts.mkdir()
  for p in A.glob('*.py'):compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['CURRENT_COHORT15_CHANNEL_BALANCE.json','EXPIRED_CLOSED_DEFAULT_VST3_BUFFER_CLEANUP.json','CLOSED_TRIAL_SCRATCH_CLEANUP.json']:
   p=A/name
   if p.exists():shutil.copyfile(p,dest/name)
  doc=f'''# Новая Side-only фазовая поправка низкой середины

Это завершённое исследование, ещё не новый принятый полный проект. Предыдущий
подтверждённый исходник: [stereo-cascade87 cohort15](../stereo-cascade87-cohort-0015/README_RU.md).
Три удерживаемые ноты41→37→36 дважды/внутреннийARP/Diva281/native06/fine32,
основной ZL и существующие postSide10000Q2+2200Q4 неизменны. Добавлен третий
AllPass в Side: фактические895.8Гц/Q13.84. Он не выравнивает RMSканалов.

91реальный VST3вариант по3новым native/inputреализациям, два heldout положительны.
Кандидат зафиксирован до8новых проверок. Fresh6mean gain{s['first6_mean_improvement']:.12f},
SEM{s['first6_SEM']:.12f},прежний max(.0005,3SEM)={s['required_improvement']:.12f}.
Cold2{s['cold2_improvements']}, оба положительны. Общий originalobjective улучшился
во всех8. Lowmid300–800Гц L/R уменьшился примерно4.8→4.2дБ; оригинал по тому же
FFTметоду около1.0дБ, так что совпадение ещё НЕ достигнуто. Верхний баланс
сохранён внутри прежних guard1.5RMS/1.6absLR. Точность/веса/819edit не менялись.

Два свежих холодных настоящих каскада ZL воспроизвели WAV с остатком0, bytes
roundtripexact, совокупный PDC0/impulsefirst0. Это не ASIO/GUI тест.
Изменились только пять XMLполей третьего SideAllPass. Monoостаток до1.2e-7.
Сохранены все30training-native/primary и fresh-native/control/candidate WAV
в двухlosslessархивах, каждый членSHA256проверен; три выбранных WAV отдельно.
Невыбранные тренировочные DSPбуферы не выдаются за полный архив всех trialWAV.
Все рендеры настоящими DLL/VST3, новыйDivaVST/GUIэкспорт не заявляется: native
получены на сохранённом реальном Divaисточнике. Оригинал толькоанализ/A-B.

Принятие требует новой полной FLP/FST/VSTpreset/ZIP сборки и actualreplay/push.
До этого рабочаябаза не заменяется; source/primary/native неизменны. У owner
stereo-lowmid-SideAP-finite-20261025 есть N/zl-stereo-continuation.stop, удалять
только при безопасном возобновлении. Старые singleZLконтроллеры не запускать.
Свободно около400MiB только после удаления закрытых регенерируемыхdefault
WinVST3 buffers: сохранённые JSON/Python ссылки и активныеhosttags защищены,
все selectedWAV/presets/GUIinputs/источники сохранены. Scratchне объявленGitbacked.
Для Git нужны ls-treeOIDкарты, не bulkдвухдеревныйdiff/ls-tree--long.
Полного совпадения пока нет, продолжать после полного проверенного экспорта.
'''
  (dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n');p=PUBLIC/'README_RU.md';p.write_text('[Новая проверенная поправка низкой середины, все30WAV](lowmid-Side-phase-after-cohort15-20261025/README_RU.md).\n\n'+p.read_text());h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve robust low-mid Side AllPass improvement, fresh6/cold2 and all actual validation audio');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  archives=[]
  for p in dest.glob('*WAVs.tar.gz'):
   rel=p.relative_to(P).as_posix();blob=subprocess.check_output(['git','-C',str(P),'show',commit+':'+rel]);assert blob==p.read_bytes();archives.append(dict(path=rel,OID=git('rev-parse','HEAD:'+rel),SHA256=hashlib.sha256(blob).hexdigest()));git('update-index','--skip-worktree','--',rel);p.unlink();private=ROOT/p.name;assert private.read_bytes()==blob;private.unlink()
  temp=A/'current-public-structural-cache';temp.mkdir(exist_ok=False);out=temp/'structural.pack';ids=[l.split()[0]for l in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
  with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
  ph=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();target=P/'.git/objects/pack'/('pack-'+ph);Path(str(target)+'.promisor').touch()
  for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(target)+suffix);out.with_suffix(suffix).unlink()
  for row in archives:
   oid=row['OID'];loose=P/'.git/objects'/oid[:2]/oid[2:]
   if loose.exists():raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid and hashlib.sha256(raw.split(b'\0',1)[1]).hexdigest()==row['SHA256'];loose.unlink()
  subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL);assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all30_WAVs_remote_byte_verified=True,archives=archives,all_prior_kits_and_PC_GUI_preserved=True,only_published_archive_cache_offloaded=True,not_yet_adopted_into_complete_kit=True,reference_match_reached=False);(A/'LOWMID_RESEARCH_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
