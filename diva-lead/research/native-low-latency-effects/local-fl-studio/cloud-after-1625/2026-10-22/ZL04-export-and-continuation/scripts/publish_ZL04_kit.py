"""Normal guarded Git backup of a verified new external-plugin WIP family."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,urllib.request
from win_vst3 import D
P=Path('/workspace/divalead');B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22'
ROOT=B/'FL20_ZL_04_WIP';LABEL='Diva_ZL_04_WIP';pause=R/'auto-backup.pause';OWNER='ZL04-complete-best-publication'
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
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
    before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/'ZL-WIP04';dest.mkdir(exist_ok=False)
    report=read(ROOT/'verification/ZL_FULL_VERIFICATION.json');proof=read(ROOT/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');assert proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']
    for name in [LABEL+'.flp',LABEL+'_complete_WIP.zip','AB_REFERENCE_ZL04_WIP.mp3','FL_STUDIO_RU.md','README_RU.md']:
        src=B/name if name.endswith('.zip')else ROOT/name;shutil.copyfile(src,dest/name)
    (dest/'verification').mkdir()
    for p in (ROOT/'verification').iterdir():
        if p.is_file()and p.suffix.lower()!='.wav':shutil.copyfile(p,dest/'verification'/p.name)
    research=PUBLIC/'ZL04-export-and-continuation';research.mkdir(exist_ok=False);scripts=research/'scripts';scripts.mkdir()
    for name in ['build_ZL04_kit.py','finalize_ZL04_kit.py','publish_ZL04_kit.py','continue_ZL_matching.py','fl20_vst3_state.py','win_vst3.py']:
        p=D/name;compile(p.read_text(),str(p),'exec');shutil.copyfile(p,scripts/name)
    copy_jsons(D/'ZL-best-continuation-export-01',research/'canonical-best-export-input')
    for name in ['RECENT_GIT_OBJECTS_LOSSLESS_PACK_VERIFICATION.json','CLOSED_ZL_CONTROLLER_HOST_SCRATCH_CLEANUP.json','ZL03_AND_OLD_KIT_STAGE_EXACT_DEDUP.json','FL20_ZL_CONTINUOUS_CONTROLLER.json']:
        shutil.copyfile(N/name,research/name)
    guide=f'''# ZL04 — новый полный промежуточный вариант

**Полного совпадения с референсом нет.** Это лучший полностью упакованный
вариант новой low-latency ветки. Только три длинные входящие ноты41→37→36
на фразу, две фразы, прежний внутренний ARP/ADSR и источник Diva.

- [Полный ZIP: FLP, WAV, Diva, MIDI,17FST, VST3 preset и проверки](ZL-WIP04/{LABEL}_complete_WIP.zip).
- [A/B: оригинал → ZL04 с4,168с](ZL-WIP04/AB_REFERENCE_ZL04_WIP.mp3).
- [Инструкция FL Studio20 и официальный установщик эффекта](ZL-WIP04/FL_STUDIO_RU.md).

Реальные12 штатных эффектов плюс бесплатный официальный **ZL Equalizer2
v1.4.1 Windows x64 VST3**. На SUM: StereoShaper→ZL. Внутри ZL12staticPeak,
2AllPass и4dynamicPeak (2Mid около1–1.3kHz,2Side около2.9kHz), lookahead0,
MinimumPhase. Vendor binaries не включены; ссылка на установщик в инструкции.

От исходной stock Native16 ветки с mean1.552 последовательно получены ZL01,
ZL02, ZL03 и этот65param refit. Последняя подтверждённая private cohort7:
mean1.485810, paired6 против её актуального контроля, все12 validation WAV
lossless-архивированы. В отдельном экспортном6 mean**{report['mean_original_objective']:.9f}**,
после распаковки нового ZIP ещё6 mean**{proof['six_fresh_whole_chain_mean']:.9f}**.
Критерий сравнения с ОРИГИНАЛОМ прежний; это не процент сходства и не новая
оценка старой v83 с недопустимой задержкой Finish.

Все12 native state bytes точны. Реальный ZL component из FLP/FST/VSTpreset
повторил один вход побитно; whole native+ZL zero-depth тоже побитно точен.
Обычный wet WAV меняется между запусками свободного Chorus. ZL PDC0,
impulse first response0; это не измерение ASIO/DAW. Новый FLP ещё не открыт
и не экспортирован из GUI FL на ПК. В инструкции есть fallback FST загрузка.
Полный WAV и все пресеты находятся внутри ZIP.

Предыдущие Native16/ZL01/ZL02/ZL03 и все номерные версии сохранены. Для места
только недавние reachable Git objects упакованы с verify-pack и проверкой всех
refs/HEAD; история не переписывалась. Удалены лишь уже упакованные loose-копии.
После проверки remote ZIP дублирующий файл ZIP в локальном Git checkout может
быть выгружен с skip-worktree: он сохранён на GitHub, в Git object и в частном
`/tmp/divalead-local-1625/{LABEL}_complete_WIP.zip`. Для восстановления checkout
используйте git restore --ignore-skip-worktree-bits по этому конкретному пути,
либо извлеките Git blob в новую рабочую папку. Это не удаление версии из Git.

Следующее продолжение — настоящий VST3 matcher и N/FL20_ZL_CONTINUOUS_CONTROLLER.json;
проверяйте реальные PID/starttime и текущие дисковые резервы. Snapshot stopped
после завершённой7 когорты из-за фактического /tmp резерва; не выдавать его за
работающий. После бэкапа можно освобождать только лишние проверенные staging
дубликаты и возобновлять от BEST_CANDIDATE при достаточном фактическом месте.
Новый topology не поддерживается обычным native x95 exporter.
'''
    (PUBLIC/'ZL04_CONTINUATION_RU.md').write_text(guide,encoding='utf-8')
    link='[Актуальный полный WIP ZL04: ZIP, A/B и инструкция FL20](ZL04_CONTINUATION_RU.md).\n\n';p=PUBLIC/'README_RU.md';p.write_text(link+p.read_text(),encoding='utf-8')
    header=f'''BEGIN_LATEST_COMPLETE_ZL04
LATEST COMPLETE PUBLIC LOW-LATENCY KIT ZL04. This supersedes older latest ZL03/02/01 statements. Read local-fl-studio/cloud-after-1625/2026-10-22/ZL04_CONTINUATION_RU.md and ZL-WIP04/FL_STUDIO_RU.md. Full ZIP includes FLP/WAV/Diva/MIDI/17FST/.vstpreset/proofs. Official free ZL1.4.1 Windowsx64 separate download, no vendor binary inGit. ZL12staticPeak+2AllPass+4dynamicPeak (2Mid~1-1.3kHz,2Side~2.9kHz), MinimumPhase/lookahead0/PDC0/impulse0. Three incoming heldnotes41->37->36 per phrase twice, internalARP/ADSR and source unchanged. Only actual source/DLL/VST3 renders, original used for analysis/AB only, no MistaTowa. No complete reference-match/GUIexport/human-audition/ASIO latency claim.

65param acceptedprivatecohort7 mean1.485810 with freshpaired6 and all12WAV losslessly archived. Dedicated full export6 mean{report['mean_original_objective']:.9f}; NEW ZIP extraction and6 actualreplays mean{proof['six_fresh_whole_chain_mean']:.9f}. All12 native states exact; all3ZLstate containers and whole zero-depth actualaudio bit-exact for this kit. Ordinary Chorus wetWAV varies, never call it bit-exact. Metadata physically reextracted from REAL JUCE component XML and610readbacks before packing, so4dynamic bands and newstatic/AP settings are current. All old full kit tree OIDs/numbered releases immutable.

STORAGE/CONTINUATION: actual matcher ended after completedcohort7 at observed/tmp reserve; N/FL20_ZL_CONTINUOUS_CONTROLLER.json is authoritative and must be checked against /proc PID/starttime before claiming alive. Best D/ZL-continuous65/BEST_CANDIDATE.json. Own export pause ZL04-full-best-export-and-replay released after backup decision. Can resume same persistent script only when real reserves allow; preserve source/archives/current best. Latest full ZIP privateB/Diva_ZL_04_WIP_complete_WIP.zip remains readable. A byte-identical duplicate of this NEW public ZIP may be removed from checkout using skip-worktree AFTER normalGitpush+remoteHTTPverification; Git still stores blob and remote release. Do not assume public glob ZIP exists; use privateB or git show HEAD:full-repo-path into a NEW folder. When regenerating aggregate SHA256SUMS include missing skip-worktree ZIP using storedGitblob. This saves only an already verified local duplicate, no history rewrite or version removal. Recent reachable Git objects were packed through stdout (avoids cross-FS rename), index/pack verified, prune-packed removed only duplicate loose objects, refs/HEAD/worktree unchanged. GC receipts available.

Actual source preset and12native state export remain supported. New external component topology always guarded against ordinaryx95export. Cold-vs-cold instances are actual parameter-replay check; actual state bytes exact, numericalerrors recorded, never call nonzero residual bit-exact. Hot/cold diagnostic only. Preserve legacy explicit stop for obsolete high-latencyFinish; oldnative matcher/watcher may be paused and are not currentexternal search. User authorized internet FL20-compatible plugins and full Git backups. No per-trial questions. Config setup append must check latest actualZL04component; saved draft still needs Publish for futureenvironment, current work doesn't wait for it.
END_LATEST_COMPLETE_ZL04

'''
    p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md')
    files=sorted(p for p in PUBLIC.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(PUBLIC/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUBLIC).as_posix()+'\n'for p in files))
    git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
    git('commit','-m','Back up best ZL04 full FL20 lead kit and real ZIP replay with four dynamic bands');commit=git('rev-parse','HEAD')
    assert all(git('rev-parse','HEAD:'+path)==oid for path,oid in old.items())
    subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    checks=[]
    for rel in [f'ZL-WIP04/{LABEL}_complete_WIP.zip','ZL-WIP04/AB_REFERENCE_ZL04_WIP.mp3','ZL-WIP04/FL_STUDIO_RU.md','ZL04_CONTINUATION_RU.md']:
        p=PUBLIC/rel
        with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix(),timeout=40)as response:data=response.read()
        assert data==p.read_bytes();checks.append(dict(path=rel,bytes=len(data),HTTP_byte_exact=True))
    archive=dest/(LABEL+'_complete_WIP.zip');local=B/archive.name;assert local.read_bytes()==archive.read_bytes();digest=hashlib.sha256(local.read_bytes()).hexdigest();rel=archive.relative_to(P).as_posix()
    git('update-index','--skip-worktree','--',rel);archive.unlink();assert hashlib.sha256(local.read_bytes()).hexdigest()==digest and not git('status','--porcelain')
    receipt=dict(commit=commit,previous_HEAD=before,full_kit='ZL-WIP04',all_old_full_kit_tree_OIDs_preserved=True,HTTP_checks=checks,
        exact_new_ZIP_checkout_duplicate_evicted_with_skip_worktree=True,private_complete_ZIP=str(local),complete_ZIP_SHA256=digest,reference_match_reached=False)
    (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
