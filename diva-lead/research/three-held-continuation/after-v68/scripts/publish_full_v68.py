"""Publish the fully tested v68 kit and completed accepted/rejected evidence."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead');ROOT=REPO/'diva-lead/research/three-held-continuation'
T=Path('/tmp/divalead-v68-build');D=T/'v68-wip';O=ROOT/'after-v68';PAUSE=R/'auto-backup.pause'

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
assert sha(T/'Diva_lead_v68_WIP_checkpoint.zip')==zip_proof['ZIP_SHA256']
assert proof['all_chosen_three_guards_passed'] and proof['original_three_held_MIDI_events_unchanged']
family=proof.get('source_family','original-user-selected-three');changes=proof.get('changed_source_fields',{})
assert (family=='PulseWidth51.90' and changes=={'OSC:PW':51.90}) or (family=='original-user-selected-three' and not changes)
assert proof['tone_score']<json.loads((REPO/'diva-lead/v67-wip/verification/selected_validation.json').read_text())['tone_score']-1e-6
assert not PAUSE.exists();write(PAUSE,dict(owner='publish-full-v68',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(60):
    status=json.loads((R/'auto-backup-state.json').read_text())
    if status['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(status)

with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    immutable={path:git('rev-parse','HEAD:'+path) for i in range(57,68) for path in [f'diva-lead/v{i}-wip',f'Diva_lead_v{i}_WIP_checkpoint.zip']}
    assert not O.exists() and not (REPO/'diva-lead/v68-wip').exists()
    shutil.copytree(D,REPO/'diva-lead/v68-wip',copy_function=immutable_copy)
    immutable_copy(T/'Diva_lead_v68_WIP_checkpoint.zip',REPO/'Diva_lead_v68_WIP_checkpoint.zip')
    O.mkdir();(O/'diagnostics').mkdir();(O/'scripts').mkdir()
    for name in ['ZIP-proof.json','clean-ZIP-Windows-proof.json','clean-extraction-proof.json','fresh-source-proof.json','release-proof.json','spectral-proof.json','selected-basis.json']:
        shutil.copyfile(T/name,O/('v68-'+name))
    scripts=['build_three_v68.py','write_v68_docs.py','finalize_v68.py','verify_zip_windows_v68.py','run_full_v68_build.py','publish_full_v68.py',
             'deduplicate_retired_basis_audio.py','share_fixed_fir_kernel_headers.py','pack_new_loose_objects_streamed.py','three_fine55_interior_projection.py','project_three_existing_vector.py']
    for name in scripts:
        shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
    for name in ['retired-basis-exact-copy-audit.json','retired-basis-exact-copy-result.json','retired-numeric-exact-copy-audit.json','fixed-fir-kernel-sharing.json','pack-initial-attempt-recovery.json','streamed-loose-packs-result.json']:
        shutil.copyfile(R/name,O/'diagnostics'/name)
    for role,first in [('main',2),('phase',31),('balance',2)]:
        for run in sorted((R/('pw5190-live-'+role)).glob('round-*')):
            if int(run.name.split('-')[1])<first:continue
            location=run/'numeric-location.json'
            if not location.exists():continue
            scratch=Path(json.loads(location.read_text())['numeric_scratch'])
            if not list(scratch.rglob('optimizer.json')):continue
            numeric_snapshot(run,O/'numeric'/role/run.name)
            numeric_snapshot(scratch,O/'numeric-scratch'/role/run.name)
    current=json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
    current={k:(v.replace('v67','v68').replace('V67','V68') if isinstance(v,str) else v) for k,v in current.items()}
    current.update(ZIP_SHA256=zip_proof['ZIP_SHA256'],DLL_SHA256=sha(D/'Diva_Lead_Finish_v68_WIP_x64.dll'),
        research_model='diva-lead/research/three-held-continuation/after-v68',score=proof['score'],tone_score=proof['tone_score'],
        AB_previous_current='diva-lead/v68-wip/AB_REFERENCE_V67_V68_WIP.wav',AB_MP3='diva-lead/v68-wip/AB_REFERENCE_V67_V68_WIP.mp3',
        source_preset_and_MIDI_unchanged_from_user_selected_three=not bool(changes),MIDI_unchanged_from_user_selected_three=True,
        Diva_changed_parameters=changes,source_family=family)
    write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
    pointer=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text())
    full_manifest=json.loads((D/'source_manifest.json').read_text())
    import numpy as np,soundfile as sf
    def same_wave(first,second):
        x,xr=sf.read(first);y,yr=sf.read(second);return xr==yr and np.array_equal(x,y)
    research=json.loads((ROOT/pointer['research_validation']).read_text())
    covered=bool(json.loads(Path(research['core_model']).read_text())==json.loads((D/'analysis/spectral_model.json').read_text())
        and sha(research['source_preset'])==sha(D/full_manifest['source_preset'])
        and same_wave(research['new_source_raw'],D/full_manifest['source_WAV'])
        and same_wave(research['new_source_before_fixture'],D/full_manifest['before_spectral_WAV'])
        and same_wave(research['NEW_independent_prebase'],D/full_manifest['NEW_independent_base'])
        and pointer['tone_score']==proof['tone_score'])
    pointer.update(selected_complete_release='diva-lead/v68-wip',selected_complete_release_tone_score=proof['tone_score'],
        selected_complete_release_score=proof['score'],selected_complete_release_source_family=family,
        selected_complete_release_source_changes=changes,latest_research_is_not_a_new_complete_DLL_release=not covered,
        research_model_already_in_selected_complete_release=covered)
    write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',pointer)
    source_text='В Diva ширина импульса 51,90; все 281 параметр, MIDI и исходный WAV совпадают с полным v67.'
    (O/'README.md').write_text(f'''# Трёхнотное продолжение: полный v68 WIP

[Полный v68](../../../v68-wip/README.md), [ZIP](../../../../Diva_lead_v68_WIP_checkpoint.zip), [FL Studio](../../../v68-wip/FL_STUDIO_RU.md), [оригинал → v67 → v68](../../../v68-wip/AB_REFERENCE_V67_V68_WIP.mp3): 0 / 4,168 / 8,336 с.

Три удерживаемые ноты на фразу, два прохода, шесть note-on; прежние длительности, огибающие и внутренний ARP Diva. {source_text} Изменены только существующие коэффициенты Finish. Ошибка тембра **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это ошибки измерений, не проценты сходства. Совпадение не достигнуто; регрессии показаны в COMPARISON_RU.md.

После v67 проверены свободное место и состояние среды. Найдены111 точных копий входных WAV в завершённых численных раундах: объединение сохранило все исходные пути/байты/SHA и фактически освободило153862144байт. Ещё27 точных копий неизменяемой FIR-таблицы объединены с сохранением исходных путей/SHA, фактически освобождено76742656байт. Отдельная ограниченная упаковка новых объектов Git в /tmp сохранила все2621 объекта и все прежние пакеты; итоговая связность проверена. Первая неудачная упаковка не удаляла историю и её временные файлы сохранены для аудита. Все три прежних PW51.90 контроллера возобновились без снижения резерва256МиБ или изменения аудиограниц. Последующие численные результаты приняты только после свежей настоящей Diva, Windows/native, полной собственной NEW-базы этого источника, отдельного fixture и всех12 произвольных причинных случаев четырёх частот. Полный комплект дополнительно прошёл API/FXP/состояние/PDC/блоки, точную пересборку и фактический полный WAV DLL из чистого ZIP.

scripts содержит независимые копии программ; numeric и numeric-scratch сохраняют завершённые новые попытки, включая слабые результаты. Gzip журналов восстановить по archived-journals.json: исходные байты проверены. Свежие отвергнутые точки не выдаются за принятые. Всё ещё используется исходный загруженный оригинал; MistaTowa исключён. Лицензионная Diva не включена. GUI FL Studio и прослушивание ассистентом не выполнялись. Полные57–67 и их ZIP неизменны.

[Текущая основа](../CURRENT_THREE_NOTE_MODEL.json) и [автоматические проверенные WAV](../after-v64/auto-checkpoints/README.md) сохраняются отдельно и могут отражать более поздний результат. Исследовательское A/B использует v64 как фиксированный контроль; полный68 сравнивает67. Промежуточная публикация не означает завершённое совпадение или прекращение подбора.
''')
    readme=REPO/'README.md';old=readme.read_text();archive=old[old.index('**Архивный исследовательский этап:**'):]
    readme.write_text(f'''# Diva: реконструкция лида для FL Studio

Три длинные ноты на фразу: MIDI 41 → 37 → 36. Повторы и октавы создаёт внутренний ARP Diva. {source_text} MIDI и длительности сохранены.

**[Полный v68 WIP](diva-lead/v68-wip/README.md)** — [скачать ZIP](Diva_lead_v68_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v68-wip/FL_STUDIO_RU.md). Пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и завершённые проверки.

**[Оригинал → v67 → v68](diva-lead/v68-wip/AB_REFERENCE_V67_V68_WIP.mp3)**: 0 / 4,168 / 8,336 с. [Готовый отдельный WAV](diva-lead/v68-wip/Diva_Lead_v68_REFERENCE_EDIT.wav), [измерения и регрессии](diva-lead/v68-wip/COMPARISON_RU.md).

Ошибка тембра v68 **{proof['tone_score']:.10f}**, общая ошибка **{proof['score']:.10f}**. Это измерения, не проценты сходства; точное совпадение ещё не достигнуто. [Новые пробы и доказательства](diva-lead/research/three-held-continuation/after-v68/README.md), [текущая основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json), [автоматические проверенные WAV](diva-lead/research/three-held-continuation/after-v64/auto-checkpoints/README.md). В автоматических снимках v64 остаётся фиксированным контролем.

Свежая Diva, Windows DLL, собственная NEW-база этого источника,12 причинных случаев четырёх частот и фактическая DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. [Предыдущий полный v67](diva-lead/v67-wip/README.md) сохранён.

'''+archive)
    p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start)
    p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v68](../../v68-wip/README.md), [FL Studio](../../v68-wip/FL_STUDIO_RU.md), [оригинал → v67 → v68](../../v68-wip/AB_REFERENCE_V67_V68_WIP.mp3). [Пробы и проверки](after-v68/README.md), [новые WAV](after-v64/auto-checkpoints/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение не достигнуто.'+text[end:])
    write(O/'checkpoint.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),full_release=current,selected_proof=selection,
        earlier_57_to_67_trees_and_ZIPs_immutable=True,retired_exact_input_copies_shared=True,match_reached=False))
    (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(O))+'\n' for p in sorted(O.rglob('*')) if p.is_file()))
    targets=['README.md','Diva_lead_v68_WIP_checkpoint.zip','diva-lead/v68-wip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json',str(O.relative_to(REPO)),str((ROOT/'README.md').relative_to(REPO)),str((ROOT/'CURRENT_THREE_NOTE_MODEL.json').relative_to(REPO))]
    git('add','--',*targets);staged=git('diff','--cached','--name-only').splitlines();assert staged and all(any(n==p or n.startswith(p+'/') for p in targets) for n in staged)
    git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
    git('commit','-m','Back up fully verified three-held Diva v68 after resumed reference matching')
    for path,oid in immutable.items():assert git('rev-parse','HEAD:'+path)==oid
    commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    public=[]
    for relative in ['Diva_lead_v68_WIP_checkpoint.zip','diva-lead/v68-wip/FL_STUDIO_RU.md','diva-lead/v68-wip/Diva_Lead_Finish_v68_WIP_x64.dll','diva-lead/v68-wip/AB_REFERENCE_V67_V68_WIP.mp3','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative,timeout=60) as response:
            content=response.read();assert response.status==200
        assert content==(REPO/relative).read_bytes();public.append(dict(path=relative,SHA256=hashlib.sha256(content).hexdigest(),byte_exact=True))
    assert not git('status','--porcelain');assert json.loads(PAUSE.read_text())['owner']=='publish-full-v68';PAUSE.unlink()
    write(R/'public-v68-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_main_exact=True,HTTP_files=public,older_57_to_67_trees_and_ZIPs_immutable=True,tone_score=proof['tone_score'],source_family=family,match_reached=False))
    print('FULL_V68_PUSHED_AND_REAL_HTTP_BYTES_VERIFIED',commit,proof['tone_score'],family,flush=True)
