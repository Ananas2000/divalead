# ZL28 WIP — небольшая следующая поправка тембра к оригиналу

- [Полный ZIP FL20/26: FLP/WAV/h2p/MIDI/FST/VSTpreset](ZL-WIP28/Diva_ZL28_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → ZL27 с4.168с → ZL28 с8.336с](ZL-WIP28/AB_ORIGINAL_ZL27_ZL28_WIP.mp3).
- [Lossless A/B](ZL-WIP28/AB_ORIGINAL_ZL27_ZL28_WIP.flac).
- [Как загрузить в FL Studio](ZL-WIP28/FL_STUDIO_RU.md).

Цель — только исходный оригинальный WAV, не v83/Finish. Полного совпадения нет.
После205настоящих VST3проб Left EQ и симметричной L/Rкоррекции принят Left Peak
1013.3Гц/Q4.786/−1.04дБ,слот4 во второмZL. Это узкая поправка тембра; нижнесредний
перекос она целиком не исправляет. SourceDiva281/nativebase07сWS48/PRIMARY27/
ARP/ADSR/входящие три длинные ноты41→37→36 дважды/маршруты прежние. Второй ZL
сохраняет все3SideAP+1StereoAP, добавлен только LeftPeak. Всего ДВАZL, безFinish.

3новыхnativeinput,2heldout, затем frozenstate и8новыхnativeпар. First6gain
.002145716687,SEM.000015547773,порог.0005; cold2+.002079447035/+.002226962712.
Все8улучшили прежнюю полнуюoriginalobjective и прошли прежнююстереозащиту.
H24ошибка1.669885→1.663020дБ, ERB1.198666→1.196684дБ, whole.087358→.087238;
relativephase слегка хуже1.182737→1.183870, envelope.149856→.149931,
stereophase15.6433→15.7793град. Эти смешанные малые изменения не скрываются;
по общему исходному критерию улучшение устойчивое, не большой скачок и не
процентперцептивногосовпадения. Веса/819alignment/пороги/допуски неизменны.

Два новых холодных реальных каскада и отдельные два каскада из распакованного
полногоZIP дали точно0/0 при strict8float32eps/1e-12. Componentsresavebyteexact,
combinedZLPDC0/impulse0, неASIO. FLP/FST/VSTpreset разобраны, все12native/Diva/
MIDI/routes неизменны от27. Nativebase07 отдельно реально проверен изZIP27,
включаяall12DLLstate/FSTreplayzeroDepth0 при2e-7; в28этибайтыпрежние.

Все30training/validationWAV сохранены losslessвисследовании original-Left-EQ-after27
сmemberSHA иpartsmanifestдляточнойсборки. Обе обработки A/B получили один настоящий
nativeinput. Только A/B выровнен общейstereoRMS; рабочийWAV безнормировки.
НовыйFLP пока неоткрывалсявWindowsGUI; реальные Linux/Winepluginrenders,
неGUIэкспорт. Субъективного прослушивания ассистентом не заявлено.

В GUIпроекте27 достаточно обновить второйZL. При переносе из26и старше нужно
также обновить SOURCE WaveShaper и PRIMARY из27/28; инструкция вZIP. Оригинал
только дляанализа/A-B, в синтез не подмешивается. MistaTowa не используется.
Старыеfullkits/PCGUI/history/privateoriginalsource48/refsсохранены.
