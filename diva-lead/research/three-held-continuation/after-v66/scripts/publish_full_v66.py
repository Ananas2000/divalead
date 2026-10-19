"""Publish the fully tested v66 kit and completed accepted/rejected evidence."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation'
T=R/'v66-build';D=T/'v66-wip';O=ROOT/'after-v66';PAUSE=R/'auto-backup.pause'
DIAGNOSTICS=Path('/tmp/divalead-pw-diagnostics-archive')
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=REPO,text=True).strip()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def immutable_copy(source,target):
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    try:os.link(source,target)
    except OSError:shutil.copyfile(source,target)
    assert sha(source)==sha(target);return str(target)
def numeric_snapshot(source,target):
    shutil.copytree(source,target,ignore=lambda folder,names:[n for n in names if n=='__pycache__' or Path(n).suffix in {'.so','.dll','.exe','.pyc','.tmp','.lock'}])
    archived=[]
    for path in target.rglob('history.json'):
        original=path.read_bytes();compressed=path.with_name(path.name+'.gz')
        compressed.write_bytes(gzip.compress(original,compresslevel=6,mtime=0));assert gzip.decompress(compressed.read_bytes())==original
        archived.append(dict(path=str(path.relative_to(target)),gzip=str(compressed.relative_to(target)),SHA256=hashlib.sha256(original).hexdigest()));path.unlink()
    write(target/'archived-journals.json',archived)

proof=json.loads((D/'verification/selected_validation.json').read_text());selection=json.loads((T/'selected-basis.json').read_text())
zip_proof=json.loads((T/'ZIP-proof.json').read_text());assert zip_proof['all_extracted_files_byte_equal'] and zip_proof['clean_extraction_release_replay_passed'] and zip_proof['byte_exact_DLL_rebuild']
assert json.loads((T/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
assert sha(T/'Diva_lead_v66_WIP_checkpoint.zip')==zip_proof['ZIP_SHA256']
assert proof['all_chosen_three_guards_passed'] and proof['original_three_held_MIDI_events_unchanged']
family=proof.get('source_family','original-user-selected-three');changes=proof.get('changed_source_fields',{})
assert (family=='PulseWidth51.90' and changes=={'OSC:PW':51.90}) or (family=='original-user-selected-three' and not changes)
assert json.loads((DIAGNOSTICS/'manifest.json').read_text())['all_members_SHA_verified']
assert not PAUSE.exists();write(PAUSE,dict(owner='publish-full-v66',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(60):
    status=json.loads((R/'auto-backup-state.json').read_text())
    if status['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(status)

with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    immutable={path:git('rev-parse','HEAD:'+path) for i in range(57,66) for path in [f'diva-lead/v{i}-wip',f'Diva_lead_v{i}_WIP_checkpoint.zip']}
    assert not O.exists() and not (REPO/'diva-lead/v66-wip').exists()
    shutil.copytree(D,REPO/'diva-lead/v66-wip',copy_function=immutable_copy)
    immutable_copy(T/'Diva_lead_v66_WIP_checkpoint.zip',REPO/'Diva_lead_v66_WIP_checkpoint.zip')
    O.mkdir();(O/'diagnostics').mkdir();(O/'scripts').mkdir()
    for path in DIAGNOSTICS.iterdir():
        if path.is_file():shutil.copyfile(path,O/'diagnostics'/path.name)
    for name in ['ZIP-proof.json','clean-ZIP-Windows-proof.json','clean-extraction-proof.json','fresh-source-proof.json','release-proof.json','spectral-proof.json','selected-basis.json']:
        shutil.copyfile(T/name,O/('v66-'+name))
    scripts=['build_three_v66.py','write_v66_docs.py','finalize_v66.py','verify_zip_windows_v66.py','run_full_v66_build.py','run_v66_after_coupled135.py','publish_full_v66.py',
             'fit_pw5190_coupled135.py','run_pw5190_coupled135.py','three_gain_interior_projection.py','project_three_existing_vector.py','fit_three_gains.py',
             'repair_pw5190_gain_all_guards.py','run_pw5190_gain_all_guards.py','probe_pw5190_accuracy.py','run_pw5190_accuracy_probe.py','archive_completed_pw_diagnostics.py',
             'auto_backup_three.py','start_three_services.py','handoff_publisher_idle.py','deduplicate_immutable_audio.py','deduplicate_completed_three_sources.py']
    for name in scripts:
        shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
    for name in ['publisher-transient-auth-diagnostic.json','publisher-idle-handoff-latest.json','pw5190-gain-research/decision.json','pw5190-gain-interior-allguards/projection.json']:
        target=O/'diagnostics'/name.replace('/','--');shutil.copyfile(R/name,target)
    run=R/'pw5190-coupled135-research';scratch=Path('/tmp/divalead-pw5190-coupled135')
    if run.exists():numeric_snapshot(run,O/'joint-numeric-run')
    if scratch.exists():numeric_snapshot(scratch,O/'joint-numeric-scratch')
    shutil.copyfile(R/'source-pw5190-coupled135-control/paused-balance-power.json',O/'diagnostics/coupled-owner-resumed.json')
    assert 'resumed_UTC' in json.loads((O/'diagnostics/coupled-owner-resumed.json').read_text())
    current=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
    current={k:(v.replace('v65','v66').replace('V65','V66') if isinstance(v,str) else v) for k,v in current.items()}
    current.update(ZIP_SHA256=zip_proof['ZIP_SHA256'],DLL_SHA256=sha(D/'Diva_Lead_Finish_v66_WIP_x64.dll'),
        research_model='diva-lead/research/three-held-continuation/after-v66',score=proof['score'],tone_score=proof['tone_score'],
        AB_previous_current='diva-lead/v66-wip/AB_REFERENCE_V65_V66_WIP.wav',AB_MP3='diva-lead/v66-wip/AB_REFERENCE_V65_V66_WIP.mp3',
        source_preset_and_MIDI_unchanged_from_user_selected_three=not bool(changes),MIDI_unchanged_from_user_selected_three=True,
        Diva_changed_parameters=changes,source_family=family)
    write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
    pointer=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text())
    pointer.update(selected_complete_release='diva-lead/v66-wip',selected_complete_release_tone_score=proof['tone_score'],
        selected_complete_release_score=proof['score'],selected_complete_release_source_family=family,
        selected_complete_release_source_changes=changes,latest_research_is_not_a_new_complete_DLL_release=pointer['tone_score']<proof['tone_score']-1e-9)
    write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',pointer)
    source_text='В Diva изменена только ширина импульса: 51,87 → 51,90; остальные 280 параметров прежние.' if changes else 'Пресет Diva и все 281 параметр прежние.'
    (O/'README.md').write_text(f'''# Трёхнотное продолжение: полный v66 WIP

[Полный v66](../../../v66-wip/README.md), [ZIP](../../../../Diva_lead_v66_WIP_checkpoint.zip), [FL Studio](../../../v66-wip/FL_STUDIO_RU.md), [оригинал → v65 → v66](../../../v66-wip/AB_REFERENCE_V65_V66_WIP.mp3): 0 / 4,168 / 8,336 с.

Три длинные ноты на фразу, два прохода, шесть note-on, прежние длительности/огибающие/внутренний ARP. {source_text} Источник: `{family}`. Выбран самый низкий полностью проверенный показатель тембра на момент начала сборки: **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это ошибки измерений, не проценты сходства; точное совпадение не достигнуто. Все регрессии указаны в таблице комплекта.

Проверены свежая настоящая Diva, сырой WAV/all281/12events, Windows DLL/native, полная независимая цепочка соответствующей именно этому источнику собственной NEW-базы, отдельный fixture, 12 причинных случаев четырёх частот, API/FXP/состояние/PDC/блоки, точная пересборка и фактический полный WAV DLL из чистого ZIP. Лицензионная Diva не включена; GUI FL Studio и прослушивание ассистентом не выполнялись. v57–v65 и их ZIP неизменны.

Сначала новая точка93 усилений провалила свежий предел огибающей на2,25e-11 и была отклонена без заявления о12 причинных случаях. Численный проектор усилен: запас нужен во всех прежних ограничениях, а не только whole/crest. Малая коррекция тех же коэффициентов с положительным запасом прошла весь фактический цикл. Аудиодопуски, исходные ограничения, источник сравнения и число нот не ослаблялись. Отдельно проверены совместные135 существующих усилений и стереозначений; завершённые численные результаты и решение сохранены независимо от того, стал ли этот опыт выбранным.

`diagnostics/` содержит8 реальных проб качества Diva/алиасинга и не принятый первоначальный gain-опыт: тар/gzip архив со всеми исходными байтами, проверенными распаковкой/SHA, плюс явные решения и отчёты. Рост точности доDivine не улучшил сравнение; дополнительный флаг подавления алиасинга дал те же сырьевые семплы в этом пресете. `joint-numeric-*` содержит отдельную совместную попытку, сжатые history.json распаковать по archived-journals.json для исторического повторения. Историческая ошибка не переименована в принятую точку.

Живые служебные программы в `scripts/` скопированы на независимые inode. Это архив исходников подготовленной среды, не самостоятельная установка. [Текущая основа](../CURRENT_THREE_NOTE_MODEL.json) и [автоматические WAV/A-B](../after-v64/auto-checkpoints/README.md) отдельно отражают более позднее исследование. Исследовательское A/B использует v64 как фиксированный контроль; полный66 сравнивает65. Промежуточная публикация не является достижением совпадения.
''')
    readme=REPO/'README.md';old=readme.read_text();archive=old[old.index('**Архивный исследовательский этап:**'):]
    readme.write_text(f'''# Diva: реконструкция лида для FL Studio

Три длинные ноты на фразу: MIDI 41 → 37 → 36. Повторы и октавы создаёт внутренний ARP Diva. {source_text} MIDI и длительности сохранены.

**[Полный v66 WIP](diva-lead/v66-wip/README.md)** — [скачать ZIP](Diva_lead_v66_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v66-wip/FL_STUDIO_RU.md). Пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и завершённые проверки.

**[Оригинал → v65 → v66](diva-lead/v66-wip/AB_REFERENCE_V65_V66_WIP.mp3)**: 0 / 4,168 / 8,336 с. [Готовый отдельный WAV](diva-lead/v66-wip/Diva_Lead_v66_REFERENCE_EDIT.wav), [измерения и регрессии](diva-lead/v66-wip/COMPARISON_RU.md).

Ошибка тембра v66 **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это измерения, не проценты сходства; точное совпадение ещё не достигнуто. [Новые пробы и доказательства](diva-lead/research/three-held-continuation/after-v66/README.md), [текущая основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json), [автоматические проверенные WAV](diva-lead/research/three-held-continuation/after-v64/auto-checkpoints/README.md). В автоматических снимках v64 остаётся фиксированным контролем.

Свежая Diva, Windows DLL, собственная NEW-база этого источника,12 причинных случаев четырёх частот и фактическая DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. [Предыдущий полный v65](diva-lead/v65-wip/README.md) сохранён.

'''+archive)
    p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start)
    p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v66](../../v66-wip/README.md), [FL Studio](../../v66-wip/FL_STUDIO_RU.md), [оригинал → v65 → v66](../../v66-wip/AB_REFERENCE_V65_V66_WIP.mp3). [Пробы и проверки](after-v66/README.md), [новые WAV](after-v64/auto-checkpoints/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение не достигнуто.'+text[end:])
    write(O/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_release=current,selected_proof=selection,
        earlier_57_to_65_trees_and_ZIPs_immutable=True,accuracy_probes=8,rejected_gain_preserved=True,match_reached=False))
    (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(O))+'\n' for p in sorted(O.rglob('*')) if p.is_file()))
    targets=['README.md','Diva_lead_v66_WIP_checkpoint.zip','diva-lead/v66-wip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json',str(O.relative_to(REPO)),str((ROOT/'README.md').relative_to(REPO)),str((ROOT/'CURRENT_THREE_NOTE_MODEL.json').relative_to(REPO))]
    git('add','--',*targets);staged=git('diff','--cached','--name-only').splitlines();assert staged and all(any(n==p or n.startswith(p+'/') for p in targets) for n in staged)
    git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
    git('commit','-m','Back up fully verified three-held Diva v66 and constrained physical-source research')
    for path,oid in immutable.items():assert git('rev-parse','HEAD:'+path)==oid
    commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    public=[]
    for relative in ['Diva_lead_v66_WIP_checkpoint.zip','diva-lead/v66-wip/FL_STUDIO_RU.md','diva-lead/v66-wip/Diva_Lead_Finish_v66_WIP_x64.dll','diva-lead/v66-wip/AB_REFERENCE_V65_V66_WIP.mp3','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative,timeout=60) as response:
            content=response.read();assert response.status==200
        assert content==(REPO/relative).read_bytes();public.append(dict(path=relative,SHA256=hashlib.sha256(content).hexdigest(),byte_exact=True))
    assert not git('status','--porcelain');assert json.loads(PAUSE.read_text())['owner']=='publish-full-v66';PAUSE.unlink()
    write(R/'public-v66-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_main_exact=True,HTTP_files=public,older_57_to_65_trees_and_ZIPs_immutable=True,tone_score=proof['tone_score'],source_family=family,match_reached=False))
    print('FULL_V66_PUSHED_AND_REAL_HTTP_BYTES_VERIFIED',commit,proof['tone_score'],family,flush=True)
