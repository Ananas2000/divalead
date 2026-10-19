"""Preserve the completed v67 runtime work without changing any audio release."""
from pathlib import Path
import datetime,fcntl,hashlib,json,shutil,subprocess,time,urllib.request

R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead')
D=REPO/'diva-lead/research/three-held-continuation/after-v67-runtime'
PAUSE=R/'auto-backup.pause';OWNER='publish-v67-runtime-support'
def git(*args):
    return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=REPO,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

assert not PAUSE.exists()
write(PAUSE,dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(60):
    state=json.loads((R/'auto-backup-state.json').read_text())
    if state['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(state)
with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    assert not git('status','--porcelain')
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    old={p:git('rev-parse','HEAD:'+p) for version in range(57,68) for p in [f'diva-lead/v{version}-wip',f'Diva_lead_v{version}_WIP_checkpoint.zip']}
    D.mkdir(exist_ok=False);(D/'scripts').mkdir()
    scripts=['continue_pw5190_main.py','continue_pw5190_phase.py','continue_pw5190_balance.py','auto_backup_three.py',
        'start_three_services.py','validate_three_source_model.py','three_candidate_decision.py','fit_three_hf_fixed_anchor.py',
        'fit_three_gains.py','fit_three_phase18.py','fit_three_fine55.py','fit_three_balance42.py','fit_three_power69.py',
        'three_hf_interior_projection.py','three_gain_interior_projection.py','three_fine55_interior_projection.py',
        'project_three_existing_vector.py','repair_pw_phase_margin.py','handoff_publisher_idle.py',
        'deduplicate_immutable_audio.py','deduplicate_completed_three_sources.py','publish_v67_runtime_support.py']
    for name in scripts:
        assert (R/name).is_file(),name
        shutil.copyfile(R/name,D/'scripts'/name)
        assert sha(R/name)==sha(D/'scripts'/name) and not (R/name).samefile(D/'scripts'/name)
    records=['active-three-source-family.json','service-start-last.json','source-cohort-handoff.json',
        'source-history-isolation-complete.json','operational-reserve-sizing-v66.json','fine55-safe-selection-integration.json',
        'current-checkout-discovery-v67.json','config-v67-save-readback.json','public-v67-verification.json',
        'v67-final-resource-state.json','v67-final-audio-dedup.json','v67-final-source-dedup.json',
        'v67-package-cache-cleanup.json','canonical-exact-copy-audit.json','start_skill_v67.md','AUTONOMOUS_ACTIVE_CURRENT.md']
    for name in records:shutil.copyfile(R/name,D/name)
    shutil.copyfile(R/'pw66-fitter-readiness/verification.json',D/'fitter-readiness-at-v66.json')
    for role in ['main','phase','balance']:
        shutil.copyfile(R/('pw5190-'+role+'-state.json'),D/('pw5190-'+role+'-state.json'))
        source=R/('pw5190-live-'+role)/'attempted-before-source-isolation.json'
        shutil.copyfile(source,D/(role+'-original-attempt-history.json'))
    (D/'README.md').write_text('''# Трёхнотный v67: программы и состояние среды

[Полный комплект v67](../../../v67-wip/README.md), [FL Studio](../../../v67-wip/FL_STUDIO_RU.md), [оригинал → v67 WAV](../../../v67-wip/AB_REFERENCE_V67_WIP.wav) — наш вариант с 4,168 с. [Оригинал → v66 → v67 MP3](../../../v67-wip/AB_REFERENCE_V66_V67_WIP.mp3) — v67 с 8,336 с.

Продолжается только выбранная пользователем схема из трёх длинных нот на фразу. Лучший полностью проверенный кандидат: pw5190-verified-fine55-interior-0030, ошибка тембра 0,8145992685, общая ошибка 0,9082733689. Это ошибки измерений, не проценты сходства; совпадение ещё не достигнуто. Пресет, все 281 параметр Diva и сырой источник прежние относительно полного v66. Все рендеры и отвергнутые попытки сохранены; полный v67 не изменён этой публикацией.

После публикации дополнительно объединены только точные копии: все пути и SHA сохранены, освобождено около 114 МиБ. На постоянном диске осталось около 185 МиБ; все три контроллера сейчас ожидают место. Численные раунды не выполняются. Прежний резерв 256 МиБ для работы и 128 МиБ для публикации не уменьшен; отдельный временный /tmp не заменяет постоянное место для доказательств, Git и снимка среды. Удаление восстанавливаемого кэша пакетов не освободило фактическое место overlay; уникальная история и исходники сохранены. Это реальный предел текущей среды, а не завершённое совпадение.

scripts — независимые копии действующих программ. Сохранены исправление выбора безопасной фазы, фактическая интеграционная проверка callback, разделение истории по источникам, проверенный идемпотентный запуск и отчёты состояния. fitter-readiness-at-v66.json относится к модели полного v66: шесть маршрутов проверены нулевым и двумя ненулевыми полными независимыми проходами; это не новый результат оптимизации. service-start-last.json проверяет текущую лучшую основу и отсутствие дубликатов процессов. Численный бюджет 2+1+1.

Конфигурация Cloud Environment Onboarding сохранена и чтением обратно подтверждена, revision79: инструкции полного v67 и точный публичный HEAD f1979a9ac8241e8a91c89667b52e107692fc9e0b. Установка, сеть, секреты и runtime requirements не менялись. Для применения снимка требуются Save и Publish в настройках среды; текущая среда не перезапускалась. Восстановление в новой задаче отдельно не проверено. Код содержит пути подготовленной среды и не является самостоятельной установкой. Лицензионный файл Diva не включён. GUI FL Studio и прослушивание ассистентом не выполнялись.
''')
    (D/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(D))+'\n' for p in sorted(D.rglob('*')) if p.is_file()))
    target=str(D.relative_to(REPO));git('add','--',target)
    assert all(n.startswith(target+'/') for n in git('diff','--cached','--name-only').splitlines())
    git('diff','--cached','--check');git('commit','-m','Preserve v67 source-specific runtime, setup and actual storage-limit evidence')
    for p,oid in old.items():assert git('rev-parse','HEAD:'+p)==oid
    commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    checked=[]
    for p in [D/'README.md',D/'config-v67-save-readback.json',D/'v67-final-resource-state.json',D/'scripts/start_three_services.py']:
        relative=str(p.relative_to(REPO))
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative,timeout=60) as response:
            data=response.read();assert response.status==200
        assert data==p.read_bytes();checked.append(dict(path=relative,SHA256=sha(p),byte_exact=True))
    assert not git('status','--porcelain')
    write(R/'public-v67-runtime-support.json',dict(commit=commit,remote_main_exact=True,HTTP_files=checked,
        full57_to67_trees_and_ZIPs_immutable=True,copied_scripts_independent_inodes=True,match_reached=False))
    assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink()
    print('V67_RUNTIME_AND_SETUP_PUBLIC_VERIFIED',commit,flush=True)
