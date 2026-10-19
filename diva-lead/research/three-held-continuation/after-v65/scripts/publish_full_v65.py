"""Publish only the finished v65 kit and completed physical-probe evidence."""
from pathlib import Path
import datetime, fcntl, hashlib, json, os, re, shutil, subprocess, time, urllib.request

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/divalead')
RESEARCH = REPO / 'diva-lead/research/three-held-continuation'
BUILD = ROOT / 'v65-build'
ARCHIVES = Path('/tmp/divalead-source-current65-archives')
DEST = RESEARCH / 'after-v65'
PAUSE = ROOT / 'auto-backup.pause'

def git(*args):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', *args], cwd=REPO, text=True).strip()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def immutable_copy(source, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
    except OSError:
        shutil.copyfile(source, target)
    assert sha(source) == sha(target)
    return str(target)

assert json.loads((BUILD/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
zip_proof = json.loads((BUILD/'ZIP-proof.json').read_text())
assert zip_proof['clean_extraction_release_replay_passed'] and zip_proof['byte_exact_DLL_rebuild']
assert sha(BUILD/'Diva_lead_v65_WIP_checkpoint.zip') == zip_proof['ZIP_SHA256']
assert json.loads((ARCHIVES/'manifest.json').read_text())['all_cases_preserved_losslessly']
assert not PAUSE.exists()
write(PAUSE, dict(owner='publish-full-v65', UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(50):
    state = json.loads((ROOT/'auto-backup-state.json').read_text())
    if state['phase'] == 'paused_for_manual_Git_work':
        break
    time.sleep(1)
else:
    raise RuntimeError(state)

with (ROOT/'auto-backup-Git.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    assert not git('status', '--porcelain')
    parent = git('rev-parse', 'HEAD')
    assert git('ls-remote', 'origin', 'refs/heads/main').split()[0] == parent
    old = {str(i): dict(tree=git('rev-parse', f'HEAD:diva-lead/v{i}-wip'),
                        ZIP=git('rev-parse', f'HEAD:Diva_lead_v{i}_WIP_checkpoint.zip')) for i in range(57,65)}
    assert not DEST.exists() and not (REPO/'diva-lead/v65-wip').exists()
    shutil.copytree(BUILD/'v65-wip', REPO/'diva-lead/v65-wip', copy_function=immutable_copy)
    immutable_copy(BUILD/'Diva_lead_v65_WIP_checkpoint.zip', REPO/'Diva_lead_v65_WIP_checkpoint.zip')
    DEST.mkdir()
    for name in ['clean-ZIP-Windows-proof.json', 'ZIP-proof.json', 'clean-extraction-proof.json',
                 'fresh-source-proof.json', 'release-proof.json', 'spectral-proof.json', 'selected-basis.json']:
        immutable_copy(BUILD/name, DEST/('v65-'+name))
    (DEST/'source-probes').mkdir()
    for path in ARCHIVES.iterdir():
        if path.is_file():
            immutable_copy(path, DEST/'source-probes'/path.name)
    for name in ['source-current65-rescore.json', 'source-current65-control/completed.json']:
        immutable_copy(ROOT/name, DEST/'source-probes'/Path(name).name)
    (DEST/'scripts').mkdir()
    for name in ['build_three_v65.py','write_v65_docs.py','finalize_v65.py','verify_zip_windows_v65.py',
                 'run_full_v65_build.py','source_current65.py','run_source_current65.py',
                 'rescore_source_current65.py','archive_source_current65.py','publish_full_v65.py',
                 'deduplicate_completed_historical_sources.py','deduplicate_completed_three_sources.py',
                 'fit_three_balance42.py','prepare_pw5190_source.py','run_pw5190_source_preparation.py',
                 'repair_pw5190_balance.py','run_pw5190_balance_repair.py',
                 'auto_backup_three.py','start_three_services.py']:
        immutable_copy(ROOT/name, DEST/'scripts'/name)
    full = json.loads((BUILD/'v65-wip/verification/selected_validation.json').read_text())
    current = json.loads((REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
    current = {k: (v.replace('v64','v65').replace('V64','V65') if isinstance(v,str) else v) for k,v in current.items()}
    current.update(ZIP_SHA256=zip_proof['ZIP_SHA256'],
                   DLL_SHA256=sha(BUILD/'v65-wip/Diva_Lead_Finish_v65_WIP_x64.dll'),
                   research_model='diva-lead/research/three-held-continuation/after-v65',
                   score=full['score'], tone_score=full['tone_score'],
                   AB_previous_current='diva-lead/v65-wip/AB_REFERENCE_V64_V65_WIP.wav',
                   AB_MP3='diva-lead/v65-wip/AB_REFERENCE_V64_V65_WIP.mp3')
    write(REPO/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json', current)
    pointer = json.loads((RESEARCH/'CURRENT_THREE_NOTE_MODEL.json').read_text())
    pointer.update(selected_complete_release='diva-lead/v65-wip',
                   selected_complete_release_tone_score=full['tone_score'],
                   selected_complete_release_score=full['score'],
                   latest_research_is_not_a_new_complete_DLL_release=pointer['tone_score'] < full['tone_score']-1e-9)
    write(RESEARCH/'CURRENT_THREE_NOTE_MODEL.json', pointer)
    (DEST/'README.md').write_text('''# Продолжение трёхнотного лида: полный v65 WIP

[Полный комплект v65](../../../v65-wip/README.md), [ZIP](../../../../Diva_lead_v65_WIP_checkpoint.zip), [инструкция FL Studio](../../../v65-wip/FL_STUDIO_RU.md), [оригинал → v64 → v65](../../../v65-wip/AB_REFERENCE_V64_V65_WIP.mp3): 0 / 4,168 / 8,336 с.

Сохранены выбранный исходный пресет Diva, все 281 параметр и три удержания на фразу: два прохода, шесть note-on. Работает внутренний ARP Diva. Полный комплект фиксирует доказанный вариант balance-power-0011-balance42, ошибка тембра 0,8163707817; это ошибка измерения, не процент сходства. Точное совпадение не достигнуто. Регрессии отдельных критериев приведены в таблице полного комплекта.

Настоящая Diva, Windows DLL, полная независимая цепочка собственной NEW-базы, отдельный fixture, 12 причинных случаев на четырёх частотах, блоки, API/FXP/состояние/PDC, точная пересборка, чистая распаковка и фактический WAV DLL из ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. Лицензионная Diva не включена. v57–v64 и их ZIP сохранены.

`source-probes/` сохраняет все 32 настоящих рендера Diva: контроль и 31 изменение ширины импульса, смеси осцилляторов, резонанса, частоты фильтра и реверберации. Для каждого есть пресет, все 281 параметр, 12 MIDI-событий, сырой WAV, обработанный WAV и повторный расчёт с более свежим Finish. Четыре gzip/tar-архива проверены распаковкой и SHA каждого участника; соответствие указано в manifest.json. Ни одна из этих исходных проб не прошла все прежние ограничения, поэтому новая физическая настройка не включена в v65. Отдельная коррекция перспективного PW51.90 исследуется и публикуется только после собственной полной проверки.

[Автоматические проверенные WAV после v64](../after-v64/auto-checkpoints/README.md) продолжают пополняться; их A/B использует v64 как фиксированный контроль. [Текущая исследовательская основа](../CURRENT_THREE_NOTE_MODEL.json) отдельно указывает полный DLL-комплект. Промежуточная публикация не завершает подбор.

`scripts/` — точные программы этого этапа. Одноразовые build/stage/probe-программы используют заданные пути и номера; не запускать их вслепую в новой среде. Настройка текущей среды и идемпотентный запуск продолжающих служб описаны в runtime-support автоматических бэкапов. При редактировании разделяемых неизменных файлов сначала создать независимую копию; инструменты экономии места не меняют пути или байты.
''')
    root_readme = REPO/'README.md'
    old_text = root_readme.read_text()
    archive = old_text[old_text.index('**Архивный исследовательский этап:**'):]
    root_readme.write_text('''# Diva: реконструкция лида для FL Studio

Работаем с выбранными тремя длинными нотами на фразу: MIDI 41 → 37 → 36. Повторы и октавы создаёт внутренний ARP Diva. Пресет, все 281 параметр и MIDI сохранены.

**[Полный v65 WIP](diva-lead/v65-wip/README.md)** — [скачать ZIP](Diva_lead_v65_WIP_checkpoint.zip), [инструкция FL Studio](diva-lead/v65-wip/FL_STUDIO_RU.md). Пресет, трёхнотный MIDI, Finish Windows x64 VST2, готовые WAV, исходники и завершённые проверки.

**[Оригинал → v64 → v65](diva-lead/v65-wip/AB_REFERENCE_V64_V65_WIP.mp3)**: 0 / 4,168 / 8,336 с. [WAV сравнения](diva-lead/v65-wip/AB_REFERENCE_V64_V65_WIP.wav), [отдельный готовый WAV](diva-lead/v65-wip/Diva_Lead_v65_REFERENCE_EDIT.wav), [измерения и регрессии](diva-lead/v65-wip/COMPARISON_RU.md).

Ошибка тембра уменьшилась с 0,8213477353 у v64 до 0,8163707817 у v65. Это измерения, не проценты сходства. Точное совпадение ещё не достигнуто. [Исследование и 32 реальные пробы Diva](diva-lead/research/three-held-continuation/after-v65/README.md), [текущая основа](diva-lead/research/three-held-continuation/CURRENT_THREE_NOTE_MODEL.json).

Свежая Diva, Windows DLL, подходящая собственная NEW-база, 12 причинных случаев четырёх частот и фактическая DLL из чистого ZIP проверены. GUI FL Studio и прослушивание ассистентом не выполнялись. [Предыдущий полный v64](diva-lead/v64-wip/README.md).

[Автоматически обновляемые проверенные WAV и A/B](diva-lead/research/three-held-continuation/after-v64/auto-checkpoints/README.md). Расчёты и публикация завершённых проверок продолжаются после промежуточных комплектов. A/B в этих исследовательских снимках использует v64 как фиксированный контроль.

'''+archive)
    readme = RESEARCH/'README.md'
    text = readme.read_text()
    start = text.index('Полный проверенный промежуточный комплект:')
    end = text.index('\n\n## Что выполнено', start)
    readme.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v65](../../v65-wip/README.md), [FL Studio](../../v65-wip/FL_STUDIO_RU.md). [Оригинал → v64 → v65](../../v65-wip/AB_REFERENCE_V64_V65_WIP.mp3). [Новые подборы и проверки](after-v65/README.md), [продолжающиеся автоматические бэкапы](after-v64/auto-checkpoints/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Точное совпадение не достигнуто; подбор продолжается.'+text[end:])
    write(DEST/'checkpoint.json', dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                     selected_complete_release=current, source_trials=32,
                                     old_releases_57_to_64_immutable=True, match_reached=False))
    (DEST/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(DEST))+'\n' for p in sorted(DEST.rglob('*')) if p.is_file()))
    paths = ['README.md','Diva_lead_v65_WIP_checkpoint.zip','diva-lead/v65-wip',
             'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',str(DEST.relative_to(REPO)),
             str((RESEARCH/'CURRENT_THREE_NOTE_MODEL.json').relative_to(REPO)),str((RESEARCH/'README.md').relative_to(REPO))]
    git('add', '--', *paths)
    allowed = set(paths)
    staged = git('diff','--cached','--name-only').splitlines()
    assert staged and all(any(name==prefix or name.startswith(prefix+'/') for prefix in allowed) for name in staged)
    git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol',
        'diff','--cached','--check','--','.',':!*.tsv',':!*.log')
    git('commit','-m','Back up verified three-held Diva v65 and 32 physical source probes')
    for i, hashes in old.items():
        assert git('rev-parse', f'HEAD:diva-lead/v{i}-wip') == hashes['tree']
        assert git('rev-parse', f'HEAD:Diva_lead_v{i}_WIP_checkpoint.zip') == hashes['ZIP']
    commit = git('rev-parse','HEAD')
    assert git('ls-remote','origin','refs/heads/main').split()[0] == parent
    git('push','origin','HEAD:main')
    assert git('ls-remote','origin','refs/heads/main').split()[0] == commit
    verified = []
    for relative in ['Diva_lead_v65_WIP_checkpoint.zip','diva-lead/v65-wip/FL_STUDIO_RU.md',
                     'diva-lead/v65-wip/Diva_Lead_Finish_v65_WIP_x64.dll',
                     'diva-lead/v65-wip/AB_REFERENCE_V64_V65_WIP.mp3','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+relative, timeout=60) as response:
            content = response.read()
            assert response.status == 200
        assert content == (REPO/relative).read_bytes()
        verified.append(dict(path=relative, SHA256=hashlib.sha256(content).hexdigest(), byte_exact=True))
    assert not git('status','--porcelain')
    write(ROOT/'public-v65-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          commit=commit, remote_main_exact=True, HTTP_files=verified,
          older_57_to_64_trees_and_ZIPs_immutable=True, match_reached=False))
    assert json.loads(PAUSE.read_text())['owner']=='publish-full-v65'
    PAUSE.unlink()
    print('FULL_V65_PUSHED_AND_ACTUAL_HTTP_BYTES_VERIFIED', commit, full['tone_score'], flush=True)
