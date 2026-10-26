# ZL30 WIP — следующий подтверждённый шаг прямо к оригиналу

- [Полный ZIP FL20/26](ZL-WIP30/Diva_ZL30_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → numeric264 с4.168с → ZL30 с8.336с](ZL-WIP30/AB_ORIGINAL_264_ZL30_WIP.mp3).
- [Lossless A/B](ZL-WIP30/AB_ORIGINAL_264_ZL30_WIP.flac).
- [Пошаговая инструкция FL Studio](ZL-WIP30/FL_STUDIO_RU.md).
- [Первые48WAV на исходном контексте](original-WS48-ref03-initial-context-proof/README_RU.md).
- [Последние48WAV на актуальном EQ264](original-WS48-ref03-latest264-base09/README_RU.md).

Полного совпадения нет. Две отдельные серии не объединялись для прохождения
порогов: сначала кривая прошла на исходном29, затем однократно на новомEQ264.
В latestfirst6 запас над3SEM невелик; latestfirst10 и обеcold положительны.
Все96validationWAV обеих серий сохранены lossless в ordinaryGit сmemberSHA и
partsmanifest. Результат не называется точным совпадением. Цель — только
исходный оригинальныйWAV на штатных Fruity и двух ZL, три длинныевходящиеноты.
НовыйFLP не открывался вWindowsGUI; actualLinux/WineDSP/состояния/ZIP проверены.

# ZL30 WIP — продолжение трёхнотного звука к исходному референсу

Полного совпадения ещё нет. Цель — загруженный Diva_original_lead_reference.wav, не v83/Finish. Nativebase09: следующая поправка48поддерживаемых координат штатного WaveShaper. Другие11native состояний, все281параметровDiva, ARP/ADSR, маршруты и входящие три длинные ноты41→37→36 дважды прежние. PRIMARY — принятый numeric264; POST тот же28 с3SideAP+1StereoAP+LeftPeak1013.3Hz. Всего ДВАZL, безстарогоFinish. Относительно264 меняется толькоWS, относительно полного29 — WS иPRIMARY.

1. Распаковать ZIP в новую папку, открыть Diva_ZL30_STEREO_WIP.flp в FL Studio20/26. Pattern,180BPM. Нужны прежние Diva,штатные Fruity и бесплатный ZL Equalizer2v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SOURCE: новая кривая WaveShaper. SUM: StereoShaper → ZL30 PRIMARY → ZL30 STEREO FIX. Mix100%, MinimumPhase/Lookahead0/AutoGainOFF уобоих. POST:SideAP10000Hz/Q2,2200Hz/Q4,895.8Hz/Q13.84; StereoAP783.2Hz/Q19.422; LeftPeak1013.3Hz/Q4.786/−1.04dB. Порядок сохранить.
3. В прежнем GUIпроекте обязательно загрузить presets/SOURCE_WaveShaper.fst в SOURCE WaveShaper и presets/SUM_ZL30_PRIMARY.fst в первый SUM ZL. Если уже стоит numeric264, PRIMARY прежний, WS обновить обязательно. POST через presets/SUM_ZL30_STEREO_FIX.fst тот же28. Только обновлениеZL безWS не воспроизводит30. Альтернатива — Mixer track states presets/01_SOURCE.fst и presets/04_SUM.fst; проверить SOURCE→MID/SIDE, MID/SIDE→SUM, SUM→Master. Работать в отдельной копии проекта.
4. Если Diva не восстановилась — загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid, шесть note-on на две фразы. Высокие скачки создаёт внутреннийARP, не быстрыйMIDIсписок.

A/B AB_ORIGINAL_264_ZL30_WIP.mp3 или losslessFLAC: оригинал0с → numeric264 с4.168с → ZL30 с8.336с. Контроль/кандидат — разные реализации свободного Chorus. Только A/B выровнен общей stereoRMS, рабочиеWAV безнормировки.

167настоящих nativeDLL/VST3вариантов. Сначала кривая прошла first6ANDfirst10+2cold на исходной обработке29: first10gain.004144567014, cold+.003638115617/+.005039594972. За время поиска принят EQ264, поэтому проведена отдельная однократная проверка новой DSPкомбинации сlatest264; старые и новые пары не объединялись. Latestfirst6gain.004093436273,SEM.001353749775,порог.004061249325 — небольшой запас. Latestfirst10gain.004505644493,SEM.000873692657,порог.002621077970; cold+.003051600354/+.005135124591. Все12 сохранили прежнююстереозащиту. Веса/819alignment/пороги/строгиедопуски прежние.

По latestпервым10 H24ошибка1.638807→1.626637дБ, upperharm1.698591→1.692816, ERB1.196369→1.194238, whole.087123→.087069. Upperoff слегка хуже3.932886→3.940408, envelope.149983→.150011, stereoBalance4.131893→4.139187; relativephaseпочтипрежняя1.183743→1.183823. Это небольшое подтверждённое улучшение общего исходного критерия, не процентсходства и не полное совпадение. First10candidateobjective1.298081008453.

FLP/FST/VSTpreset, all12native statebytes, неизменныеDiva/MIDI/маршруты/POST проверены. Два новых холодных каскадаZL из независимо распакованногоZIP повторяют сохранённый WAV при прежнемstrict8float32eps/1e-12; componentresavebyteexact. ActualnativeDLL/FSTroundtrip/zeroDepthChorusконтроль≤2e-7. ZL declaredPDC0/impulse0, неASIO/wholeDAW. Nativefirstresponse2samples и небольшиеblocksizeразличия раскрыты вverification/NATIVE_LATENCY_AND_BLOCKS.json; независимый свободныйChorus не обещается побитово одинаковым.

НовыйFLP ещё не открывалсявWindowsGUI. Реальные Linux/Winepluginrenders, не новыйGUIэкспорт; субъективное прослушивание ассистентом не заявляется. Оригинал только дляанализа/A-B и не подмешиваетсявсинтез. MistaTowa неиспользуется. Старыеfullkits/история/последнийPCGUIпроект сохранены.
