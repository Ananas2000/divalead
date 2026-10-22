"""Back up tested corrected startup/restore and completed capacity research."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
N=Path('/workspace/divalead-work/native-low-latency-effects');B=Path('/tmp/divalead-local-1625')
base=P/'diva-lead/research/native-low-latency-effects';dest=base/'local-fl-studio/cloud-after-1625/2026-10-22'
owner='corrected-controller-restoration-research';pause=R/'auto-backup.pause'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    deadline=time.monotonic()+90
    while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
        assert time.monotonic()<deadline;time.sleep(1)
    with (R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected()
        retain={p:git('rev-parse','HEAD:'+p)for p in [
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/WIP06']}
        for name in ['fl20_objective.py','export_fl20_checkpoint.py','fit_fl20_postEQ.py','fit_fl20_postEQ_scaled.py',
            'continue_corrected_fl20.py','start_corrected_fl20.py','restore_corrected_workspace.py','verify_corrected_restoration.py',
            'archive_historical_AB_cache.py','backup_corrected_continuation.py']:
            shutil.copyfile(B/name,dest/'scripts'/name)
            shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
        for family in ['fl20-common-postEQ-42-fit-03','fl20-common-postEQ-42-fit-04-scaled']:
            out=dest/'proofs'/family;out.mkdir(exist_ok=True)
            for p in (B/family).glob('*.json'):shutil.copyfile(p,out/p.name)
        for filename in ['fl20-common-postEQ-42-fit-01.log','fl20-common-postEQ-42-fit-02.log','corrected-restoration-check-01.log']:
            shutil.copyfile(B/filename,dest/'proofs'/('aborted-'+filename))
        out=dest/'proofs/corrected-restoration';out.mkdir(exist_ok=True)
        shutil.copyfile(B/'corrected-restoration-check-02/RESTORATION_PROOF.json',out/'RESTORATION_PROOF.json')
        shutil.copyfile(B/'corrected-restoration-check-02/actual-DLL-restoration-check/PROOF.json',out/'ACTUAL_DLL_REPLAY.json')
        shutil.copyfile(N/'HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json',dest/'proofs/HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json')
        current=json.loads((N/'FL20_CORRECTED_SEARCH_CONTROLLER.json').read_text());controller=current['controller']
        actual=Path(f"/proc/{controller['PID']}/stat").read_text().split()
        assert actual[21]==controller['starttime']and 'continue_corrected_fl20.py'in controller['cmdline']
        assert current['numeric_workers_observed']==4
        (dest/'proofs/CORRECTED_CONTROLLER_CURRENT_VERIFICATION.json').write_text(json.dumps(dict(
            UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller=current,
            actual_process_identity_verified=True,start_helper_called_twice_same_controller_and_cohort=True,
            proc_children_file_unavailable_ps_PPID_enumeration_used=True,
            previous_finite_suite_completed_WIP06_then_failed_research_control=True,
            failed_controls_preserved_and_diagnosed_not_accepted=True,original_native_search_stop_preserved=True,
            first_automatic_future_WIP_publication_still_pending=True,match_reached=False),indent=2)+'\n')
        latest='''CURRENT VERIFIED CORRECTED SEARCH SERVICE (2026-10-22). Supersedes all older service startup directions below. One continue_corrected_fl20.py controller is actually running, with4 observed real native DLL workers and the physical FL05 source. start_corrected_fl20.py was called twice and confirmed the same controller/cohort, without duplicates. It alternates corrected-context controls and76-coordinate actual-DLL EQ fits; accepted improvements require fresh full-chain6+6 validation. Useful future x95 improvements are exported as a complete FLP/WAV/16FST/A-B/FL-guide kit and sent through the shared Git lock. WIP06 publication is verified; automatic publication of a NEXT generated kit has not yet executed. Never mistake a recorded finite suite failure or old stopped NATIVE_SEARCH_CONTROLLER.json for this current service. State is N/FL20_CORRECTED_SEARCH_CONTROLLER.json; stop/pause are fl20-corrected-search.stop/.pause. Verify PID/starttime/cmdline, child and current progress. Retain old native-search.stop.

Corrected startup: if /tmp runtime is already valid, run /workspace/.venvs/divalead/bin/python -B /tmp/divalead-local-1625/start_corrected_fl20.py, then verify actual DLL workers/current captures. If corrected /tmp workspace disappeared, first restore the old native runtime from after-DSP-arrival as documented below with NO hosts active. Then run PUBLIC/cloud-after-1625/2026-10-22/scripts/restore_corrected_workspace.py --destination /tmp/divalead-local-1625 from the full checkout (PUBLIC=/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio), compile public fl_native_fl20_host.c beside fl_native_probe.c into a NEW W/fl_native_fl20_host.exe, and use the restored-candidate.json source_manifest. The restore helper defaults to complete WIP06; a newer supported checkpoint may be selected explicitly. The helper restores local analysis through the fixed path, source/preset/MIDI bytes from ZIP/full repo, and rewrites paths. WIP06 raw audit TSV falls back to the actually checked local FL05 TSV; its original fresh log was not embedded. Later exporters include the raw TSV/log in deterministic gzip. Don't fabricate missing logs.

Restore was actually exercised into a NEW /tmp folder, then12 native state bytes and source zero-depth audio were exact; six restored full captures mean1.648498/std0.000883 against published1.649041. This verifies the prepared machine/asset restore, not independently new-machine installation or actual FL GUI. New cloud context remains pending actual-FL validation. Scripts contain documented original absolute runtime paths; fl20_objective supports DIVALEAD_FL20_BASE for a separately restored assessment runtime.

Two common post-Chorus native EQ2s are RESEARCH ONLY. Initial zero-gain-is-identity assumption failed: native flat EQ has its own phase response. Exact BYPASS old/new control0.0 and old/new flat-placement comparison max9.39e-6/RMS2.25e-7 passed within twice the independently measured baseline block variation. No waveform shifts/gain corrections hide this response. Unscaled42 fit stopped ABNORMAL at0 iterations/595 evaluations and was not a negative capacity proof. Scaling optimizer value+gradient by1000, preserving the actual loss/optimum, overcame native .01dB quantization; fresh full mean1.644680 vs1.648600, SEM0.000548. This is a small numerical research win; source_post_EQ remains unsupported by the ordinary x95 exporter/FLP. It is NOT adopted into the12-effect WIP06 or ordinary controller. Do not silently discard metadata or claim a deployable14-effect project exists. Current supported-model refinement continues separately.

Storage:80 historical non-current v53-derived AB cache WAVs were losslessly archived (all decompressed SHA256 checked) under all-repository-selection/archived-historical-AB; actual free bytes64831488->131874816, about64MiB recovered. Only derived AB_* cache paths were removed; all source/full/reference edits/models/presets/numbered releases and complete WIP06 are retained. Per-batch receipts restore every original AB byte. No whole historical release deletion. The controller honors root64MiB/tmp512MiB reserve and backs up useful full WIPs under the common Git pause/flock. Existing managed cloud checkout is isolated; no worktree unless explicitly requested. Match=false, continue actual sound work.

'''
        private=R/'start_skill_current.md';private.write_text(latest+private.read_text(),encoding='utf-8');shutil.copyfile(private,base/'start_skill_current.md')
        summary=dest/'CONTINUATION_SERVICE_RU.md'
        summary.write_text('''# Продолжение без остановки после WIP06

Запущен отдельный исправленный controller; два вызова запуска сохранили один
процесс и четыре реальные DLL-ветки. Старый подбор с неправильным прогревом
Chorus остаётся остановленным. Новый цикл уточняет12-effect вариант WIP06.
Улучшения принимаются после6+6 свежих полных рендеров; полезные WIP получают
FLP/WAV/16FST/A-B/инструкцию и обычный Git push с проверкой скачанных байтов.
Первый автоматический следующий полный комплект ещё предстоит проверить.

Тест восстановления: новая папка из опубликованного ZIP и полного checkout,
побитные source/h2p и12 native states, точный zero-depth audio,6 новых полных
рендеров mean1.648498/std0.000883 против опубликованного mean1.649041.
Новая машина и новый экспорт в реальной FL GUI этим не проверены.
Команда: scripts/restore_corrected_workspace.py --destination NEW_FOLDER.
Runtime DLL/Wine/MinGW готовится отдельно по предыдущему after-DSP-arrival.
Затем scripts/start_corrected_fl20.py запускает один corrected controller.

Дополнительные два common EQ пока исследовательские. Native flat EQ2 не
равен bypass по фазе; именно неверная первая проверка остановила первый
запуск. Правильный bypass control побитно совпал. Разница при перестановке
flat EQ меньше ранее независимо измеренной block-size вариативности.
Исходный optimizer остановился ABNORMAL; масштабирование функции/градиента
на1000 устранило шаги меньше квантования0.01dB. Новый full fresh mean
1.644680 против1.648600, SEM0.000548 — небольшой подтверждённый численный
выигрыш. Нового14-effect проекта ещё нет; source_post_EQ нельзя передавать
в обычный x95 exporter. WIP06 по-прежнему12-effect.

Для места сохранены без потерь80 старых cache A/B: восстановлено~64MiB.
Байты восстанавливаются по receipts; исходные лиды/референсные монтажи/
модели/пресеты/номерные версии сохранены. Полного совпадения нет.
''',encoding='utf-8')
        readme=dest/'README_RU.md';readme.write_text('[Актуальная работа, восстановление и новые проверки](CONTINUATION_SERVICE_RU.md).\n\n'+readme.read_text(),encoding='utf-8')
        state=dest/'CURRENT_CORRECTED_FL20_STATE.json';data=json.loads(state.read_text());data.update(
            corrected_search_controller_running_and_idempotent_start_verified=True,
            restored_ZIP_native_audio_replay_verified=True,
            two_common_EQ_research_small_win_not_adopted=True,further_research='Live supported12-effect refinement; actual FL GUI export still pending')
        state.write_text(json.dumps(data,indent=2)+'\n')
        files=sorted(p for p in dest.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
        (dest/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix()+'\n'for p in files))
        git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Keep corrected native search running; verify ZIP restoration and retain common-EQ capacity checks')
        commit=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+p)==v for p,v in retain.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        checks=[]
        for relative in ['CONTINUATION_SERVICE_RU.md','scripts/start_corrected_fl20.py','proofs/corrected-restoration/ACTUAL_DLL_REPLAY.json']:
            p=dest/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/'+p.relative_to(P).as_posix()
            with urllib.request.urlopen(url,timeout=30)as response:body=response.read()
            assert body==p.read_bytes();checks.append(dict(path=relative,HTTP_byte_exact=True))
        receipt=dict(commit=commit,previous_HEAD=before,remote_main_exact=True,HTTP_checks=checks,
            existing_WIP06_local_FL05_numbered_releases_and_old_native_kit_preserved=True,match_reached=False)
        (N/'CORRECTED_CONTROLLER_RESTORE_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
