# ZL04 — новый полный промежуточный вариант

**Полного совпадения с референсом нет.** Это лучший полностью упакованный
вариант новой low-latency ветки. Только три длинные входящие ноты41→37→36
на фразу, две фразы, прежний внутренний ARP/ADSR и источник Diva.

- [Полный ZIP: FLP, WAV, Diva, MIDI,17FST, VST3 preset и проверки](ZL-WIP04/Diva_ZL_04_WIP_complete_WIP.zip).
- [A/B: оригинал → ZL04 с4,168с](ZL-WIP04/AB_REFERENCE_ZL04_WIP.mp3).
- [Инструкция FL Studio20 и официальный установщик эффекта](ZL-WIP04/FL_STUDIO_RU.md).

Реальные12 штатных эффектов плюс бесплатный официальный **ZL Equalizer2
v1.4.1 Windows x64 VST3**. На SUM: StereoShaper→ZL. Внутри ZL12staticPeak,
2AllPass и4dynamicPeak (2Mid около1–1.3kHz,2Side около2.9kHz), lookahead0,
MinimumPhase. Vendor binaries не включены; ссылка на установщик в инструкции.

От исходной stock Native16 ветки с mean1.552 последовательно получены ZL01,
ZL02, ZL03 и этот65param refit. Последняя подтверждённая private cohort7:
mean1.485810, paired6 против её актуального контроля, все12 validation WAV
lossless-архивированы. В отдельном экспортном6 mean**1.485379268**,
после распаковки нового ZIP ещё6 mean**1.486043351**.
Критерий сравнения с ОРИГИНАЛОМ прежний; это не процент сходства и не новая
оценка старой v83 с недопустимой задержкой Finish.

Все12 native state bytes точны. Реальный ZL component из FLP/FST/VSTpreset
повторил один вход побитно; whole native+ZL zero-depth тоже побитно точен.
Обычный wet WAV меняется между запусками свободного Chorus. ZL PDC0,
impulse first response0; это не измерение ASIO/DAW. Новый FLP ещё не открыт
и не экспортирован из GUI FL на ПК. В инструкции есть fallback FST загрузка.
Полный WAV и все пресеты находятся внутри ZIP.

Предыдущие Native16/ZL01/ZL02/ZL03 и все номерные версии сохранены. Для места
только недавние reachable Git objects упакованы с verify-pack и проверкой всех
refs/HEAD; история не переписывалась. Удалены лишь уже упакованные loose-копии.
После проверки remote ZIP дублирующий файл ZIP в локальном Git checkout может
быть выгружен с skip-worktree: он сохранён на GitHub, в Git object и в частном
`/tmp/divalead-local-1625/Diva_ZL_04_WIP_complete_WIP.zip`. Для восстановления checkout
используйте git restore --ignore-skip-worktree-bits по этому конкретному пути,
либо извлеките Git blob в новую рабочую папку. Это не удаление версии из Git.

Следующее продолжение — настоящий VST3 matcher и N/FL20_ZL_CONTINUOUS_CONTROLLER.json;
проверяйте реальные PID/starttime и текущие дисковые резервы. Snapshot stopped
после завершённой7 когорты из-за фактического /tmp резерва; не выдавать его за
работающий. После бэкапа можно освобождать только лишние проверенные staging
дубликаты и возобновлять от BEST_CANDIDATE при достаточном фактическом месте.
Новый topology не поддерживается обычным native x95 exporter.
