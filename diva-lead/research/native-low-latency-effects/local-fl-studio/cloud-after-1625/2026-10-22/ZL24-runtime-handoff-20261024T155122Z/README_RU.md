# Продолжение ZL24: настоящий двухступенчатый поиск работает

Последний полный проверенный комплект и A/B: [ZL24](../ZL24_CONTINUATION_RU.md).
Четыре настоящих ZL VST3процесса:2worker, каждый основной ZL + фиксированный
Side-only post2200Гц/Q4 и10000Гц/Q2. На момент снимка главный PID361312,
phaseactual_coordinate_sweep_running,cohort5,cases125.
Проверять актуальный N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json и реальные
PID/starttime/cmdline; snapshot не доказывает вечную работу процесса.

ROOT=/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87.
Actual script /workspace/divalead-work/pc-stereo-20261024/continue_stereo_ZL_matching.py.
Не перезапускать устаревшие singleZL continue_ZL_matching.py/watcher:
N/zl-continuation.stop и zl-useful-full-backup.stop оставлены с owner
two-ZL-stereo24-retired-single-stage. Новый stop — N/zl-stereo-continuation.stop,
новый numericalpause — N/zl-stereo-numerical.pause; не снимать чужие ownedстопы.

Поиск меняет87физических параметров только основного ZL, postфиксирован.
Тот же originalFeatures score/weights/819alignment/thresholds/coldrtol8eps
иatol1e-12. Дополнительная защита исправленного стерео: upperbandRMSerror<=1.5дБ,
|LR|<=1.6дБ по2–5/5–10/10–14кГц. Это отдельный gate, не подмена исходногоscore.
Три nativetrainingвхода,2heldout,6новых nativeпар на сохранённом Divaисточнике,
2положительных coldnativeвхода, два coldVSTкаскада и statebytes roundtrip.
Источник/Diva281/native06/fine32/ARP/ADSR/три длинные входящие ноты не меняются.

Каждый устойчивый принятый этап автоматически сохраняется в GitHub: все24
native-input/control/candidate WAV lossless+SHA, компонентprimary+точныйpost,
полный небольшой playable FL20/26 ZIP (FLP/WAV/h2p/MIDI/всеpresets/инструкция).
Эти numerical checkpoints не обозначают новое GUIподтверждение или полное
совпадение. Прежний полный base24 и старые GUI/полные комплекты защищены OID.
Все предыдущие52WAV исходного исследования сохранены в Git.

Перед остановкой Root208MiB/tmp128MiB резервируются для безопасного backup.
Большой archive в рабочем checkout жёстко ссылается на завершённый privateархив,
не копируется зря. После push обе рабочие копии выгружаются только при exactGit
проверке; publicstructuralpromisorgraph сохраняется, blobcache может быть удалён.
Git скачивает архив по требованию. Все refs и privateoriginalsource48 сохранены.
Не выполнять bulk two-treegitdiff/ls-tree--long: они повторно тянут старый кэш.
APIquota% недоступен; законченные полезные этапы сохраняются сразу.

Первая попытка запуска корректно остановилась на Root207.6MiB, поэтому были
выгружены только проверенные опубликованные локальные копии. Не удалены текущие
presets/components/WAV/native06/GUIinputs. Отдельно удалён ТОЛЬКО собственный
unreachable ZIP неудачного stagingдо TSV-formatfix; он никогда не публиковался.
Текущий ZIP16MB доступен на GitHub SHA368fc6eaa7d9b1d8effbcfb5bebe1f2e7530f98904718f510ae0e783180ad9da,
его рабочий cache skipworktree может отсутствовать. Восстанавливать выборочно.

CloudLinux/Wine; новое открытие/экспорт24 в Windows GUI не выполнялось. На ПК
предыдущий GUI ZL23 остаётся отдельным сохранённым файлом. Для загрузки нового
см. инструкцию полного24, два ZL не сводить в один. Полного совпадения пока нет;
продолжать с сохранением улучшенного баланса до совпадения либо фактических лимитов.
