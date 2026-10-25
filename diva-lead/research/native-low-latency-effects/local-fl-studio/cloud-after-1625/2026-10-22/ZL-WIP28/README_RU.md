# ZL28 WIP — следующая точечная поправка к оригиналу

Цель — исходный Diva_original_lead_reference.wav, старыйv83/Finish не цель и не эффект. Полного совпадения нет. Источник Diva281/ARP/ADSR и входящие три длинные ноты41→37→36 дважды, nativebase07 с новой WSкривой, PRIMARY27 и маршруты прежние. В POST добавлен обычный Left Peak1013.3Гц/Q4.786/−1.04дБ, слот4. Это узкая поправка тембра, не полное исправление нижнесреднего стереобаланса.

1. Распаковать ZIP в новую папку, открыть Diva_ZL28_STEREO_WIP.flp в FL20/26. Pattern,180BPM. Нужны прежние Diva и штатные Fruity, плюс бесплатный ZL Equalizer2 v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SUM: StereoShaper → ZL28 PRIMARY → ZL28 STEREO FIX. Всего ДВА ZL, Mix100%, MinimumPhase/Lookahead0/AutoGainOFF. Второй ZL: прежние SideAP10000Гц/Q2,2200Гц/Q4,895.8Гц/Q13.84 и StereoAP783.2Гц/Q19.422, плюс новый Left Peak1013.3Гц/Q4.786/−1.04дБ. Порядок сохранить.
3. В существующем проекте27 достаточно заменить второй ZL через presets/SUM_ZL28_STEREO_FIX.fst. PRIMARY тот же27: включён presets/SUM_ZL28_PRIMARY.fst. При переносе из26 и более старых вариантов обязательно также загрузить SOURCE WaveShaper через presets/SOURCE_WaveShaper.fst и новый PRIMARY из27/28. Только обновлениеPOST в старой nativeбазе не воспроизводит28. Альтернатива — Mixer track states presets/01_SOURCE.fst и presets/04_SUM.fst; проверить SOURCE→MID/SIDE, MID/SIDE→SUM, SUM→Master. Использовать отдельную копию проекта.
4. Если Diva не восстановилась — загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid: шесть note-on на две фразы, высотные скачки создаёт внутреннийARP.

A/B: AB_ORIGINAL_ZL27_ZL28_WIP.mp3 или FLAC: оригинал0с → ZL27 с4.168с → ZL28 с8.336с. Обе обработки получили один настоящий nativeinput. Только A/B выровнен общей stereoRMS, рабочий WAV без нормировки.

205 настоящих VST3проб: варианты Left EQ и симметричной L/Rкоррекции,3новыхnativeinput,2heldout. Кандидат заморожен до8новыхnativeпар. First6mean gain .002145716687,SEM.000015547773,порог.0005; cold2+.002079447035/+.002226962712. Все8 улучшили полный originalobjective и прошли прежнюю защиту стерео. Веса,819alignment и строгие допуска сохранены. Небольшое устойчивое улучшение не означает полного совпадения, остаются тембровые/динамические/стереоразличия.

Все12native FST/statebytes и Diva/MIDI/routes неизменны от27; FLP/FST/VSTpreset содержат те же PRIMARY и новыйPOST. Два новых холодных каскада и ещё два каскада из независимой распаковки ZIP воспроизвели WAV точно0/0 при прежнемstrict8float32eps/1e-12; компонентыпересохранены побитово. Два ZL PDC0/impulse0, не ASIO/wholeDAWизмерение. Состояния nativebase07 уже отдельно проверены из полногоZIP27 настоящими DLL, здесь их байты прежние.

Новый FLP ещё не открывался в WindowsGUI. Реальные рендеры Linux/Wine, без заявлений о новомGUIэкспорте или субъективном прослушивании ассистентом. Оригинал только дляанализа/A-B, в синтез не подмешивается. MistaTowa неиспользуется. Все прежние полные комплекты и PCGUIпроект сохранены.
