"""Build an explicit, portable checkpoint; do not package installed plugin DLLs."""
from pathlib import Path
import hashlib,json,zipfile,shutil,struct
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parent.parent
S=ROOT/'sessions/2026-10-22'
OUT=S/'checkpoint';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
direct=sf.read(S/'renders/DIVA_FRESH_DIRECT.wav',dtype='float32',always_2d=True)[0]
frozen=sf.read(S/'input/Diva_SOURCE_FROZEN_48k.wav',dtype='float32',always_2d=True)[0]
verified=sf.read(S/'renders/DIVA_FROM_FLP_VERIFIED.wav',dtype='float32',always_2d=True)[0]
proof=dict(direct_equals_kit_source=bool(np.array_equal(direct,frozen)),extracted_flp_source_equals_direct=bool(np.array_equal(verified,direct)),all281_dump_equal=(S/'DIVA_FRESH_ALL281.tsv').read_bytes()==(S/'DIVA_FROM_FLP_VERIFIED_ALL281.tsv').read_bytes(),source_samples_sha256=hashlib.sha256(direct.tobytes()).hexdigest(),native_dsp_declared_pdc_frames=0,end_to_end_latency_measured=False,match_reached=False)
assert all(proof[k]for k in ('direct_equals_kit_source','extracted_flp_source_equals_direct','all281_dump_equal'))
(OUT/'SOURCE_PROOF.json').write_text(json.dumps(proof,indent=2))
rankings={}
for folder in ('diva-source-screen','native-phase-screen'):
    r=json.loads((S/folder/'ranking.json').read_text())
    rankings[folder]=dict(trials=len(r),best=[{k:v for k,v in row.items()if k not in ('metrics','actual_values')}for row in r[:8]],accepted=False)
