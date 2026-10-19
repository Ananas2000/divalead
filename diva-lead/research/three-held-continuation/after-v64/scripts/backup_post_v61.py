from pathlib import Path
import json,hashlib,shutil,subprocess,os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';P=ROOT/'after-v61/continued-after-v61';P.mkdir(exist_ok=False)
assert json.loads((R/'hf-projection-module-check.json').read_text())['refactored_projection_matches_previously_full_proved_point']
ignore=shutil.ignore_patterns('*.dll','*.so','*.exe','*.pyc','__pycache__')
for source,target in [('verified-hf-interior-0001','accepted-interior-projection'),('verified-cont-0011-hf','accepted-HF11')]:
 assert (R/source/'validation.json').exists();shutil.copytree(R/source,P/target,ignore=ignore)
for source,target in [('hf-interior-repair-0001','projection-numeric'),('continuation/round-0011-hf','round11-HF')]:shutil.copytree(R/source,P/'rounds'/target,ignore=ignore)
for name in ['repair_three_hf_interior.py','three_hf_interior_projection.py','check_hf_projection_refactor.py','hf-projection-module-check.json','hf-projection-module-check.log','hf-interior-repair-0001.log','hf-interior-proof-0001.log','fit_three_hf_fixed_anchor.py','backup_post_v61.py','verify_public_v61.py','public-v61-verification.json','public-v61-check.log','continuation-state.json','phase-continuation-state.json','drift24-continuation-state.json']:
 assert (R/name).exists(),name;shutil.copyfile(R/name,P/name)
S=json.loads((R/'verified-cont-0011-hf/validation.json').read_text());v61=json.loads((REPO/'diva-lead/v61-wip/verification/selected_validation.json').read_text())
ref,sr=sf.read(REPO/'diva-lead/v61-wip/Diva_original_lead_reference.wav');edit,er=sf.read(P/'accepted-HF11/REFERENCE_EDIT_WIP.wav');old,pr=sf.read(REPO/'diva-lead/v61-wip/Diva_Lead_v61_REFERENCE_EDIT.wav');assert sr==er==pr==48000
multiplier=np.sqrt(np.mean(ref*ref)/np.mean(edit*edit));ready=edit*multiplier;gap=np.zeros((24000,2));assert np.max(abs(ready))<.99
sf.write(P/'CONTINUED_POST61_REFERENCE_EDIT_WIP.wav',ready,48000,subtype='PCM_24')
ready=sf.read(P/'CONTINUED_POST61_REFERENCE_EDIT_WIP.wav')[0]
sf.write(P/'AB_REFERENCE_V61_CONTINUED_HF11_WIP.wav',np.concatenate([ref,gap,old,gap,ready]),48000,subtype='PCM_24')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(P/'AB_REFERENCE_V61_CONTINUED_HF11_WIP.wav'),'-codec:a','libmp3lame','-b:a','320k',str(P/'AB_REFERENCE_V61_CONTINUED_HF11_WIP.mp3')],check=True)
diag=[]
for label,x in [('original',ref),('v61',old),('post-v61-HF11',ready)]:
 rms=np.sqrt(np.mean(x*x,axis=0));mid=(x[:,0]+x[:,1])*.5;side=(x[:,0]-x[:,1])*.5
 diag.append(dict(label=label,L_minus_R_dB=float(20*np.log10(rms[0]/rms[1])),side_over_mid_dB=float(20*np.log10(np.sqrt(np.mean(side*side)/np.mean(mid*mid)))),LR_correlation=float(np.corrcoef(x.T)[0,1])))
