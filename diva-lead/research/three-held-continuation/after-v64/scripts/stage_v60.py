from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';P=ROOT/'after-v60';P.mkdir(exist_ok=False);T=R/'v60-build';D=REPO/'diva-lead/v60-wip'
ignore=shutil.ignore_patterns('*.so','*.dll','*.exe','*.pyc','__pycache__')
for source,target in [('verified-phase18-0001','phase18-proof'),('verified-gain-interior-0001','gain-proof'),('verified-gain-phase-coupled-0001','coupled-proof'),('verified-cont-0003-hf','parallel-HF3-proof'),('drift24-verified-cont-0001-hf','alternate-three-source-HF1-proof')]:
 if (R/source/'validation.json').exists():shutil.copytree(R/source,P/target,ignore=ignore)
for source,target in [('phase18-numeric/complete-phase-phase18-basis','phase18'),('gain-boundary-repair/complete-joint-phase18-basis','gain-boundary-repair'),('gain-interior-repair/complete-joint-phase18-basis','gain-interior-repair'),('gain-phase-coupled-preview','coupled-fractions'),('continuation/round-0002-gain/numeric/complete-joint-basis','gain-infeasible-origin'),('continuation/round-0003-hf/numeric/complete-hf-basis','parallel-HF3'),('drift24-continuation/round-0001-hf/numeric/complete-hf-basis','alternate-three-HF1')]:
 if (R/source).exists():shutil.copytree(R/source,P/'numeric'/target,ignore=ignore)
for name in ['check_reference_identity.py','reference-identity-current.json','prepare_phase18.py','fit_three_phase18.py','run_phase18.py','continue_phase18.py','phase18-check.log','phase18-fit.log','phase18-validation.log','phase18-state.json','repair_gain_boundary.py','gain-boundary-repair.log','interior_gain_repair.py','gain-interior-repair.log','gain-interior-proof.log','combine_gain_phase.py','gain-phase-coupled-preview.log','gain-phase-coupled-proof.log','validate_three_model.py','validate_three_source_model.py','build_three_v60.py','write_v60_docs.py','finish_v60_probe.py','finalize_v60.py','verify_zip_windows_v60.py','stage_v60.py','continuation-state.json','phase-continuation-state.json','phase-controller-launch.json','drift24-continuation-state.json']:
 if (R/name).exists():shutil.copyfile(R/name,P/name)
for name in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json','spectral-proof.json','release-proof.json','fresh-source-proof.json']:
 json.loads((T/name).read_text());shutil.copyfile(T/name,P/name)
