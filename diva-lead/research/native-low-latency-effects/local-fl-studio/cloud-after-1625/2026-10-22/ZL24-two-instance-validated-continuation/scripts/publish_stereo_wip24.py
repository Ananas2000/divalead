"""Publish the complete tested two-ZL WIP, preserving every preceding kit/PC tree."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo24_full_publication')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
build=read(A/'ZL24_FINAL_BUILD_COMPLETION.json');ROOT=Path(build['root']);archive=Path(build['ZIP']);assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256']
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish complete two-ZL stereo24 kit after real ZIP replay'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main')
  before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP24';shutil.copytree(ROOT,dest);shutil.copyfile(archive,dest/archive.name)
  research=PUBLIC/'ZL24-two-instance-validated-continuation';research.mkdir(exist_ok=False);scripts=research/'scripts';scripts.mkdir()
  for p in A.glob('*.py'):compile(p.read_text(),p.name,'exec');shutil.copyfile(p,scripts/p.name)
  for name in ['ZL24_BUILD_COMPLETION.json','ZL24_FINAL_BUILD_COMPLETION.json','STEREO_RESEARCH_PUBLICATION.json','PUBLISHED_STEREO_VALIDATION_BLOB_CACHE_EVICTION.json']:
   shutil.copyfile(A/name,research/name)
  guide='''# ZL24 STEREO WIP — полный промежуточный комплект

Уменьшен частотный перекос влево и улучшен прежний общий критерий по оригиналу.
Полного совпадения ещё нет. Три удерживаемые ноты41→37→36 на фразу, дважды;
исходная Diva281/native06/fine32/ARP/ADSR и маршруты сохранены.

- [Полный ZIP FL20/26, WAV, MIDI, h2p, FST, два VSTpreset и проверки](ZL-WIP24/Diva_ZL24_STEREO_WIP_complete.zip).
- [A/B на одном настоящем GUIвходе: оригинал0с → ZL23 с4,168с → новый с8,336с](ZL-WIP24/AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.mp3).
- [Тот же A/B lossless FLAC](ZL-WIP24/AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.flac).
- [Как загрузить проект либо два FST в существующий проект FL](ZL-WIP24/FL_STUDIO_RU.md).

На SUM теперь StereoShaper → основной ZL → дополнительный ZL STEREO FIX.
Используется тот же уже установленный ZL Equalizer2 v1.4.1. Дополнительный
ZL содержит два Side AllPass10000Гц/Q2 и2200Гц/Q4; все Gain0. Изменять порядок
или переносить эти полосы внутрь первого ZL без проверки нельзя.
Самостоятельная поправка сохраняет моно с численным остатком не более1.2e-7.
Оба ZL PDC0, суммарный импульсный добавленный сдвиг0. Это не ASIO замер.

Раньше последний GUI рендер давал около5.4дБ слева в5–10кГц. На trainingвходе
новый вариант даёт около0.9дБ в5–10кГц и0.3дБ в2–5кГц; улучшение стерео
сохранилось во всех16парных проверках. Общая громкость каналов отдельно не
нормализована: у оригинала сам бас асимметричен.

Новый primary основан на настоящем проверенном cloudcohort476. Полный прежний
GUI ZL23 сохранён.8архивных GUIвходов:6mean gain.001390340275,SEM.000197903804,
порог.000593711413,cold2+.000783634280/+.001749320855. Это старые GUIвходы из
предыдущей проверки другого кандидата, не свежий нетронутый GUIholdout.
Отдельно НОВЫЕ6nativeрендеров на сохранённом реальном Divaисточнике:
mean gain.001378303479,SEM.000162043355,порог.0005;2холодных nativeэкземпляра
+.001365899223/+.000652030788. Все положительны. Новые Diva VST/GUIэкспорты
не заявляются. Исходные веса/выравнивание/пороги не менялись.

Все12native states и FST payloads точны; MIDI/исходные маршруты сохранены.
Новый FL20 проект разобран, точные оба компонента найдены в FLP/FST/VSTpreset.
Распакованный ZIP проверен целиком по CRC/SHA; два холодных настоящих каскада
на том же nativeinput дали точный0остаток. Новый FLP пока не открыт в GUI на ПК.
Загрузка двух standalone FST в уже работающий GUIпроект описана в инструкции.
Прежние полные комплекты и последний GUIFL26 tree сохранены.

[Все52контрольных/source/candidate WAV и исследования](stereo-repair-GUI-native-20261024/README_RU.md)
сохранены отдельно в losslessархивах. Непринятые Mid+Side варианты и дополнительные
primaryphase пробы не поставлены в эту сборку. Применён только зафиксированный
кандидат из FROZEN_BEFORE_VALIDATION. MistaTowa не используется, оригинал служит
только для анализа/A-B. Это WIP, остаются различия тембра/стерео.

Для продолжения требуется TWO-ZL-aware matcher/builder; старыйsingleZL код
потеряет второй эффект. Не запускать прежний continuous65/watcher поверх этой
базы. Следующий поиск должен сохранять исправление баланса, исходный objective
иfresh6/cold2, без вопросов по каждому варианту и без объявления полного совпадения.
'''
  (PUBLIC/'ZL24_CONTINUATION_RU.md').write_text(guide);(research/'README_RU.md').write_text(guide.replace('](ZL-WIP24/','](../ZL-WIP24/').replace('](stereo-repair-GUI-native-20261024/','](../stereo-repair-GUI-native-20261024/'))
  prior=PUBLIC/'stereo-repair-GUI-native-20261024/README_RU.md';prior.write_text(prior.read_text().replace('../../../../2026-10-24/README_RU.md','../../../2026-10-24/README_RU.md'));hashes=read(prior.parent/'FILE_SHA256.json');hashes['README_RU.md']=hashlib.sha256(prior.read_bytes()).hexdigest();(prior.parent/'FILE_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text('[ZL24 STEREO: новый полный ZIP, A/B и инструкция](ZL24_CONTINUATION_RU.md).\n\n'+p.read_text())
  header='''BEGIN_LATEST_ZL24_TWO_INSTANCE_STEREO_20261024
LATEST COMPLETE USERKIT ZL-WIP24/Diva_ZL24_STEREO_WIP_complete.zip. Read ZL24_CONTINUATION_RU.md and ZL24-two-instance-validated-continuation/README_RU.md. TWO-ZL topology REQUIRED: native12/base06/fine32 -> primary realcloud476 -> POST Side-only AllPass10000Hz/Q2 +2200Hz/Q4. Exactthreeheldnotes41->37->36 twice/internalARP/sourceDiva281/ADSR/native12states/routes unchanged. User NEW explicit left-ear complaint overrides old local no-LR-rebalance preference.5-10kHz~+5.4dBLeft reduced~+.9dB,2-5kHz~+.3dB; postonly mono residual<=1.2e-7. Fixedoriginalcriterion gain ARCHIVALGUI first6 .001390340275 > max(.0005,3SEM.000593711413), cold2+.000783634280/+.001749320855; these GUIinputs previouslyusedforothercandidate, NOTnewGUI/untouchedfinalholdout. NEWnative6 onpreservedactualDiva source gain.001378303479 >max(.0005,3SEM.000486130065), nativecold2+.001365899223/+.000652030788. Both originalscore/stereo improve all16pairs. No newDiva VST or newGUIexports claimed. Actual FL20newproject/FST/VSTpreset serialization, native12bytes/MIDI/routes and independentZIPCRC/SHA/2coldactualZLcascadereplay0 verified. CombinedZLPDC0/impulse0, no ASIO/wholeDAW0 claim. FullmatchFALSE, GUInewproject openingpending. All52validationWAV/source retained publiclossless in stereo-repair-GUI-native-20261024. Old kits and PC2026-10-24GUI tree unchanged. Oldsingle65matcher/publisher CANNOT handle POST and must remainstopped; new matcher must load BOTHstates and enforce additional stereo preservation, unchangedobjective/acceptancegates. No MistaTowa/referenceaudio in synthesis/pertrialquestions/fullmatchclaim. PublicGitpromisorcache has expected oldblob holes, allrefs/privateoriginalsource48 retained; avoidbulk two-treegitdiff/ls-tree--long. Back up usefulfinishedstages progressively, APIquotapercentage unavailable.
END_LATEST_ZL24_TWO_INSTANCE_STEREO_20261024

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md')
  packs=set((P/'.git/objects/pack').glob('*.promisor'));h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete ZL24 stereo WIP with two actual zero-PDC ZL instances and verified ZIP replay');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);assert set((P/'.git/objects/pack').glob('*.promisor'))==packs
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_GUI_INPUT_ZL23_ZL24_STEREO_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP24',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='06',requires_two_ZL_instances=True,original_objective_export_mean=build['mean_new_native_original_objective_with_regularizer'],ZIP_replay_fixed_native_input_max_abs_errors=[0.,0.],ZIP_replay_is_two_cold_instances_not_six_new_native_renders=True,HTTP_checks=checks,old_full_kit_and_PC_GUI_tree_OIDs_preserved=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (A/'ZL24_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
