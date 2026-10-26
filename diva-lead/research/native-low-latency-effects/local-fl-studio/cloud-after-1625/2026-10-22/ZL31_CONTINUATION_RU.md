# ZL31 WIP — штатная кривая52 и согласованный основной EQ

- [Полный ZIP FL20/26](ZL-WIP31/Diva_ZL31_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → ZL30 с4.168с → ZL31 с8.336с](ZL-WIP31/AB_ORIGINAL_ZL30_ZL31_WIP.mp3).
- [Lossless A/B](ZL-WIP31/AB_ORIGINAL_ZL30_ZL31_WIP.flac).
- [Инструкция FL Studio](ZL-WIP31/FL_STUDIO_RU.md).
- [Все файлы совместной серии и48WAV, уже сохранённые автоматически](original-WS52-primary-joint-finite-result/README_RU.md).
- [Отдельная кривая52 была отклонена](original-WS52-high4-first6-failed-not-adopted/README_RU.md).

Полного совпадения нет. Принята именно новая комбинация кривой и изменённого
PRIMARY после1189реальныхпредложений и12новыхпар, а не отвергнутая кривая52сама
по себе. Повторные попытки принять один и тот же не прошедший DSPвариант не делались.
Архив48проверочныхWAV ивсехфайлов серии уже побитово проверен вGit; повторная
копия огромногоархива не добавляется. Ссылки/receipt иmemberSHA сохранены здесь.

# ZL31 WIP — совместная поправка штатного WaveShaper и основного EQ

Полного совпадения ещё нет. Цель — исходный Diva_original_lead_reference.wav, не v83/Finish. Меняются кривая штатного FruityWaveShaper и первый ZL. ИсточникDiva281, ARP/ADSR, входящие три длинные ноты41→37→36 на фразу дважды, другие11native состояния, маршруты и второйZL прежние. Nativebase10. СтарыйFinish не нужен.

1. Распаковать ZIP в новую папку и открыть Diva_ZL31_STEREO_WIP.flp в FL Studio20/26, Pattern180BPM. Нужны прежние Diva,штатные Fruity и бесплатный ZL Equalizer2v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SOURCE: новая кривая WaveShaper. SUM: StereoShaper → ZL31 PRIMARY → ZL31 STEREO FIX. Всего ДВАZL, Mix100%,MinimumPhase/Lookahead0/AutoGainOFF. POST тот же28:3SideAP10000Hz/Q2,2200Hz/Q4,895.8Hz/Q13.84; StereoAP783.2Hz/Q19.422; LeftPeak1013.3Hz/Q4.786/−1.04dB.
3. В существующем проекте обязательно заменить SOURCE WaveShaper через presets/SOURCE_WaveShaper.fst и первый SUM ZL через presets/SUM_ZL31_PRIMARY.fst. POST через presets/SUM_ZL31_STEREO_FIX.fst тот же28/30. Только обновлениеZL безWaveShaper не воспроизводит31. Альтернатива — Mixer track states presets/01_SOURCE.fst и presets/04_SUM.fst; проверить SOURCE→MID/SIDE, MID/SIDE→SUM, SUM→Master. Использовать отдельную копию проекта.
4. Если Diva не восстановилась — загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid, шесть note-on на две фразы. Высокие скачки создаёт внутреннийARP.

A/B AB_ORIGINAL_ZL30_ZL31_WIP.mp3 или losslessFLAC: оригинал0с → ZL30 с4.168с → ZL31 с8.336с. Только A/B выровнен общей stereoRMS; рабочийWAV без нормировки. Контроль и кандидат сняты отдельными реализациями свободного Chorus, поэтому решение принято по серии новыхпар.

Добавлены4координаты формы WaveShaper возле пиков входа к прежним48, но воспроизведение использует обычный штатный FST с129точками и не требует нового эффектора. Отдельная кривая52 после173реальныхпроб НЕ прошлаfirst6 и былаотклонена. Здесь новыйDSPвариант: эта кривая плюс реально изменённый PRIMARY.1189настоящих VST3предложений,3новыхtrainingnativeinput,2heldout, кандидат зафиксирован до12новыхпар. First6gain.002670664231,SEM.000435112049,порог.001305336146. First10gain.002548778783,SEM.000493900913,порог.001481702738. Cold2+.004829697303/+.005098111877. Оба warmпорога иcoldпары прошли, all12сохранили прежнююстереозащиту. Старыеотклонённыепары не объединялисьсновыми.

First10objective1.295619568932 — не процентсходства. H24ошибка1.626737→1.618426дБ, ERB1.194090→1.190186, relativephase1.183781→1.182908. Upperharm слегка хуже1.694576→1.698896, upperoff3.939971→3.950519, whole.087069→.087104, envelope.150011→.150077. Это ограниченное подтверждённое улучшение общего исходного критерия; остаточные различия и небольшой избыток воздуха не объявляются исправленными.

ПолныйZIPCRC/SHA проверен. Два новых холодных каскадаZL из независимо распакованногоZIP воспроизводят сохранённый WAV при прежнемstrict8float32eps/1e-12, componentresavebyteexact. Actualnative12DLL/FSTroundtrip/zeroDepthChorusконтроль≤2e-7. ZL declaredPDC0/impulse0, неASIO/wholeDAW. Nativefirstresponse2samples и малыеblocksizeразличия раскрыты вverification/NATIVE_LATENCY_AND_BLOCKS.json; свободныйChorus не обещается побитовоодинаковым между независимыми рендерами.

НовыйFLP ещё неоткрывалсявWindowsGUI. Реальные Linux/Winepluginrenders, без заявленияонoвомGUIэкспорте или субъективном прослушивании ассистентом. Оригинал только дляанализа/A-B, в синтез не подмешивается. MistaTowa неиспользуется. Все старыеfullkits/история/последнийPCGUIпроект сохранены.
