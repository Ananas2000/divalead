"""Publish a complete verified kit and exact remote-backed cleanup receipts."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,os,re,shutil,subprocess,urllib.request
from win_vst3 import D
P=Path('/workspace/divalead');B=D.parent;N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22';ROOT=B/'FL20_ZL_05_WIP';LABEL='Diva_ZL_05_WIP'
PAUSE=R/'auto-backup.pause';OWNER='authorized-local-backed-copy-cleanup-20261023'
def read(p):return json.loads(Path(p).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():
 out={}
 for line in git('ls-tree','HEAD:diva-lead').splitlines():
  if re.search(r'\tv\d+-wip$',line):name='diva-lead/'+line.split('\t',1)[1];out[name]=git('rev-parse','HEAD:'+name)
 for line in git('ls-tree','HEAD').splitlines():
  if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',line):name=line.split('\t',1)[1];out[name]=git('rev-parse','HEAD:'+name)
 for d in list(PUBLIC.glob('WIP[0-9][0-9]'))+list(PUBLIC.glob('ZL-WIP*')):
  rel=d.relative_to(P).as_posix()
  if git('ls-tree','HEAD','--',rel):out[rel]=git('rev-parse','HEAD:'+rel)
 for name in ['local-fl-studio/2026-10-22','after-DSP-arrival/checkpoint-WIP','after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']:
  rel=(BASE/name).relative_to(P).as_posix();out[rel]=git('rev-parse','HEAD:'+rel)
 return out
def aggregate_hashes():
 # Include deliberately omitted old ZIPs from immutable Git blobs as well.
 rows={}
 rel=PUBLIC.relative_to(P).as_posix()
 for line in git('ls-tree','-rl','HEAD','--',rel).splitlines():
  info,path=line.split('\t',1);a=info.split();p=P/path
  if a[1]!='blob'or p.name=='SHA256SUMS.txt':continue
  data=p.read_bytes()if p.is_file()else subprocess.check_output(['git','-C',str(P),'cat-file','blob',a[2]])
  rows[p.relative_to(PUBLIC).as_posix()]=hashlib.sha256(data).hexdigest()
 for p in PUBLIC.rglob('*'):
  if p.is_file()and p.name!='SHA256SUMS.txt':rows[p.relative_to(PUBLIC).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 (PUBLIC/'SHA256SUMS.txt').write_text(''.join(h+'  '+p+'\n'for p,h in sorted(rows.items())))
assert read(PAUSE)['owner']==OWNER
with(R/'auto-backup-Git.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
 subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
 before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/'ZL-WIP05';dest.mkdir(exist_ok=False)
 report=read(ROOT/'verification/ZL_FULL_VERIFICATION.json');proof=read(ROOT/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');choice=read(D/'ZL-best-continuation-export-02/candidate-research-only.json')
 assert len(proof['all12_native_saved_states_exact'])==12
 assert all(r['component_bytes_exact']for r in proof['actual_active_state_container_replay'])
 for name in [LABEL+'.flp',LABEL+'_complete_WIP.zip','AB_REFERENCE_ZL05_WIP.mp3','FL_STUDIO_RU.md','README_RU.md']:
  p=B/name if name.endswith('.zip')else ROOT/name;shutil.copyfile(p,dest/name)
 (dest/'verification').mkdir()
 for p in(ROOT/'verification').iterdir():
  if p.is_file()and p.suffix.lower()!='.wav':shutil.copyfile(p,dest/'verification'/p.name)
 research=PUBLIC/'ZL05-export-and-storage-cleanup';research.mkdir();scripts=research/'scripts';scripts.mkdir()
 for name in ['freeze_ZL05_export_input.py','build_ZL05_kit.py','finalize_ZL05_kit.py','publish_ZL05_kit.py','continue_ZL_matching.py','study_ZL_extra_allpass.py','fl20_vst3_state.py','win_vst3.py']:
  p=D/name;compile(p.read_text(),str(p),'exec');shutil.copyfile(p,scripts/name)
 for name in ['cleanup_remote_backed_local_copies.py','cleanup_verified_tmp_copies.py','cleanup_backed_historical_work_and_balance_storage.py']:
  p=N/name;compile(p.read_text(),str(p),'exec');shutil.copyfile(p,scripts/name)
 canonical=research/'canonical-export-input';canonical.mkdir()
 for p in(D/'ZL-best-continuation-export-02').iterdir():
  if p.suffix=='.tsv':(canonical/(p.name+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0))
  else:shutil.copyfile(p,canonical/p.name)
 receipts=['REMOTE_BACKED_LOCAL_RELEASE_OMISSIONS_20261023.json','REMOTE_BACKED_TMP_COPIES_REMOVED_20261023.json','REMOTE_BACKED_HISTORICAL_WORK_CLEANUP.json','RETAINED_ARCHIVES_CROSS_VOLUME_RELOCATION.json','ZL_RESTART_AFTER_AUTHORIZED_STORAGE_CLEANUP.json','FL20_ZL_CONTINUOUS_CONTROLLER.json','ZL_EXTRA_ALLPASS_STUDY_STATE.json']
 for name in receipts:
  p=N/name;data=p.read_bytes()
  if len(data)>150000:
   blob=gzip.compress(data,mtime=0);assert gzip.decompress(blob)==data;(research/(name+'.gz')).write_bytes(blob)
  else:(research/name).write_bytes(data)
 guide=f'''# ZL05 — полный промежуточный вариант, поиск продолжается

Полного совпадения с оригиналом пока нет. Это следующий полностью проверенный
комплект ветки с12 штатными FL-эффектами и бесплатным ZL Equalizer2 v1.4.1.

- [ZIP: FLP, WAV, Diva, MIDI,17FST, VST3preset, проверки](ZL-WIP05/{LABEL}_complete_WIP.zip).
- [A/B: оригинал0с → ZL05 с4,168с](ZL-WIP05/AB_REFERENCE_ZL05_WIP.mp3).
- [Инструкция FL Studio20 и официальный установщик](ZL-WIP05/FL_STUDIO_RU.md).

Только три длинные входящие ноты41→37→36 на фразу, фраза повторяется дважды.
Движение вверх — прежний внутренний ARP Diva. Источник Diva и12 native-эффектов
в этой серии неизменны. Никаких нотных подмен и подмешивания оригинала.

Экспортируется accepted cohort{choice['source_accepted_cohort']}, mean{choice['loss']:.9f}.
Отдельный полный экспорт6: mean**{report['mean_original_objective']:.9f}**.
Восстановление ZIP в новую папку и ещё6 фактических рендеров:
mean**{proof['six_fresh_whole_chain_mean']:.9f}**. Для ZL04 export/ZIP были
1.485379268/1.486043351. Критерий по полному исходному референсу прежний;
числа не являются процентом воспринимаемого сходства.

Все12 native saved states точны, компонент ZL в FLP/FST/standardpreset точен.
Проверка целого тракта с нулевой глубиной Chorus: максимальный остаток
{proof['whole_native_plus_ZL_zero_depth_max_abs_error']}; bit-exact={proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']}.
Обычный wet Chorus меняется между дублями. ZL PDC0 и измеренный импульсный
отклик с первого отсчёта; ASIO/целая DAW здесь не измерялись. Новый FLP ещё
не открывался и не экспортировался в GUI FL Studio на ПК.

Почему ZL: он бесплатный, существует Windowsx64 VST3 для загрузки в FL20,
позволяет динамически править отдельные области Mid/Side и не добавляет
буферной задержки в данном MinimumPhase/lookahead0 режиме. Используется
официальный настоящий плагин, не имитация его эквализации. В комплекте нет
чужих DLL/MSI: официальный установщик указан в инструкции.

## Место и восстановление старых копий

По прямому разрешению пользователя выгружены только побайтно проверенные
локальные копии файлов, присутствующих в GitHub на commit{before}:
1024старых ZIP/audio в checkout,247копий в/tmp и844копии старых исследований.
В Git ничего из этих версий не удалено, история и все полные комплекты сохранены.
Из checkout файлы выгружены с skip-worktree; журнал содержит каждый путь и blob.
Суммарно реального места освободилось около2.4GiB. Дополнительно все232файла
старых rejected-cohort архивов (~1GiB) перенесены из/tmp на основной диск:
каждый SHA256 проверен, старый путь сохранён directorysymlink. Это перенос,
а не дополнительное высвобождение общего объёма.

Один отсутствующий файл checkout можно вернуть:
`git restore --ignore-skip-worktree-bits -- путь/из/журнала`.
Для удалённой старой частной копии журнал содержит git_path и local_path;
восстановите именно нужный blob командой git show в требуемый local_path.
Исходный референс, текущий Diva source, runtime, последние полные комплекты,
активные входы и принятые новые validation archives сохранены.

Основной actualVST3 matcher возобновлён; проверять реальные PID/starttime,
N/FL20_ZL_CONTINUOUS_CONTROLLER.json, а не считать snapshot доказательством
будущей работы. Отдельно запущено исследование дополнительных causalAllPass;
оно не меняет mainBEST и ещё не принято в этот FLP. Совпадение не достигнуто.
'''
 (PUBLIC/'ZL05_CONTINUATION_RU.md').write_text(guide,encoding='utf-8')
 (research/'README_RU.md').write_text(guide,encoding='utf-8')
 p=PUBLIC/'README_RU.md';p.write_text('[Актуальный полный WIP ZL05: ZIP, A/B, FL20, место и продолжение](ZL05_CONTINUATION_RU.md).\n\n'+p.read_text(),encoding='utf-8')
 live=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json')
 header=f'''BEGIN_LATEST_COMPLETE_ZL05_AND_AUTHORIZED_LOCAL_CLEANUP
LATEST COMPLETE PUBLIC LOW-LATENCY KIT ZL05, acceptedprivatecohort{choice['source_accepted_cohort']}. Full export6 mean{report['mean_original_objective']:.9f}; NEW ZIP actual replay6 mean{proof['six_fresh_whole_chain_mean']:.9f}. Read local-fl-studio/cloud-after-1625/2026-10-22/ZL05_CONTINUATION_RU.md and ZL-WIP05/FL_STUDIO_RU.md. All old complete kits/numbered trees and Git history preserved. Three heldnotes41->37->36 perphrase twice/internalARP unchanged, original only analysis/AB, no MistaTowa. Official free ZL1.4.1 Windowsx64 VST3 separate download. Native12+ZL12staticPeak/2AllPass/4dynamicPeak, MinimumPhase/lookahead0, measuredPDC0/impulse0. Full original-reference objective unchanged. No exact-reference-match, subjective audition, newFLGUIexport, fullASIO latency or independently fresh-machine claim.

USER AUTHORIZED OMITTING OLD LOCAL BACKED COPIES on2026-10-23:1024checkoutZIP/audio,247/tmp duplicates,844oldwork copies, everyblob exact against origin/main{before}; source/currentpresets/reference protected. Local removed checkout files have skip-worktree, not git rm; use git restore --ignore-skip-worktree-bits -- exactpath when needed. N cleanup receipts and public ZL05-export-and-storage-cleanup contain perpathblob/restorecommands. About2.4GiB actualtotalfreed. Separately retained232files~1GiB rejectedcohortarchives relocated fromB/archived-rejected-native-cohort-WAVs to/workspace/divalead-work/offline-storage/archived-rejected-native-cohort-WAVs; B oldpath directorysymlink preserved, everySHAverified. Do not mistake localomissions for deleted versions or blindly restoreall (would refill disk). AggregateSHA256SUMS must include omitted PUBLICZL04ZIP fromGitblob. No rewrite/prunehistory.

ACTUAL MAIN MATCHER resumed aftercleanup: N/FL20_ZL_CONTINUOUS_CONTROLLER.json snapshotphase={live['phase']}, verifyactualPID/starttime/process, not permanence. D/ZL-continuous65/BEST_CANDIDATE.json and its actualcomponent authoritative; inherited physicalarrays maybestale, so deriveXML/610readbacks beforeexport. D/continue_ZL_matching.py fourrealworkers65params/train+2heldout+freshpaired6, all12 validationWAV losslessarchive verified, statebytesexact; two NEW coldinstances float32 rtol8eps/atol1e-12, expliciterror andbitexactboolean, hot/cold diagnosticonly. Actualroot64MiB/tmp112MiB reserves, N/zl-continuation.stop ends afterfinitecurrentcohort. Numericpauseownerexternal-ZL-continuous65-refinement. Legacy native143848/watcher144989 paused and NOT currentexternal matching; no duplicates. Extra research D/study_ZL_extra_allpass.py/N/ZL_EXTRA_ALLPASS_STUDY_STATE.json separatebranch, doesNOTmodifyMainBEST or acceptedFLP. User authorizes internetFL20plugins, full backups and localoldcopycleanup, no per-trialquestions. Saved onboardingdraft remainsunpublished; do not block currentwork or claim published.
END_LATEST_COMPLETE_ZL05_AND_AUTHORIZED_LOCAL_CLEANUP

'''
 p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md')
 aggregate_hashes()
 git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
 assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
 git('commit','-m','Save verified ZL05 full FL20 kit and restoreable remote-backed local storage cleanup');commit=git('rev-parse','HEAD')
 assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in old.items())
 subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
 checks=[]
 for rel in [f'ZL-WIP05/{LABEL}_complete_WIP.zip','ZL-WIP05/AB_REFERENCE_ZL05_WIP.mp3','ZL-WIP05/FL_STUDIO_RU.md','ZL05_CONTINUATION_RU.md']:
  p=PUBLIC/rel;url='https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix()
  with urllib.request.urlopen(url,timeout=40)as r:b=r.read()
  assert b==p.read_bytes();checks.append(dict(path=rel,bytes=len(b),HTTP_byte_exact=True))
 receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP05',all_old_full_kit_and_numbered_release_tree_OIDs_preserved=True,HTTP_checks=checks,complete_ZIP_SHA256=hashlib.sha256((B/(LABEL+'_complete_WIP.zip')).read_bytes()).hexdigest(),reference_match_reached=False)
 (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps(receipt),flush=True)
# Keep the existing owned manual-Git pause until the immediate research backup
# has finished, so the old backup publisher cannot race this turn's commits.