S=json.loads((R/'verified-gain-phase-coupled-0001/validation.json').read_text());assert S['all_chosen_three_guards_passed'] and S['original_three_held_MIDI_events_unchanged']
(P/'README.md').write_text('''# v60: исключительно выбранные три удержания

Пользователь подтвердил: работаем только с предпочитаемым трёхнотным вариантом. Все новые исследования здесь сохраняют эту архитектуру. Цель сравнения заново проверена семпл в семпл с загруженным WAV-оригиналом, а не предыдущей версией: `reference-identity-current.json` и `check_reference_identity.py`.

**[Полный комплект v60](../../../v60-wip/README.md)**, [инструкция FL Studio](../../../v60-wip/FL_STUDIO_RU.md), [оригинал → v59 → v60](../../../v60-wip/AB_REFERENCE_V59_V60_WIP.mp3): 0 / 4,168 / 8,336 с. Точного совпадения ещё нет.

## Что проверено

- `phase18-proof/`: 18 существующих общих фазовых значений. Источник, ARP, огибающие и входящие 12 MIDI-событий прежние. Свежая полная проверка показала уменьшение ошибки фазового профиля гармоник; выбор не основан на заявлении о прослушивании.
- `gain-proof/`: существующие уровни гармоник. Исходное численное предложение немного нарушало предел полного спектра. В `numeric/gain-boundary-repair/` и `numeric/gain-interior-repair/` сохранены исправления нескольких существующих коэффициентов, которые вернули предложение в **те же** пределы, с дополнительным внутренним запасом для округления. Ограничения и допуски не ослаблялись. Только после этого выполнен полный actual proof.
- `coupled-proof/`: уровни и фазы объединены, проверены доли фазовой коррекции, затем сделан новый полный рендер выбранного совместного варианта. Именно он вошёл в v60. Его точный источник по-прежнему совпадает с выбранным пользователем трёхнотным пресетом, всеми281 параметром, сырьём и всеми12 событиями.
- `parallel-HF3-proof/` и `alternate-three-source-HF1-proof/`: завершённые параллельные проверки, которые уступают выбранному совместному варианту по критерию тембра. Вторая использует ранее проверенный Drift24-источник с собственной NEW-базой; её сырьё не смешивается с основной семьёй. Обе остаются трёхнотными.

Общий критерий v59 → v60: **0,941659039 → 0,933692571**. Критерий тембра: **0,848973399 → 0,843304059**. Мощность24 гармоник 1,049734195 → 1,044348514; верхние гармоники 1,299492894 → 1,280738463; фазовый профиль 0,434459357 → 0,423706734; уровни тел срабатываний 0,216428002 → 0,210937291. Небольшие регрессии остальных измерений и фиксированные пределы приведены в [отчёте](../../../v60-wip/COMPARISON_RU.md). Это ошибки, а не процент сходства на слух.

Во всех трёх принятых исследованиях выполнены свежая Diva, все281 параметр и12 событий, Windows/native, полная независимая цепочка своей подходящей NEW-базы, отдельный спектральный fixture и12 произвольных причинных входов на4частотах. Пресет физической Diva не изменился, поэтому подходит та же собственная база исходного выбранного трёхнотного источника. Неисполненные численные варианты не названы улучшениями. Полные истории, пробы и исполнявшиеся скрипты сохранены в numeric и корне этой папки. Некоторые оптимизаторы достигли бюджета итераций; это не заявление о сходимости или совпадении.

## Продолжение

Основной HF/gain-контроллер принял совместную доказанную основу и продолжил следующий раунд. Отдельный `continue_phase18.py` теперь продолжает 18 фазовых коэффициентов той же основной семьи; его нулевой и два ненулевых расчёта проверены полной независимой моделью. Оба вида обработок сохраняют принятые фазовые коэффициенты между раундами. Независимый трёхнотный Drift24-контроллер продолжает свою отдельную семью.

`validate_three_model.py` и `validate_three_source_model.py` сохраняют все три фазовых массива и соответствующие заголовки C. Итоговый validation.json появляется только после завершения всех12 случаев, чтобы другой процесс не принял незаконченный proof. Для основной семьи всегда проверяется исходный выбранный пресет/raw/all281 и собственная NEW-база, для Drift24 — точные файлы его семьи. Метрики и crest привязаны к исходному пользовательскому трёхнотному варианту, без накопления ухудшений через перенос опоры.

Контроллеры не публикуют Git автоматически. State-файлы здесь — снимки при бэкапе, а не обещание работы процессов после остановки облачной среды. Облачные скрипты используют сохранённую структуру /workspace; переносимые проверки полного пакета находятся в v60. GUI FL Studio и прослушивание ассистентом здесь не выполнялись. MistaTowa исключён.
''')
for p in P.glob('*.md'):
 s=p.read_text()
 for a,b in {'всеми281':'всеми 281','всеми12':'всеми 12','Мощность24':'Мощность 24','все281':'все 281','и12':'и 12','на4частотах':'на 4 частотах','всех12':'всех 12'}.items():s=s.replace(a,b)
 p.write_text(s)
