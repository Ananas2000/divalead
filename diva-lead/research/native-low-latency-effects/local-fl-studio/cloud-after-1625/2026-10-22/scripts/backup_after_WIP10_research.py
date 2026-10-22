"""Back up actual post-WIP10 research while the owned audio jobs keep running."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request

P=Path('/workspace/divalead');B=Path('/tmp/divalead-local-1625')
N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
base=P/'diva-lead/research/native-low-latency-effects';d=base/'local-fl-studio/cloud-after-1625/2026-10-22'
pause=R/'auto-backup.pause';owner='actual-post-WIP10-research-backup'

def read(p):return json.loads(Path(p).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():
    return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+
                  [s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])

with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    deadline=time.monotonic()+90
    while read(R/'auto-backup-state.json')['phase']!='paused_for_manual_Git_work':
        assert time.monotonic()<deadline;time.sleep(1)
    with(R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True)
        subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected()
        paths=['diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
               'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
               'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22']
        paths.extend(p.relative_to(P).as_posix()for p in sorted(d.glob('WIP[0-9][0-9]'))if p.is_dir())
        retained={p:git('rev-parse','HEAD:'+p)for p in paths}
        for name in ['continue_corrected_fl20.py','start_corrected_fl20.py','export_fl20_checkpoint.py',
                     'fit_fl20_EQ76_scaled.py','fit_fl20_EQ76_coordinates.py','search_fl20_controls.py',
                     'probe_corrected_Diva_harmonic_source.py','audit_selected_harmonic_source.py',
                     'pair_audited_harmonic_source.py','run_harmonic_source_after_scaled.py',
                     'probe_fl20_extended_WS.py','run_extended_WS_finite.py','diagnose_reference_residual.py',
                     'publish_fl20_WIP.py','backup_after_WIP10_research.py']:
            shutil.copyfile(B/name,d/'scripts'/name)
            shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
        for family in ['fl20-Diva-harmonic-source-03','fl20-EQ76-scaled1000-profile-01']:
            out=d/'proofs'/family;out.mkdir(exist_ok=True)
            for p in(B/family).glob('*.json'):
                data=p.read_bytes()
                if len(data)>200000:
                    zipped=gzip.compress(data,mtime=0);assert gzip.decompress(zipped)==data
                    (out/(p.name+'.gz')).write_bytes(zipped)
                else:shutil.copyfile(p,out/p.name)
        for name in ['FL20_SCALED_EQ76_FINITE_PROFILE.json','FL20_HARMONIC_SOURCE_SCREEN_STATE.json',
                     'FL20_EXTENDED_WS_FINITE_PROFILE.json','FL20_CORRECTED_SEARCH_CONTROLLER.json']:
            shutil.copyfile(N/name,d/'proofs'/('WIP10_'+name))
        for name in ['SIDE_LEVEL_CONTROL_EXTENSION.json','NEXT_CONTROLLER_METHOD_ROTATION.json','EQ76_COORDINATE_EXPERIMENT_SETUP.json']:
            shutil.copyfile(B/name,d/'proofs'/name)
        guide='''# Продолжение после полного WIP10

Полный [WIP10](WIP10/FL_STUDIO_RU.md) сохранён с FLP/WAV/MIDI/Diva/16 FST/A-B.
Отдельный экспорт native DLL: средняя ошибка1.588693, std0.001439 на6 рендерах;
WIP09:1.600145. Это ошибки, не проценты сходства. Совпадения нет.
Фактический экспорт этого нового проекта в GUI FL ещё предстоит.

Проверены28 наборов Diva плюс2 независимых контрольных рендера. Более широкая
сетка PW49.9..54, PW KeyFollow0..3 и совместных изменений PW/OscMix улучшения
при текущих FX не дала. Лучшим остался прежний источник6.3/+1/−58. Все281
параметров и12 входящих MIDI событий проверены в каждом реальном запуске Diva.
Поэтому более широкий поиск PW не принят; три длинные ноты на фразу и ARP прежние.

Численный подбор продолжен:76 EQ controls теперь проверяются прямыми четырьмя
изменениями на координату, с новыми полными6+6 контролями после проходов.
В controls добавлена отдельная регулировка уровня SIDE через реальные EQ Main;
уровень A/B выравнивается самими EQ, не скрытым изменением WAV.

Следующий конечный эксперимент проверяет более гибкую монотонную кривую в
настоящей Fruity WaveShaper DLL. До завершения текущего EQ задания он ожидает
через принадлежащий ему pause. Это не остановка работающего EQ. Новые curve
coordinates пока исследовательские: стандартные startup/export/accept явно
отказываются их принимать, чтобы не потерять эти настройки при воспроизведении.
Даже удачный trial сначала требует полной интеграции и проверки FLP/FST/restore.

Текущее физическое задание определяют PID/starttime/cmdline и JSON вне Git:
FL20_CORRECTED_SEARCH_CONTROLLER.json, FL20_EXTENDED_WS_FINITE_PROFILE.json.
Файлы proofs с WIP10_ — датированные снимки, а не обещание текущего статуса.
Ротация после handoff: EQ coordinates → controls/SIDE → scaled EQ → controls/SIDE.
Каждый новый best требует независимой проверки полного native графа; training
минимум не считается готовым результатом. Старый native-search.stop сохранён.
Все прежние номерные версии, корневые ZIP, локальный FL05 и полные native WIP
сохранены. Полного совпадения с оригиналом и переносаv83 пока нет.
'''
        (d/'CURRENT_RESEARCH_AFTER_WIP10_RU.md').write_text(guide,encoding='utf-8')
        readme=d/'README_RU.md';readme.write_text('[Продолжающаяся работа после WIP10](CURRENT_RESEARCH_AFTER_WIP10_RU.md).\n\n'+readme.read_text(),encoding='utf-8')
        header='''LATEST AFTER WIP10 (2026-10-22). Complete native WIP10 is public, independently exported6 captures mean1.588693/std0.001439, NOT an actual new FL GUI export and NOT a reference/v83 match. Its physical Diva remains OscMix6.3, PW KeyFollow+1, VCA ModDepth-58; only3 held notes per phrase, repeated twice. The new real28-case wider PW/KeyFollow screen was negative and is NOT adopted. See CURRENT_RESEARCH_AFTER_WIP10_RU.md and its dated proofs. Main corrected controller now rotates actual EQ76 coordinate search, controls with explicit SIDE level, scaled EQ76, controls. Each trial must pass independent full6+6; no training result is ready by itself.

IMPORTANT CURRENT CPU OWNERSHIP: run_extended_WS_finite.py owns fl20-corrected-search.pause while it waits for the active finite EQ fit to finish, then runs one real monotone WaveShaper curve experiment. Check FL20_EXTENDED_WS_FINITE_PROFILE.json AND FL20_CORRECTED_SEARCH_CONTROLLER.json, actual identities and child progress. While the finite curve job runs, the main controller is intentionally idle, not a dead task. Its finally releases ONLY its pause, then normal validated matching resumes. Source test and scaled profile are completed; their old PIDs are history. Extended WaveShaper coordinates are explicitly RESEARCH-ONLY, guarded from ordinary accept/start/export until all playback/export/restore consumers support them. Do not silently adopt an x95 candidate which also has waveshaper_curve_adjustment. New script generation must preserve actual Chorus overrides and audited physical source manifest. Old native-search.stop stays. No16-note transcription, no MistaTowa, no original-derived playback, no new PC control/FL GUI claims. User authorized useful research Git backups and full kits; keep working and do not ask per-trial questions. All Git pause/flock protections below remain mandatory; no worktrees without explicit request.

'''
        private=R/'start_skill_current.md';private.write_text(header+private.read_text(),encoding='utf-8');shutil.copyfile(private,base/'start_skill_current.md')
        files=sorted(p for p in d.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
        (d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n'for p in files))
        git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Continue WIP10 with real source controls, native coordinate fitting and guarded WaveShaper research')
        commit=git('rev-parse','HEAD');assert protected()==old
        assert all(git('rev-parse','HEAD:'+p)==v for p,v in retained.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        checks=[]
        for rel in ['CURRENT_RESEARCH_AFTER_WIP10_RU.md','scripts/probe_fl20_extended_WS.py','proofs/fl20-Diva-harmonic-source-03/completion.json']:
            path=d/rel;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/'+path.relative_to(P).as_posix()
            with urllib.request.urlopen(url,timeout=30)as response:data=response.read()
            assert data==path.read_bytes();checks.append(dict(path=rel,HTTP_byte_exact=True))
        receipt=dict(commit=commit,previous_HEAD=before,all_old_complete_kits_and_numbered_releases_preserved=True,HTTP_checks=checks,match_reached=False)
        (N/'WIP10_RESEARCH_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
