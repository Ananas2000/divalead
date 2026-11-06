"""Publish actual runtime/setup evidence and continuation scripts; no sound acceptance."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,runpy,shutil,time
J=Path(__file__).resolve().parent;A=J.parent/'pc-stereo-20261024';N=J.parent/'native-low-latency-effects';h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='checkpoint_actual_full41_and135');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
    try:
        with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='checkpoint actual adopted41, numerical639, startup135, safe cache proofs, interrupted recoveries and continued six-draw fitting'),f)
        break
    except FileExistsError:
        if time.monotonic()>deadline:raise TimeoutError('Existing Git writer active')
        time.sleep(.5)
try:
    with(C/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
        dest=PUBLIC/'original-POST-RightAP-full41/runtime-and-continuation-20261107';dest.mkdir();scripts=dest/'scripts';scripts.mkdir();logs=dest/'raw-logs';logs.mkdir();evidence=dest/'session-evidence';evidence.mkdir()
        for file in J.glob('*.py'):shutil.copyfile(file,scripts/file.name)
        for file in J.glob('*.json'):shutil.copyfile(file,evidence/file.name)
        for file in J.glob('*.log'):(logs/(file.name+'.gz')).write_bytes(gzip.compress(file.read_bytes(),mtime=0))
        prior=scripts/'prior-Nov4';prior.mkdir()
        for file in(J.parent/'continuation-20261104').glob('*.py'):shutil.copyfile(file,prior/file.name)
        runtime=scripts/'actual-current-runtime';runtime.mkdir()
        for name in ['continue_stereo_ZL_matching.py','backup_stereo_numeric_checkpoint.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
        best=json.loads((A/'stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['full_public_kit_directory']=='ZL-WIP41';(dest/'BEST_SNAPSHOT.json').write_text(json.dumps(best,indent=2)+'\n');states=[]
        for name in ['FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json','ORIGINAL_NATIVE12_JOINT109_SIXDRAW_FULL41_STUDY.json','ORIGINAL_NATIVE12_FINE_AP54_FULL41_AFTER639_STUDY.json']:
            file=N/name
            if not file.exists():continue
            state=json.loads(file.read_text());(dest/name).write_text(json.dumps(state,indent=2)+'\n');owner=state.get('owner',state);pid=owner.get('PID');proc=Path('/proc')/str(pid)/'stat';alive=False
            if proc.exists():
                stat=proc.read_text().split();alive=stat[2]!='Z'and(not owner.get('starttime')or owner['starttime']==stat[21])
            states.append(dict(controller=name,PID=pid,phase=state['phase'],actual_alive_at_capture=alive,liveness_point_in_time_only=True))
        (dest/'ACTUAL_ACTIVITY_SNAPSHOT.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),states=states,no_future_activity_promise=True),indent=2)+'\n')
        startup=(J/'start_skill_current.md').read_text();(dest/'CLOUD_START_SAVED_DRAFT135.md').write_text(startup);(C/'start_skill_current.md').write_text(startup);(h['BASE']/'start_skill_current.md').write_text(startup)
        doc='''# WIP41: фактическая среда и продолжение

[Полный FL20 комплект41, A/B и инструкция](../../ZL41_CONTINUATION_RU.md). Улучшение принято после12 новых сравнений и двух холодных ZIP-рендеров0/0; полного совпадения нет. Источник Diva/три длинные ноты/ARP/ADSR/13native/PRIMARY620 не менялись; добавлен только RightAP7 в POST. Новый native-генератор без cachedbundle и все состояния проверены. MIDI и FLP отдельно разобраны:41→37→36 дважды, шесть note-on, никаких дополнительных коротких нот.

После публикации41 реально принят и полностью опубликован численный639 с дополнительной перенастройкой PRIMARY. Его собственные6warm+2cold не наследуют строгую first10/nonincreasingAir проверку41. BEST_SNAPSHOT — снимок фактического состояния, а не новая приёмка. Все прежние комплекты и последний PCGUI сохранены. Source/референс/MistaTowa не подменяются, старого Finish нет.

Новый runtime41 холодно воспроизводит опубликованный рабочий WAV0/0. Далее проверена единая цепь native12→2ZL→nativeTrim, подтверждены состояния и два cold0/0. Перезапущен подбор от41,4реальныхZL+2nativeTrim. PID/starttime снимок доказывает активность только в момент записи; обещания фоновой работы отсутствуют.

Среда переподключалась: файлы сохранились, несколько исследовательских процессов завершились. OS2 reported757/recorded749 и sourcecutoff reported609/recorded577 сохранены как ПРЕРВАННЫЕ; старый620sixdraw сохранил seed-stage без завершённого fit. Их исходные WAV/состояния/частичные данные и точные padded .f32 контейнеры сохранены отдельно; OS2 fixed-input snapshot повторно не дублируется в overlay. Это не завершённые969 поиски и не принятые новые звуки.

Продолжение: existing109 фильтров на шести общих реальных native-входах,2неиспользованных heldout, затем только полностью новые12 при квалификации. Источник и RightAP7 сохранены. Настоящий anchor40 загружает оба исходных компонента40. Дополнительный fineAP54 от639 не дал квалифицирующего выигрыша. Контроллеры/журнал указывают фактическое состояние; отсутствие completion нельзя выдавать за завершение.

Стартовые инструкции135 сохранены и прочитаны обратно точно. Installscript/репозитории/сеть/секреты/runtime requirements не изменялись. Это черновик, он не применён и среда не опубликована; для переноса подготовленного состояния нужны сохранение в настройках среды и публикация среды. Проверка относится к текущей машине, а не новому пустому окружению. Работа по звуку этого не ожидала.

Чистились только точно удалённо проверенные старые дубликаты/логи. Сохранены корневые208MiB, временные128MiB и архивные48MiB guards. Не удалялись исходники/текущий звук/старая история/private или неизвестные pack. Rawлоги сохранены gzip побитово, включая сообщения исправленных технических отказов. Новый FLP в WindowsGUI и ASIO не проверены.
''';(dest/'README_RU.md').write_text(doc);(dest/'FILE_SHA256.json').write_text(json.dumps({file.relative_to(dest).as_posix():hashlib.sha256(file.read_bytes()).hexdigest()for file in dest.rglob('*')if file.is_file()and file.name!='FILE_SHA256.json'},indent=2)+'\n')
        h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Checkpoint actual full41 runtime, verified draft135, numerical639 and honest interrupted-study recovery');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
        for file in [dest/'CLOUD_START_SAVED_DRAFT135.md',dest/'ACTUAL_ACTIVITY_SNAPSHOT.json',runtime/'continue_stereo_ZL_matching.py',evidence/'ADOPTED_FULL41_RUNTIME_CHECK.json']:assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+file.relative_to(P).as_posix())==file.read_bytes()
        proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),actual_runtime_and_setup_evidence_HTTP_verified=True,draft_revision=135,draft_saved_not_applied_or_published=True,source_private_oldkits_PC_GUI_preserved=True,reference_match_reached=False);(J/'FULL41_RUNTIME_SETUP_PUBLICATION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('PID')==os.getpid():pause.unlink()
