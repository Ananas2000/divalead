from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent;D=Path('/tmp/divalead-v69-build/v69-wip');OLD=Path('/workspace/divalead/diva-lead/v68-wip')
v=json.loads((D/'verification/selected_validation.json').read_text());b=json.loads((D/'verification/user_selected_baseline.json').read_text());p=json.loads((OLD/'verification/selected_validation.json').read_text())
assert v['source_family']=='PulseWidth51.90' and v['changed_source_fields']=={'OSC:PW':51.90}
text=(OLD/'FL_STUDIO_RU.md').read_text().replace('v68','__CURRENT__').replace('V68','__CURRENTCAP__').replace('v67','v68').replace('V67','V68').replace('__CURRENT__','v69').replace('__CURRENTCAP__','V69')
text=text.replace('## Быстро загрузить готовый звук','В самой Diva относительно v68 изменений нет: та же ширина импульса51,90, те же остальные параметры и MIDI. Обновлены коэффициенты Finish; для звука этой версии используй комплект v69 целиком.\n\n## Быстро загрузить готовый звук')
(D/'FL_STUDIO_RU.md').write_text(text)
for file in D.glob('Diva_PREVIOUS_*_REFERENCE_EDIT.wav'):
    if file.name!='Diva_PREVIOUS_V68_REFERENCE_EDIT.wav':file.unlink()
(D/'README.md').write_text('''# Diva Lead v69 WIP — три удержания и внутренний ARP

Продолжение проверенного трёхнотного варианта. После v68 исходник Diva и все281 параметр сохранены: ширина импульса51,90, остальные параметры прежние. MIDI: три удержания на фразу, два прохода, шесть note-on; повторения и октавы создаёт внутренний ARP. Уточнены существующие коэффициенты обработки Finish. Совпадение с исходным оригиналом ещё не достигнуто.

- [Инструкция FL Studio](FL_STUDIO_RU.md).
- [Оригинал → v68 → v69](AB_REFERENCE_V68_V69_WIP.mp3):0 /4,168 /8,336с; [WAV](AB_REFERENCE_V68_V69_WIP.wav).
- [Оригинал → v69](AB_REFERENCE_V69_WIP.wav), наш с4,168с.
- [Готовый короткий WAV](Diva_Lead_v69_REFERENCE_EDIT.wav), [полная партия](Diva_Lead_v69_FULL_180BPM.wav).
- [Пресет Diva](Diva_Lead_v69_WIP.h2p), [трёхнотный MIDI](Diva_THREE_HELD_180BPM.mid), [Finish Windows x64 VST2](Diva_Lead_Finish_v69_WIP_x64.dll), [FXP](Diva_Lead_Finish_v69_WIP.fxp).
- [Замороженный источник до Finish](Diva_SOURCE_FROZEN_48k.wav), [измерения и регрессии](COMPARISON_RU.md), [сборка](BUILDING.md).

Проверены настоящая Diva, Windows DLL/native, собственная NEW-база именно этого источника, отдельный fixture и12 причинных случаев четырёх частот. Дополнительные проверки полного комплекта записаны в verification/. Лицензионная Diva не включена; GUI FL Studio и прослушивание ассистентом не выполнялись. Модель обработки реагирует на входящий сигнал и не проигрывает оригинальный WAV. MistaTowa исключён.
''')
labels={'H24':'Мощность24 гармоник','upper_harm':'Верхние гармоники','upper_off':'Энергия между верхними гармониками','low_harm':'Нижние гармоники','ERB':'Энергия ERB-полос','relative_phase':'Фазовый профиль гармоник','whole':'Спектр всего фрагмента','envelope':'Огибающая','body':'Уровни тел срабатываний','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Ошибка, меньше лучше | Выбранная исходная трёхнотная основа | v68 | v69 | Изменение к v68 |','|---|---:|---:|---:|---:|']
for key,label in labels.items():
    a,c,e=b['metrics'][key],p['metrics'][key],v['metrics'][key];rows.append(f'| {label} | {a:.9f} | {c:.9f} | {e:.9f} | {(e/c-1)*100:+.4f}% |')
