# Diva: реконструкция лида для FL Studio

**V8 уточняет ширину стерео, спектр и уровни нот.** Ошибка ширины в пяти полосах уменьшилась **0.0668 → 0.0113**, взвешенная ошибка спектра **3.48 → 3.12 dB**, ошибка уровней нот **0.200 → 0.175 dB**. Это численные измерения, а не процент сходства на слух.

- [Скачать комплект v8](Diva_lead_reference_v8.zip).
- [Установка и крутилки FL Studio](diva-lead/v8/Knobs_FL_Studio_RU.md).
- [Пресет Diva](diva-lead/v8/Diva_Lead_v8.h2p) и [эффект Windows x64 VST2](diva-lead/v8/Diva_Lead_Finish_v8_x64.dll).
- [A/B MP3: оригинал → v7 → v8](diva-lead/v8/AB_reference_v7_v8.mp3) / [WAV](diva-lead/v8/AB_reference_v7_v8.wav).
- [Готовый WAV](diva-lead/v8/Diva_v8_FINAL.wav), [совмещённый WAV](diva-lead/v8/Diva_v8_FINAL_ALIGNED.wav), [Diva с Plate2 до обработки](diva-lead/v8/Diva_v8_DIVA_ONLY.wav), [сухой Diva без FX](diva-lead/v8/Diva_v8_DIVA_DRY.wav).
- [MIDI исполнения VIDEO](diva-lead/v8/Diva_PERFORMANCE_VIDEO_180BPM.mid), [MIDI для вырезки REFERENCE](diva-lead/v8/Diva_PERFORMANCE_REFERENCE_180BPM.mid), [три удерживаемые ноты с видео](diva-lead/v8/Diva_PATTERN_3notes_VIDEO_180BPM.mid).
- [График](diva-lead/v8/comparison.png), [измерения и проверки](diva-lead/v8/validation.json), [исходники и независимый пересчёт](diva-lead/v8/analysis).

Загрузи **Diva_Lead_v8.h2p**, поставь **Diva Lead Finish v8** на отдельный Insert: **Amount 100%, Output +1.85251 dB**. Импортируй новый MIDI при **180 BPM**, сохрани velocity. В Diva **FX1 Off, FX2 Plate2 On с Wet 1%, ARP Off**. Для перехода с v7 нужны новые пресет, эффект и MIDI. Исходные эффекты автора не установлены.

A/B: оригинал **0:00**, v7 **0:04.168**, v8 **0:08.336**. RMS уравнена по целым фрагментам. V8 ближе по ширине, балансу обертонов, уровням нот, огибающей и приведённым спектральным измерениям. **Фазовая ошибка обертонов немного хуже: 11.42° → 11.60°.** Атаки и короткие переходы ещё различаются. Полное совпадение не подтверждено.

Пресет исполнен настоящим Diva rev16519, эффект — скомпилированной Windows DLL под Wine. Две свежие загрузки пресета дали одинаковый WAV; обработка прошла проверки состояния, блоков, запуска, тишины и 44,1/96 кГц без перегруза. FL Studio и субъективное прослушивание здесь не выполнялись.

Встроенный ARP **up+dn 2, две октавы, Clock 1/8, Multiply 1x** выдаёт нужные высоты из трёх нот с видео. Его испытанный вариант хуже совпал по динамике и тембру, поэтому основной комплект использует восемь отдельных атак. Подробности в инструкции. MistaTowa Vol.3 не добавлен к лиду.

Для отдельного файла нажми **Download raw file**, для репозитория — **Code → Download ZIP**. Предыдущие комплекты: [v7](Diva_lead_reference_v7.zip), [v6](Diva_lead_reference_v6.zip), [v5](Diva_lead_reference_v5.zip), [v4](Diva_lead_reference_v4.zip), [v3](Diva_lead_reference_v3.zip), [v2](Diva_lead_reference_v2.zip), [v1](Diva_lead_reference_v1.zip).
