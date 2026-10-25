# ZL25: работающий поиск, два реальных ZL, восстановление

[Полный комплект ZL25, A/B и FLинструкция](../ZL25_CONTINUATION_RU.md).
В момент снимка PID385444, phaseactual_independent6_paired_validation, cohort29,
casesNone. Проверены PID/starttime/cmdline главного процесса
и четырёх настоящих официальных VST3host. Снимок не доказывает будущую работу.

Текущий процесс: A/continue_stereo_ZL_matching.py,
A=/workspace/divalead-work/pc-stereo-20261024,
N=/workspace/divalead-work/native-low-latency-effects,
N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json и
A/stereo-continuous87/BEST_CANDIDATE.json — актуальные контроллер/кандидат.
D=/tmp/divalead-local-1625/internet-plugins-20261023,
W=/tmp/divalead-native-effects,B=/tmp/divalead-local-1625,
PYTHONPATH=A:D:W:B. Python /workspace/.venvs/divalead/bin/python -B,
OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1,PYTHONDONTWRITEBYTECODE=1.

Два worker по два реальных ZL. PRIMARY87параметров ищется, POST фиксируется
при старте из актуального BEST, SHA51dd979271b5fbfda5cffbd8cb71796009a5b3cc305289bbf9c472c672a7a96e.
POST содержит три Side AllPass10000Hz/Q2+2200Hz/Q4+895.8Hz/Q13.84.
Это два экземпляраZL, не три. Нельзя восстановить старый hardcodedPOST24.
Новый runtime и две его холодные цепочки проверены: replay0/0, exactbytes.
Новая generic startupпроверка verify_current_stereo_environment_runtime.py
--kit ZL-WIP25 --receipt /workspace/divalead-setup/STEREO25_ENV_STARTUP_PROOF.json
реально исполнялась: combinedZLPDC0/impulse0. Не ASIO/новыйGUI/всяDAW.

Прежний originalobjective, выравнивание819, tolerances и fresh6порог
max(.0005,3SEM), cold2positive сохранены. Дополнительная защита стерео:
upperRMSerror<=1.5dB,max|LR|<=1.6dB в2–5/5–10/10–14kHz;
после ZL25 ещё |LR300–800−original|<=3.35dB. Это extra preservation gate,
не изменение прежнего score. Низкая середина пока~4.2dBLeft vsoriginal~1dB.
Источник actualDiva281/native06/fine32/ADSR/ARP/3longnotes41→37→36twice
не меняется. Новые nativeDLLреализации используют сохранённый реальный
Divaисточник; новыеDivaэкземпляры/GUIэкспорты не заявляются. SoundmatchFALSE.

После принятого этапа автоматический publisher сохраняет все24WAVinput/
control/candidate lossless, оба компонента и полный небольшой playableZIP
FLP/FST/WAV/h2p/MIDI/инструкция. Он теперь читает artifact_layout.json
и full_public_kit_directory, сохраняет post25/его три полосы. Прежний singleZL
publisher это делать не умеет. Старые N/zl-continuation.stop и
zl-useful-full-backup.stop сowner two-ZL-stereo24-retired-single-stage
оставлены. Новый stop zl-stereo-continuation.stop, pause zl-stereo-numerical.pause;
не снимать чужой pause/stop. Root208MiB/tmp128MiB guards защищают backup.

На новом восстановлении сначала сверить актуальный start_skill_current.md
и живые PID/cmdline; не плодить процессы. Если A отсутствует, создать его и
скопировать пять scripts/*.py. Если BEST отсутствует, восстановить приложенный
CURRENT_BEST_AT_HANDOFF.json в A/stereo-continuous87/BEST_CANDIDATE.json,
проверить paths и соответствие primary/post сохранённому acceptedstage.
Не перезаписывать более новое существующее состояние. Нужны уже подготовленные
runtimehost/nativebase06/actualDivasource из сохранённого setup. На чистой новой
машине весь bootstrap этой стадии отдельно не исполнялся; это не fresh-taskproof.
Запускать только после реальных startup/statechecks. Не запускать старую
continue_ZL_matching.py/watcher. Исторический setup55 — readinessfixture,
его FinishVST с задержкой не является рабочей цепью.

В этой стадии освобождены только byte-verified локальные publicaudioкопии
и закрытые старые regenerableVSTscratch. Старые Gitверсии/refs/полныеZIP/PCGUI
не удалены. В рабочем publiccheckout могут отсутствовать WAV/ZIP сskipworktree;
это ожидаемый cache, восстанавливать выбранный файл через gitshow нужногоref.
Publicpromisorobjectcache тоже содержит ожидаемые старые holes. Избегать bulk
two-treegitdiff и ls-tree--long. Privateoriginalsource48/blob41e9bf7d7adba68226614297644c9661181bff6d
и его refs/archive/unpublished-pre-split-f3ed5c50 сохранены. No forcepush.
APIquotaпроцент недоступен; готовые полезные этапы сохраняются сразу.
До совпадения остаются различия. Продолжать, без вопросов по каждой пробе.
