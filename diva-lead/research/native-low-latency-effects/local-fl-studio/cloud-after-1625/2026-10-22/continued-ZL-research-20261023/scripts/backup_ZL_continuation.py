"""Normal guarded Git backup of a verified new external-plugin WIP family."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,urllib.request
from win_vst3 import D
P=Path('/workspace/divalead');B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22'
ROOT=B/'FL20_ZL_02_WIP';LABEL='Diva_ZL_02_WIP';pause=R/'auto-backup.pause';OWNER='external-ZL-continued-research-and-onboarding-backup'
def read(p):return json.loads(Path(p).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():
    paths=[s.split('\t',1)[1]for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]
    result={'diva-lead/'+name:git('rev-parse','HEAD:diva-lead/'+name)for name in paths}
    for s in git('ls-tree','HEAD').splitlines():
        if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s):name=s.split('\t',1)[1];result[name]=git('rev-parse','HEAD:'+name)
    for p in list(PUBLIC.glob('WIP[0-9][0-9]'))+list(PUBLIC.glob('ZL-WIP*')):
        result[p.relative_to(P).as_posix()]=git('rev-parse','HEAD:'+p.relative_to(P).as_posix())
    for name in ['local-fl-studio/2026-10-22','after-DSP-arrival/checkpoint-WIP','after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']:
        rel=(BASE/name).relative_to(P).as_posix();result[rel]=git('rev-parse','HEAD:'+rel)
    return result
def copy_jsons(src,dest):
    dest.mkdir(exist_ok=False)
    for p in src.glob('*.json'):
        data=p.read_bytes()
        if len(data)>150000:
            packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(dest/(p.name+'.gz')).write_bytes(packed)
        else:shutil.copyfile(p,dest/p.name)
assert read(pause)['owner']==OWNER
assert read(R/'auto-backup-state.json')['phase']in ['paused_for_manual_Git_work','paused_low_workspace_space']
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
    before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/'continued-ZL-research-20261023';dest.mkdir(exist_ok=False)
    scripts=dest/'scripts';scripts.mkdir()
    for name in ['continue_ZL_matching.py','run_ZL_extra_dynamic_study.py','resume_ZL_joint_validation.py','backup_ZL_continuation.py','onboarding_ZL_append.sh']:
        p=D/name
        if p.suffix=='.py':compile(p.read_text(),str(p),'exec')
        shutil.copyfile(p,scripts/name)
    copy_jsons(D/'ZL-extra-dynamic-original-reference-01',dest/'extra-dynamic-finite')
    copy_jsons(D/'ZL-continuous65/cohort-0001',dest/'confirmed-private-cohort-0001')
    shutil.copyfile(D/'ZL-continuous65/cohort-0001/candidate-component.bin',dest/'confirmed-private-cohort-0001/candidate-component.bin')
    shutil.copyfile(D/'ZL-continuous65/INITIAL_STRICT_REPLAY_FAILURE.json',dest/'INITIAL_STRICT_REPLAY_FAILURE.json')
    for name in ['FL20_EXTERNAL_ZL_EXTRA_DYNAMIC_STUDY.json','FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_COMPLETED_ANALYSIS_AND_HOST_SCRATCH_CLEANUP.json','NUMBERED_RELEASE_EXACT_AUDIO_HARDLINK_DEDUP_20261023.json']:
        shutil.copyfile(N/name,dest/name)
    live=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');cohort=read(D/'ZL-continuous65/cohort-0001/completion.json')
    guide=f'''# Продолжение после ZL03: исследование, не новый готовый проект

Актуальный полностью упакованный результат остаётся [ZL03](../ZL03_CONTINUATION_RU.md).
Исследование двух дополнительных dynamic полос457trials/paired12 завершено:
1.505962→1.502129, SEM0.00007755. Ещё один65param cohort с paired6 подтвердил
**{cohort['current_control_mean']:.9f}→{cohort['candidate_mean']:.9f}**,
SEM{cohort['paired_difference_SEM']:.9f}. Это не полный новый FLP/ZIP и не
утверждение совпадения тембра. Компонент и метрики сохранены, все12 проверочных
WAV этой успешной когорты — в частном lossless archive с SHA receipt.

Дальнейший matcher продолжает по исходному критерию и трём входящим нотам,
используя реальный VST3. На момент снимка phase={live['phase']},
PID={live['owner']['PID']}, starttime={live['owner']['starttime']}.
Проверяйте реальные PID/starttime/current JSON; снимок не обещает вечную работу.
Скрипт заканчивает текущую конечную когорту перед stop-файлом и проверяет
фактические резервы root64MiB/tmp144MiB перед следующей. Полные новые публикации
требуют также места под ZIP/checkout/Git object. Старый native-only matcher
не выдаётся за вычисляющий, если он стоит на numeric pause/дисковом guard.

В строгой проверке второй когорты возник max2.328e−10, RMS2.908e−13 между
hot/cold состояниями, на уровне отдельного float32 ULP. Лог/ошибка сохранены,
компонент state должен совпадать по байтам. Новый guard5e−9 (нижеfloat32 fullscale
LSB) явно сохраняет реальную ошибку, а две НОВЫЕ холодные инстанции проверяются
отдельно. Ненулевой residual никогда не называется bit-exact. Это критерий
численной воспроизводимости, не ослабление сравнения с оригинальным звуком.

Скрипт продолжения: scripts/continue_ZL_matching.py. N/FL20_ZL_CONTINUOUS_CONTROLLER.json
и D/ZL-continuous65/BEST_CANDIDATE.json — текущие авторитетные пути в этой среде.
В BEST component.bin авторитетнее старых metadata массивов: перед новой упаковкой
или refit обязательно извлечь физические значения всех Peak/AllPass/dynamic полос
из фактического JUCE component XML/реального610-param dump. Не подавать такой
кандидат обычному native x95 exporter и не потерять4 dynamic bands.

Воспроизведение официального ZL runtime и onboarding append проверены внутри
новой папки текущей машины. Это не тест совершенно нового ПК или GUI FL Studio.
Новый setup append сохраняет старый setup, добавляет pinned официальный MSI,
компиляцию и реальную проверку PDC/импульса/компонента на синтетическом входе.
Никаких vendor binaries или секретов в этом бэкапе нет.
'''
    (dest/'README_RU.md').write_text(guide,encoding='utf-8')
    header=f'''BEGIN_CURRENT_ZL_MATCHING_CONTINUATION
LATEST COMPLETE PUBLIC RESULT REMAINS ZL03. Follow-up research has4dynamic bands. Extra finite457cases/paired12 gave1.505962->1.502129; continuous cohort1/paired6 gave{cohort['current_control_mean']:.9f}->{cohort['candidate_mean']:.9f}, all12WAV archived losslessly. This private extra improvement is not a complete new FLP. Read local-fl-studio/cloud-after-1625/2026-10-22/continued-ZL-research-20261023/README_RU.md after ZL03 guide. Exact original-reference match not reached. Only3externalheldnotes per phrase twice/internalARP unchanged, no MistaTowa. Native16 latest STOCK-only. No new FL GUI or human audition claim.

ACTUAL CURRENT CONTROLLER: N=/workspace/divalead-work/native-low-latency-effects, D=/tmp/divalead-local-1625/internet-plugins-20261023. Read N/FL20_ZL_CONTINUOUS_CONTROLLER.json, verify actual PID/starttime/cmdline plus real VST3 hosts. Snapshot PID{live['owner']['PID']}/starttime{live['owner']['starttime']}/phase{live['phase']}, not permanent PID evidence. Source and12native effects unchanged. continue_ZL_matching.py uses65physicalparams for12staticPeak+2AllPass+4dynamicPeak+OutputGain, real four workers, each cohort3fresh native frozen realizations, train+2heldouts+6freshpaired, real component resave and a second cold instance, immutable compressed full validation WAV archive for each robust improvement. N/zl-continuation.stop finishes current finite cohort then stops; actual root64MiB/tmp144MiB guards end next iterations cleanly. Owned numeric pause external-ZL-continuous65-refinement excludes old native matching; release only own pause after ending. No duplicate controller/watcher. Existing native main/watcher may be paused by actual reserve, never say they compute then.

NUMERICAL REPLAY: initial overly strict second-cohort assertion caught max2.328e-10,RMS2.908e-13 at a rare float32 ULP. Original failure preserved. Active component state bytes must be exact; numerical audio tolerance5e-9 is explicit and belowfloat32fullscaleLSB. Also compare two genuinely NEW cold instances and record actual error/bitexact boolean. Never rename a nonzero error bit-exact, never change reference criteria to hide differences. ZL03's own all3container and wholezero-depth actual replay was bit-exact. Further private component state is authoritative: arrays in inherited metadata can be stale! Reextract allphysicalparams from actual JUCE component XML and610readbacks before new refit/export. Keep unsupported topology guard; no ordinary x95 export losingZL or dynamic bands.

ONBOARDING: scripts/onboarding_ZL_append.sh adds official pinned ZL1.4.1 MSI extraction/build plus actual state/PDC/impulse check to existing setup; bash syntax and same commands against independently rebuilt runtime passed. This is current-machine validation, not an independently new environment. Repo/config draft must pin exact final actual HEAD from complete workspace discovery; saving draft does not Publish. Preserve network/secrets/runtime bindings. User authorizes downloaded FL20-compatible online FX and full Git backups. All complete-kit tree OIDs and numbered releases must remain immutable; original reference only analysis input.
END_CURRENT_ZL_MATCHING_CONTINUATION

'''
    p=R/'start_skill_current.md';s=p.read_text();s=re.sub(r'BEGIN_CURRENT_ZL_MATCHING_CONTINUATION\n.*?END_CURRENT_ZL_MATCHING_CONTINUATION\n\n','',s,flags=re.S);p.write_text(header+s);shutil.copyfile(p,BASE/'start_skill_current.md')
    link='[Продолжение поиска после полного ZL03](continued-ZL-research-20261023/README_RU.md).\n\n';p=PUBLIC/'README_RU.md';p.write_text(link+p.read_text(),encoding='utf-8')
    files=sorted(p for p in PUBLIC.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(PUBLIC/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUBLIC).as_posix()+'\n'for p in files))
    git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
    assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
    git('commit','-m','Preserve continued real VST3 matching, numerical replay audit and tested ZL setup');commit=git('rev-parse','HEAD')
    assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
    subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
    (N/'LATEST_ZL_CONTINUED_RESEARCH_PUBLICATION.json').write_text(json.dumps(dict(commit=commit,previous_HEAD=before,all_complete_versions_preserved=True,reference_match_reached=False),indent=2)+'\n')
    print('CONTINUED_ZL_RESEARCH_BACKED_UP',commit,flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
