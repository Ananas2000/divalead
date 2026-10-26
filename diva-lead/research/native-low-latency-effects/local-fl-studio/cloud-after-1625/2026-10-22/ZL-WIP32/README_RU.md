# ZL32 WIP — совместная перенастройка существующих полос второго EQ

Полного совпадения ещё нет. Цель — исходный Diva_original_lead_reference.wav, не v83/Finish. ИсточникDiva281, три длинные входящие ноты41→37→36 дважды, ARP/ADSR, nativebase10 сWS52 и маршруты сохранены. PRIMARY — уже принятый numeric301. Во второмZL перенастроены11параметров прежних5полос; новые полосы и плагины не добавлены.

1. Распаковать ZIP в новую папку и открыть Diva_ZL32_STEREO_WIP.flp в FL Studio20/26. Pattern180BPM. Нужны прежние Diva,штатныеFruity и бесплатный ZL Equalizer2v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SUM: StereoShaper → ZL32 PRIMARY → ZL32 STEREO FIX. Всего ДВАZL, Mix100%,MinimumPhase/Lookahead0/AutoGainOFF. POST:SideAP10207.6Hz/Q2.198,2149.8Hz/Q4.702,930Hz/Q11.336; StereoAP782.9Hz/Q20.561; LeftPeak994Hz/Q5.871/−1.70dB. Точные значения сохранены вFST и610parameterdump.
3. В проекте31 обновить первыйZL через presets/SUM_ZL32_PRIMARY.fst и второй через presets/SUM_ZL32_STEREO_FIX.fst. Если уже установлен numeric301, первыйпрежний — обновитьPOST. WaveShaper тот же31: presets/SOURCE_WaveShaper.fst; припереносеиз30и старше обязательнообновить иего. Альтернатива — presets/04_SUM.fst какMixertrackstate, затем проверить SUM→Master. Использовать отдельнуюкопиюпроекта.
4. Если Diva не восстановилась — загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid, шесть note-on на две фразы; высотные скачки создаёт внутреннийARP.

A/B AB_ORIGINAL_301_ZL32_WIP.mp3 или FLAC: оригинал0с → прежнийnumeric301 с4.168с → ZL32 с8.336с. Контроль/кандидат получили один и тот же настоящий nativeinput. Только A/B выровнен общейstereoRMS; рабочийWAV безнормировки.

229настоящих VST3предложений,3новыхnativeinput,2heldout. Кандидат зафиксирован до12новыхпар. First6gain.001605084122,SEM.000002427358,порог.0005; first10gain.001608731104,SEM.000003252253,порог.0005; cold+.001606378666/+.001609523072. Оба warmпорога иcold прошли, все12 сохранили прежнююстереозащиту и дополнительный предел ухудшения lowmidошибки≤.02dB. LatestPRIMARY301/старыйPOST после gracefulостановки совпали сзамороженнымконтекстом.

First10objective1.290952050075 — не процентсходства. H24ошибка1.612845→1.608593дБ,ERB1.184763→1.183888,whole.087076→.087018,upperoff3.954660→3.954433. Relativephase слегка хуже1.181957→1.182715, envelope.150099→.150111, stereoBalance4.124358→4.141824; lowmidошибка3.091412→3.107133дБ, тоесть+.015721вразрешённомпределе. Заметное исправление перекоса влево не заявляется. Это небольшое устойчивое улучшение общего исходного критерия; остаточные тембровые/стереоразличия и воздух сохраняются.

FLP/FST/VSTpreset, все12native состояния/Diva/MIDI/маршруты неизменны относительно31. Два холодных каскада иещё два из независимойраспаковкиZIP воспроизводят WAV при прежнемstrict8float32eps/1e-12, componentresavebyteexact. ZL declaredPDC0/impulse0, неASIO/wholeDAW. Native10ранее проверен настоящимиDLL/FSTсzeroDepthдопуском2e-7, здесьего байтыпрежние. Малыеnativeblocksizeразличия и свободныйChorus не означают побитового совпадения между всеми независимыми рендерами.

НовыйFLP ещё неоткрывалсявWindowsGUI; это настоящие Linux/Winepluginrenders, не новыйGUIэкспорт. Субъективное прослушивание ассистентом не заявляется. Оригинал только дляанализа/A-B, в синтез не подмешивается; MistaTowa не используется. Все старыеfullkits/история/последнийPCGUIпроект сохранены.
