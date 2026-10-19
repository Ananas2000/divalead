from pathlib import Path
import json
R=Path(__file__).resolve().parent;D=R/'v66-build/v66-wip';OLD=Path('/workspace/divalead/diva-lead/v65-wip')
v=json.loads((D/'verification/selected_validation.json').read_text());b=json.loads((D/'verification/user_selected_baseline.json').read_text());prev=json.loads((OLD/'verification/selected_validation.json').read_text())
s=(OLD/'FL_STUDIO_RU.md').read_text().replace('v65','v66').replace('V65','V66')
s=s.replace('AB_REFERENCE_V64_V66_WIP','AB_REFERENCE_V65_V66_WIP').replace('v64','v65').replace('V64','V65')
s=s.replace('Это следующий промежуточный шаг после v65 на выбранной трёхнотной основе','Это следующий промежуточный шаг после v65 на выбранной трёхнотной основе')
(D/'FL_STUDIO_RU.md').write_text(s)
for p in D.glob('Diva_PREVIOUS_*_REFERENCE_EDIT.wav'):
    if p.name!='Diva_PREVIOUS_V65_REFERENCE_EDIT.wav':p.unlink()
(D/'README.md').write_text('''# Diva Lead v66 WIP — три длинные ноты и внутренний ARP

Продолжение выбранного трёхнотного источника. Сохранены исходный пресет Diva, все 281 параметр, входящие ноты и их длительности: три удержания на фразу, два прохода, шесть note-on. Повторы и октавы создаёт внутренний ARP. Уточнены существующие коэффициенты Finish; результат остаётся промежуточным, точное совпадение не достигнуто.

- [Инструкция FL Studio](FL_STUDIO_RU.md).
- [Оригинал → v65 → v66, MP3](AB_REFERENCE_V65_V66_WIP.mp3): **0 → 4,168 → 8,336 с**; [WAV](AB_REFERENCE_V65_V66_WIP.wav).
- [Оригинал → v66](AB_REFERENCE_V66_WIP.wav), v66 с 4,168 с.
- [Готовый короткий WAV](Diva_Lead_v66_REFERENCE_EDIT.wav), [полная партия](Diva_Lead_v66_FULL_180BPM.wav).
- [Пресет](Diva_Lead_v66_WIP.h2p), [MIDI трёх удержаний](Diva_THREE_HELD_180BPM.mid), [Finish Windows x64 VST2](Diva_Lead_Finish_v66_WIP_x64.dll), [программа эффекта](Diva_Lead_Finish_v66_WIP.fxp).
- [Замороженный исходник до Finish](Diva_SOURCE_FROZEN_48k.wav), [измерения](COMPARISON_RU.md), [сборка и проверки](BUILDING.md).

Проверены настоящие рендеры Diva и Windows DLL, полная независимая цепочка подходящей собственному источнику NEW-базы, отдельный спектральный fixture и 12 произвольных причинных случаев на четырёх частотах дискретизации. GUI FL Studio и прослушивание ассистентом не выполнялись. Бинарный файл лицензионной Diva не распространяется. Цель — исходный WAV пользователя, MistaTowa исключён. Предыдущие полные комплекты сохранены.
''')
labels={'H24':'Мощность 24 гармоник','upper_harm':'Верхние гармоники','upper_off':'Энергия между верхними гармониками','low_harm':'Нижние гармоники','ERB':'Энергия ERB-полос','relative_phase':'Фазовый профиль гармоник','whole':'Спектр всего фрагмента','envelope':'Огибающая','body':'Уровни тел срабатываний','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Ошибка, меньше лучше | Выбранная трёхнотная основа | v65 | v66 | Изменение к v65 |','|---|---:|---:|---:|---:|']
for k,label in labels.items():
    x,y,z=b['metrics'][k],prev['metrics'][k],v['metrics'][k];rows.append(f'| {label} | {x:.9f} | {y:.9f} | {z:.9f} | {(z/y-1)*100:+.4f}% |')
