# Diva: реконструкция лида для FL Studio

**V7 уточняет фазу и баланс каналов на отдельных нотах.** В v6 общая ширина стерео совпадала, но детали L/R на обертонах расходились с референсом. Новая обработка уменьшает измеренную фазовую ошибку **31.6° → 11.4°**, ошибку баланса обертонов **4.16 → 2.25 dB**, ошибку уровней нот **0.25 → 0.20 dB**. Это измерения, не процент сходства на слух.

- [Скачать комплект v7](Diva_lead_reference_v7.zip).
- [Установка и крутилки FL Studio](diva-lead/v7/Knobs_FL_Studio_RU.md).
- [Пресет Diva](diva-lead/v7/Diva_Lead_v7.h2p) и [готовый эффект Windows x64 VST2](diva-lead/v7/Diva_Lead_Finish_v7_x64.dll).
- [A/B MP3: оригинал → v6 → v7](diva-lead/v7/AB_reference_v6_v7.mp3) / [WAV](diva-lead/v7/AB_reference_v6_v7.wav).
- [Готовый WAV](diva-lead/v7/Diva_v7_FINAL.wav), [совмещённый WAV](diva-lead/v7/Diva_v7_FINAL_ALIGNED.wav), [сухой Diva](diva-lead/v7/Diva_v7_DIVA_DRY.wav).
- [MIDI исполнения VIDEO](diva-lead/v7/Diva_PERFORMANCE_VIDEO_180BPM.mid), [MIDI для вырезки REFERENCE](diva-lead/v7/Diva_PERFORMANCE_REFERENCE_180BPM.mid), [три удерживаемые ноты с видео](diva-lead/v7/Diva_PATTERN_3notes_VIDEO_180BPM.mid).
- [График](diva-lead/v7/comparison.png), [измерения и проверки](diva-lead/v7/validation.json), [исходники эффекта и независимый пересчёт](diva-lead/v7/analysis).

Загрузи **Diva_Lead_v7.h2p**, добавь **Diva Lead Finish v7** на отдельный Insert: **Amount 100%, Output +2.10 dB**; импортируй MIDI при **180 BPM** с сохранением velocity. В самой Diva FX1/FX2/ARP Off. Для перехода с v6 нужны оба новых файла — пресет и эффект. Эффект создан в этой работе; исходная цепочка из видео не установлена.

В A/B начало оригинала **0:00**, v6 **0:04.168**, v7 **0:08.336**. Громкость уравнена по фрагменту целиком. **V7 точнее по фазе/балансу обертонов, уровням нот и части спектральных измерений; v6 точнее по общей ширине стерео и спектральному расстоянию устойчивых участков.** V7 немного уже референса: корреляция L/R **0,9397** против **0,9223**. Первая атака также ещё отличается.

Настоящий Diva и готовая Windows DLL исполнены под Wine. Две свежие загрузки пресета дали одинаковый WAV; эффект прошёл проверки состояния, блоков, запуска, тишины и 44,1/96 кГц, без перегруза. Запуск FL Studio и субъективное прослушивание здесь не выполнялись. **Точное совпадение и 99% на слух не подтверждены.**

На видео три удерживаемые ноты длиной **1½ → 1½ → 1 доля**. `PERFORMANCE` восстанавливает слышимые восемь атак отдельными MIDI событиями; исходный способ повторов из видео не установлен. VIDEO повторяется через 8 долей, REFERENCE учитывает монтаж короткой вырезки. MistaTowa Vol.3 не добавлен к лиду.

Для отдельного файла нажми **Download raw file**, для всего репозитория — **Code → Download ZIP**.

Предыдущие комплекты: [v6](Diva_lead_reference_v6.zip), [v5](Diva_lead_reference_v5.zip), [сухой v4](Diva_lead_reference_v4.zip), [v3](Diva_lead_reference_v3.zip), [v2](Diva_lead_reference_v2.zip), [v1](Diva_lead_reference_v1.zip).
