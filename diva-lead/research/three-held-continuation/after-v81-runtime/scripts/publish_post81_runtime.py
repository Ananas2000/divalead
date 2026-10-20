"""Publish completed Plate/core work and preserve the exact configuration-save context."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');O=P/'diva-lead/research/three-held-continuation/after-v81-runtime'
OWNER='publish-completed-post81-runtime';PAUSE=R/'auto-backup.pause';PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=P,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy(a,b):
    b=Path(b);b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);assert sha(a)==sha(b)
def state(phase,**kw):write(R/'post81-runtime-publication-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,**kw))
while True:
    core=json.loads((R/'post81-core147-idle-main-state.json').read_text())
    handoff=json.loads((R/'post80-source-handoff-state.json').read_text())
    if core['phase'].startswith('failed') or handoff['phase'].startswith('failed'):raise RuntimeError(dict(core=core,handoff=handoff))
    if core.get('idle_main_slot_released') and core['phase']=='finite_core147_finished_resume_owned_handoff' and handoff['phase'] in ['new_selected_source_cohort_started_budget2_1_1','previous_source_remains_best_resume_current_cohort']:break
    state('waiting_for_closed_core_and_completed_source_handoff',core_phase=core['phase'],handoff_phase=handoff['phase']);time.sleep(5)
for script in ['verify_post81_runtime_readiness.py','summarize_current_three_variants.py','refresh_post74_startup_guide.py']:
    subprocess.run([PY,'-B',str(R/script)],env=env,check=True)
scripts=['publish_post81_runtime.py','verify_post81_runtime_readiness.py','refresh_post74_startup_guide.py','summarize_current_three_variants.py','discover_workspace_projects.py','auto_backup_three.py','start_three_services.py','probe_source_post80_plate.py','run_source_post80_plate.py','probe_source_post80_plate2.py','run_source_post80_plate2.py','verify_post80_plate_screens.py','verify_post80_plate2_screens.py','archive_post80_plate_screens.py','prepare_post80_plate_source.py','run_source_post80plateproof.py','fit_post80_plate_finish.py','run_source_post80platefit.py','handoff_to_post80_plate_source.py','prove_post80_source_transplant.py','continue_post80plate68_main.py','continue_post80plate68_phase.py','continue_post80plate68_balance.py','fit_three_core147_fixed_anchor.py','fit_post81_core147.py','run_post81_core147.py','run_post81_core147_idle_main.py','validate_three_source_model.py','validate_three_source_model_before_core147.py','project_three_existing_vector.py','prune_post79_obsolete_caches.py','prune_post80_obsolete_caches.py','share_fixed_fir_kernel_headers.py','deduplicate_completed_three_sources.py','deduplicate_immutable_audio.py','diagnose_post81_residual.py']
scripts.extend(['fit_post81_core147_projection.py','run_post81_core_projection.py','build_three_v82.py','write_v82_docs.py','finalize_v82.py','verify_zip_windows_v82.py','run_full_v82_build.py','publish_full_v82.py','prepare_next_full_v82.py'])
diags=['post79-exact-sharing-summary.json','post79-fixed-fir-kernel-sharing.json','post79-completed-three-source-dedup-last.json','post79-obsolete-cache-cleanup.json','post79-obsolete-cache-cleanup-plan.json','post80-obsolete-cache-cleanup.json','post80-obsolete-cache-cleanup-plan.json','post80-plate-parameter-checks.json','post80-plate2-parameter-checks.json','post80-new-source-publisher-checks.json','post80-publisher-restart.json','source-post80-plate-state.json','source-post80-plate2-state.json','source-post80plateproof-state.json','source-post80platefit-state.json','post80-source-handoff-state.json','post81-core-validator-before.json','post81-core-validator-regression.json','post81-core-waiter-retired.json','post81-core147-idle-main-preflight-rejection.json','post81-core147-idle-main-state.json','post81-runtime-readiness.json','post81-residual-band-diagnostic.json','current-three-note-variant-registry.json','public-v80-verification.json','public-v81-verification.json','v80-FL-instruction-file-checks.json','v81-FL-instruction-file-checks.json','active-three-source-family.json']
for name in scripts+diags:assert (R/name).is_file(),name
archives=Path('/tmp/divalead-post80-plate-physical-archives');manifest=json.loads((archives/'manifest.json').read_text())
assert manifest['original_Diva_three_held_screening_trials']==46
for row in manifest['archives']:assert sha(archives/row['file'])==row['SHA256']
assert not O.exists()
while True:
    try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:time.sleep(2);continue
    with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
    break
try:
    for _ in range(120):
        status=json.loads((R/'auto-backup-state.json').read_text())
        if status['phase']=='paused_for_manual_Git_work':break
        time.sleep(1)
    else:raise RuntimeError(status)
    with (R/'auto-backup-Git.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
        protected={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
        protected.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
        for name in scripts:copy(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
        for name in diags:copy(R/name,O/'diagnostics'/name)
        copy(R/'start_skill_current.md',O/'start_skill_current.md')
        for p in archives.iterdir():
            if p.is_file():copy(p,O/'physical-plate-screen-archives'/p.name)
        script=R/'auto_backup_three.py';ns={'__file__':str(script),'__name__':'closed_post81_snapshot'}
        exec(compile(script.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(script),'exec'),ns)
        for name in ['source-post80plate68-HF100','post81-core147-research','post80-source-transplant']:
            source=R/name;ns['snapshot'](source,O/'completed-research'/name)
            if (source/'numeric-location.json').is_file():
                scratch=Path(json.loads((source/'numeric-location.json').read_text())['numeric_scratch'])
                ns['snapshot'](scratch,O/'completed-research'/name/'numeric')
        copy(R/'post81-core147-idle-main-fit.log',O/'completed-research/core147.log')
        copy(R/'core147-validator-regression.log',O/'diagnostics/core147-validator-regression.log')
        refs=[dict(private_validation=str(p),tone_score=d['tone_score'],score=d['score'],source_family=family,upper_off_error=d['metrics']['upper_off']) for p,d,family,basis in ns['choices']() if family=='Post80 Plate2 damping68']
        write(O/'completed-proof-references.json',refs)
        (O/'README_RU.md').write_text('''# Продолжение трёхнотного лида после v81

[Полный v81](../../../v81-wip/README.md), [FL Studio](../../../v81-wip/FL_STUDIO_RU.md), [оригинал → v81](../../../v81-wip/AB_REFERENCE_V81_WIP.wav): наш с 4,168 с. Точное совпадение ещё не достигнуто. Более поздний полный комплект определяется CURRENT_FL_STUDIO_RELEASE.json.

Сохранены все 46 свежих настоящих рендеров Diva: исходные и обработанные WAV, пресеты, 281-параметрические дампы, MIDI-логи и оценки. Архивы проверены по SHA каждого распакованного файла. Три удерживаемые ноты, внутренний ARP и огибающие сохранены. Пробы с лучшей одной оценкой, нарушившие прежние пределы спектра/стерео, не приняты.

Выбранный источник v81 отличается от v80 только Plate2 Damp 72 → 68. Он прошёл свежую Diva, Windows/native, заново построенную собственную NEW-базу, отдельный fixture и 12 причинных случаев четырёх частот. Завершены дополнительный поиск 100 существующих верхних коэффициентов и поиск 147 существующих коэффициентов середины; решения и численные журналы сохранены отдельно. Завершённый расчёт сам по себе не означает принятого звука: нужны свежий рендер и все исходные ограничения. Доказательства перечислены в completed-proof-references.json; не прошедшие кандидаты явно отмечены в decision.json.

Перед переходом источника предыдущим численным попыткам и их проверкам дали завершиться. Переход выполняется только после сравнения всех подтверждённых результатов; текущие родительские процессы и автоматические бэкапы продолжают подбор. Старые состояния в этом каталоге — снимок; актуальные JSON среды и CURRENT имеют приоритет. Новые состояния DSP, MIDI-события и задержка не добавлены; записанный оригинал в эффект не встроен.

Выборочная очистка затронула только тяжёлые генерируемые файлы 152 дополнительных устаревших шестнадцатинотных кэшей. Их модели, исходники и оценки сохранены. Все номерные версии, ZIP, текущие трёхнотные доказательства и более тихие альтернативы сохранены. GUI FL Studio, субъективное прослушивание ассистентом и восстановление среды в новой задаче не выполнялись. Лицензионная Diva не включена; MistaTowa не используется.
''')
        target=str(O.relative_to(P));git('add','--',target)
        assert all(p.startswith(target+'/') for p in git('diff','--cached','--name-only').splitlines())
        git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
        git('commit','-m','Preserve completed three-held Diva Plate2, guarded core147 and source-handoff work')
        assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items())
        commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
        git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
        checked=[]
        names=['README_RU.md','start_skill_current.md','scripts/start_three_services.py']+['physical-plate-screen-archives/'+row['file'] for row in manifest['archives']]
        for name in names:
            data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes();checked.append(name)
        assert not git('status','--porcelain')
        write(R/'post81-runtime-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_and_HTTP_byte_exact=True,HTTP_paths=checked,all_older_numbered_releases_unchanged=True,all46_Diva_cases_losslessly_archived=True,core_and_finite_HF_closed=True,match_reached=False))
        subprocess.run([PY,'-B',str(R/'discover_workspace_projects.py'),'post81-runtime-checkout-discovery.json'],env=env,check=True)
        write(R/'post81-runtime-ready-for-config.json',dict(commit=commit,owner=OWNER,lock_held=True))
        state('pushed_and_ready_for_configuration_save',commit=commit);print('POST81_RUNTIME_PUSHED_READY_FOR_CONFIG',commit,flush=True)
        end=time.monotonic()+240
        while time.monotonic()<end and not (R/'post81-runtime-config-readback-complete.json').is_file():time.sleep(2)
        state('published_configuration_save_window_closed',commit=commit)
finally:
    if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==OWNER:PAUSE.unlink()
    print('POST81_RUNTIME_OWN_PAUSE_AND_GIT_LOCK_RELEASED',flush=True)
