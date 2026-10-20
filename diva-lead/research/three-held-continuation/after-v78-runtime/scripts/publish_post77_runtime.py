"""Preserve completed post77 screens, current startup and clearly labelled pending work."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,signal,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead')
O=P/'diva-lead/research/three-held-continuation/after-v78-runtime'
PAUSE=R/'auto-backup.pause';OWNER='publish-post77-runtime'
def write(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=P,text=True).strip()
def proc(pid):
    p=Path('/proc',str(pid))
    try:
        stat=(p/'stat').read_text().rsplit(')',1)[1].split()
        return dict(state=stat[0],start=stat[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
    except (FileNotFoundError,ProcessLookupError):return None
scripts=['publish_post77_runtime.py','probe_source_post77.py','run_source_post77_probe.py','archive_post77_physical_screens.py','fit_post77_coupled135.py','run_post77_coupled135.py','run_post77_cleaner_hf100.py','prove_post77_cleaner_alternative.py','fit_three_hf_cleaner100.py','fit_three_gains.py','three_hf_interior_projection.py','three_gain_interior_projection.py','project_three_existing_vector.py','three_candidate_decision.py','diagnose_post77_residual.py','auto_backup_three.py','start_three_services.py','refresh_post74_startup_guide.py','summarize_current_three_variants.py','discover_workspace_projects.py','deduplicate_completed_three_sources.py','deduplicate_immutable_audio.py','share_fixed_fir_kernel_headers.py','verify_full_kit_documentation.py']
for version in ['v77','v78']:
    scripts.extend(['build_three_'+version+'.py','write_'+version+'_docs.py','finalize_'+version+'.py','verify_zip_windows_'+version+'.py','run_full_'+version+'_build.py','publish_full_'+version+'.py','prepare_next_full_'+version+'.py'])
diags=['public-v77-verification.json','public-v78-verification.json','v77-FL-instruction-file-checks.json','v78-FL-instruction-file-checks.json','v77-publisher-input-checks.json','v78-publisher-input-checks.json','post76-fixed-fir-kernel-sharing.json','post76-completed-source-sharing.json','post76-storage-sharing-summary.json','post77-obsolete-cache-cleanup-plan.json','post77-obsolete-cache-cleanup.json','post77-local-coupling-predictions.json','post77-residual-band-diagnostic.json','post77-numeric-backup-registration.json','current-three-note-variant-registry.json','source-post77-state.json','source-post77coupled-state.json','post77-cleaner-hf100-state.json','post77-cleaner-alternative-state.json','active-three-source-family.json','v78-preparation-controller-state.json']
for name in scripts+diags:assert (R/name).is_file(),name
full=json.loads((P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
assert full['version']=='v78-wip'
archives=Path('/tmp/divalead-post77-physical-archives');manifest=json.loads((archives/'manifest.json').read_text())
assert manifest['original_Diva_three_held_screening_trials']==28
for row in manifest['archives']:assert sha(archives/row['file'])==row['SHA256']
assert not O.exists()
while True:
    try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:time.sleep(2);continue
    with os.fdopen(fd,'w') as out:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),out)
    break
try:
    for _ in range(90):
        state=json.loads((R/'auto-backup-state.json').read_text())
        if state['phase']=='paused_for_manual_Git_work':break
        time.sleep(1)
    else:raise RuntimeError(state)
    with (R/'auto-backup-Git.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert not git('status','--porcelain')
        before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
        immutable={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
        immutable.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
        # Load the newly registered numeric mirrors/export routes only at publisher idle.
        old_pid=state['publisher_PID'];old=proc(old_pid)
        assert old and str(R/'auto_backup_three.py').encode() in old['cmd']
        os.kill(old_pid,signal.SIGTERM)
        for _ in range(100):
            current=proc(old_pid)
            if current is None or current['state']=='Z':break
            time.sleep(.05)
        else:raise RuntimeError('Idle publisher did not exit')
        with (R/'auto-backup-controller.log').open('a') as log:
            child=subprocess.Popen(['/workspace/.venvs/divalead/bin/python','-B',str(R/'auto_backup_three.py')],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DIVALEAD_MIN_FREE_MIB='128'))
        for _ in range(60):
            state=json.loads((R/'auto-backup-state.json').read_text())
            if state['publisher_PID']==child.pid and state['phase']=='paused_for_manual_Git_work':break
            assert child.poll() is None
            time.sleep(.5)
        else:raise RuntimeError('New publisher did not acknowledge owned pause')
        write(R/'post77-publisher-restart.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_PID=old_pid,new_PID=child.pid,idle_owned_pause_and_Git_lock=True,numeric_audio_controllers_untouched=True,new3_numeric_export_routes_and2_private_mirror_roots=True,source_hashes_quality_caps_and_publication_triggers_unchanged=True,match_reached=False))
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(R/'start_three_services.py')],env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),check=True)
        O.mkdir();(O/'scripts').mkdir();(O/'diagnostics').mkdir()
        for name in scripts:
            shutil.copyfile(R/name,O/'scripts'/name)
            assert not (R/name).samefile(O/'scripts'/name)
        for name in diags+['post77-publisher-restart.json','service-start-last.json']:
            shutil.copyfile(R/name,O/'diagnostics'/name)
        shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md')
        for p in archives.iterdir():
            if p.is_file():
                dest=O/'physical-screen-archives'/p.name;dest.parent.mkdir(exist_ok=True)
                shutil.copyfile(p,dest);assert sha(p)==sha(dest)
        # A finite fit may still be running: freeze only valid JSON, labelled as
        # unaccepted numerical checkpoints; never add validation markers for it.
        pending=[]
        for folder in ['post77-coupled135-research','post77-cleaner-hf100-research']:
            source=R/folder
            if not source.exists():continue
            for path in source.rglob('*.json'):
                try:data=path.read_bytes();json.loads(data)
                except (FileNotFoundError,json.JSONDecodeError):continue
                target=O/'UNVALIDATED_numeric_checkpoints'/folder/path.relative_to(source)
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
                pending.append(dict(path=str(target.relative_to(O)),SHA256=hashlib.sha256(data).hexdigest(),not_a_new_full_proof=True))
        write(O/'UNVALIDATED_numeric_checkpoints/manifest.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_entries_are_frozen_numerical_records_not_accepted_audio=True,entries=pending,match_reached=False))
        (O/'README_RU.md').write_text('''# Продолжение после полного v78: три удерживаемые ноты

[Комплект v78](../../../v78-wip/README.md), [FL Studio](../../../v78-wip/FL_STUDIO_RU.md), [оригинал → v78](../../../v78-wip/AB_REFERENCE_V78_WIP.wav), наш вариант с 4,168 с. Совпадение ещё не достигнуто.

Сохранены все 28 дополнительных настоящих рендеров Diva с изменениями осциллятора и фильтра: исходный и обработанный WAV, пресет, все 281 параметр, MIDI-логи, измерения. Четыре архива проверены по SHA256 каждого распакованного файла. Ни один изменённый источник этой серии не улучшил тембр с соблюдением всех прежних ограничений; меньшая численная ошибка сама по себе не считалась успехом. Источник остаётся прежним четырёхпараметрическим; три удержания, внутренний ARP и огибающие сохранены.

Полные v77 и v78 прошли свежую Diva, Windows/native, собственную независимую NEW-базу и отдельный fixture, все 12 причинных случаев, проверки VST/FXP/состояния/PDC/блоков, точную пересборку и фактическую DLL из чистого ZIP. Документация проверена по именам файлов; HTTP-байты ZIP/DLL/инструкции/сравнения сверены после push. GUI FL Studio и субъективное прослушивание ассистентом не выполнялись.

Совместный подбор 93 гармонических и 42 стереокоэффициентов и отдельная попытка уменьшить шумовой остаток используют существующие параметры обработки. Последняя вводит дополнительное более строгое ограничение upper-off. Они временно занимают только соответствующий CPU-слот и возвращают исходные процессы. Состояния в diagnostics — снимки; актуальные JSON и процессы среды имеют приоритет. UNVALIDATED_numeric_checkpoints содержит только явно непринятые численные записи, а не готовый звук. Завершившиеся новые проверки и численные журналы публикуются отдельным контроллером; исходные ограничения не ослаблены.

Точные дубликаты освобождали место без изменения содержимого. Дополнительно удалены только тяжёлые генерируемые файлы 61 худшего старого шестнадцатинотного кэша; их модели, исходники и оценки сохранены. Все номерные комплекты, оригиналы, текущие трёхнотные доказательства и альтернативы сохранены; история Git не переписывалась. Фактические объёмы — в diagnostics, логические размеры не выдаются за освобождённое место.

Лицензионная Diva не включена; MistaTowa не используется. Сохранённые инструкции облачной среды не означают публикацию снимка или проверенное восстановление в новой задаче. Подбор после этого бэкапа продолжается.
''')
        target=str(O.relative_to(P));git('add','--',target)
        assert all(p.startswith(target+'/') for p in git('diff','--cached','--name-only').splitlines())
        git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
        git('commit','-m','Preserve 28 real Diva source trials, v78 runtime and continued three-note searches')
        assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in immutable.items())
        head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
        git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
        checked=[]
        for name in ['README_RU.md','start_skill_current.md','scripts/auto_backup_three.py','physical-screen-archives/'+manifest['archives'][0]['file']]:
            with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/'+name,timeout=60) as response:data=response.read()
            assert data==(O/name).read_bytes();checked.append(dict(path=name,SHA256=sha(O/name),byte_exact=True))
        assert not git('status','--porcelain')
        write(R/'post77-runtime-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_exact=True,HTTP_files=checked,all_numbered_releases_unchanged=True,all28_screens_archived=True,unfinished_vectors_not_accepted_as_audio=True,match_reached=False))
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(R/'discover_workspace_projects.py'),'post77-checkout-discovery.json'],check=True)
        write(R/'post77-runtime-ready-for-config.json',dict(commit=head,lock_held=True,owner=OWNER))
        print('POST77_RUNTIME_PUSHED_READY_FOR_CONFIG',head,flush=True)
        deadline=time.monotonic()+180
        while time.monotonic()<deadline and not (R/'post77-runtime-config-readback-complete.json').exists():time.sleep(2)
finally:
    if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==OWNER:PAUSE.unlink()
    print('POST77_RUNTIME_OWN_PAUSE_AND_GIT_LOCK_RELEASED',flush=True)
