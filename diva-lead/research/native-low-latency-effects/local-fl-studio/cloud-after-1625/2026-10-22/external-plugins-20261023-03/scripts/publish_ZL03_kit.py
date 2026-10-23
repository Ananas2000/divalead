"""Normal guarded Git backup of a verified new external-plugin WIP family."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,urllib.request
from win_vst3 import D
P=Path('/workspace/divalead');B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22'
ROOT=B/'FL20_ZL_03_WIP';LABEL='Diva_ZL_03_WIP';pause=R/'auto-backup.pause';OWNER='external-ZL03-complete-kit-and-research-backup'
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
    before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/'ZL-WIP03';dest.mkdir(exist_ok=False)
    report=read(ROOT/'verification/ZL_FULL_VERIFICATION.json');proof=read(ROOT/'verification/ZIP_ACTUAL_REPLAY_PROOF.json')
    assert len(proof['all12_native_saved_states_exact'])==12 and proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']
    for name in [LABEL+'.flp',LABEL+'_complete_WIP.zip','AB_REFERENCE_ZL03_WIP.mp3','FL_STUDIO_RU.md','README_RU.md']:
        src=B/name if name.endswith('.zip')else ROOT/name;shutil.copyfile(src,dest/name)
    (dest/'verification').mkdir()
    for p in (ROOT/'verification').iterdir():
        if p.is_file()and p.suffix.lower()!='.wav':shutil.copyfile(p,dest/'verification'/p.name)
    research=PUBLIC/'external-plugins-20261023-03';research.mkdir(exist_ok=False);scripts=research/'scripts';scripts.mkdir()
    for name in ['run_ZL_dynamic_study.py','run_ZL_joint_refinement.py','resume_ZL_joint_validation.py','run_ZL_extra_dynamic_study.py','build_ZL03_kit.py','finalize_ZL03_kit.py','publish_ZL03_kit.py','setup_ZL_runtime.py','fl20_vst3_state.py','win_vst3.py','vst3_effect_host.c']:
        p=D/name
        if p.suffix=='.py':compile(p.read_text(),str(p),'exec')
        shutil.copyfile(p,scripts/name)
    copy_jsons(D/'ZL-joint-static-dynamic-original-reference-01',research/'ZL-joint-static-dynamic-original-reference-01')
    raw_log=(D/'ZL-joint-coordinator.log').read_bytes();(research/'ORIGINAL_JOINT_RUN_AND_STRICT_TAIL_ASSERTION.log.gz').write_bytes(gzip.compress(raw_log,mtime=0));shutil.copyfile(D/'onboarding_ZL_append.sh',scripts/'onboarding_ZL_append.sh');shutil.copyfile(D/'ZL-runtime-bootstrap-validation/STARTUP_ACTUAL_ZL_PROOF.json',research/'STARTUP_ACTUAL_ZL_PROOF.json')
    for name in ['BOOTSTRAP_RECEIPT.json','ACTUAL_BOOTSTRAP_EXECUTION_PROOF.json']:
        shutil.copyfile(D/'ZL-runtime-bootstrap-validation'/name,research/name)
    for name in ['FL20_EXTERNAL_ZL_DYNAMIC_STUDY.json','FL20_EXTERNAL_ZL_JOINT_STUDY.json','FL20_EXTERNAL_ZL_EXTRA_DYNAMIC_STUDY.json','ZL_COMPLETED_KIT_STAGE_BYTE_IDENTICAL_DEDUP.json','OWN_UNREACHABLE_STAGED_ZIP_LOSSLESS_ARCHIVING.json','REPRODUCIBLE_PYTHON_BYTECODE_CACHE_CLEANUP_20261023.json','ZL01_IMMUTABLE_SOURCE_EXACT_HARDLINKS.json','HISTORICAL_IDENTICAL_SNAPSHOT_BINARY_DEDUP_20261023.json']:
        if(N/name).exists():shutil.copyfile(N/name,research/name)
    guide=f'''# ZL03: следующий промежуточный вариант, 23 октября 2026

Полного совпадения нет; трёхнотный вариант сохранён. После ZL02 выполнена
совместная поправка52 параметров EQ/AllPass/dynamic с нулевым lookahead. В paired12 проверке реальных
полных рендеров критерий улучшился **1.531520→1.505954**, SEM0.00004762.
Это не процент сходства и не утверждение, что тембр полностью совпал.

- [Скачать полный ZIP: FLP, WAV, Diva, MIDI,17FST, VST3 preset и проверки](ZL-WIP03/{LABEL}_complete_WIP.zip).
- [A/B: оригинал → ZL03 с4,168с](ZL-WIP03/AB_REFERENCE_ZL03_WIP.mp3).
- [Загрузка в FL Studio20 и официальный установщик ZL](ZL-WIP03/FL_STUDIO_RU.md).
- [Параметры и доказательства](ZL-WIP03/verification/ZL_FULL_VERIFICATION.json).

В экспортных6 полных рендерах mean{report['mean_original_objective']:.9f};
после распаковки ZIP в новую папку6 свежих mean{proof['six_fresh_whole_chain_mean']:.9f}.
Все12 native states точны; active ZL state из FLP/FST/VSTpreset совпадает
по байтам и аудио на одном входе. Zero-depth whole native+ZL также побитно
совпадает. Полный обычный wet WAV меняется между запусками свободного Chorus.
ZL PDC0 и impulse first response0; это не замер общей задержки ASIO.

Новый FLP ещё не открывался в GUI FL Studio. В комплекте записан VST3,
есть отдельный FST и SUM FST как запасной путь загрузки. Установите официальный
бесплатный ZL Equalizer2 **1.4.1 Windows x64 VST3** по ссылке в инструкции.
Плагин не распространяется в Git. Dynamics ON только у полос15/16,
lookahead0/MinimumPhase;12 Peak+2AllPass из ZL01 сохранены и добавлены2dynamic.
MIDI/ARP/ADSR/источник не заменены. Native16, ZL01 и ZL02 оставлены неизменными.

В отдельной новой папке повторно скачан официальный MSI (проверен SHA),
извлечён VST3 и заново собран C-хост. Реальное активное аудио совпало с
первым runtime побитно. Это проверка отдельной сборки внутри текущей машины,
не доказательство нового чистого компьютера. Скрипт воспроизведения и обе
квитанции: [external-plugins-20261023-03](external-plugins-20261023-03/).

Совместный fit625 случаев завершён. Строгая проверка hot/cold сначала
обнаружила54 различия только в затухающем хвосте, max2.22e−16. Исходный
лог ошибки сохранён; два НОВЫХ загруженных экземпляра совпали побитно,
реальный компонент state resave точен. Затем проверены12 fresh paired,
6export и6ZIP-replay. Это не попытка выдать обычный Chorus рендер за точную
копию. Точный numerical replay error находится в proofs.

Дальше запущено исследование ещё двух динамических полос после ZL03;
снимок FL20_EXTERNAL_ZL_EXTRA_DYNAMIC_STUDY.json проверять по реальным
PID/starttime. Это исследование ещё не принято. Полный WAV и все17FST
находятся ВНУТРИ ZIP. Обычный x95 exporter использовать нельзя.
'''
    (PUBLIC/'ZL03_CONTINUATION_RU.md').write_text(guide,encoding='utf-8')
    link='[Актуальный новый WIP ZL03: динамический EQ без добавленного lookahead](ZL03_CONTINUATION_RU.md).\n\n'
    p=PUBLIC/'README_RU.md';p.write_text(link+p.read_text(),encoding='utf-8')
    header=f'''BEGIN_LATEST_ZL03_CONTINUATION
LATEST EXTERNAL PLUGIN COMPLETE WIP IS ZL03. This supersedes the ZL02/ZL01-latest statements below. Read local-fl-studio/cloud-after-1625/2026-10-22/ZL03_CONTINUATION_RU.md, ZL-WIP03/FL_STUDIO_RU.md and full ZIP. Native16 remains latest STOCK-only full kit. All old complete versions immutable. Full raw WAV and17FST are inside ZIP; public worktree intentionally has ZIP/FLP/AB/docs/proofs to avoid duplicate large artifacts. ZL03 refines52 parameters of12staticPeak+2AllPass+2dynamicMid bands15/16, same official free ZL1.4.1 Windows x64 VST3, MinimumPhase/lookahead0/PDC0/impulse0. Actual625fit then freshpaired12 mean1.531520->1.505954, SEM.00004762. Strict hot/cold exact assertion initially failed only54tail samples,max2.22e-16; original errorlog retained, two NEW cold hosts bit-exact and component resave exact. Numerical replay tolerance1e-12 explicitly recorded, never call nonzero residual bit-exact. Export6 mean{report['mean_original_objective']:.9f}, independent NEW-ZIP replay6 mean{proof['six_fresh_whole_chain_mean']:.9f}. All12 native states exact, all3 ZL component containers active audio exact on one input, whole native+ZL zero-depth exact. Ordinary Chorus renders vary; no exact ordinary wetWAV or complete reference match. New FL GUI open/export and ASIO latency measurement remain pending. No subjective audition claim.

REPRODUCIBLE OFFICIAL RUNTIME: setup_ZL_runtime.py downloaded official pinnedMSI, checked exactSHA, extracted only verified VST3/resources and compiled C-host in a NEW directory; actual active plugin replay bit-exact vs original. Proof is within current machine, not fresh-machine/GUI claim. Source scripts and receipts external-plugins-20261023-03. Run after existing Wine/MinGW/native setup, with NEW --destination; never overwrite existing runtime. Wrapper win_vst3.py resolves its plugin beside itself; choose correct PYTHONPATH. Official download GitHub available normally, other official domains403must not bypass. No third-party DLL/EXE/MSI in public kit. When using a new machine obtain user's licensed Diva/native FX; no credential extraction.

CURRENT FOLLOW-UP: inspect N/FL20_EXTERNAL_ZL_EXTRA_DYNAMIC_STUDY.json with real PID/starttime/cmdline and current actual VST3 hosts. Extra2dynamic bands launched after completed joint52 fit and verified ZL03, unchanged full original criterion, same3held external notes and real Diva source. Not adopted until fresh checks/full extended export/replay. Native main/watcher still exist; integration numeric owner pause and real disk guards must be inspected, never claim paused jobs compute. Extra dynamic script owns release of external-ZL-extra-dynamic-finite-study pause in finally; avoid duplicate matcher. D=/tmp/divalead-local-1625/internet-plugins-20261023. All unsupported external candidates retain not_compatible_with_standard_x95_exporter=true; never drop ZL in ordinary stock export. Private WAV archives lossless; dead overwritten host buffers removed only after JSON reference scan and active joint tags excluded, with receipt. Space is limited: inspect actual free root/tmp before next full kit. Do not delete releases or rewrite Git history to free space.
END_LATEST_ZL03_CONTINUATION

'''
    p=R/'start_skill_current.md';s=p.read_text();s=re.sub(r'BEGIN_LATEST_ZL03_CONTINUATION\n.*?END_LATEST_ZL03_CONTINUATION\n\n','',s,flags=re.S);p.write_text(header+s);shutil.copyfile(p,BASE/'start_skill_current.md')
    p=BASE/'CLOUD_AFTER_LOCAL_1625_RU.md';p.write_text(link.replace('(ZL03_CONTINUATION_RU.md)','(local-fl-studio/cloud-after-1625/2026-10-22/ZL03_CONTINUATION_RU.md)')+p.read_text(),encoding='utf-8')
    files=sorted(p for p in PUBLIC.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(PUBLIC/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUBLIC).as_posix()+'\n'for p in files))
    git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
    assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
    git('commit','-m','Back up joint-refined ZL03 FL20 WIP with canonical state replay and setup proof');commit=git('rev-parse','HEAD')
    assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
    subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
    checks=[]
    for rel in [f'ZL-WIP03/{LABEL}_complete_WIP.zip','ZL-WIP03/AB_REFERENCE_ZL03_WIP.mp3','ZL-WIP03/FL_STUDIO_RU.md','ZL03_CONTINUATION_RU.md']:
        p=PUBLIC/rel
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix(),timeout=40)as response:data=response.read()
        assert data==p.read_bytes();checks.append(dict(path=rel,bytes=len(data),HTTP_byte_exact=True))
    receipt=dict(commit=commit,previous_HEAD=before,full_kit='ZL-WIP03',all_old_complete_kit_tree_OIDs_preserved=True,HTTP_checks=checks,reference_match_reached=False)
    (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
