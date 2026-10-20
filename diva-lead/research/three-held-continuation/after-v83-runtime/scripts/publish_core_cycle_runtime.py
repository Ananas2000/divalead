"""Publish the tested continuous core cycle and save a stable configuration context."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,signal,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');O=P/'diva-lead/research/three-held-continuation/after-v83-runtime';PY='/workspace/.venvs/divalead/bin/python'
OWNER='publish-continuous-core-cycle';PAUSE=R/'auto-backup.pause';env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0',*a],cwd=P,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def proc(pid):
    try:
        p=Path('/proc',str(pid));s=(p/'stat').read_text().rsplit(')',1)[1].split();return dict(state=s[0],start=s[19],cmd=(p/'cmdline').read_bytes().split(b'\0'))
    except FileNotFoundError:return None
def state(phase,**kw):write(R/'core-cycle-publication-state.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,match_reached=False,**kw))
while not (R/'public-v83-verification.json').is_file():
    pending=json.loads((R/'v83-preparation-controller-state.json').read_text());assert not pending['phase'].startswith('failed'),pending
    state('waiting_for_full83_publication');time.sleep(3)
assert json.loads((R/'post82-core-cycle-reload-state.json').read_text())['phase']=='main_reloaded_with_core147_HF100_gain93_cycle'
if shutil.disk_usage(R).free<352*1048576:
    subprocess.run([PY,'-B',str(R/'prune_post83_obsolete_caches.py')],env=env,check=True)
scripts=['publish_core_cycle_runtime.py','continue_post80plate68_main.py','continue_post80plate68_main_before_core_cycle.py','fit_three_core147_fixed_anchor.py','fit_three_core147_before_cycle.py','restart_main_with_core_cycle.py','auto_backup_three.py','start_three_services.py','refresh_post74_startup_guide.py','summarize_current_three_variants.py','verify_post81_runtime_readiness.py','discover_workspace_projects.py','prune_post83_obsolete_caches.py']
diags=['post82-core-cycle-reload-state.json','post82-core-cycle-exact-sharing.json','public-v83-verification.json','v83-FL-instruction-file-checks.json','post82-storage-followup-public-verification.json']
if (R/'post83-obsolete-cache-cleanup.json').is_file():diags+=['post83-obsolete-cache-cleanup.json','post83-obsolete-cache-cleanup-plan.json']
for name in scripts+diags:assert (R/name).is_file(),name
while True:
    try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:time.sleep(2);continue
    with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
    break
try:
    for _ in range(120):
        pub=json.loads((R/'auto-backup-state.json').read_text())
        if pub['phase']=='paused_for_manual_Git_work':break
        time.sleep(1)
    else:raise RuntimeError(pub)
    with (R/'auto-backup-Git.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        old=pub['publisher_PID'];d=proc(old);assert d and str(R/'auto_backup_three.py').encode() in d['cmd']
        os.kill(old,signal.SIGTERM)
        for _ in range(100):
            q=proc(old)
            if not q or q['state']=='Z':break
            assert q['start']==d['start'];time.sleep(.1)
        else:raise RuntimeError('Previous publisher remains live')
        subprocess.run([PY,'-B',str(R/'start_three_services.py')],env=env,check=True)
        started=json.loads((R/'service-start-last.json').read_text());assert sum(x['newly_started'] for x in started['services'])==1
        new=next(x for x in started['services'] if x['script']=='auto_backup_three.py');assert new['newly_started']
        write(R/'core-cycle-publisher-restart.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_PID=old,new_PID=new['PID'],owned_idle_Git_pause=True,no_duplicate_numeric_parents=True,all_original_guards_and_triggers_unchanged=True))
        script=R/'auto_backup_three.py';ns={'__file__':str(script),'__name__':'core_cycle_checks'}
        exec(compile(script.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(script),'exec'),ns)
        target=R/'post80plate68-verified-live-main-0002-core147/validation.json';assert ns['numeric_run'](target)==R/'post80plate68-live-main/round-0002-core147'
        ns['mirror_temporary_vectors']()
        cache=Path('/tmp/divalead-post80plate68-live-main/round-0002-core147/complete-core-basis/cache_checks.json');checks=json.loads(cache.read_text())
        assert checks['zero_actual_error']<2e-7 and len(checks['two_nonzero_full_SciPy_errors'])==2 and max(checks['two_nonzero_full_SciPy_errors'])<2e-10
        write(R/'core-cycle-functional-checks.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_core_round_private_numeric_mirror_registered=True,completed_core_round_export_route_checked=True,actual_current_core_zero_and_two_nonzero_predictor_checks=checks,original_guards_and_source_notes_unchanged=True,current_core_optimizer_not_claimed_finished=True,match_reached=False))
        for file in ['verify_post81_runtime_readiness.py','summarize_current_three_variants.py','refresh_post74_startup_guide.py']:
            subprocess.run([PY,'-B',str(R/file)],env=env,check=True)
        diags+=['core-cycle-publisher-restart.json','core-cycle-functional-checks.json','post81-runtime-readiness.json','current-three-note-variant-registry.json']
        parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
        protected={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
        protected.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
        assert not O.exists();O.mkdir()
        for name in scripts:
            destination=O/'scripts'/name;destination.parent.mkdir(exist_ok=True);shutil.copyfile(R/name,destination);assert sha(R/name)==sha(destination) and not (R/name).samefile(destination)
        for name in diags:
            destination=O/'diagnostics'/name;destination.parent.mkdir(exist_ok=True);shutil.copyfile(R/name,destination);assert sha(R/name)==sha(destination)
        shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md')
        (O/'README_RU.md').write_text('''# Непрерывный подбор после v83

[Полный v83](../../../v83-wip/README.md), [FL Studio](../../../v83-wip/FL_STUDIO_RU.md), [оригинал → v83](../../../v83-wip/AB_REFERENCE_V83_WIP.wav): наш с 4,168 с. Точное совпадение ещё не достигнуто.

Основной цикл теперь уточняет по очереди существующие 147 коэффициентов середины, 100 верхних и 93 гармонических коэффициента. Он остаётся в двух вычислительных потоках; фаза и стерео используют по одному. Три удерживаемые ноты, внутренний ARP, источник Diva, число состояний DSP, задержка и все исходные ограничения сохранены. Численный шаг уменьшен, а найденные недопустимые направления можно корректировать внутрь прежних пределов; сами такие направления не считаются принятыми.

Предыдущий основной расчёт и его свежая проверка завершились до замены только его родительского процесса. Все результаты и фактическая квитанция проверки сохранены; незавершённая служебная запись контроллера не выдаётся за выполненную. Проверены текущая точность прогноза нового прохода на нулевом и двух ненулевых изменениях, регистрация его численных бэкапов и два повторных запуска всех служб без дубликатов. Сам новый оптимизатор ещё может работать: его завершение и улучшение звука не объявляются по одному запуску.

Принять следующий вариант можно только после новой настоящей Diva, Windows/native, соответствующей независимой NEW-базы, отдельного fixture и всех 12 причинных случаев четырёх частот. Завершённые варианты автоматически сохраняются на GitHub. Все номерные комплекты и ZIP сохранены. GUI FL Studio, прослушивание ассистентом и восстановление среды в новой задаче не тестировались.
''')
        target=str(O.relative_to(P));git('add','--',target);assert all(p.startswith(target+'/') for p in git('diff','--cached','--name-only').splitlines());git('diff','--cached','--check');git('commit','-m','Continue three-held Diva matching with guarded core147 HF100 gain93 cycle after v83')
        assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items())
        commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
        for name in ['README_RU.md','start_skill_current.md','scripts/continue_post80plate68_main.py','scripts/auto_backup_three.py']:
            data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes()
        assert not git('status','--porcelain');write(R/'core-cycle-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_and_HTTP_byte_exact=True,all_numbered_releases_and_ZIPs_unchanged=True,main_cycle_and_publisher_reloaded=True,match_reached=False))
        subprocess.run([PY,'-B',str(R/'discover_workspace_projects.py'),'core-cycle-checkout-discovery.json'],env=env,check=True)
        write(R/'core-cycle-ready-for-config.json',dict(commit=commit,owner=OWNER,lock_held=True));state('pushed_ready_for_configuration_save',commit=commit);print('CORE_CYCLE_PUSHED_READY_FOR_CONFIG',commit,flush=True)
        end=time.monotonic()+240
        while time.monotonic()<end and not (R/'core-cycle-config-readback-complete.json').is_file():time.sleep(2)
        state('published_configuration_window_closed',commit=commit)
finally:
    if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==OWNER:PAUSE.unlink()
    print('CORE_CYCLE_OWN_PAUSE_AND_GIT_LOCK_RELEASED',flush=True)
