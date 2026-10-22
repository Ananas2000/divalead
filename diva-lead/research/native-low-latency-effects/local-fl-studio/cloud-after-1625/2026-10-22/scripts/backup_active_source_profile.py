"""Back up the actual source08 handoff while its four-worker EQ profile runs."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
B=Path('/tmp/divalead-local-1625');P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
N=Path('/workspace/divalead-work/native-low-latency-effects');base=P/'diva-lead/research/native-low-latency-effects'
d=base/'local-fl-studio/cloud-after-1625/2026-10-22';owner='actual-source08-profile-backup';pause=R/'auto-backup.pause'
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
        retained={p:git('rev-parse','HEAD:'+p)for p in [
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22',
            *['diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/WIP'+n for n in ['06','07','08']]]}
        for name in ['run_OscMix_source_profile.py','fl20_diva_wrapper.py','audit_OscMix_source.py',
            'check_Diva_source_FLP_chunk.py','pair_OscMix_against_current.py','probe_corrected_Diva_source.py',
            'probe_corrected_Diva_OscMix_edge.py','export_OscMix_WIP08.py','continue_corrected_fl20.py',
            'start_corrected_fl20.py','restore_corrected_workspace.py','verify_corrected_restoration.py',
            'export_fl20_checkpoint.py','finalize_fl20_kit.py','publish_fl20_WIP.py','backup_active_source_profile.py']:
            shutil.copyfile(B/name,d/'scripts'/name);shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
        for family in ['fl20-Diva-source-conditional-01','fl20-Diva-OscMix-edge-02']:
            out=d/'proofs'/family;out.mkdir(exist_ok=True)
            for p in(B/family).glob('*.json'):
                data=p.read_bytes()
                if len(data)>200000:(out/(p.name+'.gz')).write_bytes(gzip.compress(data,mtime=0))
                else:shutil.copyfile(p,out/p.name)
        out=d/'proofs/WIP08-restoration';out.mkdir(exist_ok=True)
        shutil.copyfile(B/'corrected-restoration-WIP08-check/RESTORATION_PROOF.json',out/'RESTORATION_PROOF.json')
        shutil.copyfile(B/'corrected-restoration-WIP08-check/actual-DLL-restoration-check/PROOF.json',out/'ACTUAL_NATIVE_REPLAY.json')
        shutil.copyfile(B/'corrected-restoration-default-latest-check/RESTORATION_PROOF.json',out/'DEFAULT_LATEST_SELECTION.json')
        for name in ['PLANNED_SOURCE08_HANDOFF.json','CORRECTED_ONBOARDING_DRAFT_READBACK.json']:
            shutil.copyfile(N/name,d/'proofs'/name)
        for folder in(N/'FL20-corrected/completed').glob('fl20-*'):
            out=d/'proofs/completed-corrected-cycles'/folder.name;out.mkdir(exist_ok=True,parents=True)
            for p in folder.iterdir():
                if p.is_file():shutil.copyfile(p,out/p.name)
        main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');finite=read(N/'FL20_FINITE_SOURCE_PROFILE.json')
        assert main['phase']=='paused_by_control_or_actual_disk_reserve'
        assert finite['phase']=='finite_source_EQ_fit_running'and finite['numeric_workers_observed']==4
        child=finite['child'];actual=Path(f"/proc/{child['PID']}/stat").read_text().split();assert actual[21]==child['starttime']
        proof=dict(main_controller=main,actual_finite_profile=finite,observed_real_native_workers=4,
            main_pause_is_CPU_ownership_not_a_stopped_audio_task=True,actual_current_source='FL05_OscMix_6p3',
            new_source_all281_MIDI_raw_and_VST_state_checked=True,main_old_source05_fit05_interrupted_purposefully=True,
            old_training_candidate_not_accepted=True,profile_result_pending=True,reference_match_reached=False)
        (d/'proofs/ACTUAL_SOURCE08_ACTIVE_HANDOFF.json').write_text(json.dumps(proof,indent=2)+'\n')
        training=read(Path(finite['root'])/'best.json');training['not_accepted_until_full_fresh_validation']=True
        (d/'proofs/SOURCE08_LIVE_TRAINING_NOT_ACCEPTED.json').write_text(json.dumps(training,indent=2)+'\n')
        header='''CURRENT ACTUAL SOURCE08 HANDOFF (2026-10-22). WIP08 is the best complete published native kit. OscMix changed5.71->6.30; all other281 values stay FL05, same12 incoming events/THREE held notes per phrase/ARP. N/source-bases/FL05_OscMix_6p3 contains fresh h2p/raw/all281/log plus ACTUAL effGetChunk bytes. Two fresh Diva instances, including real chunk reload, reproduce the exact raw. A source-only FLP record53 replacement was extracted/reloaded into actual Diva: all281/raw exact. WIP08 FLP embeds that actual program; real FL GUI export remains pending. Corrected native error improved~1.61812->1.60924 with6+6 independent captures; separate export mean1.60968. Original match=false. Prefer the complete source08 over older source05 kits unless further fresh validation beats it.

CURRENT WORK IS A FINITE FOUR-WORKER SOURCE08 PROFILE, not the paused main coordinator. Inspect N/FL20_FINITE_SOURCE_PROFILE.json and actual child/root/progress/PID/starttime. run_OscMix_source_profile.py owns fl20-corrected-search.pause; main continue_corrected_fl20.py is intentionally idle with source08 already installed. Do NOT kill the active finite fit or clear its pause as a stale controller based solely on the main idle state. The previous old-source05 fit05 was deliberately interrupted at its finally-closing boundary to move resources to verified source08; its unaccepted training proposal is preserved. The current profile uses the separate edge-validated source08 seed~1.60683 and actual native EQ76 optimization. After fresh6+6 checks, it exports/publishes a full improved kit, replaces ONLY the observed idle main coordinator with the chosen validated seed, and releases its own pause in finally so the continuous source08 search resumes. Observe actual completion/error state; don't infer it from this snapshot. Old native-search.stop stays.

NEW SOURCE REQUIREMENT: x95 alone describes FX, not source. Use source_manifest including real source_VST_chunk/SHA for changed sources. fl20_diva_wrapper.py preserves FruityWrapper subrecords and updates record53's binary chunk length using actual effGetChunk data. finalize_fl20_kit.py embeds it; it must NOT falsely claim Diva state unchanged from local FL05 when OscMix changed. source_post_EQ is still unsupported/research-only; no14-effect native kit is adopted. The source edge6.0/6.3/6.6/7/7.5/8/9/10 confirmed6.3 best in that screen, with fresh mean1.60683 vs1.61532, SEM0.000286. Higher OscMix worsened the actual criterion. All notes and ADSR/ARP remain fixed.

RESTORE: public scripts/restore_corrected_workspace.py defaults to the newest complete WIP folder, now08 (or explicit --checkpoint WIP08), and rewrites BOTH source audio/preset and VST-chunk paths. WIP08 restored into a new folder passed all12 native state-byte checks, exact zero-depth audio and six full captures mean1.609572/std0.000683. Restored real program bytes equal its FLP's actual program. This verifies these assets on the prepared machine, not an independently new cloud machine or FL GUI. Keep the prepared Wine/native SDK/DLL runtime steps below; no worktrees without explicit user request. Source08 references are restored from ZIP/full checkout, not fabricated missing logs. The cloud draft was saved/read back; install/network/secrets/runtime fields preserved. Refresh the repo pin after this new backup; saving is not publication. Continue actual renders until match or real limits; no per-trial user questions.

'''
        current=R/'start_skill_current.md';current.write_text(header+current.read_text(),encoding='utf-8');shutil.copyfile(current,base/'start_skill_current.md')
        guide=d/'SOURCE08_CONTINUATION_RU.md'
        guide.write_text('''# Текущий источник — проверенный WIP08

Лучший полный опубликованный native-комплект — WIP08. В Diva изменён только
OscMix5.71→6.30 относительно локального FL05; PWModDepth+1 и VCA−58 сохранены.
Три длинные ноты на фразу, внутренний ARP, ADSR и12 входящих событий прежние.
Два свежих запуска Diva и загрузка её настоящего effGetChunk дали побитно
тот же raw. Проектный chunk тоже извлечён и проверен в настоящей Diva.
Новый фактический экспорт в GUI FL ещё предстоит; полного совпадения нет.

WIP08: mean1.60968/std0.00060 на6 экспортных DLL-рендерах. Отдельное6+6
сравнение с прежним источником:1.61812→1.60924, SEM0.000372. Другая сетка
OscMix6.0/6.3/6.6/7/7.5/8/9/10 оставила6.3 лучшим; свежий контроль
1.61532→1.60683, SEM0.000286. Это ошибки, не проценты сходства.

Сейчас run_OscMix_source_profile.py владеет четырьмя настоящими DLL-ветками
и уточняет EQ под этот источник. Основной controller намеренно ждёт через
pause; это не остановка численного подбора. Состояние конечного задания:
FL20_FINITE_SOURCE_PROFILE.json. После свежей полной проверки полезный
вариант получит FLP/WAV/FST/A-B/инструкцию и Git-бекап, затем controller
будет продолжать с выбранным проверенным источником. Старый source05 fit05
прерван целенаправленно ради нового источника, его training не принят.

Восстановление WIP08 в новой папке проверено: реальные program bytes,
12 native states и zero-depth audio точны;6 full captures mean1.609572,
std0.000683. Helper теперь по умолчанию выбирает последний полный WIP и
восстанавливает путь к VST program, как и к WAV/h2p. GUI и новая машина
этим не тестировались. Исторический локальный FL05 и WIP06/07/08 сохранены.
''',encoding='utf-8')
        readme=d/'README_RU.md';readme.write_text('[Актуальный источник WIP08 и продолжающаяся работа](SOURCE08_CONTINUATION_RU.md).\n\n'+readme.read_text(),encoding='utf-8')
        files=sorted(p for p in d.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
        (d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n'for p in files))
        git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(s.startswith('diva-lead/research/native-low-latency-effects/')for s in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Verify real Diva source08 program state, hand off the source and continue native EQ profiling')
        commit=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+p)==v for p,v in retained.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        checks=[]
        for rel in ['SOURCE08_CONTINUATION_RU.md','scripts/run_OscMix_source_profile.py','proofs/WIP08-restoration/ACTUAL_NATIVE_REPLAY.json']:
            p=d/rel;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/'+p.relative_to(P).as_posix()
            with urllib.request.urlopen(url,timeout=30)as response:data=response.read()
            assert data==p.read_bytes();checks.append(dict(path=rel,HTTP_byte_exact=True))
        receipt=dict(commit=commit,previous_HEAD=before,all_existing_complete_kits_and_numbered_releases_preserved=True,
            actual_four_worker_source08_profile_running=True,HTTP_checks=checks,match_reached=False)
        (N/'SOURCE08_ACTIVE_PROFILE_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
