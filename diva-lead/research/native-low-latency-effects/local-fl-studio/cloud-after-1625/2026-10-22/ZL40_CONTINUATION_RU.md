# WIP40: новый проверенный трёхнотный комплект

- [Полный ZIP для FL Studio20](ZL-WIP40/Diva_ZL40_STEREO_WIP_complete.zip).
- [A/B оригинал →565→40](ZL-WIP40/AB_ORIGINAL_565_ZL40_WIP.mp3), [FLAC](ZL-WIP40/AB_ORIGINAL_565_ZL40_WIP.flac).
- [Инструкция FL Studio](ZL-WIP40/FL_STUDIO_RU.md).
- [Все60 новых проверочных WAV и состояния](original-recovered-OS17-point-new12-passed-20261104/README_RU.md).

Полного совпадения пока нет. Новая обработка прошла12 новых пар относительно565 и полного39, независимый холодный ZIP и проверку supportedгенератора. Изменены только SOURCE WaveShaper, оба ZL и финальный StereoShaper; остальные11native, Diva/MIDI/ARP/ADSR и маршруты сохранены. Новый FLP пока не открыт в WindowsGUI; ASIO не измерялась.

# WIP40: Diva, три длинные ноты и обычная обработка

Полное совпадение с исходным референсом пока не достигнуто. WIP40 — проверенное улучшение относительно565, а не окончательный звук. В SOURCE WaveShaper включена реальная native oversampling step1 и уточнена двусторонняя кривая. Оба ZL перенастроены совместно, финальный StereoShaper Left−.040dB/Right0. Diva, MIDI, ARP/ADSR, другие11native-состояний и количество эффектов сохранены.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 Windows x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . При необходимости Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL40_STEREO_WIP.flp. 180BPM, 48000Hz, режим Pattern. Если Diva попросит пресет — Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI Diva_THREE_HELD_180BPM.mid:41→37→36 дважды. Это три входящие длинные ноты на фразу, шесть note-on/12событий на два повтора. Верхние скачки создаёт внутренний ARP; дополнительных коротких нот нет.
3. Для переноса в свою копию565/39 нужны ЧЕТЫРЕ состояния: SOURCE presets/SOURCE_WaveShaper.fst; SUM первый ZL presets/ZL40_PRIMARY.vstpreset; второй ZL presets/ZL40_STEREO_FIX.vstpreset; последний StereoShaper presets/SUM_ZL40_STEREO_TRIM.fst. Предпочтителен полный FLP. При переносе Mixer track state presets/01_SOURCE.fst и presets/04_SUM.fst проверяйте маршруты SOURCE→MID/SIDE→SUM→Master.
4. SUM: прежний StereoShaper → ZL40 PRIMARY → ZL40 STEREO FIX → Fruity StereoShaper POST TRIM → Master. Всего13native и2ZL. Final raw[0, 12764, 12800, 0, 0, 0]; задержка/crossfeed не добавлены. Mix/Depth Chorus на SOURCE сохранены. Оба ZL: minimum phase/lookahead0/AutoGainOff. Старого Finish/свёртки нет. Референс не подмешан в синтез, MistaTowa не используется.

A/B AB_ORIGINAL_565_ZL40_WIP.mp3/FLAC: оригинал0с →565с4.168с →40с8.336с. Только A/B выровнен общей stereoRMS и общим peak safety; L/R отдельно не нормировались. Рабочие WAV без нормировки. Контроль и кандидат — отдельные реальные реализации Chorus; вывод основан на12 новых парах.

First6 gain0.005042418525/SEM0.000606965131; first10 gain0.005334878766/SEM0.000559609545; оба>max(.0005,3SEM). Cold2[0.008253393502500428, 0.005244765884975466]. Все12 стерео/pairedlowmid гейтов пройдены. Критерий избыточного Air first10-0.092432dB относительно565, оба cold снизились. Относительно полного39 Air также снизился. Это критерии сравнения, не процент сходства на слух. Гарантия Air относится к этой точке40, не к будущим numericcohort.

Сохранённая точка взята из прерванного поиска897 записанных испытаний; полный поиск не объявлен завершённым. Точка зафиксирована до проверки двух неиспользованных входов и до всех12 новых пар. Схема/generator/fingerprint обновлены явно: canonical Y float32 до загрузки DLL. Без cachedbundle новый генератор создаёт точный nativeWS; all12state resave и два независимых zeroDepth повтора0/0. Старые native10/11 форматы проверены, не изменены.

Проверены реальные DLL/VST3 под Wine, FLP/FST/MIDI/Diva байты, независимая распаковка ZIP и два холодных каскада. ZL PDC0 и impulse onset0 в проверенном каскаде; это не измерение ASIO/всей задержки DAW. Открытие нового FLP в WindowsGUI ещё не проверено. Прослушивание ассистентом не заявляется.