(P/'stereo-diagnostic.json').write_text(json.dumps(dict(full_excerpt_global_RMS_only=True,no_channelwise_normalization=True,diagnostics=diag,stereo_match_NOT_claimed=True),indent=2)+'\n')
(P/'README.md').write_text('''# Следующий проверенный шаг после полного v61

[A/B оригинал → v61 → HF11, MP3](AB_REFERENCE_V61_CONTINUED_HF11_WIP.mp3), [WAV](AB_REFERENCE_V61_CONTINUED_HF11_WIP.wav): **0 / 4,168 / 8,336 с**. [Отдельный готовый WAV](CONTINUED_POST61_REFERENCE_EDIT_WIP.wav).

Это более позднее исследование на **той же выбранной трёхнотной основе**, а не полный новый комплект v62. Коэффициенты отличаются от DLL v61. Полный [комплект v61](../../../../v61-wip/README.md) и [его инструкция](../../../../v61-wip/FL_STUDIO_RU.md) сохранены без изменений. Точного совпадения пока нет.

## Как послушать новый результат в FL Studio

Перетащи `CONTINUED_POST61_REFERENCE_EDIT_WIP.wav` в Playlist. Проект 180 BPM, Audio settings 48 kHz; Normalize выключен, Pitch 0, Time stretching Resample, Time Reset, без Fit to tempo. Громкость канала, Insert и Master — 0 dB, панорама по центру, без дополнительной обработки и мастер-лимитера. WAV уже содержит Diva и новый Finish; повторно ставить Finish v61 на него не нужно. Это короткий сравнительный фрагмент, выровненный с оригиналом общим стерео-RMS-множителем. Для игры через MIDI используй полный v61, с учётом того, что его обработка — предыдущая.

## Что проверено

- `accepted-interior-projection/`: перспективный численный HF-кандидат слегка выходил за прежние границы полного спектра/crest. Изменением только нескольких существующих HF-коэффициентов он возвращён внутрь **тех же** ограничений. Допуски не ослаблялись; добавлен только более строгий численный внутренний запас. Новый настоящий рендер, независимая собственная NEW-база и все 12 произвольных случаев прошли. Критерий тембра 0,837277270.
- `accepted-HF11/`: следующий завершившийся обычный HF-раунд дал немного лучший допустимый результат, **0,837143340**, общий критерий **0,927332884**. Он выбран для WAV в этой папке. v61: 0,838107207 / 0,928066435. Ошибка верхних гармоник 1,261202429 → 1,256112142; ERB 0,935095941 → 0,934738214. Это ошибки, не проценты сходства. Некоторые другие измерения немного выросли, все исходные фиксированные ограничения сохранены.

Обе проверки сохраняют сырой WAV, пресет Diva, все 281 параметр и 12 входящих MIDI-событий точно: три удержания на фразу, 6 note-on на два прохода, внутренний ARP On. Свежая Diva, Windows/native, полный matching-NEW, fixture и все 12 произвольных причинных случаев выполнены для обеих. validation.json записывается после завершения всех проверок. Новые состояния DSP, дополнительные ноты и проигрывание оригинального сэмпла не добавлены.

`three_hf_interior_projection.py` переносит отдельно проверенный способ возврата внутрь ограничений в будущие HF-подборы. На настоящей модели проверено совпадение полученной точки с уже полностью проверенным исследованием и вызов сохранения только допустимого улучшения: `hf-projection-module-check.json`. Обычный HF11 был запущен до интеграции helper, его результат не приписывается этому изменению. Полные исходные истории/seed/решения и скрипты сохранены. Численные недопустимые центры не считаются улучшениями.

Следующий gain-подбор основной семьи уже начал работу с HF11; фазы продолжаются отдельно на завершённых проверенных основах. Отдельная трёхнотная Drift24-семья сохраняет собственный источник и NEW-базу и пока уступает основной по критерию тембра. Не смешивать их файлы. Контроллеры не публикуют Git автоматически, state-файлы — снимки на момент бэкапа.

В `stereo-diagnostic.json` сохранены реальные измерения оригинала и обоих вариантов без поканальной нормализации. Например, левый канал исходного WAV сам громче правого примерно на 2,907 dB, у v61 — на 3,323 dB. Это диагностические числа по всему фрагменту; точное стереосовпадение не заявляется.

GUI FL Studio и прослушивание ассистентом здесь не выполнялись. MistaTowa исключён.
''')
current=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());current.update(research_validation='after-v61/continued-after-v61/accepted-HF11/validation.json',score=S['score'],tone_score=S['tone_score'],latest_research_is_not_a_new_complete_DLL_release=True,selected_complete_release='diva-lead/v61-wip',selected_complete_release_score=v61['score'],selected_complete_release_tone_score=v61['tone_score'])
(ROOT/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
p=ROOT/'after-v61/README.md';p.write_text(p.read_text()+'''\nПосле этого комплекта сохранён [следующий проверенный HF11 и готовый исследовательский WAV](continued-after-v61/README.md). Его коэффициенты новее DLL v61; полный комплект v61 остаётся неизменным.\n''')
def manifest(folder):
 (folder/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(folder))+'\n' for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'SHA256SUMS.txt'))
manifest(P);manifest(ROOT/'after-v61')
print('POST61_TWO_ACTUAL_FULL_PROOFS_NEW_READY_WAV_AND_FURTHER_GAIN_WORK_SAVED',flush=True)
