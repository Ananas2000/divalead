"""Publish the complete freshly verified WIP06 without replacing local FL05."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
N=Path('/workspace/divalead-work/native-low-latency-effects');B=Path('/tmp/divalead-local-1625')
base=P/'diva-lead/research/native-low-latency-effects';dest=base/'local-fl-studio/cloud-after-1625/2026-10-22'
kit=B/'FL20_NATIVE_06_WIP';z=B/'Diva_NATIVE_06_WIP_complete_WIP.zip'
assert (B/'FL20_NATIVE_06_READY.json').exists()
proof=json.loads((kit/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
assert proof['actual_FL_validation_pending'] and not proof['match_reached']
assert len(proof['modulated_captures'])==6 and proof['selected_capture_is_median_not_best']
assert (kit/'verification/FST_INDEPENDENT_PARSE.json').exists()
assert json.loads((kit/'verification/FLP_VERIFICATION.json').read_text())['all12_native_states_exact_against_real_DLL_saved_states']
owner='corrected-FL20-native-WIP06';pause=R/'auto-backup.pause'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    deadline=time.monotonic()+90
    while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
        assert time.monotonic()<deadline;time.sleep(1)
    with (R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True)
        subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected()
        retained={p:git('rev-parse','HEAD:'+p)for p in [
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22']}
        public=dest/'WIP06';public.mkdir(exist_ok=False)
        names=['Diva_NATIVE_06_WIP.flp','NATIVE_FULL_180BPM_WIP.wav','FL_STUDIO_RU.md','README_RU.md',
            'AB_ORIGINAL_V83_ACTUAL_FL05_Diva_NATIVE_06_WIP.mp3']
        for name in names:shutil.copyfile(kit/name,public/name)
        shutil.copyfile(z,public/z.name)
        shutil.copytree(kit/'verification',public/'verification',ignore=shutil.ignore_patterns('*.wav'))
        # Keep the full source/MIDI/16 FST/edit WAV in the byte-verified ZIP.
        for family in ['fl20-Chorus-shapes-EQ76-full-03','fl20-controls-full-01']:
            out=dest/'proofs'/family;out.mkdir(exist_ok=True)
            for p in (B/family).glob('*.json'):
                if p.stat().st_size>200000:
                    data=p.read_bytes();packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data
                    (out/(p.name+'.gz')).write_bytes(packed)
                else:shutil.copyfile(p,out/p.name)
        for name in ['search_fl20_controls.py','export_fl20_checkpoint.py','finalize_fl20_kit.py',
            'verify_fl20_latency.py','fit_fl20_postEQ.py','run_corrected_fl20_suite.py','publish_fl20_WIP.py']:
            shutil.copyfile(B/name,dest/'scripts'/name)
        shutil.copyfile(B/'tools/fl_native_fl20_postEQ_host.c',dest/'scripts/fl_native_fl20_postEQ_host.c')
        state=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='physical FL05 VCA ModDepth -58',
            model_family='FL20_corrected_context_three_held',host_context='Chorus_excluded_from_silent_warmup',
            objective_version='local_full_original_criteria_FL20_context_v1',only_three_held_notes_per_phrase=True,
            full_actual_native_DLL_export_mean=proof['mean_original_objective'],
            full_actual_native_DLL_export_standard_deviation=proof['std_original_objective'],
            complete_WIP='WIP06/Diva_NATIVE_06_WIP_complete_WIP.zip',candidate='WIP06/verification/candidate.json',
            actual_FL_GUI_validation_pending=True,declared_effect_PDC_frames=0,reference_match_reached=False,
            original_local_FL05_and_numbered_releases_preserved=True,old_cloud_controller_stopped=True,
            further_research='Separate post-Chorus common-EQ capacity experiment; unsupported by ordinary x95 exporter, not adopted')
        (dest/'CURRENT_CORRECTED_FL20_STATE.json').write_text(json.dumps(state,indent=2)+'\n')
        readme=dest/'README_RU.md';s=readme.read_text();s='''# Полный промежуточный комплект WIP06

[Скачать ZIP: FLP, WAV, Diva, MIDI, 16 FST, A/B и проверки](WIP06/Diva_NATIVE_06_WIP_complete_WIP.zip).
[Инструкция для FL Studio20](WIP06/FL_STUDIO_RU.md).
[A/B: оригинал → v83 → реальный FL05 → WIP06](WIP06/AB_ORIGINAL_V83_ACTUAL_FL05_Diva_NATIVE_06_WIP.mp3).
WIP06 начинается с12.504с. Новый WAV получен native DLL хостом;
его фактический экспорт в FL GUI пока не выполнен. Совпадения нет.
После загрузки комплекта дальнейший подбор продолжен отдельным проходом.

'''+s;readme.write_text(s,encoding='utf-8')
        pointer=base/'CLOUD_AFTER_LOCAL_1625_RU.md'
        pointer.write_text('''# Облачное продолжение после локального FL05

[Полный WIP06 для FL Studio20 и результаты](local-fl-studio/cloud-after-1625/2026-10-22/README_RU.md).
В комплекте FLP, WAV, Diva-пресет, MIDI,16 FST, A/B, инструкция и проверки.
Исправлен прогрев Chorus, новый вариант проверен повторными рендерами native
DLL. Новый actual-FL GUI export ещё предстоит; полного совпадения нет.
Дальнейшие эксперименты продолжаются. Проверенный локальный FL05, номерные
версии и старый полный v83 сохранены.
''',encoding='utf-8')
        private=R/'start_skill_current.md'
        header='''CURRENT CORRECTED FL20 CONTINUATION (2026-10-22). Supersedes ALL old current-state/controller startup directions below. This task is cloud continuation of actual Windows local HANDOFF_1625_RU.md. Read CLOUD_AFTER_LOCAL_1625_RU.md and local-fl-studio/cloud-after-1625/2026-10-22/README_RU.md first. The user wants continued real Diva/native renders until limits or a sound match, THREE held incoming notes per phrase repeated twice, original-reference analysis only, no MistaTowa, no16-note transcription. Preserve the verified actual local FL05 and all numbered releases/root ZIPs. WIP06 is a NEW full technical backup, not an actual FL GUI export and not a full match.

Critical correction: the old offline host warmed Chorus with65536 zero frames, advancing its LFO by1.36533sec before source input. New fl_native_fl20_host.c bypasses ONLY Chorus during this warmup, restores its flag, and leaves all other warm128 behavior intact. Independent controls: old/new bypass and zero-depth sample-exact; two new DLL instances/12 full captures close most of the actual-FL04 gap. Actual DLL hashes match the local PC. Keep old native-search.stop; DO NOT restart old continue_native_chorus.py/start_native_chorus.py or high-latency Finish fits. Their old source/objective/context is obsolete.

Current source is physical FL05 VCA ModDepth-58, not old PW-only VCA-68. Durable source-bases/FL05_VCA_minus58 has h2p/raw/all281/log/fresh proof; both independent source renders are bit-exact and match all281/12events. The full WIP06 ZIP includes source/MIDI/presets. Candidate x95 additionally has chorus_overrides; apply(x) alone resets them and is WRONG. Use export_fl20_checkpoint.py/search_fl20_controls.py/fit_fl20_EQ76_with_shapes.py with all overrides and corrected host. Ordinary old exporter must not handle source_post_EQ metadata. The post-EQ research uses a separate host and has NOT been adopted. Current corrected criterion is local full .65tone+.35standard+.05abs(log(ABgain))+clip penalty and tiny EQ L2; do not compare its loss to old cloud loss. Every acceptance needs6+6 fresh whole native-chain captures and a robust improvement beyond3SEM. FST generator was fixed against actual GUI-verified byte-exact fixtures; old canonical kit's old mixer FST remain historical. restore_checkpoint.py reference path was fixed and functionally retested.

Runtime: /tmp/divalead-local-1625 contains corrected scripts/results/restored runtime; durable code also in native-low-latency-effects/FL20-corrected/runtime-scripts, public scripts in cloud-after-1625. Private FL20_CORRECTED_SEARCH_CONTROLLER.json is distinct from old NATIVE_SEARCH_CONTROLLER.json: verify actual PID/starttime/cmdline and current finite child, do not mistake a completed suite/old heartbeat/Git coordinator for active audio work. run_corrected_fl20_suite.py was used for the actual finite sequence; do not blindly replay it into existing result paths or assume its original PID wait is portable. If /tmp lost, restore old runtime safely with NO native hosts active, then restore local analysis via fixed tools/restore_checkpoint.py, rebuild the corrected host into a NEW executable, reconstruct FL05 input from audited raw, and run real zero-depth/bypass/state and repeated full controls before further fitting. Never overwrite an executable used by workers. In this managed isolated environment use existing checkouts; do not create Git worktrees unless explicitly requested. Cloud draft persistence does not prove a new machine restore or publication.

Git pause/flock protocol below remains mandatory. The actual PC session is separate; no PC control is exposed here. User already authorized native-research commits/pushes and useful full WIP backups with FL20 instructions; do not ask per-trial questions. Continue the active corrected search. Match=false. Earlier histories below are retained for negative trials and restore context, not instructions to restart obsolete models.

'''
        private.write_text(header+private.read_text(),encoding='utf-8')
        shutil.copyfile(private,base/'start_skill_current.md')
        files=sorted(p for p in dest.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
        (dest/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix()+'\n'for p in files))
        assert not any(p.suffix.lower()in ['.dll','.exe','.rar']for p in public.rglob('*')if p.is_file())
        git('add','--','diva-lead/research/native-low-latency-effects')
        git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Back up corrected Chorus WIP06 with complete FL20 project, native WAV, presets and A/B')
        commit=git('rev-parse','HEAD');assert protected()==old
        assert all(git('rev-parse','HEAD:'+p)==v for p,v in retained.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        checked=[]
        for relative in ['README_RU.md','WIP06/FL_STUDIO_RU.md','WIP06/Diva_NATIVE_06_WIP_complete_WIP.zip','WIP06/NATIVE_FULL_180BPM_WIP.wav']:
            p=dest/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/'+p.relative_to(P).as_posix()
            with urllib.request.urlopen(url,timeout=45)as response:body=response.read()
            assert body==p.read_bytes();checked.append(dict(file=relative,HTTP_byte_exact=True,SHA256=hashlib.sha256(body).hexdigest()))
        receipt=dict(commit=commit,previous_HEAD=before,remote_main_matches=True,HTTP_checks=checked,
            old_releases_local_FL05_and_native_checkpoint_preserved=True,actual_FL_GUI_validation_pending=True,match_reached=False)
        (N/'FL20_NATIVE_06_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
