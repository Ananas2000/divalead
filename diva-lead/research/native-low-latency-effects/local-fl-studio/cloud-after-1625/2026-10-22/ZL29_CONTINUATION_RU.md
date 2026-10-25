# ZL29 WIP — ещё одна подтверждённая поправка к исходному оригиналу

- [Полный ZIP FL20/26:FLP/WAV/h2p/MIDI/FST/VSTpreset](ZL-WIP29/Diva_ZL29_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → принятыйnumeric258 с4.168с → ZL29 с8.336с](ZL-WIP29/AB_ORIGINAL_258_ZL29_WIP.mp3).
- [Lossless A/B](ZL-WIP29/AB_ORIGINAL_258_ZL29_WIP.flac).
- [Инструкция FL Studio](ZL-WIP29/FL_STUDIO_RU.md).

Полного совпадения нет. Цель — загруженный оригинальный WAV, не v83/Finish.
Nativebase08: новая поправка48поддерживаемых координат кривой штатного Fruity
WaveShaper. Другие11native состояния, все281параметровDiva, ARP/ADSR, входящие
три длинные ноты41→37→36 дважды и маршруты прежние. PRIMARY — уже подтверждённый
numeric258; POST тот же28, включая3SideAP+1StereoAP+LeftPeak1013.3Hz. Всего ДВАZL.
Относительно258 меняется толькоWS; относительно полного28 — WS иPRIMARY.

161настоящий nativeDLL/VST3вариант. Кандидат заморожен до12новыхпар. Заранее
принято двойное правило: ОБАпорога first6иfirst10>max(.0005,3SEM), обе холодные
пары положительны, all12 сохраняют прежниеstereo guards. First6gain.006999041660,
SEM.001135144400,порог.003405433199. First10gain.007092516686,SEM.000767313164,
порог.002301939492. Cold2+.006436968520/+.006033872861. Другие11native побитово
прежние, независимый zeroDepth nativeState replay0 при допуске2e-7. LatestPRIMARY/
POST после gracefulостановки основного поиска совпали с frozencontext побитово;
устаревшая EQнастройка не применена. First10objective1.302748134769 — не процентсходства.

H24ошибка1.663271→1.640222дБ, ERB1.199396→1.191644, whole.087155→.086999,
envelope.149904→.149796. Relativephase слегка хуже1.184308→1.185765,
upperoff3.913383→3.924890 и stereoBalance4.097620→4.128236: смешанные изменения
не скрыты. Общий прежний originalobjective устойчиво лучше, но остаточные
тембровые/динамические/стереоразличия сохраняются. Правила/веса/819alignment/
строгие replayдопуски не изменены. Ассистент не заявляет субъективногопрослушивания.

ПолныйZIPCRC/SHA, двахолодных настоящих каскадаZL изZIPдали0/0, componentresave
побитово. Actualnative12DLLstate/FSTroundtrip/zeroDepthконтроль изZIPдал0 при2e-7.
В FLP/FST/VSTpreset толькоWS и PRIMARY относительно28; Diva/MIDI/маршруты/POST
прежние. CombinedZLPDC0/impulse0, неASIO/wholeDAW. Native firstresponse2samples,
малые blocksizeразличия раскрыты вverification/NATIVE_LATENCY_AND_BLOCKS.json,
абсолютная blockinvariance не заявляется. НовыйFLP пока неоткрывался вWindowsGUI;
это настоящие Linux/Winepluginrenders, не новыйGUIэкспорт.

Все48новыхnative/processed контрольных/кандидатных WAV сохранены losslessвGit
сmemberSHA иparts48MiBmanifestдляточнойсборки вoriginal-WS48-refinement02-base08.
Там же supportednativebundle и internalnative08ZIP длявосстановления среды;
его не использовать вместо полногоZL29звука. Только A/B выровненобщейstereoRMS,
рабочийWAV безнормировки. НезависимыеnativeChorusреализации сравнивалисьсериями.

В прежнем GUIпроекте необходимо обновить SOURCE WaveShaper и PRIMARY; если уже
стоитnumeric258, PRIMARYпрежний, WSвсёравнообновить. POSTтотже28. Только заменаZL
безWSне воспроизводит29. Пошаговаяинструкция ивсепресеты в полномZIP. Оригинал
только дляанализа/A-B, в синтез не подмешивается. MistaTowa не используется.
Старыеполныекомплекты/PCGUI/history/privateoriginalsource48/refsсохранены.
Дополнительно освобождено1.499GiB только проверенногопубличногоGitblobcache:
61объект, всеworktreeфайлы/refs/privateданные сохранены, данныеfetch-on-demand.
