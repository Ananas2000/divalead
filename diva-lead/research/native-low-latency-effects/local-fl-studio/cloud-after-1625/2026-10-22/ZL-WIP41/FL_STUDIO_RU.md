# WIP41: три длинные ноты, Diva и обычная обработка

Это небольшое подтверждённое улучшение относительно620. Полного совпадения с оригиналом пока нет. Изменён только второй ZL: добавлен Right AllPass в полосе7,12800Hz,Q25,12dB/oct. Первый ZL, все13 Fruity, Diva, MIDI, ARP/ADSR и маршруты сохранены. Остаточный перекос по частотам остаётся.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . При необходимости выполните Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL41_STEREO_WIP.flp, включите Pattern,180BPM,48000Hz. Если Diva запросит пресет, загрузите Diva_NATIVE_WIP_THREE_HELD.h2p из ZIP. MIDI Diva_THREE_HELD_180BPM.mid содержит три длинные входящие ноты41→37→36 на фразу, два повтора. Верхние скачки создаёт внутренний ARP.
3. При переносе ИЗ620 замените только второй ZL на presets/ZL41_STEREO_FIX.vstpreset либо загрузите presets/SUM_ZL41_STEREO_FIX.fst. Первый ZL и последний Fruity Stereo Shaper оставьте как в620. Для более старого проекта предпочтителен полный новый FLP.
4. Порядок на SUM: прежний StereoShaper → ZL41 PRIMARY → ZL41 STEREO FIX → последний Fruity StereoShaper POST TRIM → Master. Оба ZL: Minimum Phase,Lookahead0,AutoGainOff,Mix100%. Всего13native+2ZL, нового плагина нет. Старого Finish/свёртки нет. Референс в синтез не подмешивается; MistaTowa не используется.

A/B AB_ORIGINAL_620_ZL41_WIP.mp3/FLAC: оригинал0с →620с4.168с →WIP41с8.336с. Оба наших варианта обработаны из одного реального native-входа. Только A/B выровнен общей stereoRMS и общей защитой пиков; каналы отдельно не нормировались. Рабочий ZL41_STEREO_FULL_WIP.wav без нормировки.

Точка прошла12 новых сравнений, оба порога first6/first10>max(.0005,3SEM), оба холодных запуска, снижение Air против620 и полного40, Tone и все стерео/paired-lowmid ограничения. Цифры находятся в verification/AP97_completion.json; это не процент сходства на слух. Проверены реальные DLL/VST3 под Wine, нативные состояния/генератор без кеша, FLP/FST/MIDI, независимая распаковка ZIP и холодные каскады. Заявленный ZL PDC0; задержка ASIO и открытие нового FLP в WindowsGUI здесь не проверены.
