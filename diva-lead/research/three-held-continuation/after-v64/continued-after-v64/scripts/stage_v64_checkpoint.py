"""Publish only completed evidence and an entirely tested immutable v64 kit."""
from pathlib import Path
import os,sys,json,hashlib,shutil,subprocess,gzip,re,datetime
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation';O=ROOT/'after-v64';T=R/'v64-build'
assert not O.exists() and not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
assert json.loads((T/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
assert json.loads((T/'ZIP-proof.json').read_text())['clean_extraction_release_replay_passed']
selection=json.loads((T/'selected-basis.json').read_text());full=json.loads(Path(selection['validation']).read_text())
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def link(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
    try:os.link(a,b)
    except OSError:shutil.copyfile(a,b)
    return str(b)
def snapshot(a,b,release=False):
    def ignore(directory,names):return [n for n in names if n=='__pycache__' or Path(n).suffix in ['.pyc','.so','.exe','.tmp','.lock'] or (not release and Path(n).suffix=='.dll')]
    shutil.copytree(a,b,copy_function=link,ignore=ignore)
seen=set()
for p in ROOT.rglob('validation.json'):
    try:seen.add(Path(json.loads(p.read_text())['core_model']).parent.parent.name)
    except (KeyError,ValueError):pass
new=sorted(p for p in R.glob('verified-*/validation.json') if p.parent.name not in seen)
assert len(new)>=3
O.mkdir();snapshot(T/'v64-wip',REPO/'diva-lead/v64-wip',True);link(T/'Diva_lead_v64_WIP_checkpoint.zip',REPO/'Diva_lead_v64_WIP_checkpoint.zip')
for p in new:snapshot(p.parent,O/'proofs'/p.parent.name)
sources=[]
for family,start in [('continuation',33),('joint-phase-continuation',30),('balance-power-continuation',1)]:
    for p in sorted((R/family).glob('round-*')):
        if int(p.name.split('-')[1])<start:continue
        scratch=Path(json.loads((p/'numeric-location.json').read_text())['numeric_scratch']) if (p/'numeric-location.json').exists() else p/'numeric'
        if not any(scratch.rglob('optimizer.json')):continue
        dest=O/'numeric'/family/p.name;snapshot(p,dest);sources.append((p,dest))
        if not scratch.is_relative_to(p):snapshot(scratch,dest/'numeric');sources.append((scratch,dest/'numeric'))
for n in ['joint30-fine55-projection','fine55-power69-combination']:
    p=R/n;dest=O/'numeric'/n;snapshot(p,dest);sources.append((p,dest))
for n in ['divalead-joint30-fine55-projection','divalead-fine55-power69-combination']:
    p=Path('/tmp')/n;assert any(p.rglob('optimizer.json'));dest=O/'numeric'/n;snapshot(p,dest);sources.append((p,dest))
archived=[]
for row in json.loads((R.parent/'history-lossless-archive.json').read_text())['files']:
    old=Path(row['path'])
    if old.exists():continue
    for source,dest in sources:
        if old.is_relative_to(source):
            gz=Path(row['gzip']);data=gzip.decompress(gz.read_bytes());assert hashlib.sha256(data).hexdigest()==row['SHA256']
            q=dest/(str(old.relative_to(source))+'.gz')
            if not q.exists():link(gz,q)
            archived.append(dict(path=str(q.relative_to(O))[:-3],gzip=str(q.relative_to(O)),SHA256=row['SHA256']));break
write(O/'archived-numeric-journals.json',archived)
(O/'scripts').mkdir()
for p in R.glob('*.py'):shutil.copyfile(p,O/'scripts'/p.name)
for n in ['public-v63-verification.json','staged-v63-verification.json','config63-save-readback.json','current-checkout-discovery.json','v63-incremental-Git-pack.json','joint-phase-idle-resource-handoff.json','drift-to-original-balance-power-handoff.json']:
    p=R/n
    if p.exists():shutil.copyfile(p,O/n)
for n in ['clean-ZIP-Windows-proof.json','ZIP-proof.json','clean-extraction-proof.json','fresh-source-proof.json','release-proof.json','spectral-proof.json']:
    shutil.copyfile(T/n,O/('v64-'+n))
pattern=re.compile('v63|V63');current=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
current={k:(pattern.sub(lambda m:'v64' if m.group()=='v63' else 'V64',v) if isinstance(v,str) else v) for k,v in current.items()}
current.update(ZIP_SHA256=hashlib.sha256((T/'Diva_lead_v64_WIP_checkpoint.zip').read_bytes()).hexdigest(),DLL_SHA256=hashlib.sha256((T/'v64-wip/Diva_Lead_Finish_v64_WIP_x64.dll').read_bytes()).hexdigest(),research_model='diva-lead/research/three-held-continuation/after-v64',score=full['score'],tone_score=full['tone_score'],AB_previous_current='diva-lead/v64-wip/AB_REFERENCE_V63_V64_WIP.wav',AB_MP3='diva-lead/v64-wip/AB_REFERENCE_V63_V64_WIP.mp3')
write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
model=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text());model.update(selected_complete_release='diva-lead/v64-wip',research_validation='after-v64/proofs/'+Path(selection['validation']).parent.name+'/validation.json',tone_score=full['tone_score'],score=full['score'],selected_complete_release_tone_score=full['tone_score'],selected_complete_release_score=full['score'],latest_research_is_not_a_new_complete_DLL_release=False)
write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',model)
write(O/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_release_selected=selection,completed_new_models=[p.parent.name for p in new],all_source_notes_and_preset_unchanged=True,match_reached=False))
(O/'README.md').write_text('''# v64: совместная проверка тонкой фазы и динамических гармоник

Полный промежуточный [v64](../../../v64-wip/README.md), [инструкция FL Studio](../../../v64-wip/FL_STUDIO_RU.md), [оригинал → v63 → v64](../../../v64-wip/AB_REFERENCE_V63_V64_WIP.mp3): 0 / 4,168 / 8,336 с.

Исходный выбранный пресет Diva, все 281 параметр, сырой WAV, ARP, огибающие и 12 входящих MIDI-событий остаются прежними. Три длинные ноты на фразу, два прохода. Подбор сравнивается именно с исходным WAV пользователя. Точное совпадение не достигнуто.

Завершённый fine55-раунд дал более низкую численную ошибку, но его последние точки нарушали фиксированные ограничения. Незначительная коррекция существующих 55 коэффициентов вернула точку внутрь прежних пределов с численным запасом; свежая Diva/Windows/собственная NEW-база/fixture/12 причинных случаев подтвердили её. Затем проверено сочетание с ранее найденными 69 коэффициентами динамических целей. Простые доли 0,25/0,5/0,75/1,0 нарушали ограничения; малая совместная коррекция тех же коэффициентов прошла всю проверку заново. Это совместный доказанный вариант, а не предположение, что два отдельных улучшения складываются.

`proofs/` содержит новые завершённые проверки; `numeric/` — завершённые раунды и обе проекции, включая не прошедшие долевые сочетания. `archived-numeric-journals.json` указывает точные gzip-журналы, если они были сжаты внешним хранителем кэша; распаковать перед повторным историческим запуском. Все ограничения и допустимые ошибки DSP прежние. Измеряемое улучшение не является процентом сходства на слух, регрессии показаны в [таблице](../../../v64-wip/COMPARISON_RU.md).

Полный v64 прошёл свежий фактический рендер Diva, Windows/native, независимый повтор полной цепочки подходящей собственной NEW-базы, отдельный fixture, все 12 произвольных причинных случаев на четырёх частотах, разные размеры блока, API/FXP/состояние/PDC, точную пересборку, чистую распаковку и фактический рендер DLL из ZIP. GUI FL Studio и прослушивание ассистентом не выполнялись. Исходная Diva не распространяется.

После бэкапа продолжаются три процесса исходного трёхнотного семейства: HF/усиления, общая/тонкая фаза, финальный баланс/динамические цели. Снимки `scripts/` содержат рабочие программы, но одноразовые handoff/build/stage-программы нельзя автоматически повторять в новой среде: они используют пути, версии и текущие PID. Живые состояния среды читаются из приватных JSON и реальных журналов. Сохранение настроек облачной среды требует публикации черновика для будущих запусков; оно не доказывает восстановление в новой задаче.
''')
p=REPO/'README.md';text=p.read_text();archive=text[text.index('**Архивный исследовательский этап:**'):]
p.write_text('''# Diva: реконструкция лида для FL Studio

Исключительно выбранный вариант с тремя длинными нотами на фразу: MIDI 41 → 37 → 36. Повторы и октавы создаёт внутренний ARP Diva. Пресет, все 281 параметр и MIDI прежние.

**[Полный v64 WIP](diva-lead/v64-wip/README.md)** — [скачать ZIP](Diva_lead_v64_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v64-wip/FL_STUDIO_RU.md). В комплекте пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и проверки.

**[Оригинал → v63 → v64](diva-lead/v64-wip/AB_REFERENCE_V63_V64_WIP.mp3)**: 0 / 4,168 / 8,336 с. [WAV сравнения](diva-lead/v64-wip/AB_REFERENCE_V63_V64_WIP.wav), [отдельный готовый WAV](diva-lead/v64-wip/Diva_Lead_v64_REFERENCE_EDIT.wav), [измерения и регрессии](diva-lead/v64-wip/COMPARISON_RU.md).

Совместно проверены новые поправки тонкой фазы и динамического баланса гармоник. Ошибка тембра уменьшилась, точное совпадение ещё не достигнуто. [Исследование и новые проверки](diva-lead/research/three-held-continuation/after-v64/README.md), [текущая основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json).

Свежая Diva, Windows DLL, подходящая собственная NEW-база, 12 причинных случаев четырёх частот и фактическая DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. [Предыдущий полный v63](diva-lead/v63-wip/README.md).

'''+archive)
p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start);p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v64](../../v64-wip/README.md), [FL Studio](../../v64-wip/FL_STUDIO_RU.md). [Оригинал → v63 → v64](../../v64-wip/AB_REFERENCE_V63_V64_WIP.mp3). [Новые подборы и проверки](after-v64/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение не достигнуто; подбор продолжается.'+text[end:])
(O/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(O))+'\n' for p in sorted(O.rglob('*')) if p.is_file()))
print('V64_COMPLETE_KIT_AND_NEW_PROOFS_STAGED',len(new),Path(selection['validation']).parent.name,flush=True)
