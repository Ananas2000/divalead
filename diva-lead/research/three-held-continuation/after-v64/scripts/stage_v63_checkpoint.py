"""Freeze completed three-held research and the independently verified v63 kit."""
from pathlib import Path
import os, sys, json, hashlib, shutil, gzip, subprocess, datetime
import numpy as np
import soundfile as sf

R=Path(__file__).resolve().parent
REPO=Path('/workspace/divalead')
ROOT=REPO/'diva-lead/research/three-held-continuation'
OUT=ROOT/'after-v63'
assert not OUT.exists()
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
subprocess.run([sys.executable,'-B',str(R/'continue_three.py'),'--check-only'],env=env,check=True)
for name in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json']:
    json.loads((R/'v63-build'/name).read_text())
assert json.loads((R/'v63-build/clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)

def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def immutable_copy(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
    try: os.link(a,b)
    except OSError: shutil.copyfile(a,b)
    return str(b)

def snapshot(a,b,release=False):
    a=Path(a);b=Path(b)
    def ignore(directory,names):
        return [n for n in names if n=='__pycache__' or Path(n).suffix in ('.pyc','.so','.exe','.tmp','.lock') or (not release and Path(n).suffix=='.dll')]
    shutil.copytree(a,b,copy_function=immutable_copy,ignore=ignore)

published=set()
for p in ROOT.rglob('validation.json'):
    try: published.add(Path(json.loads(p.read_text())['core_model']).parent.parent.name)
    except (KeyError,ValueError): pass
new=sorted(p for p in R.glob('verified-*/validation.json') if p.parent.name not in published)
assert len(new)>=29
reports=[(json.loads(p.read_text()),p) for p in new]
best,path=min(reports,key=lambda x:x[0]['tone_score'])
selected=path.parent.name
OUT.mkdir()
snapshot(R/'v63-build/v63-wip',REPO/'diva-lead/v63-wip',release=True)
immutable_copy(R/'v63-build/Diva_lead_v63_WIP_checkpoint.zip',REPO/'Diva_lead_v63_WIP_checkpoint.zip')
for d,p in reports:
    assert d['same_user_selected_Diva_preset_raw_and_all281'] and d['original_three_held_MIDI_events_unchanged']
    cases=json.loads((p.parent/'arbitrary-input-verification.json').read_text())['arbitrary_input_no_MIDI_cases']
    assert len(cases)==12 and all(x['causal_prefix_equal'] and x['independent_max_error']<2e-10 for x in cases)
    snapshot(p.parent,OUT/'proofs'/p.parent.name)

# Only completed numerical rounds are immutable snapshots. Never copy a live journal.
copied_sources=[]
for family in ['continuation','phase-continuation','joint-phase-continuation']:
    for p in sorted((R/family).glob('round-*')):
        if (p/'decision.json').exists() or any(p.rglob('optimizer.json')):
            snapshot(p,OUT/'numeric'/family/p.name);copied_sources.append((p,OUT/'numeric'/family/p.name))
for name in ['fine55-first','fine55-preview-0001','balance42-first','balance42-projection-0001','power69-first','power69-projection-0001','coupled-hf15-fine55']:
    p=R/name;snapshot(p,OUT/'numeric'/name);copied_sources.append((p,OUT/'numeric'/name))
for prefix in ['divalead-balance42-numeric','divalead-balance42-projection-0001','divalead-power69-from-balance42','divalead-power69-projection-0001']:
    p=Path('/tmp')/prefix
    assert any(p.rglob('optimizer.json')) or prefix.endswith('projection-0001')
    snapshot(p,OUT/'numeric'/prefix);copied_sources.append((p,OUT/'numeric'/prefix))

# The storage keeper alone owns its global ledger. Copy verified gzip journals
# into this snapshot without rewriting that ledger or reviving old experiments.
archived=[]
ledger=json.loads((R.parent/'history-lossless-archive.json').read_text())
for row in ledger['files']:
    old=Path(row['path'])
    if old.exists(): continue
    for source,dest in copied_sources:
        if old.is_relative_to(source):
            gz=Path(row['gzip']);data=gzip.decompress(gz.read_bytes())
            assert hashlib.sha256(data).hexdigest()==row['SHA256']
            target=dest/(str(old.relative_to(source))+'.gz')
            immutable_copy(gz,target)
            archived.append(dict(path=str(target.relative_to(OUT))[:-3],gzip=str(target.relative_to(OUT)),SHA256=row['SHA256'],uncompressed_bytes=len(data)))
            break
write(OUT/'archived-numeric-journals.json',archived)

# Preserve the quality rejection rather than allowing it to look like a proof.
from three_candidate_decision import quality_rejection
bad=quality_rejection(R/'balance42-projection-0001/validation.log',R/'verified-balance42-projection-0001')
assert bad is not None
snapshot(R/'verified-balance42-projection-0001',OUT/'rejected/verified-balance42-projection-0001')
write(OUT/'rejected/balance42-projection-decision.json',bad)

S=OUT/'scripts';S.mkdir()
scripts=['fit_three_hf_fixed_anchor.py','fit_three_gains.py','fit_three_phase18.py','fit_three_fine55.py','fit_three_balance42.py','fit_three_power69.py','validate_three_model.py','validate_three_source_model.py','continue_three.py','continue_three_joint_phase.py','continue_drift24.py','three_candidate_decision.py','project_three_existing_vector.py','repair_balance42.py','repair_power69.py','run_power69_first.py','start_balance42.py','couple_hf15_fine55.py','finish_fine55_first.py','prove_fine55_preview.py','handoff_updated_controller_idle.py','handoff_joint_phase_current.py','deduplicate_immutable_audio.py','plan_published_audio_cache.py','evict_published_audio_cache.py','restore_published_audio_cache.py','stage_v63_checkpoint.py','build_three_v63.py','write_v63_docs.py','finalize_v63.py','verify_zip_windows_v63.py','prepare_verified_git_pack.py','install_verified_git_pack.py']
for n in scripts:
    assert (R/n).is_file(),n
    shutil.copyfile(R/n,S/n) # live canonical scripts must never share an inode
for p in R.glob('*.py'):
    if p.name.startswith(('project_three_','repair_three_','three_hf_interior_projection','three_gain_interior_projection')) and not (S/p.name).exists():shutil.copyfile(p,S/p.name)
for n in ['published-audio-cache-eviction.json','published-cache-restore-test.json','required-runtime-audio-and-libraries.json','verified-git-pack-installed.json','retired-Git-pack-cache.json','immutable-ZIP-dedup.json','joint-phase-handoff.json','main-idle-resource-handoff.json','joint-phase-idle-resource-handoff.json']:
    p=R/n
    if p.exists():shutil.copyfile(p,OUT/n)
for n in ['ZIP-proof.json','clean-extraction-proof.json','clean-ZIP-Windows-proof.json','release-proof.json','fresh-source-proof.json','spectral-proof.json']:
    shutil.copyfile(R/'v63-build'/n,OUT/('v63-'+n))

C=OUT/'research-checkpoint';C.mkdir()
ref,sr=sf.read(REPO/'diva-lead/v63-wip/Diva_original_lead_reference.wav',dtype='float64')
prev,psr=sf.read(REPO/'diva-lead/v63-wip/Diva_Lead_v63_REFERENCE_EDIT.wav',dtype='float64')
edit,esr=sf.read(path.parent/'REFERENCE_EDIT_WIP.wav',dtype='float64')
assert sr==psr==esr==48000 and ref.shape==prev.shape==edit.shape==(176064,2)
gain=float(np.sqrt(np.mean(ref*ref)/np.mean(edit*edit)))
sf.write(C/'CONTINUED_AFTER63_REFERENCE_EDIT_WIP.wav',edit*gain,sr,subtype='PCM_24')
ready=sf.read(C/'CONTINUED_AFTER63_REFERENCE_EDIT_WIP.wav',dtype='float64')[0]
gap=np.zeros((24000,2))
ab=np.concatenate([ref,gap,prev,gap,ready])
assert np.max(np.abs(ab))<1
sf.write(C/'AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.wav',ab,sr,subtype='PCM_24')
subprocess.run(['ffmpeg','-v','error','-i',str(C/'AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.wav'),'-codec:a','libmp3lame','-q:a','2',str(C/'AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.mp3')],check=True)
decoded=sf.read(C/'AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.wav',dtype='float64')[0]
assert np.array_equal(decoded[:len(ref)],ref) and np.array_equal(decoded[200064:376128],prev) and np.array_equal(decoded[400128:],ready)
assert not np.any(decoded[176064:200064]) and not np.any(decoded[376128:400128])
write(C/'selected-checkpoint.json',dict(validation='../proofs/'+selected+'/validation.json',score=best['score'],tone_score=best['tone_score'],single_global_stereo_RMS_gain=gain,per_channel_or_per_note_normalization=False,original_starts_s=0,v63_starts_s=4.168,continued_starts_s=8.336,full_v63_contains_this_new_research=False,FL_GUI_tested=False,match_reached=False))
(C/'FL_STUDIO_WAV_RU.md').write_text('''# Проверить более свежий исследовательский WAV в FL Studio

Это готовый WAV после обработки с теми же тремя удержаниями и внутренним ARP Diva. Коэффициенты новее полного комплекта v63. Это промежуточный результат; совпадение не достигнуто.

1. Установить проект 180 BPM, желательно 48 kHz. Перетащить `CONTINUED_AFTER63_REFERENCE_EDIT_WIP.wav` в Playlist как Audio Clip.
2. Отключить Normalize, Reset time/stretch, оставить канальный и микшерный уровни 0 dB. Не добавлять Finish повторно и убрать лимитер Master для сравнения.
3. Для A/B открыть `AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.wav`: оригинал с 0 с, v63 с 4,168 с, продолжение с 8,336 с. Уровень продолжения выровнен одним общим коэффициентом по RMS; каналы и отдельные ноты не нормализованы.

Для игры MIDI использовать полный [комплект v63](../../../v63-wip/FL_STUDIO_RU.md). Его DLL содержит собственный зафиксированный шаг, а не этот более новый исследовательский WAV. GUI FL Studio здесь не проверялся.
''')
# From research-checkpoint the relative route to diva-lead/v63-wip has four parents.
p=C/'FL_STUDIO_WAV_RU.md';p.write_text(p.read_text().replace('../../../v63-wip/','../../../../v63-wip/'))

full=json.loads((R/'verified-cont-0031-hf/validation.json').read_text())
old=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
current={k:(v.replace('v62','v63').replace('V62','V63').replace('V61_V63','V62_V63') if isinstance(v,str) else v) for k,v in old.items()}
current.update(ZIP_SHA256=hashlib.sha256((REPO/'Diva_lead_v63_WIP_checkpoint.zip').read_bytes()).hexdigest(),DLL_SHA256=hashlib.sha256((REPO/'diva-lead/v63-wip/Diva_Lead_Finish_v63_WIP_x64.dll').read_bytes()).hexdigest(),research_model='diva-lead/research/three-held-continuation/after-v63',score=full['score'],tone_score=full['tone_score'])
current['AB_previous_current']='diva-lead/v63-wip/AB_REFERENCE_V62_V63_WIP.wav';current['AB_MP3']='diva-lead/v63-wip/AB_REFERENCE_V62_V63_WIP.mp3'
write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
model=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text())
model.update(selected_complete_release='diva-lead/v63-wip',research_validation='after-v63/proofs/'+selected+'/validation.json',tone_score=best['tone_score'],score=best['score'],selected_complete_release_tone_score=full['tone_score'],selected_complete_release_score=full['score'],latest_research_is_not_a_new_complete_DLL_release=True)
write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',model)

rows=[]
for d,p in sorted(reports,key=lambda t:t[0]['tone_score']):rows.append('| '+p.parent.name+' | '+format(d['tone_score'],'.10f')+' | '+format(d['score'],'.10f')+' |')
(OUT/'README.md').write_text('''# Продолжение исключительно трёхнотного варианта после v62

Полный промежуточный [v63](../../../v63-wip/README.md), [FL Studio](../../../v63-wip/FL_STUDIO_RU.md), [оригинал → v62 → v63](../../../v63-wip/AB_REFERENCE_V62_V63_WIP.mp3) сохранён отдельно. Его основа — `verified-cont-0031-hf`. Все 281 параметр Diva, исходный WAV и 12 входящих MIDI-событий выбранного источника прежние: 3 удержания на фразу, два повтора, внутренний ARP.

После сборки v63 подбор существующих коэффициентов финального стереобаланса и динамического баланса гармоник дал дополнительное измеряемое улучшение. [Свежий A/B оригинал → v63 → продолжение](research-checkpoint/AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.mp3), [WAV](research-checkpoint/AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.wav), [инструкция WAV в FL](research-checkpoint/FL_STUDIO_WAV_RU.md). **Более свежие коэффициенты пока не входят в DLL полного v63.** Это исследовательский снимок, точное совпадение не достигнуто.

Подбор касается 100 существующих значений верхней обработки, 93 усилений гармоник, 18 общих фазовых значений, 55 имеющихся коэффициентов тонкой фазы, 42 значений финального стереобаланса и 69 коэффициентов имеющихся динамических целей. Новые ноты, состояния и задержка не добавлялись. Каждое принятое изменение проверено свежим фактическим рендером Diva, Windows/native, подходящей собственному источнику NEW-базой, отдельной спектральной фикстурой и 12 произвольными причинными сигналами при 44,1/48/96/192 kHz. Проверки подтверждают реализацию и ограничения; они не доказывают совпадение тембра на слух. GUI FL Studio и прослушивание ассистентом не выполнялись.

Ограничения остаются привязаны к исходному выбранному трёхнотному варианту. Ошибки — не проценты сходства. Некоторые критерии могут немного ухудшаться в пределах прежних ограничений; уменьшение общего балла не означает улучшения каждого критерия. Стереобаланс не объявляется исправленным.

| Подтверждённый снимок | Ошибка тембра ↓ | Общая ошибка ↓ |
|---|---:|---:|
'''+ '\n'.join(rows)+'''

`proofs/` содержит все новые полностью завершённые проверки. В `numeric/` — только завершённые подборы и их основания. Часть больших журналов хранится без потери данных как `history.json.gz`; SHA исходного JSON и путь восстановления указаны в `archived-numeric-journals.json`. Перед повторным запуском исторического кода распаковать соответствующий журнал (`gzip -dk history.json.gz`). Абсолютные пути исходной среды в старых отчётах исторические; для переноса указать пути снимков и общей `../baseline`.

`rejected/` сохраняет отклонённую проекцию стереобаланса: свежий C-рендер превысил фиксированный предел `stereo_balance` на 4,69e-10. Итогового `validation.json` и завершённой проверки 12 сигналов у неё нет. Допуски не ослаблялись. Попытка объединить HF15/fine55 также не дала допустимого улучшения.

`scripts/` — снимки рабочих программ. Одноразовые программы handoff/build/stage содержат пути и идентификаторы текущей среды; запускать их автоматически в новой среде нельзя. Действующие продолжения выбирают только полностью доказанные модели исходного трёхнотного семейства. Другая трёхнотная ветка Drift24 не подмешивается к нему.

Освобождение места затронуло только приватные дубликаты исторических WAV, побайтно имеющиеся в опубликованном дереве и постоянном Git. Леджер `published-audio-cache-eviction.json` и `scripts/restore_published_audio_cache.py` восстанавливают конкретный путь по SHA, при необходимости из Git blob. Текущие трёхнотные источники и доказательства не удалялись. Временные Git/Wine архивы для воспроизведения результатов не нужны. Сохранённые операции упаковки Git и общий ресурсный предел не меняют звуковые допуски.
''')
rootreadme=REPO/'README.md';text=rootreadme.read_text();archive=text[text.index('**Архивный исследовательский этап:**'):]
rootreadme.write_text('''# Diva: реконструкция лида для FL Studio

Работаем исключительно с выбранными тремя длинными нотами на фразу: MIDI 41 → 37 → 36. Внутренний ARP Diva создаёт повторы и октавные движения. Сам пресет, все 281 параметр и входящие ноты сохранены.

**[Полный v63 WIP](diva-lead/v63-wip/README.md)** — [скачать ZIP](Diva_lead_v63_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v63-wip/FL_STUDIO_RU.md). Включены пресет, MIDI, Finish Windows x64 VST2, готовые WAV, исходники и проверки.

[Оригинал → v62 → v63](diva-lead/v63-wip/AB_REFERENCE_V62_V63_WIP.mp3): 0 / 4,168 / 8,336 с. [Сравнение критериев](diva-lead/v63-wip/COMPARISON_RU.md).

**[Более свежий исследовательский A/B: оригинал → v63 → продолжение](diva-lead/research/three-held-continuation/after-v63/research-checkpoint/AB_REFERENCE_V63_CONTINUED_AFTER63_WIP.mp3)**, [WAV и инструкция FL](diva-lead/research/three-held-continuation/after-v63/research-checkpoint/FL_STUDIO_WAV_RU.md). Этот шаг новее DLL v63 и сохранён отдельно. [Все новые подборы и проверки](diva-lead/research/three-held-continuation/after-v63/README.md).

Точное совпадение ещё не достигнуто. Сравнение ведётся с исходным WAV пользователя, совпадение цели по семплам подтверждено. Свежие Diva/Windows-рендеры, независимая цепочка собственной NEW-базы, причинные проверки четырёх частот дискретизации и DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись.

[Предыдущий полный v62](diva-lead/v62-wip/README.md), [текущая трёхнотная основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json).

'''+archive)
p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start)
p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v63](../../v63-wip/README.md), [FL Studio](../../v63-wip/FL_STUDIO_RU.md). [Более свежий исследовательский A/B и все новые доказательства](after-v63/README.md), [текущая трёхнотная основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение ещё не достигнуто; работа продолжается.'+text[end:])
write(OUT/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previous_public_commit=head,new_full_release='v63-wip',complete_release_selected='verified-cont-0031-hf',new_fully_proved_models=[p.parent.name for d,p in reports],selected_research=selected,tone_score=best['tone_score'],score=best['score'],archived_numeric_journals=len(archived),match_reached=False))
(OUT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(OUT))+'\n' for p in sorted(OUT.rglob('*')) if p.is_file()))
print('V63_AND_ALL_COMPLETED_RESEARCH_STAGED',selected,len(reports),len(archived),flush=True)
