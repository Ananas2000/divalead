"""Normal guarded Git backup of a verified new external-plugin WIP family."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,urllib.request
from win_vst3 import D
P=Path('/workspace/divalead');B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22'
ROOT=B/'FL20_ZL_01_WIP';LABEL='Diva_ZL_01_WIP';pause=R/'auto-backup.pause';OWNER='external-ZL-complete-kit-and-research-backup'
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
assert read(R/'auto-backup-state.json')['phase']=='paused_for_manual_Git_work'
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
    fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
    subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
    before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/'ZL-WIP01';assert not dest.exists()
    proof=read(ROOT/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');report=read(ROOT/'verification/ZL_FULL_VERIFICATION.json')
    assert proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']and len(proof['all12_native_saved_states_exact'])==12
    shutil.copytree(ROOT,dest);shutil.copyfile(B/(LABEL+'_complete_WIP.zip'),dest/(LABEL+'_complete_WIP.zip'))
    research=PUBLIC/'external-plugins-20261023-01';research.mkdir(exist_ok=False);scripts=research/'scripts';scripts.mkdir()
    for name in ['vst3_effect_host.c','win_vst3.py','fl20_vst3_state.py','run_ZL_allpass_study.py','run_ZL_EQ12_study.py','build_ZL01_kit.py','finalize_ZL01_kit.py','publish_ZL01_kit.py']:
        p=D/name
        if p.suffix=='.py':compile(p.read_text(),str(p),'exec')
        shutil.copyfile(p,scripts/name)
    for name in ['OFFICIAL_DOWNLOADS.json','EXTRACTED_PACKAGE_CONTENTS.json','VST3_HOST_BUILD.json']:shutil.copyfile(D/name,research/name)
    for folder in ['ZL-allpass-original-reference-01','ZL-post-MS-EQ12-original-reference-01']:copy_jsons(D/folder,research/folder)
    for name in ['FL20_EXTERNAL_ZL_VST3_STUDY.json','FL20_EXTERNAL_ZL_EQ12_STUDY.json','COMPLETED_NATIVE_COHORT_WAV_IDENTICAL_HARDLINK_DEDUP.json','IMMUTABLE_REFERENCE_EXACT_HARDLINK_DEDUP_20261023.json','HISTORICAL_STARTUP_RENDER_LOSSLESS_ARCHIVING_20261023.json']:
        if(N/name).exists():shutil.copyfile(N/name,research/name)
    for p in N.glob('REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING_SESSION20261023*.json'):shutil.copyfile(p,research/p.name)
    shutil.copyfile(B/'archive_rejected_native_WAVs_session20261023.py',scripts/'archive_rejected_native_WAVs_session20261023.py')
    readme=f'''# Новый промежуточный вариант ZL01, 23 октября 2026

Полного совпадения с оригиналом пока нет. Продолжаем исключительно с тремя
длинными входящими нотами41→37→36 на фразу; внутри работает прежний ARP Diva.

- [Полный ZIP: FLP, WAV, Diva, MIDI,17 FST, VST3 preset, инструкция и проверки](ZL-WIP01/{LABEL}_complete_WIP.zip).
- [A/B: оригинал → ZL01 с4,168с](ZL-WIP01/AB_REFERENCE_ZL01_WIP.mp3).
- [Как установить новый эффект и открыть в FL Studio20](ZL-WIP01/FL_STUDIO_RU.md).
- [Проверки и исходники поиска](external-plugins-20261023-01/).

Официальная бесплатная ZL Equalizer2 **v1.4.1 Windows x64 VST3** установляется
отдельно по ссылке в инструкции; её бинарник в Git не распространяется.
В новом проекте на SUM после Stereo Shaper добавлен ZL:12 статических Peak
полос (6Mid/6Side) и2 All Pass. Minimum Phase, Dynamics OFF, Lookahead0.
Штатная цепь и настоящий источник Diva сохранены, ноты/ARP/ADSR прежние.
Native16 и все старые комплекты оставлены неизменными.

В первом независимом paired24 тесте два All Pass:1.553478→1.546884.
Затем12 свежих paired тестов дополнительного EQ:1.546381→1.544842,
paired SEM0.00002227. Общий исходный критерий не менялся; это не процент
сходства или доказательство полного совпадения. В экспортных6 рендерах
всей цепи среднее **{report['mean_original_objective']:.9f}**; после распаковки
ZIP в новую папку ещё6 дали **{proof['six_fresh_whole_chain_mean']:.9f}**.
Свободный Chorus объясняет вариативность между обычными дублями.

Настоящий официальный Windows VST3 проверен положительным+6dB контролем,
активные state/audio совпали побитно после новой загрузки. FLP/FST/VST3preset
содержат один реальный component state; их повторное исполнение на одном
входе совпадает побитно.12 штатных состояний и zero-depth whole-graph replay
также точны. ZL PDC0, первая реакция на импульс0 кадров; это не измерение ASIO.
У native zero-depth block128/512/1024 есть небольшой max residual2.1e−5,
он не выдан за побитную инвариантность. Native first-response2frames.

**Новый проект не открывался в GUI FL Studio на ПК.** Контейнер VST3 сделан
по реальному образцу FL20.8.4 и проверен отдельным PyFLP event parser;
известное ограничение его high-level slot iterator явно учтено. Проверка
нового actual-FL экспорта остаётся отдельным этапом. В инструкции есть
запасная загрузка отдельного FST, если FL не восстановит новый SUM VST3.

Не подавать этот новый topology обычному native x95 exporter: в candidate
есть явный guard и отдельные ZL export/replay scripts. Все сохранённые
валидационные WAV частных исследований retained в lossless tar.gz; JSON
метрики и SHA receipts включены здесь, большие исследовательские archives
не дублируются в этом публичном комплекте. Код хоста MIT; VST3 ABI описан
по официальным MIT headers Steinberg. ZL source/license: AGPLv3,
https://github.com/ZL-Audio/ZLEqualizer/tree/1.4.1 . Vendor files не включены.
'''
    (PUBLIC/'ZL01_CONTINUATION_RU.md').write_text(readme,encoding='utf-8')
    link='[Новое продолжение: ZL01, бесплатный VST3 без добавленного буфера](ZL01_CONTINUATION_RU.md).\n\n'
    p=PUBLIC/'README_RU.md';p.write_text(link+p.read_text(),encoding='utf-8')
    live=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json')
    header=f'''BEGIN_LATEST_EXTERNAL_ZL_CONTINUATION
LATEST NEW EXTERNAL-PLUGIN WIP ZL01. This supersedes older statements that Native16 is the latest overall result, or that no actual external VST3 has been tried. Native16 remains latest complete STOCK-only WIP and is immutable. Read local-fl-studio/cloud-after-1625/2026-10-22/ZL01_CONTINUATION_RU.md and ZL-WIP01/FL_STUDIO_RU.md. Full ZIP has FLP/WAV/Diva/MIDI/17FST/standard .vstpreset/proofs. Official free ZL Equalizer2 v1.4.1 Windows x64 MSI GitHub URL and SHA are recorded; no third-party binary is redistributed. New actual SUM slot2 follows existing Stereo Shaper. MinimumPhase, lookahead0, dynamicsOff, 12 Peak bands(6Mid/6Side)+2 AllPass. User explicitly allows online plugins that are installable in FL20. Official Reaper/Airwindows/TDR sites returned proxy403; do not bypass policy. Official ZL GitHub release was accessible normally. No cloud skills are currently exposed; do not invent skill availability.

ACTUAL EXECUTION: original supplied Diva rerun, all281 values/all12 MIDI/raw float32/actualeffGetChunk exact; only3 held notes per phrase twice, internal ARP/ADSR intact. New minimal C WinVST3 host uses actual official plugin, float32 and real parameter queues, not an audio model. Flat pass bit-exact at128/512/1024, +6dB tone measured6dB, active component state and audio bit-exact on reload/new host. AllPass415 actual trials plus24 fresh paired gave1.553478->1.546884, SEM.00001403. EQ12 577 trials plus12fresh paired gave1.546381->1.544842, SEM.00002227. Export6 whole-chain mean{report['mean_original_objective']:.9f}; NEW ZIP directory actual12native states exact, native+ZL zero-depth audio exact, FLP/FST/VSTpreset component audio exact; fresh6 mean{proof['six_fresh_whole_chain_mean']:.9f}. ZL first impulse0,PDC0. Native impulse first2frames; native zero-depth block residualmax2.1e-5, not bit-exact. No GUI export, subjective audition, end-to-end ASIO measurement or exact reference match claim. FL VST3 records based on real PyFLP Loopcloud FL2084 fixture; independent parser checks actual VST3 GUID/name/effect shell and full FL events. PyFLP high-level mixer divides98 as start but real verified FL20 uses terminator; don't trust that iterator for slot positions. Fallback single-plugin and SUM FST provided.

EXTENDED TOPOLOGY GUARD: ZL candidate nests supported native_base and has not_compatible_with_standard_x95_exporter=true. Do NOT feed it to ordinary native exporter/restorer or silently drop new effect. D=/tmp/divalead-local-1625/internet-plugins-20261023; actual scripts win_vst3.py, fl20_vst3_state.py, run_ZL_allpass_study.py, run_ZL_EQ12_study.py, build_ZL01_kit.py, finalize_ZL01_kit.py. Component and all610 readbacks are in full ZIP. Dedicated new family ZL-WIP01 keeps old STOCK watcher maxWIP logic unchanged. Follow-up dynamic or extra EQ is research until real save/reload/fresh comparison/full-kit replay; latest exact reference criteria remain unchanged. Main native matcher snapshot phase {live['phase']}; inspect actual PID/starttime/current owner pause before action. Global numeric pause owner external-ZL-full-FL20-preset-integration is an owned finite workflow, release only after its actual next-job coordination. Git pause owner external-ZL-complete-kit-and-research-backup is removed by its writer finally. Do not duplicate matcher/watcher.

STORAGE: completed rejected native cohorts and historical startup verification WAV caches were archived losslessly and SHA-verified before unsqueezed files removed. Cache archival alone is not proof of free-space gain; inspect actual receipts. Complete versions, originals, source inputs and current graph retained. Byte-identical immutable reference copies hardlinked preserving every byte/path. Keep all old numbered releases, actual local20261022 subtree and ALL complete kit tree OIDs unchanged. State/progress JSON snapshots are history; read real current process state.
END_LATEST_EXTERNAL_ZL_CONTINUATION

'''
    p=R/'start_skill_current.md';s=p.read_text();s=re.sub(r'BEGIN_LATEST_EXTERNAL_ZL_CONTINUATION\n.*?END_LATEST_EXTERNAL_ZL_CONTINUATION\n\n','',s,flags=re.S);p.write_text(header+s);shutil.copyfile(p,BASE/'start_skill_current.md')
    p=BASE/'CLOUD_AFTER_LOCAL_1625_RU.md';p.write_text(link.replace('(ZL01_CONTINUATION_RU.md)','(local-fl-studio/cloud-after-1625/2026-10-22/ZL01_CONTINUATION_RU.md)')+p.read_text(),encoding='utf-8')
    files=sorted(p for p in PUBLIC.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt')
    (PUBLIC/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PUBLIC).as_posix()+'\n'for p in files))
    git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
    assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
    git('commit','-m','Back up actual zero-latency ZL VST3 lead WIP, full FL20 presets and replay proofs');commit=git('rev-parse','HEAD')
    assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
    subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
    assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
    checks=[]
    for rel in [f'ZL-WIP01/{LABEL}_complete_WIP.zip','ZL-WIP01/AB_REFERENCE_ZL01_WIP.mp3','ZL-WIP01/FL_STUDIO_RU.md','ZL01_CONTINUATION_RU.md']:
        p=PUBLIC/rel;url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix()
        with urllib.request.urlopen(url,timeout=40)as response:data=response.read()
        assert data==p.read_bytes();checks.append(dict(path=rel,bytes=len(data),HTTP_byte_exact=True))
    receipt=dict(commit=commit,previous_HEAD=before,full_kit='ZL-WIP01',all_old_complete_kit_tree_OIDs_preserved=True,HTTP_checks=checks,reference_match_reached=False)
    (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
