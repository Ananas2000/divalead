from pathlib import Path
import json,hashlib,shutil,subprocess,os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';P=ROOT/'after-v61/continued-gain2';P.mkdir(exist_ok=False)
S=json.loads((R/'verified-gain-interior-0002/validation.json').read_text());v61=json.loads((REPO/'diva-lead/v61-wip/verification/selected_validation.json').read_text())
assert S['all_chosen_three_guards_passed'] and S['tone_score']<v61['tone_score']
ignore=shutil.ignore_patterns('*.dll','*.exe','*.so','*.pyc','__pycache__')
shutil.copytree(R/'verified-gain-interior-0002',P/'accepted-gain2',ignore=ignore);shutil.copytree(R/'gain-interior-repair-0002',P/'numeric',ignore=ignore)
for name in ['three_gain_interior_projection.py','repair_three_gain_interior.py','fit_three_gains.py','gain-interior-repair-0002.log','gain-interior-proof-0002.log','backup_gain2_post_v61.py','deduplicate_immutable_audio.py','verify_v61_final_checkpoint.py','V61_FINAL_CHECKPOINT_STATUS.json','v61-final-checkpoint.log','continuation-state.json','phase-continuation-state.json','drift24-continuation-state.json']:shutil.copyfile(R/name,P/name)
ref,sr=sf.read(REPO/'diva-lead/v61-wip/Diva_original_lead_reference.wav');old=sf.read(REPO/'diva-lead/v61-wip/Diva_Lead_v61_REFERENCE_EDIT.wav')[0];edit,er=sf.read(P/'accepted-gain2/REFERENCE_EDIT_WIP.wav');assert sr==er==48000
ready=edit*np.sqrt(np.mean(ref*ref)/np.mean(edit*edit));assert np.max(abs(ready))<.99
sf.write(P/'CONTINUED_GAIN2_REFERENCE_EDIT_WIP.wav',ready,48000,subtype='PCM_24');ready=sf.read(P/'CONTINUED_GAIN2_REFERENCE_EDIT_WIP.wav')[0];gap=np.zeros((24000,2))
sf.write(P/'AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.wav',np.concatenate([ref,gap,old,gap,ready]),48000,subtype='PCM_24')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(P/'AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.wav'),'-codec:a','libmp3lame','-b:a','320k',str(P/'AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.mp3')],check=True)
prev=json.loads((R/'verified-cont-0011-hf/validation.json').read_text());labels={'H24':'24 гармоники','upper_harm':'Верхние гармоники','upper_off':'Межгармоническая энергия','low_harm':'Нижние гармоники','ERB':'ERB-полосы','relative_phase':'Фазовый профиль','whole':'Весь спектр','envelope':'Огибающая','body':'Уровни тел','stereo_phase':'Фаза L/R','stereo_balance':'Баланс L/R'}
rows=['| Ошибка, меньше лучше | v61 | Предыдущий HF11 | Новый gain2 |','| --- | ---: | ---: | ---: |']
for k,label in labels.items():rows.append(f"| {label} | {v61['metrics'][k]:.9f} | {prev['metrics'][k]:.9f} | {S['metrics'][k]:.9f} |")
(P/'README.md').write_text('''# Продолжение после v61: проверенные уровни гармоник

[A/B оригинал → v61 → новый gain2, MP3](AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.mp3), [WAV](AB_REFERENCE_V61_CONTINUED_GAIN2_WIP.wav): **0 / 4,168 / 8,336 с**. [Новый отдельный WAV](CONTINUED_GAIN2_REFERENCE_EDIT_WIP.wav).

Это следующий исследовательский WAV на той же пользовательской трёхнотной основе. Точное совпадение пока не достигнуто. Это не полный новый комплект v62, коэффициенты отличаются от DLL v61. Полный [v61](../../../../v61-wip/README.md) и [инструкция](../../../../v61-wip/FL_STUDIO_RU.md) остаются без изменений.

## Как послушать в FL Studio

Перетащи CONTINUED_GAIN2_REFERENCE_EDIT_WIP.wav в Playlist: 180 BPM, 48 kHz, Normalize Off, Pitch 0, Resample, Time Reset, без Fit to tempo. Канал, Insert и Master 0 dB, панорама по центру, без добавленной обработки и мастер-лимитера. Файл уже содержит Diva и новое Finish, повторно добавлять эффект не нужно. Это фрагмент на уровне A/B; живое исполнение полного v61 использует предыдущую обработку.

## Изменение и проверки

На основе полностью проверенного HF11 уточнены существующие 93 значения уровней гармоник, фазы сохранены. Перспективная численная точка немного выходила за прежнюю границу полного спектра. Малое изменение существующих коэффициентов вернуло её внутрь **тех же** ограничений. Crest, исходные пределы по метрикам, минимальное усиление на непрерывном диапазоне 45–220 Hz и допуски независимых проверок сохранены. Более строгий численный внутренний запас добавлен для полного спектра/crest; допуски не расширялись.

После этого выполнены новая Diva, точное совпадение пресета/raw/всех 281 параметра/12 MIDI-событий, Windows/native, полная независимая подходящая NEW-база, отдельный спектральный fixture и все 12 произвольных причинных случаев на четырёх sample rate. Итоговый validation.json создан только после них. Три удержания на фразу и внутренний ARP Diva сохранены. Никаких дополнительных нот или новых состояний DSP.

Критерий тембра: **v61 0,838107207 → HF11 0,837143340 → gain2 0,835345239**. Общий критерий **0,928066435 → 0,927332884 → 0,925824334**. Это ошибки, не проценты сходства на слух. Есть небольшие регрессии, в частности ERB по сравнению с HF11, видимые в таблице. Все исходные ограничения проверены.

'''+ '\n'.join(rows)+f'''

Crest {S['crest_RMS_dB']:.12f} dB при фиксированном пределе {S['crest_cap_dB']:.12f}. Windows/native {S['Windows_native_max_error']:.3g}, полная собственная NEW-цепочка {S['full_NEW_SOURCE_independent_max_error']:.3g}, fixture {S['spectral_fixture_max_error']:.3g}; прежние допуски 2e-7 / 3e-7 / 2e-7. 12 произвольных случаев находятся в accepted-gain2/arbitrary-input-verification.json.

Следующие раунды gain используют тот же способ малой коррекции внутри ограничений через three_gain_interior_projection.py; численное улучшение всё равно требует полного нового actual proof. Метод реально исполнен в этом исследовании до включения в будущие раунды. Сохранены seed, полный расчёт, точка, исходники и логи. Текущий основной gain-раунд был запущен до изменения helper; его результаты будут оценены отдельно. HF/gain и фазовые процессы продолжаются; state-файлы — снимки на момент бэкапа, не обещание их переживания остановки машины.

Сравнение выполняется с исходным WAV пользователя. В A/B используется один RMS-множитель на весь стереофрагмент, без отдельной нормировки каналов или нот. GUI FL Studio и прослушивание ассистентом здесь не выполнялись. MistaTowa исключён.
''')
current=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());current.update(research_validation='after-v61/continued-gain2/accepted-gain2/validation.json',score=S['score'],tone_score=S['tone_score'],latest_research_is_not_a_new_complete_DLL_release=True)
(ROOT/'CURRENT_THREE_NOTE_MODEL.json').write_text(json.dumps(current,indent=2)+'\n')
p=ROOT/'after-v61/README.md';p.write_text(p.read_text()+'''\nЗатем выполнен [следующий gain-подбор и полный новый proof](continued-gain2/README.md): новый WAV/MP3, исходники и инструкция FL. Полный комплект v61 остаётся прежним.\n''')
def manifest(folder):
 (folder/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(folder))+'\n' for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'SHA256SUMS.txt'))
manifest(P);manifest(P.parent)
print('POST61_GAIN2_FULL_ACTUAL_PROOF_AUDIO_AND_FL_INSTRUCTIONS_SAVED',flush=True)
