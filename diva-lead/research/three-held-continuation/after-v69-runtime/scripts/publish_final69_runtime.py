"""Preserve final startup/state evidence without modifying any complete audio kit."""
from pathlib import Path
import datetime,fcntl,hashlib,json,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;REPO=Path('/workspace/divalead')
D=REPO/'diva-lead/research/three-held-continuation/after-v69-runtime'
PAUSE=R/'auto-backup.pause';OWNER='publish-final69-runtime'
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=REPO,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
assert not PAUSE.exists();write(PAUSE,dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(90):
    s=json.loads((R/'auto-backup-state.json').read_text())
    if s['phase']=='paused_for_manual_Git_work':break
    time.sleep(1)
else:raise RuntimeError(s)
with (R/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    old={p:git('rev-parse','HEAD:'+p) for i in range(57,70) for p in [f'diva-lead/v{i}-wip',f'Diva_lead_v{i}_WIP_checkpoint.zip']}
    D.mkdir(exist_ok=False);(D/'scripts').mkdir()
    records=['start_skill_current.md','AUTONOMOUS_ACTIVE_CURRENT.md','FINAL69_RESOURCE_STATE.json','post67-rounds-final-summary.json',
        'service-start-last.json','final69-service-readiness.log','public-v68-verification.json','public-v69-verification.json',
        'post69-audio-sharing.json','post69-source-sharing.json','post69-fixed-table-sharing.json','streamed-loose-packs-result.json',
        'pack-initial-attempt-recovery.json','post67-rejected-archive-result.json','active-three-source-family.json']
    for name in records:shutil.copyfile(R/name,D/name)
    scripts=['start_three_services.py','continue_pw5190_main.py','continue_pw5190_phase.py','continue_pw5190_balance.py',
        'auto_backup_three.py','validate_three_source_model.py','three_candidate_decision.py','three_fine55_interior_projection.py',
        'project_three_existing_vector.py','deduplicate_retired_basis_audio.py','share_fixed_fir_kernel_headers.py',
        'archive_post67_rejected_attempts.py','publish_final69_runtime.py']
    for name in scripts:
        shutil.copyfile(R/name,D/'scripts'/name);assert not (R/name).samefile(D/'scripts'/name)
    (D/'README.md').write_text('''# v69 WIP: окончание текущего прохода по пределу диска

[Полный комплект v69](../../../v69-wip/README.md), [инструкция FL Studio](../../../v69-wip/FL_STUDIO_RU.md), [оригинал → v69 WAV](../../../v69-wip/AB_REFERENCE_V69_WIP.wav): наш вариант с 4,168 с.

Продолжение использует только три удерживаемые ноты на фразу, внутренний ARP Diva, два прохода и шесть note-on. После v67 выполнены10 новых попыток:9 кандидатов прошли свежую Diva/Windows/native/собственную NEW-базу/fixture/все12 причинных случаев;1 отклонён по исходным ограничениям и сохранён без ложного заявления о завершённой проверке. Более слабые результаты также сохранены. Выбран лучший по прежней взвешенной метрике тембра: 0,8134342326, общая ошибка0,9068992457. Это ошибки измерений, не проценты сходства. Полного совпадения ещё нет; GUI FL Studio и прослушивание ассистентом не выполнялись.

Полный v68 опубликован, после него подбор продолжался. Полный v69 включает дальнейшие усиления гармоник и верхнюю матрицу Finish; сам пресет Diva, все281 параметр, источник, MIDI, длительности, ARP и огибающие сохранены относительно v68. Относительно исходного выбранного трёхнотного пресета остаётся одно прежнее изменение PW51,87→51,90. Комплект прошёл также API/FXP/состояние/PDC/блоки, точную пересборку и фактический полный WAV DLL из чистого ZIP. Все старые полные комплекты57–68 и их ZIP неизменны; v69 этим коммитом не меняется. Регрессии отдельных метрик показаны в COMPARISON_RU.md.

Все запущенные проходы завершены. После дальнейшего объединения точных копий осталось около151МиБ на постоянном диске; все три контроллера ожидают прежний резерв256МиБ. Новые раунды не выполняются. Резерв публикации128МиБ и аудиограницы не снижались. Оригинальные байты, пути, история, исходники и все восемь Git-пакетов сохранены. Временный /tmp не заменяет постоянное место для рабочего состояния, Git и снимка среды. Для новых полностью сохраняемых раундов требуется больше постоянного места.

start_skill_current.md содержит обновлённые инструкции подготовленной среды и проверенный идемпотентный запуск. Повторная проверка текущей основы и всех108 завершённых доказательств сохранена в final69-service-readiness.log; дубликаты процессов не запускались. scripts — независимые копии действующих программ, а не самостоятельная установка с нуля. Лицензионная Diva не включена. Backend-конфигурация сохраняется отдельно после этого коммита; сохранение и чтение обратно не означают применение/публикацию снимка или проверку восстановления в новой задаче. При requires_publish=true нужны Save и Publish в настройках среды.
''')
    (D/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(D))+'\n' for p in sorted(D.rglob('*')) if p.is_file()))
    target=str(D.relative_to(REPO));git('add','--',target)
    assert all(p.startswith(target+'/') for p in git('diff','--cached','--name-only').splitlines())
    git('diff','--cached','--check');git('commit','-m','Preserve final v69 three-held runtime, completed trials and storage-limit evidence')
    for p,oid in old.items():assert git('rev-parse','HEAD:'+p)==oid
    commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
    git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    public=[]
    for p in [D/'README.md',D/'start_skill_current.md',D/'FINAL69_RESOURCE_STATE.json',D/'scripts/start_three_services.py']:
        path=str(p.relative_to(REPO))
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path,timeout=60) as response:data=response.read();assert response.status==200
        assert data==p.read_bytes();public.append(dict(path=path,SHA256=sha(p),byte_exact=True))
    assert not git('status','--porcelain')
    write(R/'public-final69-runtime.json',dict(commit=commit,remote_main_exact=True,HTTP_files=public,full57_to69_trees_and_ZIPs_immutable=True,live_scripts_archived_as_independent_copies=True,match_reached=False))
    assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink()
    print('FINAL69_RUNTIME_PUBLIC_AND_HTTP_VERIFIED',commit,flush=True)
