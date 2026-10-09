# Diva: реконструкция лида для FL Studio

**V5 — пресет Diva + один готовый эффект Diva Lead Finish v5.** Все настройки уже выставлены. Сухой тембр v4 сохранён; подобрана дополнительная коррекция тембра и ширины по частотам. На видео у Diva видны три удерживаемые ноты: **1½ → 1½ → 1 доля**, **180 BPM**. MistaTowa Vol.3 в подборе не используется.

- [Скачать весь комплект v5](Diva_lead_reference_v5.zip).
- [Установка и крутилки в FL Studio](diva-lead/v5/Knobs_FL_Studio_RU.md).
- [Пресет Diva](diva-lead/v5/Diva_Lead_v5.h2p) и [готовый эффект Windows x64 VST2](diva-lead/v5/Diva_Lead_Finish_v5_x64.dll).
- [Сравнение MP3: оригинал → сухой v4 → готовый v5](diva-lead/v5/AB_reference_v4_v5_FINAL.mp3) / [WAV](diva-lead/v5/AB_reference_v4_v5_FINAL.wav).
- [Готовый рендер v5](diva-lead/v5/Diva_v5_FINAL.wav) и [версия с совмещением начала](diva-lead/v5/Diva_v5_FINAL_ALIGNED.wav).
- [MIDI с повтором как в видео](diva-lead/v5/Diva_PERFORMANCE_VIDEO_180BPM.mid), [MIDI для аудиовырезки](diva-lead/v5/Diva_PERFORMANCE_REFERENCE_180BPM.mid), [три удерживаемые ноты по структуре видео](diva-lead/v5/Diva_PATTERN_3notes_VIDEO_180BPM.mid).
- [График сравнения](diva-lead/v5/comparison.png), [кадр видео](diva-lead/v5/Video_pattern_3_notes.png), [проверка](diva-lead/v5/validation.json), [исходники эффекта и пересчёт измерений](diva-lead/v5/analysis).

Загрузи `.h2p` в Diva, назначь ей отдельный Insert и добавь **Lead Finish v5** в FX-слот этого Insert. У эффекта **Amount 100%, Output +1,88 dB**. В самой Diva **FX1 Off, FX2 Off, ARP Off**; импортируй MIDI `PERFORMANCE` при **180 BPM**. Подробные шаги находятся в инструкции.

Оба плагина реально проверены рендером под Wine. Все 281 параметр Diva совпали с v4 после загрузки нового пресета. У эффекта проверены сохранение состояния, разные размеры блоков и частоты дискретизации; перегруза нет. Стандартные настройки DLL сразу воспроизводят выбранную обработку.

В активных участках корреляция L/R **0,999 dry v4 → 0,922 v5**, у оригинала **0,922**. Ошибка стерео в пяти диапазонах снизилась **0,305 → 0,031**. Ошибка обертонов снизилась **5,18 → 3,74 dB**, изменение спектрального расстояния всего фрагмента умеренное: **0,094 → 0,093**. Остались небольшие отличия в динамике и атаках. **99% сходства на слух не заявляются:** здесь выполнено численное сравнение; прослушивание и запуск FL Studio не выполнялись. Пресет и цепочка обработки оригинала не установлены.

Для скачивания файла на GitHub нажми **Download raw file**. Весь репозиторий доступен через **Code → Download ZIP**.

Предыдущие материалы: [сухой v4](Diva_lead_reference_v4.zip), [его инструкция](diva-lead/v4/Knobs_FL_Studio_RU.md), [ранний тест встроенного chorus](diva-lead/v4-fx-test/README_RU.md), [v3](Diva_lead_reference_v3.zip), [v2](Diva_lead_reference_v2.zip), [v1](Diva_lead_reference_v1.zip).
