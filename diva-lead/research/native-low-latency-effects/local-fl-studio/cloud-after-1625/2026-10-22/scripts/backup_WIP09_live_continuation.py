"""Record the completed source profile and verified continuing WIP09 search."""
from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
N=Path('/workspace/divalead-work/native-low-latency-effects');B=Path('/tmp/divalead-local-1625')
base=P/'diva-lead/research/native-low-latency-effects';d=base/'local-fl-studio/cloud-after-1625/2026-10-22'
owner='WIP09-live-corrected-continuation';pause=R/'auto-backup.pause'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def read(p):
    for attempt in range(8):
        try:return json.loads(Path(p).read_text())
        except json.JSONDecodeError:
            if attempt==7:raise
            time.sleep(.05)
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    deadline=time.monotonic()+90
    while read(R/'auto-backup-state.json')['phase']!='paused_for_manual_Git_work':assert time.monotonic()<deadline;time.sleep(1)
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected()
        retain={p:git('rev-parse','HEAD:'+p)for p in [
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22',
            *['diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/WIP'+n for n in ['06','07','08','09']]]}
        source=B/'fl20-OscMix6p3-EQ76-profile-01';out=d/'proofs'/source.name;out.mkdir(exist_ok=True)
        for p in source.glob('*.json'):shutil.copyfile(p,out/p.name)
        for name in ['run_OscMix_source_profile.py','continue_corrected_fl20.py','start_corrected_fl20.py',
            'restore_corrected_workspace.py','verify_corrected_restoration.py','finalize_fl20_kit.py',
            'export_fl20_checkpoint.py','publish_fl20_WIP.py','backup_WIP09_live_continuation.py']:
            shutil.copyfile(B/name,d/'scripts'/name);shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
        s=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');f=read(N/'FL20_FINITE_SOURCE_PROFILE.json')
        assert f['phase']=='finite_profile_completed_continuous_controller_ready'
        assert s['phase']=='corrected_pipeline_step_running'and s['numeric_workers_observed']==4
        assert not(N/'fl20-corrected-search.pause').exists()
        for item in [s['controller'],s['child'],*s['actual_native_hosts']]:
            fields=Path(f"/proc/{item['PID']}/stat").read_text().split()
            assert fields[21]==item['starttime']
        proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_controller=s,
            completed_finite_profile=f,source09_selected_and_running=True,actual_numeric_workers=4,
            same_three_held_notes_per_phrase=True,only_validated_full_native_graphs_accepted=True,
            old_source05_fit05_planned_interruption_recorded=True,all_saved_DLLs_private=True,
            first_automatic_full_WIP07_publication_passed=True,full_WIP09_published_and_HTTP_checked=True,
            actual_FL_GUI_export_pending=True,reference_match_reached=False)
        (d/'proofs/WIP09_ACTUAL_CONTINUATION.json').write_text(json.dumps(proof,indent=2)+'\n')
        shutil.copyfile(N/'HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json',d/'proofs/HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING_LATEST.json')
        header='''CURRENT AFTER COMPLETED WIP09 SOURCE PROFILE (2026-10-22). This overrides older active-finite-profile snapshots below. WIP09 is now the best complete published native kit. Its actual source is FL05_OscMix_6p3 (PWModDepth+1, VCA ModDepth-58, OscMix6.3), with independent real Diva/all281/12MIDI/raw/effGetChunk/effSetChunk proof and a real program embedded in the FLP. Native effect PDC0, THREE held notes per phrase repeated twice. Full original-reference match remains false and actual FL GUI export of the cloud WIPs is pending.

Finite run_OscMix_source_profile.py COMPLETED:5050 actual EQ-DLL evaluations, fresh whole-graph mean1.600775 vs1.606594 seed, SEM0.000419, robust. The complete export was independently repeated6times at mean1.600145/std0.000849 and full FLP/WAV/16FST/A-B/guide ZIP was normally pushed and HTTP-byte-verified. A separate source08 comparison had established source5.71->6.3; higher6.6/7/7.5/8/9/10 did not improve that source screen. Source profile and all source audits are backed up; no unsupported source_post_EQ extension was adopted.

CURRENT LIVE SERVICE: finite source profile's pause was released and the main continue_corrected_fl20.py controller was handed off at a verified IDLE boundary to WIP09/verification/candidate.json. Actual new controller/child/four native worker PID+starttime are checked in proofs/WIP09_ACTUAL_CONTINUATION.json. Inspect current N/FL20_CORRECTED_SEARCH_CONTROLLER.json and real current progress, not the old finite-running snapshots below. FL20_FINITE_SOURCE_PROFILE.json now says completed. New controller starts only once via start_corrected_fl20.py, checks source hashes, retains chorus_overrides, alternates actual EQ76/Chorus trials, accepts only fresh6+6 improvements, and creates full useful WIP backups. Its old NATIVE_SEARCH_CONTROLLER/native-search.stop remain retired. Root64MiB/tmp512MiB reserve applies; per-batch lossless historical AB cache receipts retain all original bytes. Do not infer activity from saved heartbeat alone or launch duplicate fits.

RESTORE: newest complete WIP is selected automatically by restore_corrected_workspace.py, currently09; explicit --checkpoint WIP09 is also supported. It restores actual source audio/h2p/real VST program paths and fixed local original-analysis layout, then native runtime/host prerequisites below and start_corrected_fl20.py apply. Changed sources MUST keep the real source_manifest VST chunk when building FLP; fl20_diva_wrapper.py preserves all wrapper subrecords except53 and updates the actual chunk length. WIP08 restore was already functionally replayed: all12 states/zero-depth exact,6 full captures mean1.609572. No independently fresh-machine or FL-GUI claim. Existing isolated managed checkout is used; no worktree unless requested. User authorized continued Git backups and render comparisons; continue until sound match or actual limits without per-trial questions.

'''
        current=R/'start_skill_current.md';current.write_text(header+current.read_text(),encoding='utf-8');shutil.copyfile(current,base/'start_skill_current.md')
        (d/'WIP09_CONTINUATION_RU.md').write_text('''# WIP09: подбор продолжает работать

WIP09 — текущий лучший полный native-комплект на трёх длинных нотах на фразу.
Используется заново проверенный Diva OscMix6.30, PWModDepth+1, VCA−58.
Исходник/281 параметр/12 MIDI/настоящий VST program проверены; партии и ARP
сохранены. Нового actual-FL GUI экспорта ещё нет, полного совпадения нет.

Подгонка EQ под источник завершена:5050 actual-DLL оценок, fresh mean
1.600775 против1.606594, SEM0.000419. Ещё6 независимых экспортных рендеров
дали mean1.600145/std0.000849. FLP/WAV/16FST/A-B/инструкция включены в
полный ZIP; скачанные GitHub WAV/ZIP/инструкция проверены по байтам.

Конечная подгонка завершена и освободила pause. Основной controller реально
продолжает работу с WIP09 на4 DLL-ветках; PID/starttime/новый источник/текущий
прогресс проверены. Старые снимки с ожидающим main и active finite относятся
к предыдущему этапу. Файл FL20_FINITE_SOURCE_PROFILE.json теперь completed;
актуальное состояние — FL20_CORRECTED_SEARCH_CONTROLLER.json.

Дальше чередуются EQ и Chorus. Только устойчивые улучшения после6+6 свежих
полных рендеров допускаются к бекапу с FLP/WAV/FST/A-B/инструкцией. Старый
модельный контекст Chorus и source05 автоматически не возобновляются.
''',encoding='utf-8')
        readme=d/'README_RU.md';readme.write_text('[Актуальная работа после полного WIP09](WIP09_CONTINUATION_RU.md).\n\n'+readme.read_text(),encoding='utf-8')
        state=d/'CURRENT_CORRECTED_FL20_STATE.json';data=read(state);data.update(
            best_complete_checkpoint='WIP09',actual_continuous_controller_handed_off_to_WIP09=True,
            finite_source_profile_completed=True,native_numeric_workers_verified=4,
            further_research='Actual corrected EQ76 and Chorus search continues from WIP09; reference match false')
        state.write_text(json.dumps(data,indent=2)+'\n')
        files=sorted(p for p in d.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
        (d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n'for p in files))
        git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(s.startswith('diva-lead/research/native-low-latency-effects/')for s in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Keep WIP09 source matching live after completed native profile and verified full backup')
        commit=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+p)==v for p,v in retain.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        for relative in ['WIP09_CONTINUATION_RU.md','proofs/WIP09_ACTUAL_CONTINUATION.json']:
            path=d/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/'+path.relative_to(P).as_posix()
            with urllib.request.urlopen(url,timeout=30)as response:assert response.read()==path.read_bytes()
        receipt=dict(commit=commit,previous_HEAD=before,all_complete_kits_and_numbered_releases_preserved=True,
            current_source09_native_search_actually_running_on4workers=True,reference_match_reached=False)
        (N/'WIP09_LIVE_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
