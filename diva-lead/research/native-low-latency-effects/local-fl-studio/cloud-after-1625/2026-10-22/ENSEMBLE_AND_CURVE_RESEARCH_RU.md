# Продолжение подбора после Native WIP12

Последний полный воспроизводимый комплект: [Native WIP13](WIP13_CONTINUATION_RU.md).
Полное совпадение с оригиналом ещё не достигнуто. Поисковые настройки
принимаются только после независимой проверки и не объявляются final.

Проверяются два направления:

- EQ76 подбирается по среднему ошибки трёх настоящих WS/Chorus-рендеров.
  Ещё два рендера не участвуют в обучении; после подбора заново рендерится
  полная цепь, по12 проходов нового и исходного вариантов. При выигрыше
  проводится ещё отдельный выбор и12+12 контрольных проходов.
- Четыре плавные локальные поправки WaveShaper теперь поддерживаются общим
  кодом fitting/export/restore. Все12 native состояний и zero-depth аудио
  побитно совпали с фактически сохранённой DLL-кривой. На текущем улучшенном
  EQ новая кривая прошла выбор12 captures, затем независимые24+24 captures:
  1.575384 против1.578485, SEM0.000317. Принята в полный Native WIP13.
- Измерение WIP12 показало сильный перевес левого верха:5–10kHz около+10dB
  L/R против−0.41dB у оригинала. Исследуется отдельная post-L/R EQ-ветка из
  настоящих Stereo Shaper и EQ2. Первый тест обнаружил перепутанные матричные
  регуляторы; он не был принят. После исправления bypass контроль побитно
  совпал с исходной цепью. Активный flat EQ не предполагается тождественным:
  у настоящей DLL измерено изменение фазы. Сравнение идёт с исходным графом,
  а не только с новой flat-EQ основой. Новая ветка ещё не интегрирована в FLP.

Общий источник: настоящий Diva OscMix6.3/PW KeyFollow+1/VCA ModDepth−58,
только три длинные входящие ноты на фразу, внутренний ARP. Референс используется
лишь для анализа и A/B. Длинная задержка прежнего Finish не возвращается.

Конечные задания получают свою паузу только на границе завершённого цикла
основного поиска и освобождают её вfinally. Обычный подбор затем продолжается.
Для текущего состояния проверяйте живые PID/starttime/cmdline и актуальные
FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json, а затем
FL20_CORRECTED_SEARCH_CONTROLLER.json. Датированные JSON ниже являются снимками.
Это native-DLL проверки в подготовленной среде; новый контрольный экспорт
в GUI FL Studio остаётся отдельной незавершённой проверкой.

Последний снимок: 20261022T233709Z.

- FL20_CORRECTED_SEARCH_CONTROLLER.json: `paused_by_control_or_actual_disk_reserve`.
- FL20_ENSEMBLE_EQ_FINITE.json: `ensemble3_complete_continuous_matching_resumes`.
- FL20_LOCAL4_WS_FINITE_PROFILE.json: `local4_curve_screen_complete_not_automatically_adopted`.
- FL20_POST_LR_EQ_FINITE.json: `post_LR_EQ_failed_preserve_and_diagnose`.
- FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json: `local4_integration_and_repaired_LR_profile_complete_matching_resumes`.
- FL20_POST_LR_EQ_PHASE20_FINITE.json: `post_LR_EQ_phase20_complete_not_automatically_adopted`.
- FL20_POST_LR_CURRENT_COMPARISON_FINITE.json: `post_LR_vs_current_independent24_complete_matching_resumes`.
- FL20_POST_RESEARCH_BEST_BACKUP.json: `actual_best_full_kit_export_validation_or_publication`.
- FL20_EXTRA_MS_EQ_FINITE.json: `queued_after_verified_full_supported_best_backup`.

[Снимки и проверяемые результаты](proofs/ensemble-and-local-curve-20261022T233709Z/).


ПослеWIP13 обычный EQ76 в прежней цепи прошёл полную проверку приmean1.572109
против1.575753 у своей основы. Отдельная post-L/R EQ16 ветка дала1.570970
против старого WIP13-контроля1.576133; добавление4 SS delay/phase controls
дало1.570474 против старого1.575896. Это ещё не подтверждало выигрыш над
обновлённым EQ76. Поэтому отдельно проверены четыре новых/перенесённых
ветки, выбор12 captures, затем24+24:лучший1.570928 против текущего1.571932,
SEM0.000376. Порог3SEM не пройден; новая post-L/R схема НЕ принята.

FL20_POST_RESEARCH_BEST_BACKUP.json отвечает за полный бекап поддерживаемого
улучшенного EQ; его актуальное состояние проверяйте отдельно. Следующий
конечный тест FL20_EXTRA_MS_EQ_FINITE.json проверяет два дополнительных EQ2
в существующих MID/SIDE ветках, без новых маршрутов микшера. Новая схема
исследовательская и не принимается до фактического сравнения и интеграции.
Для места освобождены ещё92 завершённых перезаписываемых host-буфера225MiB,
все meaningful captures, исходники и старые полные комплекты сохранены.
