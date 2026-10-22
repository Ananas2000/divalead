# Продолжение проекта Diva: локальный итог 22 октября 2026

**Точный тембр пока не получен.** В FL открыта версия `Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp`. Она сохраняет ноты, маршруты и 12 состояний native-эффектов исходного набора. Отличие от проверенной калиброванной версии04 — только параметр Diva171 **VCA1: ModDepth −68→−58**. Проверка всех281 параметров находится в `DIVA_FLP05_PARAMETER_DIFF.json`. PWModDepth+1.00 и KeyFollow2 сохранены.

Версия05 — отдельный WIP с небольшим улучшением огибающей/уровня тела. По тембру доказанного улучшения нет; версия04 сохранена как контрольная точка переноса. Не называть05 финальным пресетом или точным совпадением. Сравнительная v83 всё ещё значительно ближе по критериям, но имеет недопустимую задержку Finish12416frames.

## Открыть и послушать

- `Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp` — текущая открытая проба.
- `Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp` — проверенная базовая цепь.
- `renders/FL_NATIVE_05_MODDEPTH.wav` — настоящий WAV из FL, не offline имитация.
- `AB_ORIGINAL_V83_FL04_FL05.flac` — lossless A/B: оригинал0.000s, v83 4.168s, FL04 8.336s, FL05 12.504s. Только этот файл выровнен по RMS; исходные рендеры не нормализованы. Соответствующий WAV остался на ПК и восстанавливается через make_local_ab.py.

## Фактические результаты

| Проверка | Score | Tone score |
| --- | ---: | ---: |
| v83 | 0.9011 | 0.8044 |
| Облачный native checkpoint | 1.74041 | 1.65705 |
| Реальный FL04 | 1.814036 | 1.748587 |
| Реальный FL05 | 1.807872 | 1.750164 |

Меньше лучше; эти числа не являются процентом похожести. Повторы FL04 дали1.815340/1.814317 против первого1.814036. Изменение05 немного улучшает body/envelope, но Tone остаётся примерно прежним. Peak05=0.702274, клиппинга нет. Native DLL декларируют PDC0; end-to-end задержка не измерена.

На10 свежих native-повторах: baseline score mean=1.742556, std=0.001380; ModDepth−58 mean=1.726824, std=0.001288. Tone mean меняется лишь 1.659571→1.656706. Поэтому это улучшение общей оценки/огибающей, а не решение тембровой задачи.

## Что уже исследовано

Помимо исправления FST, сборки маршрута и калибровки реального FL, проведены63 исходных source-пробы,65 фазовых/Chorus-проб,286 проб static Fruity Phaser,216 полиномиальных WaveShaper-кривых,31 проба широкого диапазона VCA ModDepth,30 повторов для подтверждения ModDepth. Совместный поиск34 параметров EQ/main gain/SUM matrix по полному исходному критерию сделал1534 оценки и не превзошёл baseline. Fast-proxy EQ раньше дал ложное улучшение, провалившее полный критерий: его состояния отклонены.

Подробные JSON, параметры, native bin, TSV/h2p и логи находятся в `RESEARCH_DETAILS.zip`. Промежуточные WAV всех проб остались на ПК и воспроизводятся исходниками. Vendor DLL и лицензии в GitHub не включены. Повреждённый экспериментальный OGG на ПК не использовать: опубликован проверенный lossless FLAC.

## Проверенные инварианты и важные ловушки

Шесть удерживаемых нот41→37→36 дважды,180BPM; ARP внутри Diva. SOURCE1→MID2/SIDE3→SUM4→Master, без прямого SOURCE→Master. Все12 native payloads точны. Chorus mix4923/12800. Исходный текстовый пресет из FL04 даёт все281 тех же значений и побитно тот же raw, что direct Diva и текущий kit frozen source. У05 отличается только VCA ModDepth.

В калиброванном04/05 channel volume raw11148. Регулятор FL не равен линейному коэффициенту. Вариант02_UNITY отклонён: raw12800 фактически усилил аудио×1.81486, peak1.1468. Его не использовать. При выключении всех insert FX через параллельный MID/SIDE маршрут складываются две одинаковые копии: raw bypass делить на2. После проверки вернуть insert effects ON.

