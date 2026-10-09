# Diva: пресет по аудиореференсу

Актуальная **версия 2** подобрана с рендером присланного Diva, revision 16519, под Wine. Пресеты сохранены движком Diva, повторно загружены и проверены: параметры сохранились, все 10 MIDI-нот звучат, перегруза нет. FL Studio в облаке не запускалась; совпадение с референсом 1:1 не подтверждено.

[Скачать комплект v2 одним ZIP-файлом](Diva_lead_reference_v2.zip). Открой файл на GitHub и нажми **Download raw file**. Весь репозиторий также доступен через **Code → Download ZIP**.

- [Сухой пресет v2, без эффектов](diva-lead/v2/Diva_Lead_Reference_v2_DRY.h2p).
- [Пресет v2 со встроенным хорусом](diva-lead/v2/Diva_Lead_Reference_v2_STEREO.h2p).
- [Все крутилки и загрузка в FL Studio](diva-lead/v2/Knobs_FL_Studio_RU.md).
- [Аудиосравнение MP3: референс → сухой → стерео](diva-lead/v2/AB_reference_dry_stereo.mp3).
- [То же сравнение в WAV](diva-lead/v2/AB_reference_dry_stereo.wav).
- [Сухой рендер Diva](diva-lead/v2/Diva_v2_DRY.wav) и [стереорендер](diva-lead/v2/Diva_v2_STEREO.wav).
- [MIDI-фраза, 180 BPM](diva-lead/v2/Lead_reference_180BPM.mid).
- [Исходный аудиореференс WAV](diva-lead/v2/Diva_original_lead_reference.wav).
- [Результаты проверки и метод сравнения](diva-lead/v2/validation.json).

Главные изменения после v1: **Osc Mix 10,88; Cutoff 130,76; Resonance 7,64; KeyFollow 99,88; PW 52; Attack 16; Mode mono**. Это значения Diva, не герцы и миллисекунды. Полные списки параметров находятся в [папке v2](diva-lead/v2).

Пресет загружай через встроенный браузер **PRESETS** в Diva. Для первого сравнения используй DRY, импортируй MIDI в Piano Roll и отключи эффекты на канале и мастере. Аудиосравнение содержит три отрезка одинаковой общей RMS-громкости с паузами по 0,5 секунды.

Первая черновая версия сохранена в [архиве v1](Diva_lead_reference_v1.zip) и [исходной папке](diva-lead). Её инструкция описывает состояние до запуска Diva в облаке; для текущих настроек используй инструкцию v2.
