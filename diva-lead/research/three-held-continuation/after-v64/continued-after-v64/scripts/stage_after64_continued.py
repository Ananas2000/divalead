"""Freeze completed follow-up research; do not overwrite a full release."""
from pathlib import Path
import os,sys,json,shutil,hashlib,subprocess,gzip,datetime
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';O=ROOT/'after-v64/continued-after-v64'
assert not O.exists() and not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def link(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
    try:os.link(a,b)
    except OSError:shutil.copyfile(a,b)
    return str(b)
def snapshot(a,b):
    shutil.copytree(a,b,copy_function=link,ignore=lambda d,ns:[n for n in ns if n=='__pycache__' or Path(n).suffix in ['.so','.dll','.exe','.pyc','.tmp','.lock']])
seen=set()
for p in ROOT.rglob('validation.json'):
    try:seen.add(Path(json.loads(p.read_text())['core_model']).parent.parent.name)
    except (KeyError,ValueError):pass
new=sorted(p for p in R.glob('verified-*/validation.json') if p.parent.name not in seen)
branch=R/'tslop0-verified-cross-0001/validation.json'
assert branch.exists();new.append(branch)
reports=[(json.loads(p.read_text()),p) for p in new]
best,path=min([(d,p) for d,p in reports if d.get('same_user_selected_Diva_preset_raw_and_all281')],key=lambda x:x[0]['tone_score'])
O.mkdir()
for d,p in reports:
    cases=json.loads((p.parent/'arbitrary-input-verification.json').read_text())['arbitrary_input_no_MIDI_cases'];assert len(cases)==12 and all(c['causal_prefix_equal'] and c['independent_max_error']<2e-10 for c in cases)
    snapshot(p.parent,O/'proofs'/p.parent.name)
snapshot(R/'source-tslop0-basis',O/'TuneSlop0-unaccepted-initial-basis')
assert not (O/'TuneSlop0-unaccepted-initial-basis/validation.json').exists()
shutil.copyfile(R/'source-pan64-archive.json',O/'source-pan64-archive.json')
link(Path('/tmp/divalead-source-pan64-completed.tar.gz'),O/'source-pan64-completed.tar.gz')
shutil.copyfile(Path('/tmp/divalead-source-pan64/history.json'),O/'source-pan64-history.json')
shutil.copyfile(R/'tslop0-cross-model-decision.json',O/'tslop0-cross-model-decision.json')
sources=[]
for family,start in [('continuation',34),('joint-phase-continuation',32),('balance-power-continuation',1)]:
    for p in sorted((R/family).glob('round-*')):
        if int(p.name.split('-')[1])<start:continue
        scratch=Path(json.loads((p/'numeric-location.json').read_text())['numeric_scratch']) if (p/'numeric-location.json').exists() else p/'numeric'
        if not any(scratch.rglob('optimizer.json')):continue
        dest=O/'numeric'/family/p.name;snapshot(p,dest);sources.append((p,dest))
        if not scratch.is_relative_to(p):snapshot(scratch,dest/'numeric');sources.append((scratch,dest/'numeric'))
for n in ['joint32-fine55-projection','joint32-power69-combination','source-pan64-control']:
    p=R/n;dest=O/'numeric'/n;snapshot(p,dest);sources.append((p,dest))
for n in ['divalead-joint32-fine55-projection','divalead-joint32-power69-combination','divalead-tslop0-cross-models']:
    p=Path('/tmp')/n;dest=O/'numeric'/n;snapshot(p,dest);sources.append((p,dest))
archived=[]
for row in json.loads((R.parent/'history-lossless-archive.json').read_text())['files']:
    old=Path(row['path'])
    if old.exists():continue
    for source,dest in sources:
        if old.is_relative_to(source):
            gz=Path(row['gzip']);assert hashlib.sha256(gzip.decompress(gz.read_bytes())).hexdigest()==row['SHA256'];q=dest/(str(old.relative_to(source))+'.gz')
            if not q.exists():link(gz,q)
            archived.append(dict(path=str(q.relative_to(O))[:-3],gzip=str(q.relative_to(O)),SHA256=row['SHA256']));break
write(O/'archived-numeric-journals.json',archived)
(O/'scripts').mkdir()
for p in R.glob('*.py'):shutil.copyfile(p,O/'scripts'/p.name)
for n in ['fine55-projection-integration-check.json','public-v64-verification.json','staged-v64-verification.json','pending-512MiB-resource-handoffs.json']:
    shutil.copyfile(R/n,O/n)
# The live source gain optimizer is deliberately not copied as a completed study.
shutil.copyfile(R/'tslop0-research/state.json',O/'source-gain-fit-state-at-backup.json')
C=O/'research-checkpoint';C.mkdir();ref,sr=sf.read(REPO/'diva-lead/v64-wip/Diva_original_lead_reference.wav');full,fr=sf.read(REPO/'diva-lead/v64-wip/Diva_Lead_v64_REFERENCE_EDIT.wav');edit,er=sf.read(path.parent/'REFERENCE_EDIT_WIP.wav');variant,vr=sf.read(branch.parent/'REFERENCE_EDIT_WIP.wav')
assert sr==fr==er==vr==48000 and ref.shape==full.shape==edit.shape==variant.shape==(176064,2)
gap=np.zeros((24000,2))
def ready(x,name):
    gain=float(np.sqrt(np.mean(ref*ref)/np.mean(x*x)));sf.write(C/name,x*gain,sr,subtype='PCM_24');return sf.read(C/name)[0],gain
chosen,gain=ready(edit,'CONTINUED_AFTER64_REFERENCE_EDIT_WIP.wav');other,vgain=ready(variant,'TUNESLOP0_THREE_HELD_RESEARCH_WIP.wav')
for name,parts in [('AB_REFERENCE_V64_CONTINUED_AFTER64_WIP',[ref,gap,full,gap,chosen]),('AB_REFERENCE_CONTINUED_AFTER64_TUNESLOP0_WIP',[ref,gap,chosen,gap,other])]:
    data=np.concatenate(parts);assert np.max(np.abs(data))<1;wav=C/(name+'.wav');sf.write(wav,data,sr,subtype='PCM_24');decoded=sf.read(wav)[0];np.testing.assert_array_equal(decoded[:176064],ref);assert not np.any(decoded[176064:200064]) and not np.any(decoded[376128:400128]);np.testing.assert_array_equal(decoded[200064:376128],parts[2]);np.testing.assert_array_equal(decoded[400128:],parts[4]);subprocess.run(['ffmpeg','-v','error','-i',str(wav),'-codec:a','libmp3lame','-q:a','2',str(wav.with_suffix('.mp3'))],check=True)
write(C/'selection.json',dict(canonical_original_source_proof='../proofs/'+path.parent.name+'/validation.json',tone_score=best['tone_score'],score=best['score'],single_global_stereo_RMS_gain=gain,TuneSlop0_single_global_RMS_gain=vgain,TuneSlop0_full_proof='../proofs/'+branch.parent.name+'/validation.json',TuneSlop0_not_adopted_into_canonical_original_source=True,full_v64_DLL_does_not_contain_newer_research=True,match_reached=False))
(C/'FL_STUDIO_WAV_RU.md').write_text('''# Проверить продолжение после v64 в FL Studio

1. Проект 180 BPM, желательно 48 kHz. Перетащить `CONTINUED_AFTER64_REFERENCE_EDIT_WIP.wav` в Playlist. Это готовый обработанный звук: Normalize выключен, Pitch 0, Resample, Time → Reset, громкость канала и микшера 0 dB, панорама по центру, Master без лимитера и дополнительной обработки. Finish повторно не добавлять.
2. `AB_REFERENCE_V64_CONTINUED_AFTER64_WIP.wav` / MP3: оригинал с 0 с → полный v64 с 4,168 с → продолжение с 8,336 с.
3. `AB_REFERENCE_CONTINUED_AFTER64_TUNESLOP0_WIP.wav` / MP3: оригинал → лучшее продолжение исходного источника → отдельная проба TuneSlop0. Все фрагменты выровнены одним общим стерео RMS-множителем каждый; поканальной или понотной нормализации нет. Новый источник сохраняет ровно те же три удержания и ARP; меняется один параметр случайного разброса строя.

Коэффициенты исследования новее DLL полного v64. Для игры MIDI использовать [полный комплект v64](../../../../../v64-wip/FL_STUDIO_RU.md). Этот комплект остаётся промежуточным и отдельно зафиксированным. Исследовательские пресеты и исходники не следует смешивать с DLL другой версии для попытки точно повторить эти WAV. GUI FL Studio здесь не проверялся; точное совпадение с референсом не достигнуто.
''')
model=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());model.update(research_validation='after-v64/continued-after-v64/proofs/'+path.parent.name+'/validation.json',tone_score=best['tone_score'],score=best['score'],latest_research_is_not_a_new_complete_DLL_release=True);write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',model)
rows=['| Полностью проверенный снимок | Семейство | Ошибка тембра ↓ | Общая ошибка ↓ |','|---|---|---:|---:|']
for d,p in sorted(reports,key=lambda x:x[0]['tone_score']):rows.append(f"| {p.parent.name} | {'Исходный выбранный' if d.get('same_user_selected_Diva_preset_raw_and_all281') else 'TuneSlop0, та же трёхнотная архитектура'} | {d['tone_score']:.10f} | {d['score']:.10f} |")
(O/'README.md').write_text('''# Продолжение после полного v64

[Новый A/B: оригинал → v64 → продолжение](research-checkpoint/AB_REFERENCE_V64_CONTINUED_AFTER64_WIP.mp3), [WAV](research-checkpoint/AB_REFERENCE_V64_CONTINUED_AFTER64_WIP.wav), [загрузить WAV в FL Studio](research-checkpoint/FL_STUDIO_WAV_RU.md). Начала: 0 / 4,168 / 8,336 с. Это более свежие исследовательские коэффициенты; DLL полного v64 содержит свой прежний снимок. Полный комплект v64 и все более ранние релизы сохранены без изменений. Точное совпадение не достигнуто.

Продолжен подбор существующих фаз, верхнего диапазона и гармонических усилений. В `scripts/` сохранены вместе обновлённый fine55-подбор, его новый `three_fine55_interior_projection.py` и общий проектор. Интеграция реально воспроизводит ранее полностью проверенную точку joint30 в точности, с нулевым отличием коэффициентов. Все ограничения и допуски прежние; численный запас внутри ограничений усилен. Текущий ранее запущенный раунд32 ещё не использовал новую интеграцию; новые процессы используют её. Расчётная точка не заменяет свежую Diva/Windows/собственную NEW-базу/fixture/12 причинных случаев.

Попытка дополнительно объединить новые fine55-параметры с прежними динамическими целями не дала допустимой точки. Все доли и решение проектора сохранены. Отдельная проекция fine55 прошла полную проверку, но по свежей ошибке тембра слегка уступила обычному принятому fine55-раунду. Разные частные улучшения не объявляются автоматически совместимыми.

'''+ '\n'.join(rows)+'''

## Реальные пробы самой Diva

`source-pan64-completed.tar.gz` содержит все 15 завершённых проб: исходные WAV Diva, WAV после обработки, пресеты, 281 параметр каждого рендера, фактические 12 MIDI-событий, команды и оценки. Весь архив проверен по SHA каждого файла (`source-pan64-archive.json`); распаковать через `tar -xzf source-pan64-completed.tar.gz`. Ноты, ARP и огибающие сохранены. Просто смещение панорамы к центру ухудшило совпадение с текущим Finish. Собственный генератор шума в исходном пресете уже выключен.

TuneSlop0 уменьшил случайный разброс строя осцилляторов. С прежним v64 DSP он снижал ошибку тембра, но нарушал прежний crest-предел; исходная диагностическая база явно сохранена без `validation.json` в `TuneSlop0-unaccepted-initial-basis`. Для изменённого источника заново построена собственная независимая NEW-база, проверены все 281 параметр и 12 событий. Затем перенос уже доказанной тонкой фазы дал вариант, прошедший все прежние ограничения и полный свежий Windows/NEW/12 случаев. Его собственный отчёт находится в `proofs/tslop0-verified-cross-0001`; это другое исходное звучание Diva, а не побитовое совпадение с исходным выбранным пресетом. Входящие ноты остаются прежними.

[A/B оригинал → основное продолжение → TuneSlop0](research-checkpoint/AB_REFERENCE_CONTINUED_AFTER64_TUNESLOP0_WIP.mp3). TuneSlop0 пока не принят в канонический исходный источник. Дальнейший подбор его 93 усилений ещё выполнялся во время бэкапа; состояние сохранено отдельно и не выдаётся за завершённый результат. Если эта ветка сравнивается по цели принятия, эталоном улучшения служит последний полностью проверенный v64, а не её начальная недопустимая диагностическая точка. Абсолютные ограничения по метрикам/динамике и допуски DSP не менялись.

Три действующих вычислительных слота сохраняют бюджет 2+1+1: основной HF/gain, фазовый, временная отдельная гипотеза Diva. Последняя временно приостановила баланс/динамические цели и возобновит его в `finally` по точным PID+starttime; одноразовые программы повторно автоматически не запускать. Новые контроллеры могут использовать операционный резерв512MiB после измерения размеров сборки/архива; это не изменение звуковых критериев. Отчёт о готовности требует реального продвижения журнала, а не только наличия PID. GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
write(O/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_complete_proofs=[p.parent.name for d,p in reports],canonical=path.parent.name,tone_score=best['tone_score'],score=best['score'],match_reached=False))
p=REPO/'README.md';s=p.read_text();needle='Точное совпадение ещё не достигнуто.';s=s.replace(needle,needle+' [Более свежее исследование после v64](diva-lead/research/three-held-continuation/after-v64/continued-after-v64/README.md): новые WAV, подтверждённые фазовые шаги и отдельная проба Diva TuneSlop0.',1);p.write_text(s)
(O/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(O))+'\n' for p in sorted(O.rglob('*')) if p.is_file()))
print('AFTER64_COMPLETED_RESEARCH_AND_ALL15_PHYSICAL_PROBES_STAGED',len(reports),path.parent.name,flush=True)
