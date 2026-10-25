"""Publish the verified complete WIP25; preserve old full kits and actual PC work."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil
A=Path(__file__).resolve().parent
D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo25_complete_publication')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']]
git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
build=read(A/'ZL25_BUILD_COMPLETION.json');ROOT=Path(build['root']);archive=Path(build['ZIP'])
assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256']
assert build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.]
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish full tested two-ZL WIP25 with low-mid Side phase improvement'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main')
  before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  old24=git('rev-parse','HEAD:'+str((PUBLIC/'ZL-WIP24').relative_to(P)))
  dest=PUBLIC/'ZL-WIP25';shutil.copytree(ROOT,dest);shutil.copyfile(archive,dest/archive.name)
  research=PUBLIC/'ZL25-complete-kit-validation-20261025';research.mkdir();scripts=research/'scripts';scripts.mkdir()
  for p in A.glob('*.py'):compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['ZL25_BUILD_COMPLETION.json','LOWMID_RESEARCH_PUBLICATION.json']:
   shutil.copyfile(A/name,research/name)
  guide='''# ZL25 STEREO WIP — полный комплект, три удерживаемые ноты

Следующий проверенный промежуточный результат. Полного совпадения нет.

- [Полный ZIP FL Studio20/26, FLP/WAV/MIDI/h2p/FST/VSTpreset](ZL-WIP25/Diva_ZL25_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → предыдущий принятый cohort15 с4,168с → ZL25 с8,336с](ZL-WIP25/AB_ORIGINAL_BEST15_ZL25_WIP.mp3).
- [Тот же A/B без потерь](ZL-WIP25/AB_ORIGINAL_BEST15_ZL25_WIP.flac).
- [Инструкция для FL Studio и загрузки двух FST в текущий проект](ZL-WIP25/FL_STUDIO_RU.md).
- [Результирующий рабочий WAV](ZL-WIP25/ZL25_STEREO_FULL_WIP.wav).

Используется тот же официальный бесплатный ZL Equalizer2v1.4.1. SUM:
StereoShaper → PRIMARY → STEREO FIX. PRIMARY взят из принятого cohort15;
во втором ZL сохранены Side AllPass10000Гц/Q2 и2200Гц/Q4 и добавлен895.8Гц/Q13.84.
Это три полосы внутри второго ZL, не третий экземпляр плагина. Оба ZL
MinimumPhase/Lookahead0/AutoGainOFF, Mix100%; новые эффекты скачивать не требуется.

По той же FFT диагностике перекос300–800Гц уменьшен примерно4.8→4.2дБ;
у оригинала около1дБ, поэтому остаток ещё есть. Верх сохранил исправленный
баланс. Моно после Side-only поправки сохранено с остатком до1.2e-7.
Не делалось отдельного нормирования каналов. Бас оригинала асимметричен.

Кандидат зафиксирован до8новых тестов. Fresh6mean improvement.001388351833,
SEM.000015055695, прежний порог.0005; cold2+.001292979650/+.001385139518.
Все8положительны. Исходный objective/веса/выравнивание/пороги не менялись.
[Все30training/validationWAV и воспроизводимое исследование](lowmid-Side-phase-after-cohort15-20261025/README_RU.md).

Настоящие nativeDLL и два официальных ZLVST3 на сохранённом реальном
Divaисточнике. Новые Divaэкземпляры или GUIэкспорт наПК не заявляются.
Сохранены Diva281/native06/fine32/ADSR/ARP/MIDI и маршруты. Входящие три
удерживаемые ноты41→37→36 на фразу дважды; движение вверх делает ARP.
Проверены оба savedcomponent в FLP/FST/VSTpreset,12native statebytes,
CRC/SHA всех файлов ZIP и две холодные реальные ZLцепочки из распакованного
комплекта: остаток0/0. Declared ZLPDC0, добавочный импульсный сдвиг0;
это не измерение ASIO или всей DAW. Открытие нового FLP в реальном GUI ещё
не проверено. Предыдущие полные комплекты и последний PCGUIпроект сохранены.
Оригинал используется только для анализа/A-B, MistaTowa не используется.

Для продолжения требуется TWO-ZL matcher: фиксировать новый POST с тремя
полосами и искать PRIMARY, сохраняя native06 и исправленный стереобаланс.
Старые single-ZL matcher/watcher остаются выключены. Это WIP, поиск продолжается.
'''
  (PUBLIC/'ZL25_CONTINUATION_RU.md').write_text(guide)
  (research/'README_RU.md').write_text(guide.replace('](ZL-WIP25/','](../ZL-WIP25/').replace('](lowmid-Side-phase-','](../lowmid-Side-phase-'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL25: полный трёхнотный WIP, исправление низкой середины, A/B и инструкция](ZL25_CONTINUATION_RU.md).\n\n'+p.read_text())
  header='''BEGIN_LATEST_ZL25_STEREO_20261025
Latest complete fullkit ZL-WIP25/Diva_ZL25_STEREO_WIP_complete.zip, read ZL25_CONTINUATION_RU.md. TWO actual ZL instances required: native12/base06/fine32 -> accepted primarycohort15 -> POST SIDE ALLPASS10000Hz/Q2+2200Hz/Q4+895.8Hz/Q13.84. THREEbands insecondZL, not3instances. Lowmid300-800Hz L/R~4.8to4.2dB vsoriginal~1dB, residualremains, upperrepairpreserved. Originalcriterion fresh6gain.001388351833 SEM.000015055695 threshold.0005; twoindependentcoldnativegain+.001292979650/+.001385139518. NewnativeonpreservedactualDivasource; no newDivaVST/GUIexportsclaimed. All30training/validationWAVremote in lowmid-Side-phase-after-cohort15-20261025. CompleteFL20serialization andtwoactualcoldZLreplays afterZIPextract botherror0; GUIopeningnewFLPpending, fullsoundmatchFALSE. ExactsourceDiva281/native06/fine32/ARP/ADSR/3longincomingnotes41-37-36twice/routesunchanged. Preservealloldfullkits/PC2026-10-24GUI/privateoriginalsource48. OldsingleZLmatcher/watcherretired. RuntimepostmustfollowadoptedBESTpost, neverhardcodeold2bandpost. Originalobjective/tolerances/acceptancegatesunchanged. No MistaTowa/referenceaudioinsynthesis/pertrialquestions. StandardpromisorGitcacheexpectedoldholes; no bulk2treegitdiff/ls-tree--long. Usefulcompletedstagesbackupprogressively,APIquotapercentageunavailable.
END_LATEST_ZL25_STEREO_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md')
  h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
  git('commit','-m','Publish complete ZL25 three-note stereo WIP with verified low-mid repair and cold ZIP replay');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;assert git('rev-parse','HEAD:'+str((PUBLIC/'ZL-WIP24').relative_to(P)))==old24
  h['push_and_confirm'](commit);checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_BEST15_ZL25_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP25',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='06',requires_two_ZL_instances=True,post_Side_AllPasses=build['post_Side_AllPasses'],original_objective_export_mean=build['original_objective_export_mean'],ZIP_replay_fixed_native_input_max_abs_errors=[0.,0.],ZIP_replay_is_two_cold_ZL_chains_not_six_new_native_renders=True,HTTP_checks=checks,old_full_kits_and_PC_GUI_preserved=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (A/'ZL25_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
