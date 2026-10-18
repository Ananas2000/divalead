from pathlib import Path
import json
R=Path(__file__).resolve().parent
D=R/'v59-build/v59-wip'
V=json.loads((D/'verification/selected_validation.json').read_text())
B=json.loads((D/'verification/user_selected_baseline.json').read_text())
old=Path('/workspace/divalead/diva-lead/v58-wip')
guide=(old/'FL_STUDIO_RU.md').read_text().replace('v58','v59').replace('V58','V59')
a=guide.index('Выбранный v59 использует')
b=guide.index('## Быстро загрузить',a)
guide=guide[:a]+'''Основная версия теперь продолжает **выбранный пользователем трёхнотный вариант**: три удерживаемые ноты на фразу, два прохода, всего 6 входящих note-on. Повторы и октавные скачки создаёт **внутренний ARP Diva, On**. Пресет Diva и MIDI побайтово сохранены из понравившегося трёхнотного варианта v58. В v59 изменена обработка верхнего диапазона в Finish. Это рабочая реконструкция; механизм оригинального автора по видео окончательно не установлен.

'''+guide[b:]
guide=guide.replace('Дополнительно `AB_REFERENCE_V57_V59_WIP.wav` содержит оригинал с 0 с, v57 с 4,168 с и v59 с 8,336 с.','Дополнительно `AB_REFERENCE_THREE58_V59_WIP.wav` / `.mp3` содержит оригинал с 0 с, выбранный ранее трёхнотный вариант с 4,168 с и v59 с 8,336 с. Здесь предыдущий звук — именно трёхнотный, который ты выбрал.')
a=guide.index('3. Через **Piano Roll')
b=guide.index('4. Громкость канала',a)
guide=guide[:a]+'''3. Через **Piano Roll → File → Import MIDI file** импортируй **`Diva_THREE_HELD_180BPM.mid`** в канал Diva. Темп **180 BPM**. На фразу — MIDI-номера **41 → 37 → 36**, длительности **1½ → 1½ → 1 доля**. В файле два прохода, второй начинается через 8 долей. Названия октав в DAW могут различаться; ориентируйся на номера MIDI. В Diva оставь **ARP On**, Direction **up+dn 2**, Octaves **2**, Multiply **1x**, Order **serial**, Restart **none**, Clock 100%, TimeBase **1/8**, Swing 0. Всё уже сохранено в H2P. Встроенный арпеджиатор FL на канале должен быть выключен. Не нарезай удержания на дополнительные ноты и не импортируй 16-нотный MIDI из старых версий.
'''+guide[b:]
guide=guide.replace('новый v57 заменять','старый v58 заменять').replace('старый v57 заменять','старый v58 заменять')
(D/'FL_STUDIO_RU.md').write_text(guide)
(D/'README.md').write_text('''# Diva Lead v59 WIP — продолжение трёхнотного варианта

Это полный промежуточный комплект для FL Studio Windows x64. Основой стал **трёхнотный вариант из v58, выбранный пользователем на слух**. Три удержания на фразу, внутренний ARP Diva On; пресет и MIDI сохранены. В Finish уточнены 100 существующих коэффициентов обработки верхнего диапазона. Точного совпадения с оригиналом ещё нет.

- [Загрузить в FL Studio](FL_STUDIO_RU.md).
- [Оригинал → выбранные три ноты v58 → v59, MP3](AB_REFERENCE_THREE58_V59_WIP.mp3): **0 → 4,168 → 8,336 с**.
- [То же сравнение WAV](AB_REFERENCE_THREE58_V59_WIP.wav); [оригинал → v59](AB_REFERENCE_V59_WIP.wav), v59 с **4,168 с**.
- [Короткий обработанный WAV](Diva_Lead_v59_REFERENCE_EDIT.wav); [полная партия](Diva_Lead_v59_FULL_180BPM.wav).
- [Пресет Diva](Diva_Lead_v59_WIP.h2p), [трёхнотный MIDI](Diva_THREE_HELD_180BPM.mid), [эффект Finish x64 VST2](Diva_Lead_Finish_v59_WIP_x64.dll).
- [Замороженный исходник Diva до Finish](Diva_SOURCE_FROZEN_48k.wav), [программа эффекта](Diva_Lead_Finish_v59_WIP.fxp).
- [Что изменилось и что остаётся](COMPARISON_RU.md); [сборка и проверки](BUILDING.md).

Ошибка верхних гармоник снизилась с 1,360101 до 1,299493 по прежнему измерению, примерно на 4,46%. Это уменьшение конкретной ошибки, не процент сходства на слух. Огибающая и стерео почти прежние; небольшие регрессии других измерений приведены в отчёте. Прослушивание ассистентом и GUI FL Studio здесь не выполнялись.

Свежая Diva воспроизвела исходник, все 281 параметр и 12 MIDI-событий точно. Проверены Windows DLL, native-расчёт, собственная независимая NEW-база именно для этого трёхнотного источника, разные блоки и 12 произвольных входов на четырёх частотах дискретизации. Это WIP; дальнейший подбор продолжается.

Сама лицензионная Diva в архив не включена. Используется только исходный референс пользователя; MistaTowa к этому лиду не относится.
''')
labels={'H24':'Ошибка мощности 24 гармоник','upper_harm':'Ошибка верхних гармоник','upper_off':'Ошибка энергии между верхними гармониками','low_harm':'Ошибка нижних гармоник','ERB':'Ошибка энергии ERB-полос','relative_phase':'Относительные фазы гармоник','whole':'Спектр всего фрагмента','envelope':'Огибающая','body':'Уровни тел срабатываний','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Измерение, меньше лучше | Выбранные три ноты v58 | v59 | Изменение ошибки |','| --- | ---: | ---: | ---: |']
for k,label in labels.items():
 x,y=B['metrics'][k],V['metrics'][k];rows.append(f'| {label} | {x:.9f} | {y:.9f} | {(y/x-1)*100:+.4f}% |')
