# v47 WIP: загрузка и параметры

Загрузите `Diva_Lead_v47_WIP.h2p`, затем поставьте `Diva_Lead_Finish_v47_WIP_x64.dll` после Diva. Amount = 1, Output = +1,852506397 dB; включите PDC. Темп исполнения — 180 BPM. Совпадение с оригиналом пока не достигнуто.

Tune2 изменён с 24,00 на 24,02. Остальные 280 параметров Diva сохранены v46. Полный фактический список — `Diva_v47_DIVA_parameters.tsv`; для точного воспроизведения используйте пресет.

| Поле Diva | Значение |
|---|---:|
| VCC:FTun | 1.02 |
| OSC:Drift | 24.80 |
| VCF1:Res | 12.24 |
| OPT:TSlop | 3.86 |
| OPT:V2T1 | 21.43 |
| OPT:V3T1 | 46.00 |
| Plate2:Decay | 35.25 |
| Plate2:Damp | 72.00 |
| Plate2:Wet | 1.12 |
| OSC:PW | 51.87 |
| ENV1:Atk | 3.02 |
| ENV1:Sus | 93.85 |
| VCF1:KeyScl | 8.38 |
| OSC:Tune2 | 24.02 |
| OSC:OscMix | 5.55 |

В WAV для сравнения сохранено предзвучание. Значения DSP и результаты независимых проверок находятся в `Finish_settings.json`, `validation.json` и `analysis/`.
