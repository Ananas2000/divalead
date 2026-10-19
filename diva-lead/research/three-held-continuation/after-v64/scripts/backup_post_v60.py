from pathlib import Path
import json,hashlib,shutil,os
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');P=REPO/'diva-lead/research/three-held-continuation/after-v60';D=P/'continued-after-v60';D.mkdir(exist_ok=False);ignore=shutil.ignore_patterns('*.so','*.dll','*.exe','*.pyc','__pycache__')
for source,target in [('verified-phase-cont-0001-phase','accepted-phase1'),('verified-phase-cont-0002-phase','rejected-phase2'),('verified-cont-0004-gain','accepted-gain4')]:shutil.copytree(R/source,D/target,ignore=ignore)
for source,target in [('phase-continuation/round-0001-phase','phase1'),('phase-continuation/round-0002-phase','phase2'),('continuation/round-0004-gain','gain4')]:shutil.copytree(R/source,D/'rounds'/target,ignore=ignore)
for name in ['continue_three.py','continue_drift24.py','continue_phase18.py','three_candidate_decision.py','recover_current_three_parents.py','phase-controller-recovery.json','current-three-parent-handoff-state.json','reference-identity-current.json','public-v60-verification.json','verify_public_v60.py','deduplicate_immutable_audio.py']:
 if (R/name).exists():shutil.copyfile(R/name,D/name)
accepted=json.loads((D/'accepted-gain4/validation.json').read_text());assert accepted['all_chosen_three_guards_passed'] and accepted['original_three_held_MIDI_events_unchanged'];assert not (D/'rejected-phase2/validation.json').exists();assert not json.loads((D/'rounds/phase2/decision.json').read_text())['accepted']
ref=sf.read(REPO/'diva-lead/v60-wip/Diva_original_lead_reference.wav')[0];previous=sf.read(REPO/'diva-lead/v60-wip/Diva_Lead_v60_REFERENCE_EDIT.wav')[0];edit=sf.read(D/'accepted-gain4/REFERENCE_EDIT_WIP.wav')[0];sf.write(D/'CONTINUED_GAIN4_REFERENCE_EDIT_WIP.wav',edit*np.sqrt(np.mean(ref*ref)/np.mean(edit*edit)),48000,subtype='PCM_24');new=sf.read(D/'CONTINUED_GAIN4_REFERENCE_EDIT_WIP.wav')[0]
sf.write(D/'AB_REFERENCE_V60_CONTINUED_GAIN4_WIP.wav',np.concatenate([ref,np.zeros((24000,2)),previous,np.zeros((24000,2)),new]),48000,subtype='PCM_24')
(D/'README.md').write_text('''# Проверенное продолжение после полного v60

Тот же выбранный трёхнотный источник: пресет Diva, все 281 параметр, шесть входящих note-on за два прохода и внутренний ARP сохранены. Это последующий исследовательский бэкап, полный комплект v60 не перезаписан.

- `accepted-phase1/`: первый полностью проверенный фазовый шаг после v60, критерий тембра 0,843304059 → 0,843124196.
- `rejected-phase2/`: следующий численный фазовый вариант при свежем сравнении с оригиналом не улучшил свою основу. Он **отклонён**, итогового validation.json у него нет, 12 произвольных случаев для него не заявляются. Сам рендер и измерения сохранены для анализа.
- `accepted-gain4/`: новый полностью проверенный шаг по уровням гармоник, критерий тембра **0,842066966**, общий критерий **0,931111974**. Ошибка мощности24 гармоник 1,044348514 у v60 → 1,040058860, ошибка уровней тел срабатываний 0,210937291 → 0,208095733. Ошибка верхних гармоник немного выросла 1,280738463 → 1,281259736. Все исходные трёхнотные ограничения и независимые допуски сохранены.

[A/B оригинал → v60 → новое исследование](AB_REFERENCE_V60_CONTINUED_GAIN4_WIP.wav): **0 → 4,168 → 8,336 с**. [Отдельный обработанный WAV](CONTINUED_GAIN4_REFERENCE_EDIT_WIP.wav). В A/B один общий RMS-множитель на весь стереофрагмент каждого кандидата. Точное совпадение не достигнуто.

## Загрузить исследовательский WAV в FL Studio

Перетащи `CONTINUED_GAIN4_REFERENCE_EDIT_WIP.wav` в Playlist. Normalize Off, Pitch 0, Time stretching Resample, Time Reset; канал, Insert и Master 0 dB, панорама по центру, без дополнительной обработки. Finish уже записан в аудио. Этот последующий WAV содержит более новые коэффициенты, чем DLL v60; для живой игры текущий полный проверенный комплект — [v60](../../../../v60-wip/README.md). Нового полного релиза DLL здесь не заявляется.

## Продолжение после отклонения

Контроллер фазы останавливался на ожидаемом отказе по свежей метрике. Добавлен `three_candidate_decision.py`: распознаётся только подтверждённый отказ на этапе измеряемого качества, он сохраняется в decision.json, после чего подбор идёт дальше от лучшей доказанной основы. Сбои Diva, компилятора, хешей, независимой математики или причинности не превращаются в принятые результаты. Обработка проверена на настоящем отклонённом рендере; принятый совместный proof не классифицируется как отказ. Неизменность всех требований сохранена. Старый фазовый раунд и его файлы не удалялись, контроллер продолжил новый раунд.

Два других родителя, запущенные до этого исправления, получают такой же код при следующем старте; одноразовый помощник текущей среды восстановит их только при том же распознанном отказе качества. В новой среде сразу используется исправленный код. Текущее состояние процессов на дату бэкапа — в state-файлах; это не обещание работы после выключения среды. Автоматических Git-публикаций нет. GUI FL Studio и прослушивание ассистентом не выполнялись.
'''.replace('мощности24','мощности 24'))
p=P/'README.md';p.write_text(p.read_text()+'\nПоследующие принятые и отклонённые результаты, новый WAV и восстановление после отказа: [продолжение после v60](continued-after-v60/README.md).\n')
root=P.parent;current=json.loads((root/'CURRENT_THREE_NOTE_MODEL.json').read_text());current.update(research_validation='after-v60/continued-after-v60/accepted-gain4/validation.json',tone_score=accepted['tone_score'],score=accepted['score'],selected_complete_release_tone_score=0.843304058842936,selected_complete_release_score=0.9336925705440734,latest_research_is_not_a_new_complete_DLL_release=True)
(root/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
(P/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(P))+'\n' for p in sorted(P.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
print('POST_V60_ACCEPTED_AND_REJECTED_THREE_NOTE_RESULTS_BACKED_UP',sum(1 for p in D.rglob('*') if p.is_file()))
