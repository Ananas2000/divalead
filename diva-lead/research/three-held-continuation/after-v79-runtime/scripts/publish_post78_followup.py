"""Publish closed finite experiments and preserve exact setup configuration context."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');O=P/'diva-lead/research/three-held-continuation/after-v79-runtime'
OWNER='publish-post78-closed-followup';PAUSE=R/'auto-backup.pause'
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=P,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy(a,b):b=Path(b);b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);assert sha(a)==sha(b)
stage=json.loads((R/'post78-followup-stage.json').read_text());assert stage['phase']=='all_finite_jobs_closed_and_shape_archives_verified' and not stage['shape_source_requires_new_matching_own_NEW_full_proof']
assert json.loads((P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())['version']=='v79-wip'
scripts=['publish_post78_followup.py','prepare_post78_followup.py','probe_source_post78_shapes.py','run_source_post78_shapes.py','verify_post78_shape_screens.py','archive_post78_shape_screens.py','verify_post77_physical_screens.py','prune_more_obsolete_caches.py','start_three_services.py','auto_backup_three.py','refresh_post74_startup_guide.py','summarize_current_three_variants.py','discover_workspace_projects.py']
diags=['post78-followup-stage.json','post78-shape-parameter-checks.json','post77-physical-screen-parameter-checks.json','post78-obsolete-cache-cleanup.json','post78-obsolete-cache-cleanup-plan.json','post78-exact-sharing-summary.json','post77-runtime-public-verification.json','post77-runtime-config-readback-complete.json','source-post77coupled-state.json','source-post78-shapes-state.json','post77-cleaner-hf100-state.json','post77-cleaner-alternative-state.json','current-three-note-variant-registry.json','public-v79-verification.json','v79-FL-instruction-file-checks.json']
scripts.extend(['probe_source_post78_dual.py','run_source_post78_dual.py','verify_post78_dual_screens.py','archive_post78_dual_screens.py'])
scripts.append('make_post78_quieter_comparison.py')
diags.extend(['source-post78-dual-state.json','post78-dual-parameter-checks.json'])
for name in scripts+diags:assert (R/name).is_file(),name
archives=Path('/tmp/divalead-post78-shapes-physical-archives');manifest=json.loads((archives/'manifest.json').read_text())
for row in manifest['archives']:assert sha(archives/row['file'])==row['SHA256']
dual_archives=Path('/tmp/divalead-post78-dual-physical-archives');dual_manifest=json.loads((dual_archives/'manifest.json').read_text())
for row in dual_manifest['archives']:assert sha(dual_archives/row['file'])==row['SHA256']
assert json.loads((R/'source-post78-dual-state.json').read_text())['slot_released']
comparison=Path('/tmp/divalead-post78-quieter-comparison');assert (comparison/'comparison.json').is_file()
assert not O.exists()
while True:
    try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:time.sleep(2);continue
    with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
    break
try:
    for _ in range(90):
        state=json.loads((R/'auto-backup-state.json').read_text())
        if state['phase']=='paused_for_manual_Git_work':break
        time.sleep(1)
    else:raise RuntimeError(state)
    with (R/'auto-backup-Git.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
        before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
        protected={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
        protected.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
        for name in scripts:copy(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
        for name in diags:copy(R/name,O/'diagnostics'/name)
        copy(R/'start_skill_current.md',O/'start_skill_current.md')
        for path in archives.iterdir():
            if path.is_file():copy(path,O/'physical-shape-screen-archives'/path.name)
        for path in dual_archives.iterdir():
            if path.is_file():copy(path,O/'physical-dual-screen-archives'/path.name)
        shutil.copytree(comparison,O/'quieter-comparison')
        # Only the completed finite attempts are copied here; live normal rounds remain private.
        script=R/'auto_backup_three.py';ns={'__file__':str(script),'__name__':'closed_post78_snapshot'};exec(compile(script.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(script),'exec'),ns)
        for name in ['post77-coupled135-research','post77-cleaner-hf100-research']:
            source=R/name;ns['snapshot'](source,O/'completed-numeric-research'/name)
            scratch=Path(json.loads((source/'numeric-location.json').read_text())['numeric_scratch'])
            ns['snapshot'](scratch,O/'completed-numeric-research'/name/'numeric')
        alternative=R/'post77-cleaner-hf100-alternative-numeric'
        if alternative.exists():ns['snapshot'](alternative,O/'completed-numeric-research'/alternative.name)
        copy(R/'source-post77coupled-control/probe.log',O/'completed-numeric-research/coupled135.log')
        models=[]
        for path,d,family,basis in ns['choices']():
            if 'post77' in path.parent.name:models.append(dict(private_validation=str(path),tone_score=d['tone_score'],upper_off_error=d['metrics']['upper_off'],all_original_guards_and_fresh_source_and12_cases_checked=True,quieter_alternative_not_primary=d.get('quieter_alternative_not_claimed_primary_tone_improvement',False)))
        write(O/'completed-proof-references.json',models)
        (O/'README_RU.md').write_text('''# Завершённые дополнительные опыты после v78

[Полный v79](../../../v79-wip/README.md), [FL Studio](../../../v79-wip/FL_STUDIO_RU.md), [оригинал → v79](../../../v79-wip/AB_REFERENCE_V79_WIP.wav), наш вариант с 4,168 с. Точное совпадение ещё не достигнуто.

Здесь сохранены законченный совместный поиск существующих 93 гармонических и 42 стереокоэффициентов, попытка уменьшить остаток между верхними гармониками с дополнительным более строгим ограничением и все новые реальные пробы форм волн осцилляторов. Три удерживаемые ноты, MIDI, ARP и огибающие сохранены. Проверены фактические 281-параметрические дампы и MIDI-логи. В архивах — все исходные/обработанные WAV и пресеты этих проб, с SHA256 распакованных членов.

13 проб Shape1/Shape2 показали побитово одинаковый сырой звук: эти регуляторы не действуют у выбранного Dual VCO. Следующие 13 проб проверяли уже активные переключатели его волн и настройки Ladder. Улучшения при соблюдении всех исходных ограничений они не дали; источник сохранён. Отрицательная проба Feedback −0,01 была ограничена самой Diva до 0,00 и отмечена в проверке параметров; она не считается изменившим звук пресетом.

Численные журналы и их завершение сами по себе не являются принятым звуком. Полные доказательства перечислены отдельно и опубликованы автоматическим контроллером. Более тихий по остаточной метрике вариант, если он прошёл проверку, явно отмечается как компромисс, а не новый главный победитель по тембру. Не прошедшие все исходные ограничения пробы не становились релизами. Допуски, число состояний DSP и задержка не расширялись.

Все временно занятые CPU-слоты возвращены исходным контроллерам; обычный трёхнотный подбор и автоматические бэкапы продолжаются. Состояния и лучший результат в этом каталоге являются снимками: текущие JSON среды и CURRENT_THREE_NOTE_MODEL.json имеют приоритет.

Дополнительная очистка касается только тяжёлых генерируемых файлов ещё 65 худших старых шестнадцатинотных кэшей; модели, исходники и оценки сохранены. Все номерные версии и текущие трёхнотные доказательства сохранены. GUI FL Studio, субъективное прослушивание ассистентом и восстановление среды в новой задаче не проверялись. Лицензионная Diva не включена; MistaTowa не используется.
''')
        target=str(O.relative_to(P));git('add','--',target)
        assert all(p.startswith(target+'/') for p in git('diff','--cached','--name-only').splitlines())
        git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
        git('commit','-m','Preserve completed three-note coupled, cleaner and oscillator-shape research after v79')
        assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items())
        head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
        for name in ['README_RU.md','start_skill_current.md','scripts/start_three_services.py','physical-shape-screen-archives/'+manifest['archives'][0]['file']]:
            data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes()
        assert not git('status','--porcelain')
        write(R/'post78-followup-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_and_HTTP_byte_exact=True,all_numbered_releases_unchanged=True,all_finite_jobs_completed_and_slots_released=True,all_shape_trials_archived=True,match_reached=False))
        subprocess.run(['/workspace/.venvs/divalead/bin/python','-B',str(R/'discover_workspace_projects.py'),'post78-followup-checkout-discovery.json'],check=True)
        write(R/'post78-followup-ready-for-config.json',dict(commit=head,owner=OWNER,lock_held=True));print('POST78_CLOSED_FOLLOWUP_PUSHED_READY_FOR_CONFIG',head,flush=True)
        end=time.monotonic()+180
        while time.monotonic()<end and not (R/'post78-followup-config-readback-complete.json').exists():time.sleep(2)
finally:
    if PAUSE.exists() and json.loads(PAUSE.read_text()).get('owner')==OWNER:PAUSE.unlink()
    print('CLOSED_FOLLOWUP_OWN_PAUSE_AND_GIT_LOCK_RELEASED',flush=True)