(D/'COMPARISON_RU.md').write_text('''# v69: сравнение с загруженным оригиналом

Цель — исходный Diva_original_lead_reference.wav:176064 стереофрейма48kHz, decodedfloat64 SHA450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c, проверенный посемплово. Предыдущая версия служит контролем прогресса; подбор ведётся к оригиналу.

После v68 все281 параметр Diva, включая PW51,90, MIDI, длительности, огибающие и ARP неизменны. Относительно самого первого выбранного трёхнотного пресета v58 остаётся ровно одно изменение Diva: PW51,87→51,90. Оно не добавлялось повторно в v69. Подходящие собственному источнику NEW и before-spectral fixture сохранены и проверены с новым Finish; чужая база другого сырья не использовалась.

Кандидат выбран только после свежего рендера Diva и проверок Windows/native, полной собственной NEW-цепочки, отдельного fixture и 12 произвольных причинных случаев. Пограничные численные результаты сами по себе не считаются подтверждёнными. Допуски не расширялись. Изменены только существующие коэффициенты; новых состояний DSP, задержки, MIDI-нот, расписания нот или аудиозаписи оригинала в эффект не добавлено.

'''+ '\n'.join(rows)+f'''

Общая ошибка **{p['score']:.10f} → {v['score']:.10f}**; ошибка тембра **{p['tone_score']:.10f} → {v['tone_score']:.10f}**. Это ошибки измерений, не проценты сходства. Веса/масштабы прежние, ограничения всегда относительно первоначальной выбранной трёхнотной основы, без накопления ухудшений.

Crest-ошибка **{v['crest_RMS_dB']:.12f}dB**, прежний предел **{v['crest_cap_dB']:.12f}dB**. Небольшие регрессии приведены в таблице. Стереобаланс и тембр не объявляются совпавшими.

Windows/native максимум **{v['Windows_native_max_error']:.3g}**, полная собственная NEW-цепочка **{v['full_NEW_SOURCE_independent_max_error']:.3g}**, отдельный fixture **{v['spectral_fixture_max_error']:.3g}**; пределы2e-7/3e-7/2e-7 прежние. Все12 произвольных причинных случаев44,1/48/96/192kHz пройдены. Свежая Diva воспроизводит сырой WAV, все281 параметр и12 входящих MIDI-событий точно.

A/B выровнено одним общим стерео RMS-множителем на фрагмент; отдельные каналы или ноты не нормализуются. FULL-WAV сохранён на рабочем уровне эффекта. Точное совпадение не достигнуто; GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
(D/'BUILDING.md').write_text((OLD/'BUILDING.md').read_text().replace('v68','v69').replace('0x444c3638','0x444c3639').replace('0x368680000','0x369690000'))
old=(OLD/'verification/Diva_all281.tsv').read_bytes();new=(D/'verification/Diva_all281.tsv').read_bytes();assert old==new
old_model=json.loads((OLD/'analysis/spectral_model.json').read_text());new_model=json.loads((D/'analysis/spectral_model.json').read_text())
changed_fields=[key for key in sorted(set(old_model)|set(new_model)) if old_model.get(key)!=new_model.get(key)]
assert changed_fields and set(changed_fields)<=set(['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters'])
(D/'verification/Finish_changed_fields.json').write_text(json.dumps(dict(relative_to='full v68',changed_existing_model_fields=changed_fields,Diva_source_and_MIDI_unchanged=True,new_DSP_states_or_latency_added=False,match_reached=False),indent=2)+'\n')
(D/'verification/Diva_parameter_difference.json').write_text(json.dumps(dict(relative_to='full v68',changed_parameters=[],all281_parameters_byte_equal=True,three_held_MIDI_unchanged=True,relative_to_original_user_selection={'OSC:PW':51.90}),indent=2)+'\n')
print('V69_SOURCE_UNCHANGED_FROM_V68_DOCUMENTED_AND_ALL281_VERIFIED',flush=True)
