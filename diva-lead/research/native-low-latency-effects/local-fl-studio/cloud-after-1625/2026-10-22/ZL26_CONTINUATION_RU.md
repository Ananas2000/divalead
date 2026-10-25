# ZL26 WIP — следующая поправка непосредственно к оригиналу

- [Полный ZIP FL20/26:FLP/WAV/h2p/MIDI/FST/VSTpreset](ZL-WIP26/Diva_ZL26_STEREO_WIP_complete.zip).
- [A/B:оригинал0с → принятый155 с4.168с → ZL26 с8.336с](ZL-WIP26/AB_ORIGINAL_BEST155_ZL26_WIP.mp3).
- [Тот же A/B без потерь](ZL-WIP26/AB_ORIGINAL_BEST155_ZL26_WIP.flac).
- [Как загрузить в FLStudio](ZL-WIP26/FL_STUDIO_RU.md).

Цель — загруженный оригинальный WAV на обычной обработке с малой задержкой.
v83/старый Finish не используются как цель подбора или эффект. Это небольшое
устойчивое улучшение фазовой формы сигнала; полного совпадения нет.
Три входящие длинные ноты41→37→36 дважды,внутреннийARP/ADSR/Diva281/native06/
fine32/маршруты сохранены. PRIMARY — принятый155. В POST к прежним трём SideAP
добавлен StereoAllPass783.2Гц/Q19.422. Всего два экземпляра того же ZL1.4.1.

133настоящих VST3пробы,3новыхnativeinput,2heldout,затем frozenstate и новые
fresh6+2coldnativeпары. Mean gain.001321763822,SEM.000017126913, прежний порог
.0005. Cold2+.001319150380/+.001294888173. Все8улучшили полный originalobjective
и сохранили дополнительные стереоguards. Веса/819alignment/tolerances прежние.
Ошибка фазового профиля1.21164→1.18280. H24почтипрежняя1.68402→1.68455дБ,
ERB1.19308→1.19344дБ: эти малые регрессии не скрыты, оценка общая улучшилась.
Не заявляются большой слышимыйскачок или процентсовпадения.

Настоящие два холодных каскада воспроизвели сохранённый WAV точно0/0,
оба компонента resavebytesexact. НовыйFLP/FST/VSTpreset разобран, native12/
Diva/MIDI/routes неизменны. ПолныйZIPCRC/SHA и отдельные два холодных реальных
каскада из распакованногоZIP дали0/0. CombinedZLPDC0/impulse0, не ASIO/wholeDAW.
Новый проект не открывался вWindowsGUI. Это cloudLinux/Wine render, не GUIэкспорт.

[Все30training/validationWAV и исследования](original-target-stereo-phase-study01/README_RU.md).
Отдельно [21настоящий вариантDiva, все42source/processedWAV](original-target-actual-Diva-tone-study01/README_RU.md)
не улучшили полный originalcriterion и не применены. Оригинал только дляанализа/
A-B, не подмешиваетсявсинтез; MistaTowa не используется. Старые комплекты и
последний PCGUIпроект сохранены. Далее искать к оригиналу, сохраняя три ноты
и normalnative/twoZLобработку. СтарыйsingleZLкод потеряет второйэффект.
