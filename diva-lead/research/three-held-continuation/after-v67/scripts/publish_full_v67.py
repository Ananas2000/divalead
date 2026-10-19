"""Publish the fully tested v67 kit and completed accepted/rejected evidence."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation'
T=Path('/tmp/divalead-v67-build');D=T/'v67-wip';O=ROOT/'after-v67';PAUSE=R/'auto-backup.pause'
DIAGNOSTICS=Path('/tmp/divalead-post66-phase-diagnostics')
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
assert sha(T/'Diva_lead_v67_WIP_checkpoint.zip')==zip_proof['ZIP_SHA256']
assert proof['all_chosen_three_guards_passed'] and proof['original_three_held_MIDI_events_unchanged']
family=proof.get('source_family','original-user-selected-three');changes=proof.get('changed_source_fields',{})
assert (family=='PulseWidth51.90' and changes=={'OSC:PW':51.90}) or (family=='original-user-selected-three' and not changes)
assert json.loads((DIAGNOSTICS/'manifest.json').read_text())['all_members_SHA_verified']
assert not PAUSE.exists();write(PAUSE,dict(owner='publish-full-v67',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(60):
    status=json.loads((R/'auto-backup-state.json').read_text())
    if status['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(status)

with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    immutable={path:git('rev-parse','HEAD:'+path) for i in range(57,67) for path in [f'diva-lead/v{i}-wip',f'Diva_lead_v{i}_WIP_checkpoint.zip']}
    assert not O.exists() and not (REPO/'diva-lead/v67-wip').exists()
    shutil.copytree(D,REPO/'diva-lead/v67-wip',copy_function=immutable_copy)
    immutable_copy(T/'Diva_lead_v67_WIP_checkpoint.zip',REPO/'Diva_lead_v67_WIP_checkpoint.zip')
    O.mkdir();(O/'diagnostics').mkdir();(O/'scripts').mkdir()
    for path in DIAGNOSTICS.iterdir():
        if path.is_file():shutil.copyfile(path,O/'diagnostics'/path.name)
    for name in ['ZIP-proof.json','clean-ZIP-Windows-proof.json','clean-extraction-proof.json','fresh-source-proof.json','release-proof.json','spectral-proof.json','selected-basis.json']:
        shutil.copyfile(T/name,O/('v67-'+name))
    scripts=['build_three_v67.py','write_v67_docs.py','finalize_v67.py','verify_zip_windows_v67.py','run_full_v67_build.py','publish_full_v67.py',
             'three_fine55_interior_projection.py','fit_three_fine55.py','repair_pw_phase_margin.py','project_three_existing_vector.py',
             'continue_pw5190_main.py','continue_pw5190_phase.py','continue_pw5190_balance.py','auto_backup_three.py','start_three_services.py']
    for name in scripts:
        shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
    for name in ['fine55-safe-selection-integration.json','source-history-isolation-complete.json','operational-reserve-sizing-v66.json']:
        shutil.copyfile(R/name,O/'diagnostics'/name)
    numeric_snapshot(R/'pw5190-live-phase/round-0030-fine55',O/'initial-phase-numeric-run')
    numeric_snapshot(R/'pw5190-phase-interior-0030',O/'interior-phase-numeric-run')
    current=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
    current={k:(v.replace('v66','v67').replace('V66','V67') if isinstance(v,str) else v) for k,v in current.items()}
    current.update(ZIP_SHA256=zip_proof['ZIP_SHA256'],DLL_SHA256=sha(D/'Diva_Lead_Finish_v67_WIP_x64.dll'),
        research_model='diva-lead/research/three-held-continuation/after-v67',score=proof['score'],tone_score=proof['tone_score'],
        AB_previous_current='diva-lead/v67-wip/AB_REFERENCE_V66_V67_WIP.wav',AB_MP3='diva-lead/v67-wip/AB_REFERENCE_V66_V67_WIP.mp3',
        source_preset_and_MIDI_unchanged_from_user_selected_three=not bool(changes),MIDI_unchanged_from_user_selected_three=True,
        Diva_changed_parameters=changes,source_family=family)
    write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
    pointer=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text())
    full_manifest=json.loads((D/'source_manifest.json').read_text())
    import numpy as np,soundfile as sf
    def same_wave(first,second):
        x,xr=sf.read(first);y,yr=sf.read(second);return xr==yr and np.array_equal(x,y)
    covered=bool(json.loads(Path(proof['core_model']).read_text())==json.loads((D/'analysis/spectral_model.json').read_text())
        and sha(proof['source_preset'])==sha(D/full_manifest['source_preset'])
        and same_wave(proof['new_source_raw'],D/full_manifest['source_WAV'])
        and same_wave(proof['new_source_before_fixture'],D/full_manifest['before_spectral_WAV'])
        and same_wave(proof['NEW_independent_prebase'],D/full_manifest['NEW_independent_base'])
        and pointer['tone_score']==proof['tone_score'])
    assert covered
    pointer.update(selected_complete_release='diva-lead/v67-wip',selected_complete_release_tone_score=proof['tone_score'],
        selected_complete_release_score=proof['score'],selected_complete_release_source_family=family,
        selected_complete_release_source_changes=changes,latest_research_is_not_a_new_complete_DLL_release=False,
        research_model_already_in_selected_complete_release=True)
    write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',pointer)
    source_text='В Diva ширина импульса 51,90; все 281 параметр, MIDI и исходный WAV совпадают с полным v66.'
    (O/'README.md').write_text(f'''# Трёхнотное продолжение: полный v67 WIP

[Полный v67](../../../v67-wip/README.md), [ZIP](../../../../Diva_lead_v67_WIP_checkpoint.zip), [FL Studio](../../../v67-wip/FL_STUDIO_RU.md), [оригинал → v66 → v67](../../../v67-wip/AB_REFERENCE_V66_V67_WIP.mp3): 0 / 4,168 / 8,336 с.

Три длинные ноты на фразу, два прохода, шесть note-on, прежние длительности, огибающие и внутренний ARP. {source_text} Уточнены существующие коэффициенты обработки Finish. Ошибка тембра **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это ошибки измерений, не проценты сходства. Точное совпадение не достигнуто; все регрессии показаны в COMPARISON_RU.md.

Свежая настоящая Diva, all281/raw/12events, Windows DLL/native, полная независимая цепочка собственной NEW-базы этого источника, отдельный fixture, 12 причинных случаев четырёх частот, API/FXP/состояние/PDC/блоки, точная пересборка, чистый ZIP и фактический полный WAV DLL из этого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. Лицензионная Diva не включена. Полные v57–v66 и их ZIP сохранены неизменными.

После публикации v66 завершены новые HF100, balance42 и fine55 попытки. Первоначальный fine55 дал низкую численную ошибку, но фактический новый рендер нарушил whole/stereo-phase: точка отклонена, validation.json не создан и 12 причинных случаев для неё не заявляются. Архив diagnostics сохраняет её реальные WAV, параметры и решение с проверкой каждого распакованного SHA. Исправлена минимальная коррекция тех же 55 коэффициентов внутрь всех прежних ограничений; исправленный кандидат прошёл весь свежий цикл и выбран для v67. Пределы качества и DSP не ослаблены, новых нот или состояний обработки не добавлено.

Фактическая интеграционная проверка исполнила callback настоящего fitter: прежний пограничный best сохранён байт-в-байт, вариант с положительным запасом выбран даже при немного большей численной ошибке; выбранные коэффициенты точно совпали с полностью проверенным исправленным кандидатом. История попыток отделена по семействам без прерывания работающего fit; исходные записи сохранены для аудита. scripts содержит независимые копии служебных программ, numeric-run содержит исходные и исправленные результаты с lossless gzip журналами. Это архив подготовленной среды, не самостоятельная установка.

[Текущая основа](../CURRENT_THREE_NOTE_MODEL.json) и [автоматические WAV](../after-v64/auto-checkpoints/README.md) сохраняются отдельно. Исследовательское A/B использует v64 как фиксированный контроль, полный v67 сравнивает v66. Новые раунды ожидают свободного места; предыдущие результаты сохранены.
''')
    readme=REPO/'README.md';old=readme.read_text();archive=old[old.index('**Архивный исследовательский этап:**'):]
    readme.write_text(f'''# Diva: реконструкция лида для FL Studio

Три длинные ноты на фразу: MIDI 41 → 37 → 36. Повторы и октавы создаёт внутренний ARP Diva. {source_text} MIDI и длительности сохранены.

**[Полный v67 WIP](diva-lead/v67-wip/README.md)** — [скачать ZIP](Diva_lead_v67_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v67-wip/FL_STUDIO_RU.md). Пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и завершённые проверки.

**[Оригинал → v66 → v67](diva-lead/v67-wip/AB_REFERENCE_V66_V67_WIP.mp3)**: 0 / 4,168 / 8,336 с. [Готовый отдельный WAV](diva-lead/v67-wip/Diva_Lead_v67_REFERENCE_EDIT.wav), [измерения и регрессии](diva-lead/v67-wip/COMPARISON_RU.md).

Ошибка тембра v67 **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это измерения, не проценты сходства; точное совпадение ещё не достигнуто. [Новые пробы и доказательства](diva-lead/research/three-held-continuation/after-v67/README.md), [текущая основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json), [автоматические проверенные WAV](diva-lead/research/three-held-continuation/after-v64/auto-checkpoints/README.md). В автоматических снимках v64 остаётся фиксированным контролем.

Свежая Diva, Windows DLL, собственная NEW-база этого источника,12 причинных случаев четырёх частот и фактическая DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. [Предыдущий полный v66](diva-lead/v66-wip/README.md) сохранён.

'''+archive)
    p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start)
    p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v67](../../v67-wip/README.md), [FL Studio](../../v67-wip/FL_STUDIO_RU.md), [оригинал → v66 → v67](../../v67-wip/AB_REFERENCE_V66_V67_WIP.mp3). [Пробы и проверки](after-v67/README.md), [новые WAV](after-v64/auto-checkpoints/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение не достигнуто.'+text[end:])
    write(O/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_release=current,selected_proof=selection,
        earlier_57_to_66_trees_and_ZIPs_immutable=True,rejected_phase_preserved=True,fine55_selection_integration_passed=True,match_reached=False))
    (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(O))+'\n' for p in sorted(O.rglob('*')) if p.is_file()))
    targets=['README.md','Diva_lead_v67_WIP_checkpoint.zip','diva-lead/v67-wip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json',str(O.relative_to(REPO)),str((ROOT/'README.md').relative_to(REPO)),str((ROOT/'CURRENT_THREE_NOTE_MODEL.json').relative_to(REPO))]
    git('add','--',*targets);staged=git('diff','--cached','--name-only').splitlines();assert staged and all(any(n==p or n.startswith(p+'/') for p in targets) for n in staged)
    git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
    git('commit','-m','Back up fully verified three-held Diva v67 and guarded phase correction')
    for path,oid in immutable.items():assert git('rev-parse','HEAD:'+path)==oid
    commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    public=[]
    for relative in ['Diva_lead_v67_WIP_checkpoint.zip','diva-lead/v67-wip/FL_STUDIO_RU.md','diva-lead/v67-wip/Diva_Lead_Finish_v67_WIP_x64.dll','diva-lead/v67-wip/AB_REFERENCE_V66_V67_WIP.mp3','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative,timeout=60) as response:
            content=response.read();assert response.status==200
        assert content==(REPO/relative).read_bytes();public.append(dict(path=relative,SHA256=hashlib.sha256(content).hexdigest(),byte_exact=True))
    assert not git('status','--porcelain');assert json.loads(PAUSE.read_text())['owner']=='publish-full-v67';PAUSE.unlink()
    write(R/'public-v67-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_main_exact=True,HTTP_files=public,older_57_to_66_trees_and_ZIPs_immutable=True,tone_score=proof['tone_score'],source_family=family,match_reached=False))
    print('FULL_V67_PUSHED_AND_REAL_HTTP_BYTES_VERIFIED',commit,proof['tone_score'],family,flush=True)
