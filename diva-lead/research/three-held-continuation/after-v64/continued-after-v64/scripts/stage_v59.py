from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parent;T=R/'v59-build';REPO=Path('/workspace/divalead');P=REPO/'diva-lead/research/three-held-continuation'
assert not P.exists();P.mkdir(parents=True)
ignore=shutil.ignore_patterns('*.so','*.exe','*.dll','*.pyc','__pycache__')
for name in ['baseline','verified-hf1','verified-initial-hf2','source-fine']:
 shutil.copytree(R/name,P/name,ignore=ignore)
for parent,child,target in [('numeric','complete-hf-baseline','HF-round1'),('numeric2','complete-hf-round2-basis','HF-round2'),('gain-numeric','complete-joint-round2-basis','gain-round1'),('gain-repair','complete-joint-round2-basis','gain-repair')]:
 shutil.copytree(R/parent/child,P/'numeric'/target,ignore=ignore)
for name in ['bootstrap_three.py','fit_three_hf.py','fit_three_hf_fixed_anchor.py','fit_three_gains.py','source_fine.py','source_wide.py','validate_three_model.py','continue_three.py','build_three_v59.py','write_v59_docs.py','finalize_v59.py','verify_zip_windows.py','stage_v59.py','fit-definition.json','HF-round2.log','gain-fit.log','gain-repair.log','source-fine.log','paused-old-sixteen-searches.json','BEST_ACTUAL.json','continuation-state.json','controller-launch.json']:
 if (R/name).exists():shutil.copyfile(R/name,P/name)
for name in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json','spectral-proof.json','release-proof.json','fresh-source-proof.json']:
 json.loads((T/name).read_text());shutil.copyfile(T/name,P/name)
