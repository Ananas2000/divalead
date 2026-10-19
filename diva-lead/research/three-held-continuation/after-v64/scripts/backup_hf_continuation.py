from pathlib import Path
import shutil,json,hashlib
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');P=REPO/'diva-lead/research/three-held-continuation/after-v59';D=P/'hf-continuation-0001';assert not D.exists()
S=R/'verified-cont-0001-hf';V=json.loads((S/'validation.json').read_text());assert V['all_chosen_three_guards_passed'] and V['same_user_selected_Diva_preset_raw_and_all281']
shutil.copytree(S,D,ignore=shutil.ignore_patterns('*.dll','*.so','*.exe','*.pyc','__pycache__'))
shutil.copytree(R/'continuation/round-0001-hf/numeric/complete-hf-basis',D/'numeric',ignore=shutil.ignore_patterns('*.dll','*.so','*.exe','*.pyc','__pycache__'))
for name in ['fit.log','decision.json','validation.log']:shutil.copyfile(R/'continuation/round-0001-hf'/name,D/name)
ref,sr=sf.read(REPO/'diva-lead/v59-wip/Diva_original_lead_reference.wav');previous,pr=sf.read(REPO/'diva-lead/v59-wip/Diva_Lead_v59_REFERENCE_EDIT.wav');edit,er=sf.read(S/'REFERENCE_EDIT_WIP.wav');assert sr==pr==er==48000 and ref.shape==edit.shape
level=np.sqrt(np.mean(ref*ref)/np.mean(edit*edit));out=D/'AFTER_V59_HF_0001_REFERENCE_EDIT.wav';sf.write(out,edit*level,48000,subtype='PCM_24');ready=sf.read(out)[0]
sf.write(D/'AB_REFERENCE_V59_HF0001_RESEARCH_WIP.wav',np.concatenate([ref,np.zeros((24000,2)),previous,np.zeros((24000,2)),ready]),48000,subtype='PCM_24')
(D/'README.md').write_text('''# Проверенное продолжение после v59: HF0001

Ещё один промежуточный WAV на **неизменённом выбранном трёхнотном пресете**, с тем же ARP и шестью входящими note-on. Уточнены существующие коэффициенты верхней обработки. Точное совпадение ещё не достигнуто.

[Оригинал → v59 → этот исследовательский WAV](AB_REFERENCE_V59_HF0001_RESEARCH_WIP.wav): 0 / 4,168 / 8,336 с. [Отдельный готовый фрагмент](AFTER_V59_HF_0001_REFERENCE_EDIT.wav).

Ошибка верхних гармоник: 1,299492894 у v59 → 1,288604338 здесь, против 1,360101187 у выбранной исходной трёхнотной версии. Общий критерий 0,941659039 → 0,940059963; критерий тембра 0,848973399 → 0,846836584. Небольшие остальные изменения приведены в validation.json; все фиксированные ограничения по исходной трёхнотной основе соблюдены. Ухудшения между раундами не накапливаются через перенос опоры.

Прошли свежая Diva, все 281 параметр, все 12 событий, Windows/native, полная независимая цепочка именно этого источника, спектральный fixture и 12 произвольных причинных проверок на четырёх частотах. Численный подбор завершился по бюджету итераций; после полной проверки контроллер **сам начал следующий gain-раунд**, а отдельная трёхнотная настройка Drift24 продолжает свой HF-подбор. Совпадение и субъективное предпочтение на слух не объявляются.

## Загрузить этот промежуточный WAV в FL Studio

Перетащи `AFTER_V59_HF_0001_REFERENCE_EDIT.wav` в Playlist. Audio Clip: Normalize Off, Pitch 0, Time stretching Resample, Time Reset. Громкость канала/Insert/Master 0 dB, панорама по центру, микшер без дополнительной обработки. Finish повторно ставить не нужно: он уже записан в WAV. `AB_...wav` — сравнение трёх фрагментов, наш новый звук с 8,336 с.

Это исследовательский WAV/исходники/параметры, а не новый полный релиз DLL для живой игры. Полный самостоятельный комплект с DLL/MIDI/пресетом и основной инструкцией — [v59](../../../v59-wip/README.md). Его DLL ещё содержит коэффициенты v59, поэтому через неё данный новый WAV точно не воспроизводится. Сам пресет и MIDI здесь совпадают с основным трёхнотным v59. Для нового живого комплекта потребуется отдельная сборка и проверка с новым ID; опубликованный v59 не перезаписывается.

GUI FL Studio и прослушивание ассистентом здесь не выполнялись.
''')
p=P/'README.md';p.write_text(p.read_text()+'\nСледующий полностью проверенный шаг на исходном трёхнотном пресете: [HF0001, WAV и инструкция](hf-continuation-0001/README.md). В опубликованный комплект v59 этот более поздний шаг не включён.\n')
(P/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(P))+'\n' for p in sorted(P.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
print('ACTUAL_HF0001_PROOF_WAV_AND_NUMERIC_HISTORY_BACKED_UP')