assert not D.exists();shutil.copytree(T/'v60-wip',D);shutil.copyfile(T/'Diva_lead_v60_WIP_checkpoint.zip',REPO/'Diva_lead_v60_WIP_checkpoint.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
for key,value in list(release.items()):
 if isinstance(value,str):release[key]=value.replace('v59','v60').replace('V59','V60').replace('AB_REFERENCE_THREE58_V60_WIP','AB_REFERENCE_V59_V60_WIP')
release.update(ZIP_SHA256=sha(REPO/'Diva_lead_v60_WIP_checkpoint.zip'),DLL_SHA256=sha(D/'Diva_Lead_Finish_v60_WIP_x64.dll'),score=S['score'],tone_score=S['tone_score'],research_model='diva-lead/research/three-held-continuation/after-v60',only_three_held_current_work=True,reference_decoded_float64_SHA256='450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c')
(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').write_text(json.dumps(release,indent=2)+'\n')
current=dict(architecture='three-held-notes',exclusive_user_choice=True,incoming_notes_per_phrase=3,incoming_note_on_count=6,Diva_ARP=True,source_preset_SHA256=sha(D/'Diva_Lead_v60_WIP.h2p'),source_decoded_float32_SHA256=S['source_render_history']['source_samples_SHA256'],selected_complete_release='diva-lead/v60-wip',research_validation='after-v60/coupled-proof/validation.json',tone_score=S['tone_score'],score=S['score'],match_reached=False,reference_decoded_float64_SHA256=release['reference_decoded_float64_SHA256'])
(ROOT/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
p=ROOT/'README.md';s=p.read_text();s=s.replace('Полный проверенный промежуточный комплект: [v59](../../v59-wip/README.md), [инструкция FL Studio](../../v59-wip/FL_STUDIO_RU.md). [A/B оригинал → выбранные три ноты v58 → v59](../../v59-wip/AB_REFERENCE_THREE58_V59_WIP.mp3): 0 / 4,168 / 8,336 с.','Полный проверенный промежуточный комплект: [v60](../../v60-wip/README.md), [инструкция FL Studio](../../v60-wip/FL_STUDIO_RU.md). [A/B оригинал → v59 → v60](../../v60-wip/AB_REFERENCE_V59_V60_WIP.mp3): 0 / 4,168 / 8,336 с. [Новые уровни/фазы и полные проверки](after-v60/README.md), [текущий трёхнотный выбор](CURRENT_THREE_NOTE_MODEL.json).')
p.write_text(s)
p=REPO/'README.md';s=p.read_text();archive=s[s.index('**Архивный исследовательский этап:**'):]
p.write_text('''# Diva: реконструкция лида для FL Studio

**Работаем исключительно с трёхнотным вариантом, выбранным пользователем.** На фразу — три удержания MIDI 41 → 37 → 36; повторы и октавные движения создаёт внутренний ARP Diva. Сам пресет, все281 параметр и входящие ноты сохранены.

**[Diva Lead v60 WIP](diva-lead/v60-wip/README.md)** — [скачать полный ZIP](Diva_lead_v60_WIP_checkpoint.zip), [инструкция для FL Studio](diva-lead/v60-wip/FL_STUDIO_RU.md). Пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и проверки включены.

**[Оригинал → v59 → v60](diva-lead/v60-wip/AB_REFERENCE_V59_V60_WIP.mp3)**: **0 → 4,168 → 8,336 с**. [WAV сравнения](diva-lead/v60-wip/AB_REFERENCE_V59_V60_WIP.wav), [отдельный обработанный WAV v60](diva-lead/v60-wip/Diva_Lead_v60_REFERENCE_EDIT.wav).

В Finish уточнены уровни и фазы гармоник. Сравнение выполнено с исходным WAV пользователя, идентичность цели подтверждена по семплам. Ошибки верхних гармоник, фазового профиля и уровней срабатываний уменьшились; остальные изменения — в [отчёте](diva-lead/v60-wip/COMPARISON_RU.md). Точное совпадение ещё не достигнуто, подбор продолжается.

Свежие Diva/Windows-рендеры, независимая цепочка подходящей трёхнотной NEW-базы, причинные проверки на четырёх sample rate, чистый ZIP и DLL из него проверены. [Исследование и все новые результаты](diva-lead/research/three-held-continuation/after-v60/README.md), [текущая трёхнотная основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json). GUI FL Studio и прослушивание ассистентом здесь не выполнялись.

[Предыдущий полный v59](diva-lead/v59-wip/README.md), [v58](diva-lead/v58-wip/README.md) и [v57](diva-lead/v57-wip/README.md) сохранены. Старые 16-нотные версии и рейтинги ниже относятся к истории. MistaTowa к этому лиду не относится.

---

'''.replace('все281','все 281')+archive)
(P/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(P))+'\n' for p in sorted(P.rglob('*')) if p.is_file()))
print('STAGED_FULL_V60_AND_NEW_THREE_NOTE_PROOFS',sum(1 for p in P.rglob('*') if p.is_file()),flush=True)