(D/'COMPARISON_RU.md').write_text('''# v59: измерения относительно выбранных трёх нот

Пользователь предпочёл трёхнотный звук прежнему 16-нотному варианту. Поэтому новый подбор начинается от **v58/THREE_HELD_RESEARCH**, независимо от численного рейтинга разных архитектур. Основной v58 с 16 нотами здесь не является базой сравнения.

Diva, H2P, 281 параметр и входящие удержания сохранены. Проверены 25 малых изменений PW, баланса/расстройки осцилляторов, фильтра и KeyScale; убедительного улучшения не получили. Эти изменения не приняты. v59 содержит только два последовательных подбора 100 существующих коэффициентов верхней обработки Finish; фазы, динамические и явные стереонастройки сохранены. DSP использует поступающий сигнал и измеренную высоту, без воспроизведения сэмпла оригинала или расписания его нот.

'''+ '\n'.join(rows)+f'''

Общий прежний критерий: **{B['score']:.9f} → {V['score']:.9f}**. Дополнительный критерий тембра: **{B['tone_score'] if 'tone_score' in B else 0.8607868280379641:.9f} → {V['tone_score']:.9f}**. Его веса: H24 0,30; верхние гармоники 0,25; ERB 0,20; нижние гармоники 0,10; верхняя межгармоническая энергия 0,10; относительные фазы 0,05. Определения измерений, исходные окна и нормирующие масштабы прежние. Это цель данного подбора, а не доказательство предпочтения на слух.

Небольшие ухудшения огибающей, полного спектра и уровней тел видны в таблице. Чтобы они не накапливались, ограничения во всех раундах привязаны к исходному выбранному трёхнотному варианту, а не к предыдущей итерации: 0,1% или 0,2% в зависимости от измерения. Предел ошибки crest **{V['crest_cap_dB']:.12f} dB**, получено **{V['crest_RMS_dB']:.12f} dB**. Старые абсолютные пределы для 16-нотной ветки к этой основе не применялись. Все ограничения и веса сохранены в JSON.

Свежий рендер Windows DLL с выбранным исследовательским WAV совпал точно. Windows/native: **{V['Windows_native_max_error']:.3g}**, полная независимая цепочка собственной NEW-базы: **{V['full_NEW_SOURCE_independent_max_error']:.3g}**, отдельная спектральная проверка: **{V['spectral_fixture_max_error']:.3g}**. Пределы проверок не ослаблялись. Независимая база заново создана из этого трёхнотного источника; старый 16-нотный исходник не использован.

В A/B каждый кандидат выровнен с оригиналом одним общим RMS-множителем на весь стереофрагмент. Поканального и понoтного выравнивания A/B нет. FULL-WAV сохранён на рабочем уровне эффекта. Совпадение на слух не объявляется, настройка ещё продолжается.
''')
(D/'BUILDING.md').write_text('''# Сборка и проверки v59

Для загрузки в FL Studio Python не нужен. Пакет содержит Windows x64 VST2 DLL с ID `0x444c3539`, два параметра Amount и Output, без отдельного GUI. Собственная лицензионная Diva нужна для живого исполнения; готовый WAV работает без неё.

Из корня комплекта с MinGW x64:

```sh
x86_64-w64-mingw32-gcc -O3 -shared -static-libgcc -Wl,--no-insert-timestamp -Wl,--image-base,0x359590000 -o Diva_Lead_Finish_v59_WIP_x64.dll analysis/lead_finish.c -lm
```

На Windows имя компилятора может быть `gcc`. Pinned image base нужен для побайтового сравнения при той же версии компилятора. Для независимых проверок установи зависимости из `analysis/requirements.txt`, затем:

```sh
python -B analysis/verify_spectral.py --fixtures
python -B analysis/verify_release.py
```

Первая команда компилирует временный спектральный C-компонент за пределами комплекта и проверяет 12 произвольных сигналов на 44,1/48/96/192 kHz, причинность, константы, собственный спектральный fixture. Вторая проверяет хеши, MIDI/лог, весь выбранный WAV через сохранённую собственную NEW-базу, PDC и A/B. Эта команда использует уже сохранённую подходящую NEW-базу, а не строит её заново.

Для настоящего источника скомпилируй `analysis/diva_source_render_host.c` MinGW и запусти `analysis/replay_source.py --help`. Нужны Wine, его prefix/DLL path и предоставленная пользователем совместимая Diva rev16519. Файл пользователя имеет суффикс .vst3, но фактически экспортирует VST2 `VSTPluginMain`; его нельзя распространять в пакете. Помощник всегда исполняет трёхнотную версию: 6 note-on / 12 событий, ARP On. Он сравнивает новые семплы и все 281 параметр точно с комплектом.

Свежий source, полная новая независимая трёхнотная база и Windows/native уже проверены при подготовке. Сведения находятся в `source_manifest.json` и `verification/`. Реальный DLL проверен с блоками 47/127/512/2048; запуск/параметры/сохранение состояния/PDC проверены отдельным Windows VST-хостом. GUI FL Studio не запускался. История прогрева Diva в DAW может различаться, поэтому побитовое повторение живого синтезатора в FL не гарантируется; для точного источника есть frozen WAV.
''')
p=D/'analysis/replay_source.py';s=(old/'analysis/replay_source.py').read_text();s=s.replace("p.add_argument('--three-held',action='store_true')\n",'')
a=s.index('if a.three_held:');b=s.index("output=a.output",a)
s=s[:a]+'''preset=D/'Diva_Lead_v59_WIP.h2p';fixture=D/'Diva_SOURCE_FROZEN_48k.wav'
expected=[[e[k] for k in ['frame','status','pitch','velocity']] for e in json.loads((D/'verification/MIDI_note_events_48k.json').read_text())['events']]
assert len(expected)==12 and sum(e[1]==144 for e in expected)==6
roots=json.loads((D/'render_timing_180BPM.json').read_text())['root_velocities']
commands=['pattern 3 0 8','velocities '+' '.join(map(str,roots))]
'''+s[b:]
s=s.replace("expected_dump=(D/'THREE_HELD_RESEARCH/Diva_all281.tsv') if a.three_held else (D/'verification/Diva_all281.tsv')","expected_dump=D/'verification/Diva_all281.tsv'").replace('three_held=a.three_held','three_held=True');p.write_text(s)
# Correct inherited research labels; no model values are changed.
p=R/'fit_three_gains.py';s=p.read_text().replace('Existing111 gain and phase values for a complete verified model/source manifest.','Optimize 93 harmonic gain values of the selected three-held source; freeze phase.').replace("selected_basis='v53-wip'","selected_basis=str(B)").replace('existing111_gain_phase_values_only=True','existing93_harmonic_gain_values_only=True,common_phase_frozen=True');p.write_text(s)
print('V59_THREE_ONLY_DOCUMENTATION_AND_SOURCE_REPLAY_WRITTEN')
