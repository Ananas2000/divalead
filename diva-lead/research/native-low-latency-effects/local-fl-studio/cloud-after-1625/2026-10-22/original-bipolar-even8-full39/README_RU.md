# WIP39: новый проверенный трёхнотный комплект

- [Полный ZIP для FL Studio20](../ZL-WIP39/Diva_ZL39_STEREO_WIP_complete.zip).
- [A/B оригинал →556→39](../ZL-WIP39/AB_ORIGINAL_556_ZL39_WIP.mp3), [FLAC](../ZL-WIP39/AB_ORIGINAL_556_ZL39_WIP.flac).
- [Инструкция FL Studio](../ZL-WIP39/FL_STUDIO_RU.md).
- [Все60 проверочных WAV и состояния](../original-bipolar-even8-Mid20-Side22-margin39-new12-passed-20261031/README_RU.md).

Полного совпадения пока нет. Изменены WaveShaper на SOURCE и MID20/SIDE22 в первом ZL. Три длинные входящие ноты, источник Diva, ARP/ADSR, остальные11native, POST и финальный StereoShaper сохранены. Проверены12 новых пар и полный ZIP настоящими DLL/VST3 под Wine. Новый FLP ещё не открыт в WindowsGUI; задержка ASIO не измерялась.

# WIP39: три длинные ноты, Diva и обычная обработка

Полного совпадения с оригиналом пока нет. WIP39 прошёл новое сравнение с принятой556: изменена двухсторонняя кривая Fruity WaveShaper на SOURCE и немного уменьшены связанные Gain/TargetGain MID20 и SIDE22 в PRIMARY. Остальные11 native-состояний, POST38, последний StereoShaper, Diva, MIDI, ARP и ADSR сохранены. Цель — исходный оригинал, не предыдущая версия.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 Windows x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . После установки при необходимости Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL39_STEREO_WIP.flp, 180BPM/48000Hz/Pattern. При запросе Diva загрузите Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI Diva_THREE_HELD_180BPM.mid:41→37→36 дважды, шесть note-on/12событий. Верхние скачки создаёт внутренний ARP.
3. Для переноса в свою копию556/38: на SOURCE Fruity WaveShaper загрузите presets/SOURCE_WaveShaper.fst; на SUM замените первый ZL через presets/ZL39_PRIMARY.vstpreset. Без нового WaveShaper переноса нет. Полный presets/01_SOURCE.fst и presets/04_SUM.fst можно загрузить как Mixer track state; при переносе проверяйте SOURCE→MID/SIDE→SUM маршруты. Для остальных версий предпочтителен полный FLP. POST38 и финальный StereoShaper те же.
4. На SUM: прежний StereoShaper → ZL39 PRIMARY → ZL39 STEREO FIX → Fruity StereoShaper POST TRIM → Master. Всего13native и2ZL. Финальный raw[0,12782,12800,0,0,0], Left−.020dB/Right0dB, без задержки/crossfeed. Сохранённый MixChorus на SOURCE не меняйте. Оба ZL minimum phase/lookahead0/AutoGainOff; Finish/свёртки нет.

A/B: AB_ORIGINAL_556_ZL39_WIP.mp3/FLAC, оригинал0с →556с4.168с →39с8.336с. Только A/B выровнен общей stereoRMS; L/R отдельно не нормировались. Рабочие WAV без нормировки. Контроль и кандидат содержат отдельные реальные реализации Chorus, поэтому решение основано на12 новых парах, а не одном рендере.

First6gain0.007671013425/SEM0.000961954757; first10gain0.007711540974/SEM0.000675546813; оба>max(.0005,3SEM). Cold2[0.006944963723116038, 0.0045717267407072715]. Все12 stereo/pairedlowmid гейтов пройдены. Airfirst10−.09261dB относительно556 и−.08304dB относительно38; оба cold также снизились. Это значения критерия, не процент сходства на слух. Гарантия нерастущего Air относится к этой точке39, не к будущим промежуточным.

Проверены настоящий DLL/VST3-рендер, байты FLP/FST/пресетов, независимая распаковка ZIP и два холодных каскада. Новый nativeгенератор без cachedbundle сохраняет точное WS-состояние; повторный zeroDepthрендер0/0, старый формат сохранён. Оба ZL PDC0; это не измерение ASIO/всей задержки DAW. Открытие нового FLP в WindowsGUI ещё не проверено. Прослушивание ассистентом не заявляется. Исходный референс не подмешан в синтез; MistaTowa не используется.
