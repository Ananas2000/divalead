"""Back up verified cloud-after-local research under the shared Git writer lock."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
N=Path('/workspace/divalead-work/native-low-latency-effects');W=Path('/tmp/divalead-native-effects')
B=Path('/tmp/divalead-local-1625');base=P/'diva-lead/research/native-low-latency-effects'
dest=base/'local-fl-studio/cloud-after-1625/2026-10-22'
owner='corrected-FL20-Chorus-context-research';pause=R/'auto-backup.pause'
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():
    return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
    deadline=time.monotonic()+90
    while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
        assert time.monotonic()<deadline;time.sleep(1)
    with (R/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        assert not git('status','--porcelain')
        subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True)
        subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
        before=git('rev-parse','HEAD');old=protected()
        retained={k:git('rev-parse','HEAD:'+k)for k in [
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP',
            'diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip',
            'diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22']}
        dest.mkdir(parents=True,exist_ok=False);scripts=dest/'scripts';scripts.mkdir();proofs=dest/'proofs';proofs.mkdir()
        for name in ['fl_native_fl20_host.c','fl_native_host_context_diag.c','fl_native_probe.c']:
            shutil.copyfile(B/'tools'/name,scripts/name)
        for name in ['fl20_objective.py','fit_fl20_EQ76.py','fit_fl20_EQ76_with_shapes.py',
            'repro_cloud_1625.py','probe_host_context.py','isolate_Chorus_warm.py',
            'verify_fl20_host.py','render_local05_sources.py','calibrate_Chorus_io_correct_units.py',
            'build_Chorus_mix_diagnostics.py','probe_Chorus_shapes_correct_context.py',
            'publish_corrected_context_research.py']:
            shutil.copyfile(B/name,scripts/name)
        shutil.copyfile(W/'native_fst.py',base/'after-DSP-arrival/scripts/native_fst.py')
        shutil.copyfile(B/'restore_checkpoint_fixed.py',base/'local-fl-studio/tools/restore_checkpoint.py')
        for name in ['FL20_FST_SERIALIZATION_PROOF.json','Chorus-toggle-native-mapping.json',
            'Chorus-WetOnly-actual-values.json','fresh-Diva04-05/PROOF.json',
            'fresh-Diva04-05/source_manifest.json','fl20-host-verification-01/PROOF.json',
            'Chorus-io-calibration-02/RESULTS.json','Chorus-warm-isolation-01/RESULTS.json',
            'host-context-screen-01/RESULTS.json','host-context-screen-01/completion.json']:
            out=proofs/name;out.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(B/name,out)
        for family in ['reproduction','fl20-EQ76-bounded-integration-01','fl20-EQ76-full-01','Chorus-shapes-correct-context-01']:
            folder=proofs/family;folder.mkdir()
            for p in (B/family).glob('*.json'):
                if p.stat().st_size>200000:
                    data=p.read_bytes();packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data
                    (folder/(p.name+'.gz')).write_bytes(packed)
                else:shutil.copyfile(p,folder/p.name)
        shutil.copytree(B/'FL-Chorus-diagnostic-projects',dest/'FL-Chorus-diagnostic-projects')
        actual=json.loads((B/'restore-fixed-check/sessions/2026-10-22/assessment/LOCAL_COMPARISON.json').read_text())[0]
        assert abs(actual['score']-2.2474370787947078)<1e-10
        (proofs/'RESTORE_HELPER_VERIFICATION.json').write_text(json.dumps(dict(
            fixed_reference_relative_path='analysis-runtime/diva-lead/v55-wip/Diva_original_lead_reference.wav',
            fixed_helper_executed_against_full_checkout=True,new_destination_used=True,
            subsequent_unchanged_local_assessment_executed=True,actual_assessment=actual,
            original_reference_used_only_for_analysis=True,reference_match_reached=False),indent=2)+'\n')
        state=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source='actual local FL05 Diva state, VCA ModDepth -58',
            context='Chorus bypassed only during silent pre-roll; other nodes retain warm128',
            old_cloud_controller_stopped=True,old_objective_not_comparable=True,
            only_three_held_notes_per_phrase=True,two_phrases=True,actual_FL_GUI_validation_pending=True,
            current_complete_candidate='proofs/Chorus-shapes-correct-context-01/full-validated-candidate.json',
            best_completed_fresh_objective=1.7079473518454165,previous_fresh_control=1.737162015630197,
            full_EQ_refit_after_new_Chorus_shapes_running=True,reference_match_reached=False)
        (dest/'CURRENT_CORRECTED_FL20_STATE.json').write_text(json.dumps(state,indent=2)+'\n')
        (dest/'README_RU.md').write_text('''# Облачное продолжение после локального handoff 16:25

Полного совпадения нет. Проверенный на ПК FL05 и все номерные релизы сохранены.
Новые кандидаты здесь проверяются настоящими Diva и native DLL, но ещё требуют
контрольного экспорта в реальной FL Studio. WAV тестового хоста нельзя называть
экспортом FL или доказательством полного переноса.

## Исправленный контекст Chorus

Прежний offline-хост пропускал 128×512 нулевых кадров через Chorus до первой ноты,
сдвигая его LFO на 1.36533 с. Новый fl_native_fl20_host.c исключает только Chorus
из этого прогрева; остальные эффекты получают прежний прогрев. Bypass до прогрева
восстанавливается. Исходный хост сохранён. Старый облачный подбор остановлен.

С отключённым Chorus Wine-рендер побитно совпал с переданным Windows-native WAV.
Двенадцать новых полных рендеров с исправленным запуском дали mean full score
1.811409, tone 1.745196 против реальных FL04 1.814036 / 1.748587.
Расстояние признаков до actual FL04 сократилось с ~0.00953 до ~0.00218.
Это близость тестового окружения, а не доказанное побитное совпадение с FL.
Bypass и zero-depth controls старого/нового хостов побитно одинаковы.

WetOnly включается raw1024, а не raw1. При нулевой глубине в изолированном
native Chorus измерено full=0.7×dry+wet_only с max residual 1.5e-8.
In-place/два отдельных dest-буфера дали одинаковые отсчёты. Закон Mix реальной
FL ещё не измерен; четыре минимальных диагностических FLP сохранены отдельно.

## Подбор

Физически заново запущен Diva FL05: all281 совпали с локальным TSV, 12 MIDI
событий сохранены; два независимых raw-рендера побитно одинаковы. Исходник
отличается от v83 по PWModDepth +1 и VCA ModDepth -58; ARP и ADSR сохранены.

Критерий теперь использует прежние полные local original-reference metrics:
0.65×tone+0.35×standard+0.05×abs(log(ABgain))+clip penalty, плюс малый EQ L2.
Его значения нельзя сравнивать со старой cloud transfer/proxy loss.
6580 полных actual-DLL EQ-evaluations, затем 6+6 новых полных рендеров:
1.762394→1.737264, standard error 0.000430; улучшение подтверждено.
После этого 141 вариант LFO shapes/crossover: отдельный свежий контроль
1.737162→1.707947, standard error 0.000636, ещё 6+6 рендеров.
Сейчас refit EQ под новые Chorus shapes продолжается.

Новые shapes записаны в chorus_overrides. Вектора x95 недостаточно:
после apply(x) обязательно применить и проверить readback этих overrides.
Только три длинные входящие ноты на фразу (две фразы), pitch movement — ARP.
Оригинальный WAV используется для анализа и A/B, не как материал синтеза.

## Проверенные исправления сохранения

Mixer FST writer теперь завершает каждый слот event98 и ставит zero-based
slot index в wrapper212. Четыре baseline FST побитно совпали с исправленными
пресетами, которые реально открывались в локальной FL20. Старый checkpoint-WIP
не переписан; его старые mixer FST требуют compatible-presets из локальной
папки 2026-10-22. Новый GUI-сеанс в облаке не заявляется.

restore_checkpoint.py исправлен: original reference нужен в
analysis-runtime/diva-lead/v55-wip, без лишнего research/. Helper реально
выполнен в новой папке; assessment после восстановления повторил score
2.2474370788 и tone 2.5189500318 на переданном FL bypass WAV.

## Воспроизведение и продолжение

Нужен полный checkout, штатные лицензированные DLL и настроенные Wine/MinGW
из after-DSP-arrival. Сначала tools/restore_checkpoint.py --destination NEW,
затем восстановить runtime в /tmp/divalead-local-1625/runtime. Исследовательские
скрипты содержат исходные абсолютные пути для этой среды. Не запускать их
в существующие каталоги результатов: они специально требуют новый ROOT.

Сборка нового C-хоста рядом с fl_native_probe.c:
`x86_64-w64-mingw32-gcc -O3 -static-libgcc -DFL_PRESET_GRAPH -DCOMMON_PHASE_PAIR -o fl_native_fl20_host.exe fl_native_fl20_host.c -lole32 -luuid -lm`
Не включать RELOAD_CHORUS_STATE: он сбрасывает параметры кандидатов.
Проверки/полные таблицы в proofs; большие JSON сжаты gzip без потери байтов.
Проприетарных DLL/EXE в этом бекапе нет. declared PDC0 не означает нулевую
задержку звуковой карты. Следующий шаг — refit, WAV/FLP WIP и независимый
контроль, после него — дальнейшая подгонка самого тембра.
''',encoding='utf-8')
        pointer=base/'CLOUD_AFTER_LOCAL_1625_RU.md'
        pointer.write_text('''# Актуальное облачное продолжение

После локального FL05 найдено расхождение в прогреве Chorus и проверен новый
тестовый хост. Подбор продолжается с реальным FL05-источником и тремя нотами.
[Результаты, проверки и продолжение](local-fl-studio/cloud-after-1625/2026-10-22/README_RU.md).
Полного совпадения нет. Старый cloud controller остановлен; его прежняя loss
несопоставима с новым критерием. Локальный FL05 сохранён.
''',encoding='utf-8')
        files=sorted(p for p in dest.rglob('*')if p.is_file())
        (dest/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix()+'\n'for p in files))
        assert not any(p.suffix.lower()in ['.dll','.exe','.rar']for p in dest.rglob('*')if p.is_file())
        git('add','--','diva-lead/research/native-low-latency-effects')
        git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
        assert all(s.startswith('diva-lead/research/native-low-latency-effects/')for s in git('diff','--cached','--name-only').splitlines())
        git('commit','-m','Correct silent Chorus pre-roll, reproduce local FL05 and validate fresh native timbre improvements')
        commit=git('rev-parse','HEAD');assert protected()==old
        assert all(git('rev-parse','HEAD:'+k)==v for k,v in retained.items())
        subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
        assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
        checks=[]
        for rel in ['CLOUD_AFTER_LOCAL_1625_RU.md','local-fl-studio/cloud-after-1625/2026-10-22/README_RU.md','after-DSP-arrival/scripts/native_fst.py']:
            p=base/rel;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/diva-lead/research/native-low-latency-effects/{rel}'
            with urllib.request.urlopen(url,timeout=30)as response:data=response.read()
            assert data==p.read_bytes();checks.append(dict(path=rel,HTTP_byte_exact=True))
        receipt=dict(commit=commit,previous_HEAD=before,main_remote_matches=True,clean_worktree=True,
            numbered_releases_old_native_kit_and_actual_local_FL05_unchanged=True,HTTP_checks=checks,match_reached=False)
        (N/'CORRECTED_CONTEXT_RESEARCH_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt),flush=True)
finally:
    if pause.exists()and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
