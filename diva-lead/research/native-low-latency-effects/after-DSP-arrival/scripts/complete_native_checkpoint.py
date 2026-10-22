"""Add honest FL instructions and level-matched A/Bs to a verified native WIP."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np
import soundfile as sf
root=Path(sys.argv[1]);source=Path('/workspace/divalead/diva-lead/v83-wip')
proof=json.loads((root/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
chorus=proof.get('modulated_audio_sample_exact_expected') is False
mix_percent=proof.get('native_Chorus_mixer_slot_mix_percent',0)
assert not proof['v83_transfer']['decoded_float32_bit_exact'] and not proof['match_reached']
native=sf.read(root/'NATIVE_REFERENCE_EDIT_WIP.wav',dtype='float64')[0]
original=sf.read(source/'Diva_original_lead_reference.wav',dtype='float64')[0]
old=sf.read(source/'Diva_Lead_v83_REFERENCE_EDIT.wav',dtype='float64')[0]
rms=lambda y:float(np.sqrt(np.mean(y*y)))
gains=[1.,rms(original)/rms(old),rms(original)/rms(native)]
gap=np.zeros((24000,2));ab=np.concatenate([original,gap,old*gains[1],gap,native*gains[2]])
peak=float(abs(ab).max());global_gain=min(1.,.95/max(peak,1e-30));ab*=global_gain
sf.write(root/'AB_ORIGINAL_V83_NATIVE_WIP.wav',ab,48000,subtype='PCM_24')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(root/'AB_ORIGINAL_V83_NATIVE_WIP.wav'),'-codec:a','libmp3lame','-b:a','320k',str(root/'AB_ORIGINAL_V83_NATIVE_WIP.mp3')],check=True)
(root/'verification/AB_LEVELS.json').write_text(json.dumps(dict(order=['original','v83','native-WIP'],starts_seconds=[0,len(original)/48000+.5,2*(len(original)/48000+.5)],per_clip_RMS_gains=gains,common_peak_safety_gain=global_gain,only_AB_is_gain_normalized=True,full_native_render_not_gain_normalized=True),indent=2)+'\n')
guide='''# Штатные эффекты FL — технический WIP

Это рабочий перенос на родные эффекты, **звучание v83 ещё не сохранено на 100%**.
До оригинала он тоже пока дальше, чем v83. Основным результатом остаётся v83;
этот комплект сохранён для проверки малой задержки и дальнейшего подбора.
В FL Studio GUI комплект здесь не открывался. Проверены формат FST, настоящие
DLL эффектов и повторный рендер после загрузки сохранённых настроек.

## Загрузка в FL Studio

1. Открой отдельный тестовый проект, выставь **180 BPM**. Загрузи Diva и в её
   браузере пресетов открой `Diva_Lead_v83_WIP.h2p`. Перетащи
   `Diva_THREE_HELD_180BPM.mid` на Diva. Здесь **три длинные входящие ноты**
   на фразу: MIDI 41 → 37 → 36, две фразы. Внутренний ARP Diva включён;
   верхние движения не расписаны дополнительными входящими нотами.
2. Выдели четыре пустых дорожки микшера: **SOURCE, MID, SIDE, SUM**.
   Направь Diva на SOURCE.
3. Открой соответствующее состояние дорожки через меню микшера
   **File → Open mixer track state**: `presets/01_SOURCE.fst`,
   `02_MID.fst`, `03_SIDE.fst`, `04_SUM.fst`.
   Если версия FL не открывает состояние целой дорожки, добавь штатные эффекты
   в порядке из таблицы и загрузи одноимённые отдельные `.fst` в их окнах.
4. Вручную выставь маршрутизацию ниже. Пресеты дорожек её не сохраняют.
   Все указанные посылы — **100%**, фейдеры — **0 dB**, панорама и Stereo
   Separation — по центру. Лишние посылы выключи.

| Дорожка | Слоты по порядку | Куда отправить |
| --- | --- | --- |
| SOURCE | WaveShaper: `SOURCE_WaveShaper.fst` | Только MID и SIDE, Master выключен |
| MID | Stereo Shaper: `MID_Encode`; EQ 2: `MID_EQ_A`; EQ 2: `MID_EQ_B` | Только SUM, Master выключен |
| SIDE | Stereo Shaper: `SIDE_Encode`; EQ 2: `SIDE_EQ_A`; EQ 2: `SIDE_EQ_B`; Stereo Shaper: `SIDE_Decode` | Только SUM, Master выключен |
| SUM | Stereo Shaper: `SUM_Stereo.fst` | Только Master |

Сокращения в таблице обозначают соответствующие `.fst` из `presets`.
Инверсия одного канала на SIDE — часть M/S-декодирования; оценивать надо SUM.
В тестовом проекте старый Finish не нужен. Используются встроенные
**Fruity WaveShaper, Fruity Parametric EQ 2, Fruity Stereo Shaper**.
Сканировать присланные DLL как VST не требуется; они в комплект не включены.

## Прослушивание и задержка

`NATIVE_FULL_180BPM_WIP.wav` — полный нативный рендер без скрытой подгонки
уровня и времени. `NATIVE_REFERENCE_EDIT_WIP.wav` — прежний монтаж под
оригинальный фрагмент. В A/B порядок **оригинал → v83 → штатная цепочка**;
только для A/B средние уровни выровнены, коэффициенты есть в `AB_LEVELS.json`.

Эффекты заявляют **0 сэмплов PDC** против 12416 у старого Finish при 48 kHz.
Это не измерение задержки звуковой карты или всего FL. В контрольном импульсе
нет отклика до входного сигнала. Смена размера блока немного меняет отсчёты;
числа записаны в `NATIVE_LATENCY_AND_BLOCKS.json`.

`Diva_SOURCE_FROZEN_48k.wav` — сохранённый сырой источник для точного сравнения
эффектов. У живого синтезатора результат также зависит от истории запуска;
здесь источник заново отрендерен через Diva и совпал с сохранённым по всем
отсчётам, MIDI-событиям и 281 параметру.

Побитная повторяемость `.fst` относится к этой новой цепочке при одинаковом
блоке, **не к совпадению с v83 или оригиналом**. Строгая разность с v83 и
сравнение с оригиналом сохранены в `verification`. Это промежуточный бекап;
подбор продолжается.
'''
(root/'FL_STUDIO_RU.md').write_text(guide)
if chorus:
    guide=guide.replace('SOURCE | WaveShaper: `SOURCE_WaveShaper.fst` |','SOURCE | WaveShaper: `SOURCE_WaveShaper.fst`; Chorus: `SOURCE_Chorus.fst` |')
    guide=guide.replace('**Fruity WaveShaper, Fruity Parametric EQ 2, Fruity Stereo Shaper**.','**Fruity WaveShaper, Fruity Chorus, Fruity Parametric EQ 2, Fruity Stereo Shaper**.')
    guide=guide.replace('Сокращения в таблице обозначают соответствующие `.fst` из `presets`.','Сокращения в таблице обозначают соответствующие `.fst` из `presets`.\n**У Chorus ручка Mix именно слота микшера должна быть 8%**; это не\nвнутренняя ручка плагина. Состояние `01_SOURCE.fst` уже содержит 8%.\nПри загрузке отдельных эффектов выставь 8% вручную, остальные слоты — 100%.')
    guide=guide.replace('Смена размера блока немного меняет отсчёты;','Для проверки размера блока отдельно отключена глубина Chorus;\nсвободная фаза его LFO иначе мешает такому сравнению. Для рабочего\nмодулированного варианта также отдельно измерен импульс. Все')
    guide=guide.replace('Побитная повторяемость `.fst` относится к этой новой цепочке при одинаковом\nблоке, **не к совпадению с v83 или оригиналом**.','Байты состояний всех десяти эффектов после повторной загрузки совпали.\nАудиоконтроль с нулевой глубиной Chorus тоже совпал по отсчётам. У рабочего\nChorus свободная фаза LFO: повторные рендеры немного различаются, поэтому\nдля него не заявляется побитная повторяемость аудио. Проверены шесть\nнезависимых рендеров, для WAV выбран средний по оценке, а не лучший.\nЭто **не совпадение с v83 или оригиналом**.')
    guide=guide.replace('8%',f'{mix_percent:.6g}%')
    (root/'FL_STUDIO_RU.md').write_text(guide)
if proof.get('source_manifest'):
    guide=(root/'FL_STUDIO_RU.md').read_text().replace('Diva_Lead_v83_WIP.h2p',proof['source_preset_filename'])
    guide=guide.replace('здесь источник заново отрендерен через Diva и совпал с сохранённым по всем\nотсчётам, MIDI-событиям и 281 параметру.','источник этой ветки отличается от v83 только параметром ширины импульса\nпо высоте ноты (OSC: PWModDepth = +1.00). Повторный настоящий запуск Diva\nсовпал с сохранённым источником по всем отсчётам, всем 281 параметру\nэтого варианта и тем же 12 MIDI-событиям. Три удержания и ARP сохранены.')
    (root/'FL_STUDIO_RU.md').write_text(guide)
if proof.get('source_manifest') and len(proof['source_manifest'].get('changed_parameters',{}))>1:
    guide=(root/'FL_STUDIO_RU.md').read_text()
    old_description='источник этой ветки отличается от v83 только параметром ширины импульса\nпо высоте ноты (OSC: PWModDepth = +1.00).'
    rows=['| Параметр Diva | v83 | Этот источник |','| --- | --- | --- |']
    for label,change in proof['source_manifest']['changed_parameters'].items():
        rows.append('| '+label+' | '+change['before']['display']+' | '+change['after']['display']+' |')
    guide=guide.replace(old_description,'источник этой ветки отличается от v83 следующими параметрами:\n\n'+'\n'.join(rows)+'\n')
    (root/'FL_STUDIO_RU.md').write_text(guide)
if proof.get('common_phase_pair'):
    guide=(root/'FL_STUDIO_RU.md').read_text().replace('Chorus: `SOURCE_Chorus.fst` |','Chorus: `SOURCE_Chorus.fst`; Stereo Shaper: `SOURCE_Phase_R.fst`; Stereo Shaper: `SOURCE_Phase_L.fst` |')
    guide=guide.replace('всех десяти эффектов','всех двенадцати эффектов')
    guide+='\nДва Stereo Shaper после Chorus поворачивают фазу обоих каналов одинаково.\nПорядок SOURCE: WaveShaper → Chorus → SOURCE_Phase_R → SOURCE_Phase_L.\nMix у этих двух Stereo Shaper — 100%; Mix слота Chorus указан выше.\nЗагрузи все четыре эффекта SOURCE, иначе этот вариант не воспроизведётся.\n'
    (root/'FL_STUDIO_RU.md').write_text(guide)
(root/'README_RU.md').write_text('''# Native FL effects WIP — три длинные ноты

DSP-библиотека получена, настоящие штатные эффекты запущены. Цепочка работает
без PDC старого Finish, но пока уступает v83 по звучанию относительно оригинала.
100% переноса и совпадения с референсом нет.

[Загрузка в FL Studio](FL_STUDIO_RU.md). Содержит Diva-пресет, MIDI,
13 FST (4 состояния дорожек и 9 отдельных эффектов), WAV и A/B.
Проприетарные DLL отсутствуют. Проверка в GUI FL не проводилась.
''')
if chorus:
    readme=(root/'README_RU.md').read_text().replace('13 FST (4 состояния дорожек и 9 отдельных эффектов)','14 FST (4 состояния дорожек и 10 отдельных эффектов)')
    (root/'README_RU.md').write_text(readme+'\nChorus подмешан на 8% ручкой Mix слота микшера. Его LFO свободный;\nповторные рендеры слегка различаются. Настройки и контроль маршрутизации\nпрошли повторную загрузку, улучшение проверено на нескольких рендерах.\n')
    (root/'README_RU.md').write_text((root/'README_RU.md').read_text().replace('8%',f'{mix_percent:.6g}%'))
if proof.get('common_phase_pair'):
    p=root/'README_RU.md';p.write_text(p.read_text().replace('14 FST (4 состояния дорожек и 10 отдельных эффектов)','16 FST (4 состояния дорожек и 12 отдельных эффектов)'))
(root/'verification/CHECKPOINT_KIND.json').write_text(json.dumps(dict(native_port_checkpoint=True,technical_WIP=True,replace_main_v83=False,transfer_complete=False,reference_match_reached=False),indent=2)+'\n')
print('NATIVE_WIP_GUIDE_AND_AB_CREATED')