(D/'COMPARISON_RU.md').write_text('''# v66: сравнение с загруженным оригиналом

Цель — исходный `Diva_original_lead_reference.wav`, проверенный по каждому семплу: 176064 стереофрейма при 48000 Hz, decoded float64 SHA256 `450ab495963c48a8a3c5e94e64475a59ffdd04db4e7d4b5ad0d595e137ce512c`. Предыдущая версия служит контролем прогресса; подбор ведётся к оригиналу.

Входящие ноты, исходный пресет Diva, все 281 параметр, огибающие и ARP прежние. После v65 продолжен подбор верхнего диапазона, усилений гармоник, общей и тонкой фазы, финального стереобаланса и динамических целей гармоник. В этот комплект вошла полностью проверенная точка с наименьшей ошибкой тембра на момент начала сборки. Последующие расчёты выполняются отдельно и не изменяют этот комплект. Этот комплект фиксирует один полностью проверенный совместный вариант, указанный в `verification/selected_validation.json`, `analysis/selected_candidate.json` и `source_manifest.json`. Набор коэффициентов целиком проверен новым Windows-рендером. Новых состояний DSP, задержки, MIDI-нот, расписания нот или проигрывания оригинального сэмпла не добавлено.

'''+ '\n'.join(rows)+f'''

Общая ошибка **{prev['score']:.9f} → {v['score']:.9f}**; ошибка тембра **{prev['tone_score']:.9f} → {v['tone_score']:.9f}**. Это ошибки измерений, не проценты сходства на слух. Веса тембра: H24 0,30; верхние гармоники 0,25; ERB 0,20; нижние гармоники 0,10; верхняя межгармоническая энергия 0,10; фазовый профиль 0,05. Определения и масштабы прежние.

Все ограничения остаются относительно исходной выбранной трёхнотной основы, без накопления ухудшений от версии к версии. Crest-ошибка **{v['crest_RMS_dB']:.12f} dB**, предел **{v['crest_cap_dB']:.12f} dB**. Небольшие регрессии приведены в таблице. Стереобаланс и тембр не объявляются совпавшими.

Свежая Diva воспроизводит сырой WAV, все 281 параметр и 12 входящих событий точно. Windows/native максимум **{v['Windows_native_max_error']:.3g}**, полная независимая цепочка сохранённой собственной NEW-базы **{v['full_NEW_SOURCE_independent_max_error']:.3g}**, отдельный спектральный fixture **{v['spectral_fixture_max_error']:.3g}**. Пределы прежние: 2e-7 / 3e-7 / 2e-7. База заново создана для этого трёхнотного источника и используется с тем же сырьём. Все 12 произвольных причинных случаев на 44,1/48/96/192 kHz пройдены.

В A/B каждый фрагмент выровнен с оригиналом одним общим стерео RMS-множителем. Каналы и отдельные ноты не нормализованы отдельно. FULL-WAV сохранён на рабочем уровне эффекта, REFERENCE_EDIT — на уровне A/B. Точное совпадение не достигнуто; подбор продолжается. GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
(D/'BUILDING.md').write_text((OLD/'BUILDING.md').read_text().replace('v65','v66').replace('0x444c3635','0x444c3636').replace('0x365650000','0x366660000'))
print('V66_THREE_HELD_DOCS_WRITTEN',flush=True)

if v.get('source_family')=='PulseWidth51.90':
 # Explicitly document the newly proved physical source instead of claiming an unchanged preset.
 p=D/'FL_STUDIO_RU.md';text=p.read_text();old='Пресет Diva и MIDI побайтово сохранены из понравившегося трёхнотного варианта v58.';assert old in text;text=text.replace(old,'MIDI, ARP, огибающие и длительности сохранены из понравившегося трёхнотного варианта v58. В Diva изменена только ширина импульса: 51,87 → 51,90; остальные 280 параметров прежние. Используй новый H2P этого комплекта.');p.write_text(text)
 p=D/'README.md';text=p.read_text();old='Сохранены исходный пресет Diva, все 281 параметр, входящие ноты и их длительности';assert old in text;text=text.replace(old,'Входящие ноты, их длительности, ARP и огибающие прежние. В Diva изменена только ширина импульса: 51,87 → 51,90; остальные 280 параметров сохранены');p.write_text(text)
 p=D/'COMPARISON_RU.md';text=p.read_text();old='Входящие ноты, исходный пресет Diva, все 281 параметр, огибающие и ARP прежние.';assert old in text;text=text.replace(old,'Входящие ноты, их длительности, огибающие и ARP прежние. В исходном пресете Diva изменена только ширина импульса: 51,87 → 51,90; остальные 280 параметров сохранены. Для изменённого источника заново построена и независимо проверена собственная NEW-база и отдельный before-spectral fixture; прежняя база другого источника не подменялась. Все ограничения качества по-прежнему привязаны к первоначальному выбранному трёхнотному варианту.');p.write_text(text)

old_dump=(OLD/'verification/Diva_all281.tsv').read_text().splitlines();new_dump=(D/'verification/Diva_all281.tsv').read_text().splitlines();differences=[dict(before=a,after=b) for a,b in zip(old_dump,new_dump) if a!=b];assert len(old_dump)==len(new_dump)==282
if v.get('source_family')=='PulseWidth51.90':assert len(differences)==1 and 'PulseWidth' in differences[0]['before']
else:assert not differences
(D/'verification/Diva_parameter_difference.json').write_text(json.dumps(dict(relative_to='full v65',changed_parameters=differences,all_other_parameters_equal=True,three_held_MIDI_unchanged=True),indent=2)+'\n')
