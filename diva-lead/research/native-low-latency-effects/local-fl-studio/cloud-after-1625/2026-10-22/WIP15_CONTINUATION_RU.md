# Native WIP15: полный промежуточный комплект

[Короткое A/B: оригинал → Native WIP15](listening-Native15/AB_REFERENCE_NATIVE15_WIP.mp3).
Наш вариант начинается с4.168с. [Полный ZIP: FLP/WAV/Diva/MIDI/16FST/проверки](WIP15/Diva_NATIVE_15_WIP_complete_WIP.zip).
[Как открыть в FL Studio20](WIP15/FL_STUDIO_RU.md).

Уточнены EQ в прежней цепи SOURCE → MID/SIDE → SUM. Источник: настоящий Diva
OscMix6.3, PW KeyFollow+1, VCA ModDepth−58. Три удерживаемые ноты на фразу,
две фразы, внутренний ARP. Поддерживаемая кривая WaveShaper сохранена в
состоянии native плагина:2 исходных коэффициента и4 локальные поправки
smooth_local_bumps4_v1; текущая поправка[0,0,0.025,0].

Дополнительно приняты8 узких поправок smooth_detail_bumps8_v1: [0.00025, 0.00075, -0.008, 0.00525, -0.004, 0.0, 0.006, -0.015]. Все2+4+8 коэффициентов входят в native состояние и общий helper для fitting/export/replay; отдельно проверены реальные12 states и zero-depth audio, затем независимые24+24.


Отдельный полный экспорт6 captures:mean1.556936517,
std0.000639733; у WIP14 mean1.571449147.
Это критерий ошибки, не процент сходства. В ZIP медианный WAV, не лучший.
Только A/B выровнен по RMS; полный6с WAV48kHz stereoFLOAT32 не изменён.

ZIP восстановлен в новой папке этой подготовленной среды. Все12 native
состояний и реальный program chunk Diva совпали; zero-depth контроль
побитно точен. Шесть новых обычных рендеров:mean1.556223276,
std0.001082365. Работающий Chorus свободно
меняет повторные WAV. Это не тест новой машины или новый экспорт из GUI FL.
Полного совпадения с референсом пока нет; GUI экспорт ещё предстоит.

Проверены две отдельные post-L/R EQ/phase ветки. Их первоначальный выигрыш
относился к более старой основе. На обновлённом EQ, после выбора4 веток и
ещё24+24 независимых рендеров:1.570928 против1.571932, SEM0.000376;
порог3SEM не пройден. Эти новые маршруты не включены в комплект.

Дополнительные MID/SIDE EQ16 и цепь EQ→WaveShaper→EQ проверены на
настоящих DLL и не приняты. Физические Diva Pan−20 и Pan0 получили свои
EQ76 и controls fit: лучший независимый результат1.628857 против1.572446,
то есть хуже. Производственный источник и его Pan−39.33 сохранены.

Новое исследование: внутренний Plate2 Wet Diva1.12 оставляет предыдущую
ноту в октавных окнах заметно сильнее референса. Настоящая Diva с Wet0 и0.1
проверена по281 параметру,12 MIDI событиям и двум свежим загрузкам h2p/
реального native chunk; относительное изменение только index235. С Wet0
после полной прежней FX цепи half-carrier/carrier снизился на24–27dB.
Это спектральная диагностика остатка ноты, не процент сходства или шумомер.
Прямое сравнение с прежней обработкой пока хуже по полному критерию:
Wet0.1 mean1.635701 против1.571826, independent24+24. Поэтому сухой источник
не принят по этому прямому тесту. Его отдельные EQ76/controls refit и новая
независимая проверка описаны в FL20_DIVA_PLATE_SOURCE_PROFILES.json.
Следующее исследование:8 узких поправок WaveShaper поверх2+4 прежних.
Исследовательская metadata защищена от обычного exporter; принятие возможно
лишь после реального state/audio round-trip и независимого сравнения.
Общий старый критерий не менялся; residue измеряется отдельно. Смотрите также
FL20_DETAIL8_WS_FINITE_PROFILE.json,
затем corrected controller с проверкой PID/starttime/cmdline.
Снимки ниже — история, не текущий статус. Никакого полного совпадения нет.

Статус на момент резервной копии:

FL20_DIVA_PLATE_SOURCE_PROFILES.json: conditional_Diva_Plate_profiles_completed_continuous_matching_resumes. {"proposals": 4, "selection_captures_per_path": 12, "independent_captures_per_path": 24, "independent_selected_mean": 1.6089866493752314, "independent_control_mean": 1.5718711591706598, "SEM": 0.0003025440459436203, "robust_improvement": false, "actual_native_DLL_audio": true, "match_reached": false}

FL20_DETAIL8_WS_FINITE_PROFILE.json: detail8_curve_screen_complete_not_automatically_adopted. {"cases": 398, "fresh_mean_loss": 1.5572427824070176, "fresh_control": 1.572324017290211, "robust_improvement": true, "seconds": 253.2683860440011, "match_reached": false}

FL20_DETAIL8_INTEGRATION_AND_BACKUP.json: supported_detail8_complete_kit_published_and_actual_ZIP_replayed_continuous_matching_resumes. {"proposals": 2, "selection_captures_per_path": 12, "independent_captures_per_path": 24, "independent_selected_mean": 1.5574531502609343, "independent_control_mean": 1.571895874996187, "SEM": 0.00038455719525226634, "robust_improvement": true, "actual_native_DLL_audio": true, "match_reached": false}

[Снимок состояния и проверки](proofs/WIP15-continued-20261023T012630Z/).
Сохранены все номерные версии, старые полные комплекты и полезные captures.
Для места удалены только проверенные перезаписываемые рабочие буферы.
Исторические A/B cache и captures завершённых отвергнутых cohorts сжаты
без потерь; SHA каждого WAV проверен до освобождения несжатой копии.
Исходники и релизы сохранены; пооперационные квитанции включены в proofs.
