from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent;D=Path('/tmp/divalead-v67-build/v67-wip');OLD=Path('/workspace/divalead/diva-lead/v66-wip')
v=json.loads((D/'verification/selected_validation.json').read_text());b=json.loads((D/'verification/user_selected_baseline.json').read_text());p=json.loads((OLD/'verification/selected_validation.json').read_text())
assert v['source_family']=='PulseWidth51.90' and v['changed_source_fields']=={'OSC:PW':51.90}
text=(OLD/'FL_STUDIO_RU.md').read_text().replace('v66','__CURRENT__').replace('V66','__CURRENTCAP__').replace('v65','v66').replace('V65','V66').replace('__CURRENT__','v67').replace('__CURRENTCAP__','V67')
text=text.replace('## Быстро загрузить готовый звук','В самой Diva относительно v66 изменений нет: та же ширина импульса51,90, те же остальные параметры и MIDI. Обновлены коэффициенты Finish; для звука этой версии используй комплект v67 целиком.\n\n## Быстро загрузить готовый звук')
(D/'FL_STUDIO_RU.md').write_text(text)
for file in D.glob('Diva_PREVIOUS_*_REFERENCE_EDIT.wav'):
    if file.name!='Diva_PREVIOUS_V66_REFERENCE_EDIT.wav':file.unlink()
(D/'README.md').write_text('''# Diva Lead v67 WIP — три удержания и внутренний ARP

Продолжение проверенного трёхнотного варианта. После v66 исходник Diva и все281 параметр сохранены: ширина импульса51,90, остальные параметры прежние. MIDI: три удержания на фразу, два прохода, шесть note-on; повторения и октавы создаёт внутренний ARP. Уточнены существующие коэффициенты тонкой фазы Finish. Совпадение с исходным оригиналом ещё не достигнуто.

- [Инструкция FL Studio](FL_STUDIO_RU.md).
- [Оригинал → v66 → v67](AB_REFERENCE_V66_V67_WIP.mp3):0 /4,168 /8,336с; [WAV](AB_REFERENCE_V66_V67_WIP.wav).
- [Оригинал → v67](AB_REFERENCE_V67_WIP.wav), наш с4,168с.
- [Готовый короткий WAV](Diva_Lead_v67_REFERENCE_EDIT.wav), [полная партия](Diva_Lead_v67_FULL_180BPM.wav).
- [Пресет Diva](Diva_Lead_v67_WIP.h2p), [трёхнотный MIDI](Diva_THREE_HELD_180BPM.mid), [Finish Windows x64 VST2](Diva_Lead_Finish_v67_WIP_x64.dll), [FXP](Diva_Lead_Finish_v67_WIP.fxp).
- [Замороженный источник до Finish](Diva_SOURCE_FROZEN_48k.wav), [измерения и регрессии](COMPARISON_RU.md), [сборка](BUILDING.md).

Проверены настоящая Diva, Windows DLL/native, собственная NEW-база именно этого источника, отдельный fixture и12 причинных случаев четырёх частот. Дополнительные проверки полного комплекта записаны в verification/. Лицензионная Diva не включена; GUI FL Studio и прослушивание ассистентом не выполнялись. Модель обработки реагирует на входящий сигнал и не проигрывает оригинальный WAV. MistaTowa исключён.
''')
labels={'H24':'Мощность24 гармоник','upper_harm':'Верхние гармоники','upper_off':'Энергия между верхними гармониками','low_harm':'Нижние гармоники','ERB':'Энергия ERB-полос','relative_phase':'Фазовый профиль гармоник','whole':'Спектр всего фрагмента','envelope':'Огибающая','body':'Уровни тел срабатываний','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Ошибка, меньше лучше | Выбранная исходная трёхнотная основа | v66 | v67 | Изменение к v66 |','|---|---:|---:|---:|---:|']
for key,label in labels.items():
    a,c,e=b['metrics'][key],p['metrics'][key],v['metrics'][key];rows.append(f'| {label} | {a:.9f} | {c:.9f} | {e:.9f} | {(e/c-1)*100:+.4f}% |')
(D/'COMPARISON_RU.md').write_text('''# v67: сравнение с загруженным оригиналом

Цель — исходный Diva_original_lead_reference.wav:176064 стереофрейма48kHz, decodedfloat64 SHA450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c, проверенный посемплово. Предыдущая версия служит контролем прогресса; подбор ведётся к оригиналу.

После v66 все281 параметр Diva, включая PW51,90, MIDI, длительности, огибающие и ARP неизменны. Относительно самого первого выбранного трёхнотного пресета v58 остаётся ровно одно изменение Diva: PW51,87→51,90. Оно не добавлялось повторно в v67. Подходящие собственному источнику NEW и before-spectral fixture сохранены и проверены с новым Finish; чужая база другого сырья не использовалась.

Численная fine55-точка сначала нарушила свежие whole/stereo ограничения и была отклонена. Малая коррекция тех же существующих55 коэффициентов дала положительный запас внутри всех прежних границ. Свежая Diva/Windows/native/полная собственная NEW-цепочка/fixture/12 произвольных причинных случаев подтвердили исправленную точку. Допуски не расширялись. Изменены только существующие коэффициенты; новых состояний DSP, задержки, MIDI-нот, расписания нот или аудиозаписи оригинала в эффект не добавлено.

'''+ '\n'.join(rows)+f'''

Общая ошибка **{p['score']:.10f} → {v['score']:.10f}**; ошибка тембра **{p['tone_score']:.10f} → {v['tone_score']:.10f}**. Это ошибки измерений, не проценты сходства. Веса/масштабы прежние, ограничения всегда относительно первоначальной выбранной трёхнотной основы, без накопления ухудшений.

Crest-ошибка **{v['crest_RMS_dB']:.12f}dB**, прежний предел **{v['crest_cap_dB']:.12f}dB**. Небольшие регрессии приведены в таблице. Стереобаланс и тембр не объявляются совпавшими.

Windows/native максимум **{v['Windows_native_max_error']:.3g}**, полная собственная NEW-цепочка **{v['full_NEW_SOURCE_independent_max_error']:.3g}**, отдельный fixture **{v['spectral_fixture_max_error']:.3g}**; пределы2e-7/3e-7/2e-7 прежние. Все12 произвольных причинных случаев44,1/48/96/192kHz пройдены. Свежая Diva воспроизводит сырой WAV, все281 параметр и12 входящих MIDI-событий точно.

A/B выровнено одним общим стерео RMS-множителем на фрагмент; отдельные каналы или ноты не нормализуются. FULL-WAV сохранён на рабочем уровне эффекта. Точное совпадение не достигнуто; GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
(D/'BUILDING.md').write_text((OLD/'BUILDING.md').read_text().replace('v66','v67').replace('0x444c3636','0x444c3637').replace('0x366660000','0x367670000'))
old=(OLD/'verification/Diva_all281.tsv').read_bytes();new=(D/'verification/Diva_all281.tsv').read_bytes();assert old==new
(D/'verification/Diva_parameter_difference.json').write_text(json.dumps(dict(relative_to='full v66',changed_parameters=[],all281_parameters_byte_equal=True,three_held_MIDI_unchanged=True,relative_to_original_user_selection={'OSC:PW':51.90}),indent=2)+'\n')
print('V67_SOURCE_UNCHANGED_FROM_V66_DOCUMENTED_AND_ALL281_VERIFIED',flush=True)