(OUT/'RESEARCH_SUMMARY.json').write_text(json.dumps(rankings,indent=2))
doc='''# Продолжение локальной сессии FL Studio — 22 октября 2026

## Текущий результат

Это рабочая контрольная точка, совпадение с оригиналом НЕ достигнуто. Текущий локальный проект: `Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp`, фактический рендер из FL: `renders/FL_NATIVE_04_CALIBRATED.wav`. Ни один из новых вариантов тембра не принят как улучшение. Предыдущая v83 всё ещё ближе по исходным критериям, но её Finish имеет неприемлемую задержку 12416 frames.

Продолжать нужно с исходного задания `../LOCAL_FL_STUDIO_HANDOFF_RU.md` и набора `../after-DSP-arrival/checkpoint-WIP/`, затем прочитать этот файл. Пользователь разрешил загрузить результаты в этот же GitHub и попросил при остатке лимита 5% сразу зафиксировать работу и планы. Часовые ограничения относятся к сессии 22 октября; новый запуск не должен автоматически ожидать свободной мыши.

## Что действительно сделано в FL

FL Studio 20.0.3 build 532 x64, Diva VST2. Исправлена несовместимость облачных mixer FST: event 98 должен завершать блок, а DWORD offset 4 в event 212 должен содержать настоящий индекс слота. Все 12 родных DSP-состояний загружены и побайтно совпадают с комплектом. Исправленные FST лежат в `compatible-presets/`; предыдущий коммит содержит описание формата.

Построена и проверена маршрутизация SOURCE(1)→MID(2)/SIDE(3)→SUM(4)→Master. SOURCE не идёт прямо в Master. Все фейдеры 0 dB, pan/separation=0. Chorus slot mix=4923/12800. Сохранённый FLP содержит ровно шесть длинных нот, 180 BPM, PPQ 96: 41/37/36, позиции 0/144/288 и 768/912/1056, длины 144/144/96, velocities 96/96/101. Верхние ноты делает ARP Diva. Аудиосэмпл оригинала не используется в синтезе.

В FLP сохранён именно нужный Diva: извлечён настоящий h2p из VST wrapper chunk, все 281 значения совпали. Отдельный свежий запуск установленной Diva с извлечённым h2p дал побитно тот же raw-аудиомассив, что и штатный h2p; raw также побитно совпадает с `Diva_SOURCE_FROZEN_48k.wav` в текущем комплекте. См. SOURCE_PROOF.json и TSV. Следовательно имя FROZEN у ЭТОГО файла не означает старый пресет: здесь уже принятые PWModDepth +1.00 и KeyFollow2.

## Уровень — важная поправка

Исходный GUI-проект 01 имеет channel-volume raw=10000/12800. Это нельзя линейно делить на 0.78125 и выдавать за положение регулятора unity. Реальный переход регулятора FL к raw=12800 увеличил аудио в 1.8148577 раза. Проект `02_UNITY` — отклонённый эксперимент, peak=1.1468, НЕ использовать как правильную версию.

Raw bypass в данном маршруте при отключении всех insert FX складывает две одинаковые ветки: делить его на 2 перед сравнением с Diva source. Измеренное исходное отношение к direct Diva около 0.77916. Калибровочный проект03 raw11172 дал отношение1.00518; поэтому выбран проект04 raw11148. Сохранённые DSP, ноты и маршруты при этом не изменены. AB RMS-gain рендера04=1.03807, близко к облачному контрольному уровню.

## Проверка качества (меньше лучше; это не процент сходства)

| Версия | Исходный score | Tone score | Комментарий |
| --- | ---: | ---: | --- |
| v83 | 0.9011 | 0.8044 | Сравнительная опора; задержка Finish12416 |
| Облачный native WIP | 1.7404109 | 1.65705 | Исходная контрольная точка |
| Локальный FL01 | 1.84261 | 1.78914 | Старый уровень канала |
| Локальный FL04 | 1.8140361 | 1.7485874 | Фактический рендер FL, peak0.71947 |
| Offline native, direct Diva | около1.742 | около1.66 | Полная родная цепь, свежий Chorus |

Все критерии взяты из исходного репозитория без перенастройки весов под результат. Анализ применяет только документированные +819 frames и монтаж референса. Chorus свободно запускает LFO, поэтому один удачный рендер не доказывает улучшение.

Полные метрики FL04: H24=2.33352, upper_harm=2.40776, upper_off=5.18410, ERB=1.44553, relative_phase=1.26043, stereo_phase=17.1544°, stereo_balance=4.18356dB. Сведение RMS каналов к одинаковым значениям не решает характер стерео оригинала. Между raw FL03 и direct Diva корреляция mono≈0.999596; после скалярного gain-fit остаётся residual≈2.85%. Причина остатка GUI/offline ещё не установлена. Не объявлять перенос побитно одинаковым целиком только на основании точного preset/state.

## Поиски и отрицательные результаты

1. `fit_local_eq.py`: 831 оценка, fast-proxy улучшился примерно на19%, но три независимых полных native рендера дали score≈2.28 вместо1.74. ОТКЛОНЁН. Его EQ bin не подставлять в финальный FLP.
2. `fit_original_gain_matrix.py`: 469 оценок исходного критерия, L-BFGS завершился ABNORMAL, улучшение лишь порядка шума. ОТКЛОНЁН.
3. `screen_local_diva.py`: 63 свежих Diva+native рендера с подтверждением281 параметра и12 MIDI-событий. Проверены cutoff/resonance/PW/modulation/drift/fine tune/envelopes/reverb/pan. Малые улучшения score у moddepth-3/-4 не подтверждены повторами; tone почти прежний. Ничего не принято.
4. `screen_native_phase.py`: 65 проб common phase pair, SUM phase/delay, Chorus mix. Крупная сетка не дала устойчивого улучшения исходной точки. Кандидатов не принято.

В RESEARCH_DETAILS.zip сохранены параметры, native bin, полные ranking JSON, все TSV/h2p/log новых проб. Многократно воспроизводимые промежуточные WAV в архив не включены; они остались на ПК. Файлы DIVA_FROM_SAVED_PROJECT из первой попытки неверно передавали wrapper chunk в Diva и вернули defaults: их результаты недействительны и в архив не включены. Правильный результат имеет имя DIVA_FROM_FLP_VERIFIED.

## Где продолжать на ПК

Рабочий корень: `D:\\проекты фл\\Diva пытаемся накрутить лид\\codex\\local-fl-matching`. Все новые файлы класть внутрь него. Установленные DLL читать из разрешённых папок, не загружать DLL/лицензии в GitHub. Diva DLL: `C:\\Program Files\\VstPlugins\\Diva(x64).dll`. Native DLL: `C:\\Program Files\\Image-Line\\FL Studio 20\\Plugins\\Fruity\\Effects\\<Name>\\<Name>_x64.dll`.

Открыть04 FLP; если потребуется создать новый проект и FL спросит о более новой версии — Yes, при invalid data — No. Пустой исходный проект специально сохранять не нужно. В параметрах рендера:48k, WAV float32 stereo, Pattern3bars, HQ all plugins, insert/master effects ON, Leave remainder. После bypass-проверок обязательно вернуть insert effects ON.

Нативные эффекты декларируют PDC0. Реальная end-to-end задержка не измерена. FLASIO512frames и прочая буферизация остаются; нельзя писать, что доказана нулевая задержка всего тракта.

## Воспроизведение offline / облако

В дереве `tools/native-host` сохранены адаптированные исходники существующих исследовательских хостов. Для запуска на Windows нужен уже установленный MinGW gcc, numpy/scipy/soundfile. Собирать из local-fl-matching:

```powershell
gcc -O2 -static -o tools/native-host/fl_native_probe.exe tools/native-host/fl_native_probe.c -lole32 -luuid -luser32 -lgdi32
gcc -O2 -static -DFL_PRESET_GRAPH -DCOMMON_PHASE_PAIR -o tools/native-host/fl_native_common_phase_host.exe tools/native-host/fl_native_chain_host.c -lole32 -luuid -luser32 -lgdi32
gcc -O2 -static -o tools/native-host/diva_source_render_host.exe tools/native-host/diva_source_render_host.c
python tools/native-host/render_diva_fresh.py
python tools/verify_saved_flp.py sessions/2026-10-22/Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp
python tools/assess_local_render.py sessions/2026-10-22/renders/FL_NATIVE_04_CALIBRATED.wav
```

Облачный Linux не может запускать FL GUI нативно: использовать существующий облачный Wine/native workflow из репозитория; установленные DLL в checkpoint не входят. Портативный analysis-runtime содержит исходные Python-модули и ranking_scales; WAV референса для пути `analysis-runtime/diva-lead/research/v55-wip/Diva_original_lead_reference.wav` взять из исходного репозитория. `local_native_chain.py` ориентирован на реальные Windows DLL; менять платформенную оболочку отдельно от DSP.

## Следующие конкретные шаги

1. Не менять сразу весь пресет. Сначала повторить FL04 3–5 раз и raw bypass с тем же состоянием/HQ, проверить остаточную разницу GUI/offline и разброс Chorus. Уточнить channel gain только по фактическому аудио.
2. Подтвердить moddepth-3/-4 на 10 свежих полных рендерах с исходными критериями; принять только устойчивое улучшение и затем обязательно проверить фактическим FL рендером.
3. Малую сетку SUM phase/delay вокруг0 можно исследовать отдельно; крупная сетка уже отрицательная. Исходная форма гармоник/relative phase остаётся существенным ограничением.
4. Возможная новая структура: родной Fruity Phaser как static all-pass/comb. Только probe сделан:9params, declared PDC0, default state40bytes. Sweep2500, min100,max800,range0,stereo512,stages7,feedback400,drywet512,output4000. Пока НЕ включён в цепь и НЕ проверен как улучшение. Сначала bypass-null, затем min=max,feedback0,stereo0,stages/wet/frequency. Нужны полные свежие рендеры, проверка конечности/PDC, затем реальный FLP и GUI-render.
5. Если структура не помогает, пересмотреть waveshaper polynomial/распределение фаз по гармоникам. Не повторять оптимизацию proxy, уже провалившую полную проверку.

## Управление экраном и сохранение

Используется computer-use skill и @oai/sky. Штатный WGC выдавал FrameArrived timeout; пользователь разрешил ограниченный GDI-захват видимого FL и fl_click.py. Capture маскирует всё вне окон того же PID, click проверяет свежесть≤90s, foreground PID, bounds, hash и локальный patch. Если захват ещё работает — дождаться exit0 и НЕ смотреть старый PNG. Окно должно быть видимо и desktop разблокирован. Координаты брать из свежего полного размера, не из уменьшенной картинки. После каждого действия — новое наблюдение.

GitHub checkpoint опубликован через Git blobs/tree/commit/ref с expected_sha; локальный sparse clone может отставать, не делать слепой push. Нужна новая проверка main перед следующей записью. Пользователь уже разрешил публикацию результатов этого проекта. Если физический Esc остановит Computer Use, прекратить ввод и ждать нового указания; последний случай был мискликом, после него пользователь снова сказал продолжать.
'''
(S/'LOCAL_CONTINUATION_RU.md').write_text(doc,encoding='utf-8')
archive=S/'RESEARCH_DETAILS.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for folder in ('diva-source-screen','native-phase-screen','local-eq-search','original-gain-search'):
        for p in sorted((S/folder).rglob('*')):
            if p.is_file()and p.suffix in ('.json','.tsv','.h2p','.log','.bin')and not any(x in p.parts for x in ('cache','scores','__pycache__')):
                z.write(p,p.relative_to(S))
    for name in ('DIVA_FRESH_ALL281.tsv','DIVA_FROM_FLP_VERIFIED_ALL281.tsv','DIVA_FROM_FLP_EXTRACTED.h2p','DIVA_FROM_FLP_VERIFIED.log','native-parameter-snapshot.json','PHASER_DEFAULT.bin'):
        z.write(S/name,name)
