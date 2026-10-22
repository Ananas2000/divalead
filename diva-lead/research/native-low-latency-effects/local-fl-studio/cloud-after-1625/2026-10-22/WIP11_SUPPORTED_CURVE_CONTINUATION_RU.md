# Поддерживаемая кривая и полный WIP11

[Полный ZIP, FLP, WAV, Diva, MIDI и16 FST](WIP11/Diva_NATIVE_11_WIP_complete_WIP.zip).
[Инструкция для FL20](WIP11/FL_STUDIO_RU.md).
[A/B: оригинал → v83 → реальный FL05 → WIP11](WIP11/AB_ORIGINAL_V83_ACTUAL_FL05_Diva_NATIVE_11_WIP.mp3).
WIP11 начинается с12.504с. Три длинные ноты на фразу и ARP сохранены.
Полного совпадения с референсом или переносаv83 пока нет; новый GUI FL export
ещё предстоит. Это WAV настоящих native DLL и подготовленный FLP.

Ошибка независимого6+6 сравнения:1.586350→1.583332, SEM0.000655.
Отдельный экспорт6 рендеров: mean1.583736/std0.001179; WIP10 mean1.588693.
Эти числа — ошибки, не проценты сходства. В новом каталоге восстановлен
опубликованный ZIP:6 новых DLL captures mean1.582952/std0.000522. Все12 native
состояний и program Diva совпали с FLP/ZIP, контрольный zero-depth WAV побитно
точен. Это проверка подготовленной машины, не нового компьютера или GUI FL.

Состояние WaveShaper теперь включает дополнительные2 коэффициента. Они
поддерживаются fl20_curve.py во всех актуальных playback/fit/controls/export/
latency/restore scripts. Новый shared helper дал ровно те же12 native states
и zero-depth audio, что настоящий сохранённый native preset. Сам FLP/FST
содержит готовую кривую; пользователю не требуется вводить её формулу.

Для продолжения подбора x95 недостаточно: сохраняйте source_manifest,
chorus_overrides, waveshaper_curve_format=native_monotone_bump_v1 и
waveshaper_curve_adjustment=[0.2995963583619089,-0.4069654303527342].
Применяйте apply_candidate(c,x,candidate) из fl20_curve.py, затем Chorus
settings. Голый apply(x) потеряет кривую. Кандидат из раннего исследования
с флагом not_compatible_with_standard_x95_exporter=true по-прежнему не
принимается: используйте полностью проверенный WIP11 с поддерживаемым форматом.

Предыдущий старый curve fit03 намеренно закрыт через SIGINT/finally ради
проверенного улучшения; его training не принят. Новый controller установлен
только на наблюдаемой idle границе. Интеграционный pause снят после фактической
проверки восстановления. Сейчас идёт следующий реальный четырёхпроцессный fit
с кривой WIP11. Контролируется FL20_CORRECTED_SEARCH_CONTROLLER.json и реальные
PID/starttime/cmdline. Старые finite snapshots описывают завершённые задания.
Ротация: EQ coordinates → controls/SIDE/curve → scaled EQ → controls/SIDE/curve.
Все новые best требуют свежих полных6+6; полезные улучшения получают полный
комплект и Git backup. Прежние WIP, FL05, номерные версии и корневые ZIP сохранены.