Реальный FL04 после калибровки всё ещё хуже offline native:1.814 против~1.742. Raw FL03/direct Diva имеют mono correlation≈0.999596, residual после gain-fit≈2.85%. Причина остатка не доказана. Не приписывать её конкретному багу; проверить историю/warmup, host/render settings и обработку в FL. Параметры Accuracy=great, OfflineAcc=same. Перебор фазы/Chorus не устранил разницу.

## Как восстановить рабочее дерево

GitHub хранит дату в `local-fl-studio/2026-10-22`, а исследовательские скрипты используют `sessions/2026-10-22`. Для нового ПК из полного checkout репозитория запустить:

```powershell
python diva-lead/research/native-low-latency-effects/local-fl-studio/tools/restore_checkpoint.py --destination "D:\new-local-fl-matching"
```

Выбрать НОВУЮ папку: скрипт не заменяет существующие файлы. Он восстановит sessions, input, analysis-runtime и поддерево исходного комплекта. На текущем ПК всё уже находится в `D:\проекты фл\Diva пытаемся накрутить лид\codex\local-fl-matching`; восстанавливать поверх него не надо.

Installed Diva: `C:\Program Files\VstPlugins\Diva(x64).dll`; native FX: `C:\Program Files\Image-Line\FL Studio 20\Plugins\Fruity\Effects`. Компилятор MinGW gcc уже установлен. Для Windows:

```powershell
gcc -O2 -static -o tools/native-host/fl_native_probe.exe tools/native-host/fl_native_probe.c -lole32 -luuid -luser32 -lgdi32
gcc -O2 -static -DFL_PRESET_GRAPH -DCOMMON_PHASE_PAIR -o tools/native-host/fl_native_common_phase_host.exe tools/native-host/fl_native_chain_host.c -lole32 -luuid -luser32 -lgdi32
gcc -O2 -static -DFL_PRESET_GRAPH -DCOMMON_PHASE_PAIR -DEXTRA_PHASER -o tools/native-host/fl_native_phaser_host.exe tools/native-host/fl_native_chain_host.c -lole32 -luuid -luser32 -lgdi32
gcc -O2 -static -o tools/native-host/diva_source_render_host.exe tools/native-host/diva_source_render_host.c
python tools/verify_saved_flp.py sessions/2026-10-22/Diva_NATIVE_LOCAL_05_MODDEPTH_WIP.flp
python tools/assess_local_render.py sessions/2026-10-22/renders/FL_NATIVE_05_MODDEPTH.wav
```

Для облака использовать прежний Linux/Wine workflow репозитория и разрешённые DLL; local_native_chain.py содержит Windows-оболочку. Оригинальный WAV нужен только анализатору. В реальный кандидат он не подмешивается.

## Следующее продолжение

1. Прослушать A/B и оставить04 или05 как WIP; не считать score доказательством нужного тембра.
2. Выяснить устойчивый остаток GUI/offline до новой масштабной оптимизации. Для экспортов:48k stereo float32,Pattern3bars,HQ all plugins,Leave remainder,insert/master effects ON. При создании нового проекта: вопрос о версии Yes, invalid data No. Пустой проект отдельно сохранять не требуется.
3. Пересмотреть структуру low-latency обработки или источник. Широкая статическая Phaser-сетка и простая полиномиальная WaveShaper-сетка уже не дали существенного результата; не начинать с их повторения. Не вводить16 входных нот и не использовать оригинал как материал синтеза.
4. Сохранять новые пробы отдельно; принять их только после свежих native повторов и реального рендера FL с исходными критериями.

Computer-use: штатный WGC давал FrameArrived timeout. Пользователь разрешил ограниченный GDI capture и guarded fl_click.py; они уже работали. Для GUI нужен видимый разблокированный desktop. После каждого действия свежее наблюдение; физический Esc означает прекращение ввода до нового сообщения пользователя. Последний Esc был мискликом, после него пользователь повторно разрешил продолжение.

В начале нового запуска перечитать user/skill instructions. Публикация результатов этого проекта в Ananas2000/divalead уже разрешена. GitHub обновлялся через blob/tree/commit/ref с expected_sha; локальный sparse clone отстаёт и не должен делать слепой push. При остатке лимита5% пользователь просил сразу сохранить готовое и планы. Данные первоначальной миграции сохранены отдельно в INITIAL_CHECKPOINT_RU.md.
