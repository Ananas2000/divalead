"""Package the completed independent GUI validation without replacing its failed result."""
from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parent.parent;S=R/'sessions/2026-10-24';E=S/'extension-1621'
O=R/'divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24/extension-1621'
summary=json.loads((E/'FRESH_SUMMARY.json').read_text())
assert summary['pairs']==8 and summary['accepted'] is False
note='''# Финальная независимая GUI проверка, 24 октября 2026, 16:37–16:52 МСК

**База остаётся ZL23. Новый кандидат отклонён.** Пользователь продлил локальную работу ещё на20 минут. В16:52 восстановлен `sessions/2026-10-24/Diva_ZL23_BEST_FL26.flp`; на экране настоящей Diva виден `Diva_ZL23_20261024`. Воспроизведение остановлено на начале, Pattern1,180BPM: Space запускает прослушивание. Скриншот `BEST_RESTORED_1652.png`. Не оставлен capture/bypass проект.

Ранее замороженный кандидат `OPPOSED_CANDIDATE.bin` меняет только TargetGain16 15.11→15.61dB, TargetGain17 15.73→16.23dB и Mid AllPass Freq19 3023.5→3053.7Hz. Он не подстраивался по новой когорте. Источник Diva, native цепочка, objective и выравнивание+819 неизменны.

`CAPTURE_NATIVE_ONLY.flp` фактически открыт в GUI FL26. Standard VST3 Bypass1652125811=1 исключает ZL; реальный GUI export FRESH_00 имеет tone1.535223648, raw peak.7748529, а обработанный ZL tone около1.282, что подтверждает правильную точку съёма. Это НЕ повторная обработка уже полного ZL выхода. Все экспорты float32 stereo48k, Pattern3bars, Leave remainder,512point sinc,HQ,insert/master effects и Trim PDC включены. Экспортировать полную native цепочку через FL20 DLL NULL-host не удаётся; использованы настоящие GUI рендеры FL26.

FRESH_00..05 — шесть последовательных независимых GUI рендеров. Для FRESH_06 и07 каждый раз заново открыт сохранённый capture FLP и вручную через реальный GUI снова загружен именованный User preset Diva. Это две **холодные загрузки проекта/плагинов, не перезапуски процесса FL/Windows**. Все восемь SHA256 источников различаются. В каждом случае один и тот же исходный GUI WAV подан контролю и кандидату в свежие настоящие ZL VST3 процессы; порядок control/candidate чередуется. Тем самым стохастика Diva/Chorus внутри пары совпадает, а между парами меняется.

| Вход | Улучшение objective (положительное лучше) |
|---|---:|
| fresh00 | .000462994103 |
| fresh01 | .000734934469 |
| fresh02 | .000651591593 |
| fresh03 | .000391793144 |
| fresh04 | .000320653080 |
| fresh05 | .000608887669 |
| cold06 | .000379735234 |
| cold07 | **−.000064310003** |

Среднее fresh6 **.000528475676**, SEM **.000065931539**, порог max(.0005,3SEM)=.0005. Fresh часть едва проходит, однако cold07 отрицателен: обязательное условие двух положительных cold улучшений **не выполнено**. Не усреднять cold в свежую шестёрку ради принятия, не отбрасывать последний вход, не снижать порог. Новый принятый пресет/полный GUI candidate render не создавался, поскольку acceptance уже провален. Исследовательский FL20 candidate остаётся seed, не ZL24. Прежний подтверждённый компонент ZL23 SHA25637130685093f401343d9599d86f7426d224187a4c9d0abf1dbae2a8aafad4dce и все281 параметр Diva сохранены.

Все8 исходных GUI WAV,16 парных выходов, JSON с точными loss/tone/standard/peak и SHA, исходник проверки, capture FLP и состояния включены в FRESH_VALIDATION.zip (собирается из частей). Хвосты исходных WAV имеют разные длины222667–225833 сэмпла; метрика использует прежний фиксированный video edit176064, а не подгоняет длину отдельно для кандидата. Это полностью воспроизводимая отрицательная проверка. Full main ZL23 FLP/h2p/A-B и готовый комплект находятся уровнем выше.

## Следующий запуск в облаке

1. Читать этот файл, FRESH_SUMMARY и основной handoff. Скачать все части обоих архивов; `python join_extension_audio.py` собирает исходные57 исследовательских WAV, `python join_fresh_validation.py` собирает эти24 свежих WAV. Проверить SHA256/ZIP CRC. Распаковать с сохранением `local-fl-matching`.
2. Брать подтверждённый ZL23 и его component, не пограничный OPPOSED. Заранее объявить новую гипотезу и training/holdout разбиение: FRESH_00..07 уже использованы для оценки этого кандидата и больше не считаются нетронутым final holdout.
3. Не повторять локальные28+28 конфигураций. Две почти совпадающие Side dynamic полосы имеют derivative cosine .99745; искать в общей/разностной координатах, не считать их независимыми. Совместный gain+phase кандидат недостаточно устойчив; detector SideFreq/SideQ грубые пробы все хуже. Возможная следующая узкая гипотеза — attack/release двух detector полос в общей/разностной координате при фиксированных main gain/frequency/Q; отдельный bounded screen на training без изменения источника.
4. После нового достаточного training улучшения нужны **новые** fresh6/cold2, тот же floor и exact component roundtrip/replay. Source/Chorus модификации требуют новых целых GUI native реализаций и281 readbacks. Для Windows возврата открыть лучший FL26, загрузить актуальный h2p реально в Diva, подтвердить полный GUI WAV и portable kit до повышения статуса. Совпадение с оригиналом пока не достигнуто.

Публикация выполнена через подключённый GitHub connector: у CLI push нет интерактивной авторизации. Не искать токены и не включать DLL/лицензии. Локальный clone может оставаться на14bf899, тогда как remote main содержит новые checkpoint; перед продолжением fetch main и прочитать этот handoff. Окончательный remote SHA записывается отдельно в локальный GITHUB_PUBLICATION_EXTENSION.json после проверки main.
'''
(E/'FRESH_VALIDATION_RU.md').write_text(note,encoding='utf-8')
old=(E/'README_RU.md').read_text(encoding='utf-8')
header='''> **Финальное обновление 16:52:** после нового разрешения пользователя проведены8 независимых GUI проверок. Fresh6 mean+.000528476 проходит floor, но второй cold−.000064310: кандидат отклонён, ZL23 восстановлен в FL. [Полный итог, материалы и следующий план](FRESH_VALIDATION_RU.md). Текст ниже описывает первый этап до этого продления; его утверждения «не снимали/ещё требует GUI» относятся только к тому этапу.

'''
if not old.startswith('> **Финальное обновление'): (E/'README_RU.md').write_text(header+old,encoding='utf-8')
audio=sorted(E.glob('FRESH_??.wav'))+sorted((S/'renders').glob('FRESHPAIR_*.wav'))
assert len(audio)==24,len(audio)
meta=sorted(E.glob('FRESH*.json'))+[E/'FRESH_VALIDATION_RU.md',E/'BEST_RESTORED_1652.png',E/'CAPTURE_NATIVE_ONLY.flp',E/'CAPTURE_BYPASS.bin',E/'OPPOSED_CANDIDATE.bin',R/'tools/fresh_extension_20261024.py',Path(__file__)]
archive=E/'FRESH_VALIDATION.zip';manifest=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in audio+meta:
  arc='local-fl-matching/'+p.relative_to(R).as_posix();z.write(p,arc)
  manifest.append(dict(path=arc,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
with zipfile.ZipFile(archive)as z:assert z.testzip()is None
data=archive.read_bytes();parts=[]
for start in range(0,len(data),10*1024*1024):
 name=f'FRESH_VALIDATION.zip.part{len(parts)+1:02}';b=data[start:start+10*1024*1024];(O/name).write_bytes(b);parts.append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
desc=[dict(file=archive.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),parts=parts)]
(O/'FRESH_VALIDATION_PARTS.json').write_text(json.dumps(desc,indent=2))
(O/'FRESH_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
(O/'join_fresh_validation.py').write_text((O/'join_extension_audio.py').read_text().replace('EXTENSION_AUDIO_PARTS.json','FRESH_VALIDATION_PARTS.json'))
for p in meta+[E/'README_RU.md']:shutil.copyfile(p,O/p.name)
for rel in ['diva-lead/research/native-low-latency-effects/start_skill_current.md','diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24/README_RU.md']:
 p=R/'divalead'/rel;old=p.read_text(encoding='utf-8');link='local-fl-studio/2026-10-24/extension-1621/FRESH_VALIDATION_RU.md'if p.name=='start_skill_current.md'else'extension-1621/FRESH_VALIDATION_RU.md'
 p.write_text('> **Последний локальный итог 24 октября16:52:**8 независимых GUI пар; fresh mean+.000528476, cold2 +.000379735/−.000064310. Кандидат отклонён, ZL23 открыт в FL с правильным h2p. [Материалы и следующий план]('+link+').\n\n'+old,encoding='utf-8')
print(json.dumps(dict(audio=len(audio),bytes=len(data),parts=len(parts),sha256=desc[0]['sha256'])))
