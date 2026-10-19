from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';P=ROOT/'after-v61';T=R/'v61-build';D=REPO/'diva-lead/v61-wip'
assert json.loads((T/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
assert json.loads((T/'ZIP-proof.json').read_text())['clean_extraction_release_replay_passed']
P.mkdir(exist_ok=False);assert not D.exists()
ignore=shutil.ignore_patterns('*.so','*.dll','*.exe','*.pyc','__pycache__')
for index in [5,7,9]:
 source=R/f'verified-cont-{index:04d}-hf';assert (source/'validation.json').exists();shutil.copytree(source,P/f'accepted-HF{index}',ignore=ignore)
for index,kind in [(5,'hf'),(6,'gain'),(7,'hf'),(8,'gain'),(9,'hf'),(10,'gain')]:
 source=R/'continuation'/f'round-{index:04d}-{kind}'
 if source.exists():shutil.copytree(source,P/'rounds'/source.name,ignore=ignore)
for name in ['build_three_v61.py','write_v61_docs.py','finalize_v61.py','verify_zip_windows_v61.py','stage_v61.py','continue_three.py','continue_phase18.py','continue_drift24.py','fit_three_hf_fixed_anchor.py','fit_three_gains.py','fit_three_phase18.py','validate_three_model.py','validate_three_source_model.py','three_candidate_decision.py','check_reference_identity.py','reference-identity-current.json','apply_historical_immutable_dedup.py','historical-immutable-audio-dedup.json','continuation-state.json','phase-continuation-state.json','drift24-continuation-state.json']:
 if (R/name).exists():shutil.copyfile(R/name,P/name)
for name in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json','spectral-proof.json','release-proof.json','fresh-source-proof.json']:
 json.loads((T/name).read_text());shutil.copyfile(T/name,P/name)
S=json.loads((R/'verified-cont-0009-hf/validation.json').read_text());old=json.loads((REPO/'diva-lead/v60-wip/verification/selected_validation.json').read_text())
(P/'README.md').write_text('''# v61: продолжение исключительно трёхнотной основы

[Полный комплект v61](../../../v61-wip/README.md), [инструкция FL Studio](../../../v61-wip/FL_STUDIO_RU.md), [оригинал → v60 → v61](../../../v61-wip/AB_REFERENCE_V60_V61_WIP.mp3): **0 / 4,168 / 8,336 с**. Все сравнения направлены на исходный WAV пользователя. Предыдущая версия — контроль прогресса. Точного совпадения пока нет.

После опубликованного gain4 сохранены три полностью проверенных шага верхней обработки: `accepted-HF5`, `accepted-HF7`, `accepted-HF9`. В v61 включён **HF9**, лучший из этих завершённых proof. Пресет физической Diva, все 281 параметр, сырой источник и 12 MIDI-событий остались точной копией выбранной пользователем трёхнотной основы. Три удержания на фразу, внутренний ARP On; дополнительных MIDI-нот нет. Уточнены существующие коэффициенты Finish; новые состояния DSP и проигрывание сэмпла оригинала не добавлены.

Критерий тембра v60 → v61: **0,843304059 → 0,838107207**; общий прежний критерий **0,933692571 → 0,928066435**. Ошибка верхних гармоник **1,280738463 → 1,261202429**, межгармонической энергии **1,961901713 → 1,952728588**. Это ошибки, не проценты сходства на слух. Небольшие регрессии и все измерения приведены в [COMPARISON_RU.md](../../../v61-wip/COMPARISON_RU.md).

Каждый accepted-HF содержит настоящий новый запуск Diva, Windows/native, полный независимый replay собственной трёхнотной NEW-базы, спектральный fixture и 12 произвольных причинных входов на четырёх sample rate. validation.json записан только после всех 12 случаев. Пределы относительно первоначальной выбранной трёхнотной основы, crest, непрерывная положительность gain и допуски проверок не ослаблялись. Неудачные численные центры в `rounds/` не названы улучшениями. Сохранены полные истории, начальные модели, проверенные seed/cache расчёты и решения. Достижение бюджета итераций не является заявлением о сходимости.

У нового Finish отдельный ID 0x444c3631 и image base 0x361610000. Подтверждены точный рендер выбранного HF9 при параметрах DLL по умолчанию, блоки 47/127/512/2048, программа FXP, состояние, PDC и четыре sample rate. Сборка DLL повторена побайтово с тем же basename. Пакет проверен после чистой распаковки; **реальная DLL из ZIP** воспроизводит полный готовый WAV семпл в семпл. GUI FL Studio и прослушивание ассистентом здесь не выполнялись.

Дальнейшие HF/gain и фазовые подборы продолжают ту же архитектуру. Отдельная семья Drift24 также использует три удержания и собственную подходящую NEW-базу; её нельзя смешивать с исходным сырьём. Её численные показатели пока уступают выбранной основной семье, в v61 она не включена. State-файлы — снимки при бэкапе, не обещание работы после остановки машины. Контроллеры не пишут в Git автоматически.

Для сохранения места 647 идентичных WAV из завершённых исторических proof теперь разделяют inode. Их пути и каждый байт сохранены и проверены SHA256. Это не изменение звука; перед редактированием таких неизменяемых файлов требуется отдельная копия. Ledger и использованный скрипт сохранены. Критические runtime-библиотеки и fixtures не переносились во временное хранилище.

MistaTowa исключён. Старые полные комплекты и ZIP, включая v60, сохранены без изменений.
''')
shutil.copytree(T/'v61-wip',D);shutil.copyfile(T/'Diva_lead_v61_WIP_checkpoint.zip',REPO/'Diva_lead_v61_WIP_checkpoint.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
for key,value in list(release.items()):
 if isinstance(value,str):release[key]=value.replace('v60','v61').replace('V60','V61').replace('AB_REFERENCE_V59_V61','AB_REFERENCE_V60_V61')
release.update(ZIP_SHA256=sha(REPO/'Diva_lead_v61_WIP_checkpoint.zip'),DLL_SHA256=sha(D/'Diva_Lead_Finish_v61_WIP_x64.dll'),score=S['score'],tone_score=S['tone_score'],research_model='diva-lead/research/three-held-continuation/after-v61',only_three_held_current_work=True)
(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').write_text(json.dumps(release,indent=2)+'\n')
current=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());current.update(selected_complete_release='diva-lead/v61-wip',research_validation='after-v61/accepted-HF9/validation.json',tone_score=S['tone_score'],score=S['score'],selected_complete_release_tone_score=S['tone_score'],selected_complete_release_score=S['score'],latest_research_is_not_a_new_complete_DLL_release=False,match_reached=False)
(ROOT/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
p=ROOT/'README.md';s=p.read_text();start=s.index('Полный проверенный промежуточный комплект:');end=s.index('\n\n',start)
s=s[:start]+'''Полный проверенный промежуточный комплект: [v61](../../v61-wip/README.md), [инструкция FL Studio](../../v61-wip/FL_STUDIO_RU.md). [A/B оригинал → v60 → v61](../../v61-wip/AB_REFERENCE_V60_V61_WIP.mp3): 0 / 4,168 / 8,336 с. [Новые HF-подборы и полные проверки](after-v61/README.md), [текущий трёхнотный выбор](CURRENT_THREE_NOTE_MODEL.json). Точного совпадения ещё нет.'''+s[end:];p.write_text(s)
p=REPO/'README.md';s=p.read_text();before,archive=s.split('**Архивный исследовательский этап:**',1)
before=before.replace('v60','v61').replace('V60','V61').replace('AB_REFERENCE_V59_V61','AB_REFERENCE_V60_V61').replace('Оригинал → v59 → v61','Оригинал → v60 → v61').replace('[Предыдущий полный v59](diva-lead/v59-wip/README.md)','[Предыдущий полный v60](diva-lead/v60-wip/README.md)')
before=before.replace('В Finish уточнены уровни и фазы гармоник.','В Finish продолжен подбор верхнего диапазона и уровней гармоник.').replace('Ошибки верхних гармоник, фазового профиля и уровней срабатываний уменьшились','Ошибки верхних гармоник, межгармонической энергии и уровней срабатываний уменьшились')
p.write_text(before+'**Архивный исследовательский этап:**'+archive)
(P/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n' for p in sorted(P.rglob('*')) if p.is_file()))
print('V61_FULL_KIT_AND_RESEARCH_STAGED',sum(1 for p in P.rglob('*') if p.is_file()),flush=True)
