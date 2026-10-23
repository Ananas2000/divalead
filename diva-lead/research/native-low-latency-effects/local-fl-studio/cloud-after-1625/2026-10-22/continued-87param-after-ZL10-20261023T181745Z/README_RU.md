# Текущее продолжение87params после ZL10

Полного совпадения с оригиналом пока нет. [Полный ZL10 с FLP/WAV/Diva/MIDI/FST/инструкцией](ZL-WIP10/Diva_ZL_10_WIP_complete_WIP.zip)
и [A/B: оригинал0с → ZL10 с4,168с](ZL-WIP10/AB_REFERENCE_ZL10_WIP.mp3).
Полный экспорт6 mean1.411652354, отдельная распаковка/ещё6 actualrenders
mean1.410393589. Числа — прежний полный original-reference критерий, не процент.
Штатная эквализация и поддерживаемая WaveShaper2+4+8форма перенастроены в
контексте настоящего ZL. Потом добавлены две дополнительные динамические
MidPeak полосы:21около5.3kHz (тихий уровень приглушён),22около8.4kHz.
Их реальная работа сначала подтверждена синтетическим тестом официального VST3:
−6dB на тихом синусе и почти0dB на громком. Затем actual6paired на оригинальном
трёхнотном источнике:1.436448947→1.423234635, SEM0.000184997. После совместного
87param refit получен полный ZL10. MinimumPhase/lookahead0/PDC0/impulse0;
это не измерение ASIO/целойDAW. Новый GUIэкспорт FL20 ещё не выполнен.

Свежая фактическая Diva отдельно запущена из H2P и из chunk, извлечённого
из FLP09. Обе:all281/12MIDI/rawfloat32/effGetChunk совпали точно с исходником.
Затем весь actualnative+officialVST3 тракт выполнен из этого нового источника,
loss1.441275041 для тех настроек ZL09. Полный отчёт/WAV/обе sourceпроверки
сохранены в этом checkpoint. Это подтверждение источника и исполненияDSP,
не замена отсутствующему GUI FLэкспорту. Три внешние heldnotes41→37→36 дважды,
ARP/ADSR/Diva source неизменны; оригинал только analysis/A-B, MistaTowa не используется.

Текущий принятый частный mean1.390077411, фактический компонент и все
его independentvalidationWAV также сохранены. В MAIN актуальны реальные
componentXML/610readbacks: унаследованные массивы параметров могут устаревать.
Сейчас12staticPeak+4AllPass+6dynamicPeak; у каждой dynamic настраивается также
baseGain:36+8+42+OutputGain=87. На каждой итерации joint48proposals,
coordinate87,2heldouts,paired6, actualstatebytes и2NEWcoldinstances проверка.
SnapshotactualmainPID235828, snapshotbackupPID235829.
Проверять actualPID/starttime, не считать snapshot постоянным доказательством.

База stockFX теперь FL20_NATIVE_ZL_REBASED_01; брать старую Native17 по умолчанию
нельзя. Её полный проверенный архив сохранён в rebased-native-bases/
FL20_NATIVE_ZL_REBASED_01-verified-base.zip, SHA256
f13ae339bc0c6655d356db417888af71354e5061a18036789074979f4c4e86c3.
Будущий экспорт читает native_base_export_directory и этот архив. Stock-only
mean может быть хуже, важна вся связка native+ZL. Native16 остаётся прежним
самостоятельным stock-only комплектом. Все прежние completekit/treeOID сохранены.

Место дополнительно освобождено строго в127завершённых старых отклонённых
подборах: удалены1016auxiliaryprefix/fresh-check WAV, каждый основной bestWAV,
recordedWAV, все параметры/состояния/метаданные сохранены; принятые варианты,
исходники, runtime и Gitверсии не затронуты. Журнал содержитSHA/решения;
randomChorus trainingrealization при перегенерации может отличаться, основной
WAV каждого старого варианта оставлен. Снято~2.4GiB именно дублей проверок.
Плюс ранее181MB закрытого studyIO/remote-backedduplicatedproof освобождены.
После фактического порога места matcher завершил finitecohort, затем после
очистки был снова запущен. Сейчас вычисления/полные backups реально работают.
Пользователь просит сохранять всё до5%остатка; процентAPIнедоступен, поэтому
проверенные этапы и полные комплекты публикуются по мере готовности.
