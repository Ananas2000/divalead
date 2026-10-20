"""Write current-version instructions from actual source metadata, without stacked history."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=Path('/tmp/divalead-v75-build/v75-wip');OLD=Path('/workspace/divalead/diva-lead/v74-wip')
v=json.loads((D/'verification/selected_validation.json').read_text());b=json.loads((D/'verification/user_selected_baseline.json').read_text());p=json.loads((OLD/'verification/selected_validation.json').read_text())
family=v['source_family'];assert family in ['PulseWidth51.90','Post74 joint oscillator-filter']
if family=='PulseWidth51.90':
 description='Относительно v74 пресет Diva и все 281 параметр прежние: ширина импульса 51,90. Уточнены коэффициенты Finish.'
 source_changes={};expected_indices=set()
else:
 description='Относительно v74 уточнены четыре параметра самой Diva: PulseWidth 51,90 → 51,91; OscMix 5,72 → 5,71; VCF1 Frequency 144,17 → 144,16; VCF1 Resonance 12,14 → 12,13. Остальные 277 параметров прежние. Для этого источника заново построены собственная независимая NEW-база и отдельный fixture; обработка Finish проверена именно с ним.'
 source_changes={'OSC:PW':51.91,'OSC:OscMix':5.71,'VCF1:Res':12.13,'VCF1:Freq':144.16};expected_indices={90,96,148,149}
head='''# Diva Lead v75 WIP — загрузка в FL Studio

Комплект для FL Studio 64-bit под Windows. Это проверенный промежуточный результат после v74; совпадение с оригиналом ещё не достигнуто. Используй пресет, WAV и Finish одной версии.

Три удерживаемые ноты MIDI 41 → 37 → 36 на фразу; два прохода, всего шесть входящих note-on. Повторы и октавные скачки создаёт внутренний ARP Diva. MIDI, огибающие и длительности сохранены. MistaTowa не используется.

'''+description+'\n\n'
body=(OLD/'FL_STUDIO_RU.md').read_text().split('## Быстро загрузить готовый звук',1)[1]
body=body.replace('v74','v75').replace('V74','V75').replace('AB_REFERENCE_V72_V75','AB_REFERENCE_V74_V75').replace('v72 с 4,168','v74 с 4,168').replace('старый v72','старый v74')
guide=head+'## Быстро загрузить готовый звук'+body
assert 'AB_REFERENCE_V74_V75_WIP' in guide and 'AB_REFERENCE_V72' not in guide
(D/'FL_STUDIO_RU.md').write_text(guide)
(D/'README.md').write_text('''# Diva Lead v75 WIP — три удерживаемые ноты

'''+description+'''

Исходный оригинал остаётся целью. Совпадение ещё не достигнуто; измерения не заменяют прослушивание пользователем. Три удержания на фразу, внутренний ARP, без дополнительных входящих нот.

- [Инструкция FL Studio](FL_STUDIO_RU.md).
- [Оригинал → v74 → v75](AB_REFERENCE_V74_V75_WIP.mp3), [WAV](AB_REFERENCE_V74_V75_WIP.wav): 0 / 4,168 / 8,336 с.
- [Оригинал → v75](AB_REFERENCE_V75_WIP.wav), v75 с 4,168 с.
- [Готовый короткий WAV](Diva_Lead_v75_REFERENCE_EDIT.wav), [полная партия](Diva_Lead_v75_FULL_180BPM.wav).
- [Пресет Diva](Diva_Lead_v75_WIP.h2p), [трёхнотный MIDI](Diva_THREE_HELD_180BPM.mid).
- [Finish Windows x64 VST2](Diva_Lead_Finish_v75_WIP_x64.dll), [FXP](Diva_Lead_Finish_v75_WIP.fxp).
- [Замороженный источник](Diva_SOURCE_FROZEN_48k.wav), [измерения и регрессии](COMPARISON_RU.md), [сборка](BUILDING.md).

Проверены свежая настоящая Diva, все параметры и MIDI, Windows/native, собственная независимая NEW-база, отдельный fixture и 12 причинных случаев четырёх частот. Дополнительные проверки полного комплекта — в verification/. Лицензионная Diva не включена. GUI FL Studio и субъективное прослушивание ассистентом не выполнялись. Finish обрабатывает входящий сигнал; оригинальный WAV в эффект не встроен.
''')
for file in D.glob('Diva_PREVIOUS_*_REFERENCE_EDIT.wav'):
 if file.name!='Diva_PREVIOUS_V74_REFERENCE_EDIT.wav':file.unlink()
labels={'H24':'Мощность 24 гармоник','upper_harm':'Верхние гармоники','upper_off':'Энергия между верхними гармониками','low_harm':'Нижние гармоники','ERB':'Энергия ERB-полос','relative_phase':'Фазовый профиль гармоник','whole':'Спектр всего фрагмента','envelope':'Огибающая','body':'Уровни тел срабатываний','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Ошибка, меньше лучше | Исходная трёхнотная основа | v74 | v75 | Изменение к v74 |','|---|---:|---:|---:|---:|']
for key,label in labels.items():
 a,c,e=b['metrics'][key],p['metrics'][key],v['metrics'][key];rows.append(f'| {label} | {a:.9f} | {c:.9f} | {e:.9f} | {(e/c-1)*100:+.4f}% |')
(D/'COMPARISON_RU.md').write_text('''# v75: сравнение с загруженным оригиналом

Цель — исходный Diva_original_lead_reference.wav: 176064 стереофрейма, 48 kHz, decoded float64 SHA256 450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c. Предыдущая версия служит контролем прогресса; подбор ведётся к оригиналу.

'''+description+'''

Трёхнотный MIDI, внутренний ARP, огибающие и длительности сохранены. Ограничения и веса ошибок прежние, относительно первоначально выбранной трёхнотной основы. Качество не принимается по одной численной оценке: нужны свежий Windows-рендер и все независимые проверки. Новые состояния DSP, задержка, расписание MIDI и воспроизведение записанного оригинала в эффект не добавлены.

'''+ '\n'.join(rows)+f'''

Общая ошибка **{p['score']:.10f} → {v['score']:.10f}**; ошибка тембра **{p['tone_score']:.10f} → {v['tone_score']:.10f}**. Это ошибки измерений, не проценты сходства. Небольшие регрессии приведены в таблице; стерео и тембр не объявляются совпавшими.

Crest-ошибка **{v['crest_RMS_dB']:.12f} dB**, прежний предел **{v['crest_cap_dB']:.12f} dB**. Windows/native максимум **{v['Windows_native_max_error']:.3g}**, полная собственная NEW-цепочка **{v['full_NEW_SOURCE_independent_max_error']:.3g}**, отдельный fixture **{v['spectral_fixture_max_error']:.3g}**; пределы 2e-7 / 3e-7 / 2e-7 прежние. Пройдены все 12 причинных случаев 44,1/48/96/192 kHz.

A/B выровнено одним общим стерео RMS-множителем на фрагмент, без раздельной нормализации каналов или нот. FULL-WAV сохранён на рабочем уровне. Точное совпадение не достигнуто. GUI FL Studio и субъективное прослушивание ассистентом не выполнялись.
''')
(D/'BUILDING.md').write_text((OLD/'BUILDING.md').read_text().replace('v74','v75').replace('0x444c3734','0x444c3735').replace('0x374740000','0x375750000'))
old=(OLD/'verification/Diva_all281.tsv').read_text().splitlines();new=(D/'verification/Diva_all281.tsv').read_text().splitlines();assert len(old)==len(new)==282
pairs=[(a,c) for a,c in zip(old,new) if a!=c];assert {int(a.split('\t')[0]) for a,c in pairs}==expected_indices
(D/'verification/Diva_parameter_difference.json').write_text(json.dumps(dict(relative_to='full v74',changed_parameters=[dict(before=a,after=c) for a,c in pairs],all281_parameters_byte_equal=not bool(pairs),three_held_MIDI_unchanged=True,relative_to_original_user_selection=v['changed_source_fields']),indent=2)+'\n')
old_model=json.loads((OLD/'analysis/spectral_model.json').read_text());new_model=json.loads((D/'analysis/spectral_model.json').read_text());changed_fields=[key for key in sorted(set(old_model)|set(new_model)) if old_model.get(key)!=new_model.get(key)]
assert set(changed_fields)<=set(['hf_matrix_parameters','harmonic_gain_parameters','common_phase_radians','common_phase_key_slopes','common_phase_key_quadratic','fine_phase_harmonic_parameters','final_stereo_balance','dynamic_harmonic_parameters'])
assert changed_fields or pairs
(D/'verification/Finish_changed_fields.json').write_text(json.dumps(dict(relative_to='full v74',changed_existing_model_fields=changed_fields,Diva_source_unchanged=not bool(pairs),MIDI_unchanged=True,new_DSP_states_or_latency_added=False,match_reached=False),indent=2)+'\n')
print('V75_SOURCE_METADATA_DOCUMENTED_AND_ALL281_CHANGES_VERIFIED',family,flush=True)
