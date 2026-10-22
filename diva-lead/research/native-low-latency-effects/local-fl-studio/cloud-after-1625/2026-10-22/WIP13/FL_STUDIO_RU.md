# Diva_NATIVE_13_WIP — промежуточный вариант на трёх нотах

Полного совпадения с оригиналом нет. Этот кандидат улучшает критерии в
исправленном native-хосте, но его новый контрольный экспорт в реальной FL
Studio ещё не выполнен. WAV получен настоящими DLL эффектов из свежего
Diva FL05; он не выдаётся за экспорт из вашей FL. Проверенный FL05 сохранён.

## Как загрузить в FL Studio 20

1. Распакуйте комплект в новую папку. Откройте `Diva_NATIVE_13_WIP.flp` через File → Open.
   Нужна установленная Diva и штатные Fruity WaveShaper, Chorus, Parametric EQ 2,
   Stereo Shaper. Присланные DLL не надо сканировать как VST; в архиве их нет.
2. Включите **Pattern**, выбранный паттерн с Diva, **180 BPM**. Нажмите Play.
   Уже записаны три длинные ноты 41→37→36 на фразу, две фразы. Вверх звук
   уходит за счёт внутреннего ARP Diva; MIDI на короткие ноты не заменён.
3. Diva обновлена по проверенному VST chunk. Исходный channel volume11148 и маршруты взяты из проверенного
   локального FL05. Новый пресет Diva отдельно: `Diva_NATIVE_WIP_THREE_HELD.h2p`.
   PWModDepth +1, KeyFollow2, VCA ModDepth−58; ARP/ADSR прежние.
4. Проверьте цепочку SOURCE → MID/SIDE → SUM → Master по таблице ниже.
   Старый Finish здесь не используется. Все посылы100%, фейдеры0dB, у SOURCE
   прямой посыл Master выключен; у MID/SIDE только SUM, у SUM только Master.

| Дорожка | Порядок эффектов |
| --- | --- |
| SOURCE | WaveShaper → Chorus → Stereo Shaper Phase_R → Stereo Shaper Phase_L |
| MID | Stereo Shaper Encode → EQ2 A → EQ2 B |
| SIDE | Stereo Shaper Encode → EQ2 A → EQ2 B → Stereo Shaper Decode |
| SUM | Stereo Shaper Stereo |

Mix именно **слота Chorus: 43.765625%** (raw5602/12800).
Остальные слоты100%. Native WetOnly=0. Две формы LFO изменены, их actual
raw-значения сохранены в candidate.json/chorus_overrides и внутри FST/FLP.
При желании собрать вручную: загрузите четыре `presets/01_SOURCE.fst` …
`04_SUM.fst` через Mixer → File → Open mixer track state и выставьте маршруты
вручную. Эти новые FST используют исправленный FL20 slot shell. Отдельные
12 plugin FST также включены. Состояния каждого плагина реально прочитаны
обратно из DLL; zero-depth control повторил весь аудиотракт по отсчётам.

## Что слушать

`NATIVE_FULL_180BPM_WIP.wav` — 6с, 48kHz stereo FLOAT32, полный рендер без
скрытых gain/time corrections. `NATIVE_REFERENCE_EDIT_WIP.wav` — прежний
фиксированный монтаж под референс. A/B: **оригинал → v83 со старым Finish →
реальный FL05 → этот WIP**. Начала сегментов0 / 4.168 / 8.336 / 12.504с.
Только в A/B выровнены RMS и общий безопасный peak; коэффициенты в AB_LEVELS.
Свободный Chorus слегка меняет повторные WAV: выбрана медианная оценка из6,
а не самый удачный дубль. Оригинал используется только для сравнения.

Цепочка сообщает declared PDC0, старый Finish сообщал12416 кадров при48kHz.
Это не измерение задержки звуковой карты или всей FL. Если нужно сравнить
сам звук, не добавляйте мастер-лимитер/нормализацию. Контрольный экспорт:
48kHz stereo FLOAT32, HQ all plugins, insert/master FX ON, Leave remainder,
Pattern3bars. Первый новый actual-FL экспорт остаётся обязательной проверкой
переноса; данные хоста сами по себе её не заменяют.

Изменения источника относительно v83 (все281 и12 входящих MIDI проверены):

| Параметр Diva | v83 | Этот источник |
| --- | --- | --- |
| OSC: OscMix | 5.71 | 6.30 |
| OSC: PWModDepth | 0.00 | 1.00 |
| VCA1: ModDepth | -68.00 | -58.00 |

В FLP записан настоящий effGetChunk Diva, успешно загруженный обратно с побитно тем же raw-аудио. Внешняя оболочка, MIDI и маршруты сохранены от FL05; сам источник обновлён по таблице. Новый экспорт из FL GUI ещё предстоит.