S=json.loads((R/'verified-initial-hf2/validation.json').read_text());B=json.loads((R/'baseline/validation.json').read_text())
(P/'SOURCE_SCREEN_DECISION.json').write_text(json.dumps(dict(trials=25,adopted=False,reason='No convincing source improvement. Tiny KeyScale screening proposal has a worse standard score than the unchanged-source HF1 control and does not pass the stricter final crest cap. Screening feasibility is not final acceptance.',screening_guards_differ_from_DSP_acceptance_guards=True,source_changed_requires_new_own_NEW_base=True,selected_source_unchanged=True,match_reached=False),indent=2)+'\n')
(P/'README.md').write_text('''# Продолжение выбранного трёхнотного лида

Пользователь выбрал на слух `v58-wip/THREE_HELD_RESEARCH`. Эта оценка определяет новую основу. Основная ветка теперь сохраняет три удержания на фразу и внутренний ARP Diva. Прежний рейтинг 16-нотного варианта не является основанием возвращаться к нему.

Полный проверенный промежуточный комплект: [v59](../../v59-wip/README.md), [инструкция FL Studio](../../v59-wip/FL_STUDIO_RU.md). [A/B оригинал → выбранные три ноты v58 → v59](../../v59-wip/AB_REFERENCE_THREE58_V59_WIP.mp3): 0 / 4,168 / 8,336 с. Точного совпадения ещё нет.

## Что выполнено

1. `baseline/`: свежая Diva, точный сырой WAV, все 281 параметр и 12 входящих событий. Независимая NEW-база заново построена именно для этого источника, проверены Windows/native/полная цепочка. Старые 16-нотные базы не использованы.
2. `verified-hf1/`: первый полный подбор 100 существующих коэффициентов верхней обработки, подтверждён настоящим Windows-рендером, собственной NEW-базой и 12 произвольными сигналами на 4 частотах.
3. `source-fine/`: 25 настоящих проб Diva с теми же удержаниями, ARP и огибающими; PW, баланс и расстройка осцилляторов, фильтр и KeyScale. Изменение источника не принято. Здесь более свободные диагностические ограничения; `feasible` в скрининге не означает финальное принятие. Решение — `SOURCE_SCREEN_DECISION.json`.
4. `verified-initial-hf2/`: второй полностью подтверждённый шаг, источник и MIDI прежние. Именно этот снимок вошёл в v59.
5. `numeric/`: полные истории двух HF-подборов, отдельного подбора 93 усилений гармоник с замороженными фазами и попытки восстановить допустимость. Недопустимые точки не являются улучшениями. Отдельный gain-подбор не дал допустимого улучшения и не вошёл в v59.

Метрика верхних гармоник: 1,360101187 → 1,299492894 (ошибка меньше примерно на 4,46%). Общий прежний критерий: 0,950568429 → 0,941659039. Смешанные остальные изменения и все пределы приведены в [отчёте комплекта](../../v59-wip/COMPARISON_RU.md). Снижение ошибки не является процентом сходства. Подтверждения точного совпадения на слух нет.

Веса цели тембра сохранены в `fit-definition.json` и файлах истории. Метрические определения, нормирующие масштабы и референс прежние, цель подбора изменена явно. Пределы не накапливают ухудшения между раундами: опора — исходный выбранный трёхнотный вариант. Независимые допуски не менялись. Финальная проверка использует заново измеренные характеристики настоящего Windows-рендера.

## Воспроизводимость и продолжение

Самодостаточные переносимые проверки звука, MIDI, исходников и DLL находятся в полном комплекте v59. Скрипты этого исследования дополнительно сохраняют точные пути подготовленной облачной среды `/workspace/divalead-work/three-held-continuation`; они служат журналом и продолжением в подготовленном snapshot, а не универсальным установщиком. Исходный бинарный Diva пользователя не распространяется. Требуются Wine/MinGW и установленные Python-зависимости; пригодность цепочки подтверждена фактическими рендерами.

`continue_three.py --check-only` проверяет источник, хеши, собственную NEW-базу, выбранные пределы и 12 независимых случаев. Контроллер чередует HF и harmonic-gain, а каждый принятый результат требует свежей Diva/Windows/NEW-проверки. Он не пишет в Git автоматически. Записанный `continuation-state.json` — снимок состояния при бэкапе, не обещание вечной работы после остановки облачной машины. Старые 16-нотные контроллеры приостановлены, их файлы сохранены. Отдельный более широкий скрининг параметров настоящей Diva начат после сборки v59; его новые результаты не включены в этот снимок.

`ZIP-proof.json`, `clean-extraction-proof.json`, `clean-ZIP-Windows-proof.json` подтверждают чистую распаковку, независимый пересчёт и фактический запуск DLL из архива. GUI FL Studio и субъективное прослушивание здесь не выполнялись. MistaTowa исключён.
''')
D=REPO/'diva-lead/v59-wip';assert not D.exists();shutil.copytree(T/'v59-wip',D)
shutil.copyfile(T/'Diva_lead_v59_WIP_checkpoint.zip',REPO/'Diva_lead_v59_WIP_checkpoint.zip')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
release=dict(version='v59-wip',release_directory='diva-lead/v59-wip',ZIP='Diva_lead_v59_WIP_checkpoint.zip',ZIP_SHA256=sha(REPO/'Diva_lead_v59_WIP_checkpoint.zip'),FL_Studio_instructions='diva-lead/v59-wip/FL_STUDIO_RU.md',AB_WAV='diva-lead/v59-wip/AB_REFERENCE_V59_WIP.wav',AB_previous_current='diva-lead/v59-wip/AB_REFERENCE_THREE58_V59_WIP.wav',AB_MP3='diva-lead/v59-wip/AB_REFERENCE_THREE58_V59_WIP.mp3',DLL='diva-lead/v59-wip/Diva_Lead_Finish_v59_WIP_x64.dll',DLL_SHA256=sha(D/'Diva_Lead_Finish_v59_WIP_x64.dll'),source_preset='diva-lead/v59-wip/Diva_Lead_v59_WIP.h2p',MIDI='diva-lead/v59-wip/Diva_THREE_HELD_180BPM.mid',research_model='diva-lead/research/three-held-continuation',score=S['score'],tone_score=S['tone_score'],user_selected_three_baseline_score=B['score'],chosen_incoming_notes_per_phrase=3,chosen_note_on_count=6,Diva_ARP=True,source_preset_and_MIDI_unchanged_from_user_selected_three=True,VST2_x64=True,FL_GUI_tested=False,match_reached=False)
(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').write_text(json.dumps(release,indent=2)+'\n')
p=REPO/'README.md';s=p.read_text();start=s.index('**Архивный исследовательский этап:**');archive=s[start:];head='''# Diva: реконструкция лида для FL Studio

**Продолжаем трёхнотный вариант, выбранный пользователем на слух.** На фразу — три удержания MIDI 41 → 37 → 36; повторы и октавные движения создаёт внутренний ARP Diva. В новом основном комплекте сохранены именно его пресет и MIDI.

**[Diva Lead v59 WIP](diva-lead/v59-wip/README.md)** — [скачать полный ZIP](Diva_lead_v59_WIP_checkpoint.zip), [загрузить в FL Studio](diva-lead/v59-wip/FL_STUDIO_RU.md). Включены пресет, трёхнотный MIDI, Finish Windows x64 VST2, WAV, исходники и проверки.

**[Оригинал → выбранные три ноты v58 → v59](diva-lead/v59-wip/AB_REFERENCE_THREE58_V59_WIP.mp3)**: **0 → 4,168 → 8,336 с**. [WAV сравнения](diva-lead/v59-wip/AB_REFERENCE_THREE58_V59_WIP.wav), [отдельный готовый WAV v59](diva-lead/v59-wip/Diva_Lead_v59_REFERENCE_EDIT.wav).

В обработке уточнён верхний диапазон; ошибка верхних гармоник уменьшилась примерно на 4,46% относительно выбранных трёх нот. Изменение небольшое, точного совпадения ещё нет. [Все измерения и небольшие регрессии](diva-lead/v59-wip/COMPARISON_RU.md), [исследование и пробы](diva-lead/research/three-held-continuation/README.md). Настоящие рендеры Diva, Windows DLL, независимая цепочка именно трёхнотного источника и распакованный ZIP проверены. GUI FL Studio здесь не запускался.

Подбор продолжается от этой трёхнотной основы. [Предыдущий v58](diva-lead/v58-wip/README.md) и [v57](diva-lead/v57-wip/README.md) сохранены. Их 16-нотные варианты и старые рейтинги ниже — история исследования; текущий выбор пользователя и комплект указаны выше. MistaTowa к этому лиду не относится.

---

''';p.write_text(head+archive)
print('STAGED_V59_AND_THREE_NOTE_RESEARCH',sum(1 for p in P.rglob('*') if p.is_file()),flush=True)