paths=[S/'LOCAL_CONTINUATION_RU.md',archive,S/'Diva_NATIVE_LOCAL_01_WIP.flp',S/'Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.flp',S/'Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.verification.json',S/'Diva_NATIVE_LOCAL_04_CALIBRATED_WIP.changes.json',S/'renders/FL_NATIVE_04_CALIBRATED.wav',S/'assessment/FL_NATIVE_04_CALIBRATED.json',S/'checkpoint/SOURCE_PROOF.json',S/'checkpoint/RESEARCH_SUMMARY.json']
paths += sorted(p for p in (ROOT/'tools').rglob('*')if p.is_file()and p.suffix in ('.py','.c')and '__pycache__'not in p.parts)
paths += sorted(p for p in (ROOT/'analysis-runtime').rglob('*')if p.is_file()and p.suffix in ('.py','.json')and '__pycache__'not in p.parts)
manifest=[]
for p in paths:
    local=p.relative_to(ROOT).as_posix()
    dest=local.replace('sessions/2026-10-22/','2026-10-22/',1)
    manifest.append(dict(local=local,repo='diva-lead/research/native-low-latency-effects/local-fl-studio/'+dest,bytes=p.stat().st_size,sha256=sha(p)))
mp=S/'UPLOAD_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2))
manifest.append(dict(local=mp.relative_to(ROOT).as_posix(),repo='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22/UPLOAD_MANIFEST.json',bytes=mp.stat().st_size,sha256=sha(mp)))
(OUT/'UPLOAD_PLAN.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(dict(files=len(manifest),bytes=sum(x['bytes']for x in manifest),archive_bytes=archive.stat().st_size,proof=proof)))
