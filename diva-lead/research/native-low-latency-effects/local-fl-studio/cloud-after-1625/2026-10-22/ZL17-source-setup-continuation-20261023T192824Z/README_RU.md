# ZL17: новый источник, фактический полный рендер и продолжение

Полного совпадения с оригиналом ещё нет. [Полный ZIP для FL20](../ZL-WIP17/Diva_ZL_17_WIP_complete_WIP.zip),
[A/B: оригинал0с → ZL17 с4,168с](../ZL-WIP17/AB_REFERENCE_ZL17_WIP.mp3),
[инструкция и официальный бесплатный эквалайзер](../ZL-WIP17/FL_STUDIO_RU.md).
Три длинные ноты41→37→36 на фразу, дважды, внутренний ARP; MIDI/ADSR не меняются.

Diva OscMix6.3→6.5 принят после отдельной заранее фиксированной48pair проверки:
mean1.347429927→1.344884890, SEM0.000404493. Остальные280 параметров и12MIDI точны.
Предшествующая12pair проверка была неуверенной и НЕ принята. Все96 WAV новой48
сохранены lossless в трёх64MiB частях с SHA, поскольку единый191MiB архив был
отклонён GitHub. Только собственный неопубликованный commit исправлен после
проверенного preservationbundle; remoteистория не переписывалась. Части проверены HTTP.

ZL17 export6 mean1.344694005, независимая распаковка/ещё6actual mean1.345885435.
После этого ещё раз фактически запущена Diva из H2P и из chunk самого новогоFLP:
all281/12MIDI/rawfloat32/effGetChunk точны, полный native+officialZL из нового raw
дал1.344075286. Отчёт, actualDiva raw/dumps/logs/chunks и свежий финальный WAV здесь.
Новый GUI FL20 экспорт, субъективное прослушивание и точное совпадение не заявляются.

ОБЯЗАТЕЛЬНА новая nativeбаза FL20_NATIVE_ZL_REBASED_03 с источником6.5;
архив в rebased-native-bases/, SHA86643bdb02077aa494de329a174d4510e623de5704440fb0003302f31862251d.
Сохранять native12states, все2+4+8WSmetadata, настоящий Diva chunk, реальные610
параметров ZL. Текущий acceptedprivate mean1.343718283 также сохранён здесь.

Сейчас идёт cycle03: штатный EQ76/WaveShaper16 заново согласуются с принятым
источником6.5 и текущим ZL. Main87/watcher намеренно могут быть остановлены на
границе finitecohort; актуальные fitterPID/phase в ACTUAL_WORK_SNAPSHOT.json и N.
Они снова запускаются после полного экспорта/проверки либо сохранения старого
варианта при отказе. Проверять /procPID/starttime/cmdline: snapshot не доказывает
будущую работу. Actual живые процессы на момент snapshot: [{'state': 'NATIVE_ZL_CONTEXT_CYCLE03_STATE.json', 'PID': 258267, 'phase': 'finite_actual_plugin_job_running'}, {'state': 'ZL_NATIVE_EQ76_STUDY_STATE.json', 'PID': 258351, 'phase': 'actual_native_EQ76_and_fixed_ZL_fit'}].

Onboardingdraft106 сохранён и прочитан обратно точно; repoSHA95477a7e…,
обновлены startupпроверка реального компонента17 и восстановление base03/source.
Изолированное datarestore55files и actualVST3 PDC0/impulse0/statebytes прошли,
bashsyntax проверен. Это не полная установка с нуля. Draft НЕ применён/опубликован;
для будущих запусков нужны Save/Publish в настройках среды. Работа сейчас не блокируется.

Место:58старых явно отклонённых архивов лишились только auxiliaryprefix/freshcheck
WAV, каждый основной/training/recordedWAV и все метаданные/пресеты сохранены.
Освобождено654602241bytes; решения/полные SHA manifests приложены. Старые localZIP
и proofpart дубли выгружены только после точной origin/HTTP проверки, версииGitHub
сохранены. Исходный191MiB архив и три части дополнительно lossless упакованы вGit:
все4 объекта/история сохранены, освобождено ещё~200MBroot; privateдубль можно вернуть
из Gitblob41e9bf7d… или трёх удалённых частей, все96WAVdata сохранены.
Gitconnectivity и все прежние completekit treeOID проверены. Restoreкоманды в receipt.

Процент APIлимита не предоставлен. По просьбе о backup при5% этапы публикуются
сразу после проверки. Оригинал — только analysis/A-B, не источник подмешанного звука.
