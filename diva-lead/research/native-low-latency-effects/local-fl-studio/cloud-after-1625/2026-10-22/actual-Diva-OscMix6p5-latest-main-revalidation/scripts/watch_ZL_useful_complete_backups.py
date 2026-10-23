"""Keep actual matching running; publish useful complete FL20 checkpoints.
Each kit is rendered, independently parsed, ZIP-extracted and actually replayed
before a scoped normal Git push. This does not claim exact reference matching.
"""
from pathlib import Path
import argparse,datetime,fcntl,gzip,hashlib,json,os,re,shutil,subprocess,time,traceback,urllib.request
from win_vst3 import D
B=D.parent;P=Path('/workspace/divalead');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
BASE=P/'diva-lead/research/native-low-latency-effects';PUBLIC=BASE/'local-fl-studio/cloud-after-1625/2026-10-22'
STATE=N/'ZL_USEFUL_COMPLETE_BACKUP_CONTROLLER.json';STOP=N/'zl-useful-full-backup.stop';OWNER='actual-ZL-useful-full-kit-backups';PY='/workspace/.venvs/divalead/bin/python'
env=dict(os.environ,PYTHONPATH=f'{D}:/tmp/divalead-native-effects:{B}',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):
 for k in range(10):
  try:return json.loads(Path(p).read_text())
  except json.JSONDecodeError:
   if k==9:raise
   time.sleep(.05)
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def fetch_main():
 for attempt in range(4):
  try:
   subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True)
   return
  except subprocess.CalledProcessError:
   if attempt==3:raise
   time.sleep(2**attempt)
def push_and_confirm(commit):
 # A transient upstream503 must not invalidate an already verified kit.
 # Retry only normal pushes; conflicts and a persistent failure still surface.
 for attempt in range(4):
  try:
   subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
   assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
   return
  except (subprocess.CalledProcessError,AssertionError):
   if attempt==3:raise
   time.sleep(2**attempt)
def read_public_bytes(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(url,timeout=40)as response:return response.read()
  except (urllib.error.URLError,TimeoutError):
   if attempt==3:raise
   time.sleep(2**attempt)
def record(phase,**kw):
 o=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),starttime=Path(f'/proc/{os.getpid()}/stat').read_text().split()[21],phase=phase,only_three_held_notes=True,reference_match_reached=False,actual_FL_GUI_validation_pending=True,**kw)
 q=STATE.with_suffix('.partial');q.write_text(json.dumps(o,indent=2)+'\n');q.replace(STATE)
def alive(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
def initializing_main_after(stored_pid):
 expected=os.fsencode(str(D/'continue_ZL_matching.py'))
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   if int(proc.name)!=stored_pid and expected in(proc/'cmdline').read_bytes().split(b'\0')and alive(int(proc.name)):return int(proc.name)
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 return None
def protected():
 result={}
 for line in git('ls-tree','HEAD:diva-lead').splitlines():
  name=line.split('\t',1)[1]
  if re.fullmatch(r'v\d+-wip',name):result['diva-lead/'+name]=git('rev-parse','HEAD:diva-lead/'+name)
 for line in git('ls-tree','HEAD').splitlines():
  name=line.split('\t',1)[1]
  if re.fullmatch(r'Diva_lead_v\d+_WIP_checkpoint.zip',name):result[name]=git('rev-parse','HEAD:'+name)
 for d in list(PUBLIC.glob('WIP[0-9][0-9]'))+list(PUBLIC.glob('ZL-WIP[0-9][0-9]')):
  rel=d.relative_to(P).as_posix()
  if git('ls-tree','HEAD','--',rel):result[rel]=git('rev-parse','HEAD:'+rel)
 for name in ['local-fl-studio/2026-10-22','after-DSP-arrival/checkpoint-WIP','after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']:
  rel=(BASE/name).relative_to(P).as_posix();result[rel]=git('rev-parse','HEAD:'+rel)
 return result
def aggregate():
 hashes={};rel=PUBLIC.relative_to(P).as_posix()
 for line in git('ls-tree','-rl','HEAD','--',rel).splitlines():
  info,path=line.split('\t',1);a=info.split();p=P/path
  if a[1]!='blob'or p.name=='SHA256SUMS.txt':continue
  b=p.read_bytes()if p.is_file()else subprocess.check_output(['git','-C',str(P),'cat-file','blob',a[2]])
  hashes[p.relative_to(PUBLIC).as_posix()]=hashlib.sha256(b).hexdigest()
 for p in PUBLIC.rglob('*'):
  if p.is_file()and p.name!='SHA256SUMS.txt':hashes[p.relative_to(PUBLIC).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 (PUBLIC/'SHA256SUMS.txt').write_text(''.join(h+'  '+p+'\n'for p,h in sorted(hashes.items())))
def copy_evidence(src,dst,include_audio=False):
 dst.mkdir()
 for p in src.iterdir():
  if not p.is_file()or p.suffix in ['.f32','.log','.exe','.dll','.msi']:continue
  if p.suffix=='.wav'and not include_audio:continue
  if p.suffix=='.tsv'or(p.suffix=='.json'and p.stat().st_size>150000):
   b=p.read_bytes();g=gzip.compress(b,mtime=0);assert gzip.decompress(g)==b;(dst/(p.name+'.gz')).write_bytes(g)
  else:shutil.copyfile(p,dst/p.name)
def build(code,candidate=None):
 record('freezing_accepted_component_for_next_full_kit',code=code)
 canonical=D/f'ZL-auto-export-input-{code}';assert not canonical.exists()
 jobs=[('freeze_ZL_export_input.py',['--destination',str(canonical)]+(['--candidate',str(candidate)]if candidate else[]))]
 # Export each candidate with its own verified native base; never revert native settings.
 for stem in ['build','finalize']:
  s=(D/f'{stem}_ZL05_kit.py').read_text().replace('ZL05','ZL'+code).replace('ZL_05','ZL_'+code).replace('ZL 05','ZL '+code).replace('ZL-best-continuation-export-02',canonical.name)
  name=f'{stem}_ZL{code}_kit.py';(D/name).write_text(s);jobs.append((name,[]))
 for name,args in jobs:
  if name.startswith('finalize'):
   count=len(read(canonical/'candidate-research-only.json')['ZL_allpass_bands']);p=D/name;p.write_text(p.read_text().replace('2 All Pass',str(count)+' All Pass'))
  record('actual_full_kit_render_parse_restore_and_replay',code=code,script=name)
  with(N/f'auto-{code}-{name}.log').open('w')as out:subprocess.run([PY,'-B',str(D/name),*args],env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
def publish(code):
 label=f'Diva_ZL_{code}_WIP';kit=B/f'FL20_ZL_{code}_WIP';canonical=D/f'ZL-auto-export-input-{code}'
 report=read(kit/'verification/ZL_FULL_VERIFICATION.json');proof=read(kit/'verification/ZIP_ACTUAL_REPLAY_PROOF.json');choice=read(canonical/'candidate-research-only.json')
 assert len(proof['all12_native_saved_states_exact'])==12 and all(r['component_bytes_exact']for r in proof['actual_active_state_container_replay'])
 assert report['ZL_impulse']['declared_PDC_frames']==0 and report['ZL_impulse']['first_response_delay_frames']==0
 pause=R/'auto-backup.pause';created=False
 if pause.exists():assert read(pause)['owner']=='authorized-local-backed-copy-cleanup-20261023'
 else:
  with pause.open('x')as f:json.dump(dict(owner=OWNER,PID=os.getpid(),reason='publish a rendered/replayed complete ZL kit'),f)
  created=True
 try:
  with(R/'auto-backup-Git.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
   fetch_main();subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
   before=git('rev-parse','HEAD');old=protected();dest=PUBLIC/f'ZL-WIP{code}';dest.mkdir()
   for name in [label+'.flp',label+'_complete_WIP.zip',f'AB_REFERENCE_ZL{code}_WIP.mp3','FL_STUDIO_RU.md','README_RU.md']:
    shutil.copyfile(B/name if name.endswith('.zip')else kit/name,dest/name)
   (dest/'verification').mkdir()
   for p in(kit/'verification').iterdir():
    if p.is_file()and p.suffix!='.wav':shutil.copyfile(p,dest/'verification'/p.name)
   research=PUBLIC/f'ZL{code}-validated-continuation';research.mkdir();scripts=research/'scripts';scripts.mkdir()
   for name in ['freeze_ZL_export_input.py',f'build_ZL{code}_kit.py',f'finalize_ZL{code}_kit.py','watch_ZL_useful_complete_backups.py','continue_ZL_matching.py','study_ZL_extra_allpass.py','merge_confirmed_ZL_extra_allpass.py','fl20_vst3_state.py','win_vst3.py','prepare_native_base_for_combined_ZL.py','package_verified_native_base.py','study_native_EQ_with_ZL.py','study_native_WS_with_ZL.py','backup_finite_ZL_study.py','study_ZL_high_band_dynamics.py','probe_real_ZL_upward_band.py','merge_confirmed_ZL_high_band_dynamics.py']+[n for n in ['study_ZL_extra_allpass_LR.py','merge_confirmed_ZL_extra_allpass_LR.py']if(D/n).exists()]:
    compile((D/name).read_text(),name,'exec');shutil.copyfile(D/name,scripts/name)
   for name in ['study_actual_Diva_tone_in_current_ZL_context.py','prepare_audited_Diva_OscMix6p5.py','adopt_Diva_source_OscMix6p5.py']:
    p=D/name
    if p.exists():compile(p.read_text(),name,'exec');shutil.copyfile(p,scripts/name)
   copy_evidence(canonical,research/'canonical-export-input')
   if choice.get('native_base_archive_path'):
    archive=Path(choice['native_base_archive_path']);assert hashlib.sha256(archive.read_bytes()).hexdigest()==choice['native_base_archive_SHA256']
    registry=PUBLIC/'rebased-native-bases';registry.mkdir(exist_ok=True);saved=registry/archive.name
    if saved.exists():assert saved.read_bytes()==archive.read_bytes()
    else:shutil.copyfile(archive,saved)
    (research/'NATIVE_BASE_ARCHIVE_PROVENANCE.json').write_text(json.dumps(dict(archive=saved.relative_to(PUBLIC).as_posix(),SHA256=choice['native_base_archive_SHA256'],restore_parent=str(B),native_base_export_directory=choice['native_base_export_directory']),indent=2)+'\n')
   if code=='06':
    copy_evidence(D/'ZL-extra-allpass-after-ZL05-01',research/'extra-causal-allpass-study',True)
    copy_evidence(D/'ZL-confirmed-extra-allpass-merge-01',research/'extra-allpass-current-control-merge',True)
    for name in ['LEGACY_IDLE_CONTROLLERS_RETIRED_FOR_CURRENT_ZL_MATCHING.json','ZL_POST_EXTRA_ALLPASS_MERGE_RESTART.json']:
     shutil.copyfile(N/name,research/name)
   if (D/'ZL-extra-allpass-LR-after-ZL06-01/completion.json').exists()and not list(PUBLIC.glob('ZL*-validated-continuation/LR-causal-study')):
    copy_evidence(D/'ZL-extra-allpass-LR-after-ZL06-01',research/'LR-causal-study',True)
    if(D/'ZL-confirmed-extra-allpass-LR-merge-01/completion.json').exists():copy_evidence(D/'ZL-confirmed-extra-allpass-LR-merge-01',research/'LR-current-control-merge',True)
   live=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');(research/'FL20_ZL_CONTINUOUS_CONTROLLER.json').write_text(json.dumps(live,indent=2)+'\n')
   count=len(choice['ZL_allpass_bands']);dynamic_count=len(choice['ZL_dynamic_bands']);parameter_count=37+2*count+7*dynamic_count
   native_note='Настройки12 штатных эффектов перенастроены совместно с ZL.'if choice.get('native_parameters_changed')else'Настройки12 штатных эффектов сохранены.'
   source_note='Diva OscMix изменён с6.3 на6.5 после реальных source- и full-chain-проверок. ARP/ADSR/ноты сохранены.'if choice.get('source_tone_changed_since_ZL16')else'Источник Diva сохранён.'
   guide=f'''# ZL{code} — полный промежуточный комплект

Полного совпадения с оригиналом ещё нет. Продолжается подбор только на трёх
длинных входящих нотах41→37→36 на фразу, фраза дважды; движение делает ARP Diva.
{source_note} {native_note} Бесплатный ZL Equalizer2 v1.4.1
на SUM:12staticPeak+{count}AllPass+{dynamic_count}dynamicPeak, MinimumPhase/lookahead0.

- [Полный ZIP: FLP, WAV, Diva, MIDI,17FST, VSTpreset, проверки](ZL-WIP{code}/{label}_complete_WIP.zip).
- [A/B: оригинал0с → ZL{code} с4,168с](ZL-WIP{code}/AB_REFERENCE_ZL{code}_WIP.mp3).
- [Инструкция FL Studio20, официальный установщик эквалайзера](ZL-WIP{code}/FL_STUDIO_RU.md).

Принятый исходный cohort: {choice['source_accepted_cohort']}, mean{choice['loss']:.9f}.
Новый полный экспорт6 mean**{report['mean_original_objective']:.9f}**;
независимая распаковка ZIP и ещё6 настоящих рендеров
mean**{proof['six_fresh_whole_chain_mean']:.9f}**. Тот же полный исходный референс,
тот же критерий. Это не процент воспринимаемого сходства. Обычный wet Chorus
варьируется между дублями. Данные всех610 параметров взяты из реального компонента.

Все12 native state bytes проверены. Компонент ZL из FLP/FST/VSTpreset точен.
Целый тракт при нулевой глубине Chorus: максимальный остаток
{proof['whole_native_plus_ZL_zero_depth_max_abs_error']},
bit-exact={proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']}.
ZL заявилPDC0; импульсный первый отклик0. Это не ASIO/wholeDAW измерение.
Новый FLP разобран отдельно, но не открыт/экспортирован в GUI FL на вашемПК.
Fallback загрузка штатных FST и ZL FST описана в инструкции.

Дополнительные AllPass сначала проверялись отдельными фактическими
исследованиями и повторно против актуального mainBEST. В этом комплекте
реальный компонент содержит {count} AllPass; все они входят в дальнейший
поиск. Объявленная задержка и первый импульсный отклик проверены выше.
Legacy stock-only matcher, watcher и старый spectralFinish Gitpublisher
завершены на idle границе. Их сохранённые версии остаются в Git.

Старые локальные копии выгружены по прямому разрешению пользователя; версии
и история GitHub сохранены. Подробности и команды восстановления:
[журнал места и предыдущий полный ZL05](ZL05_CONTINUATION_RU.md).
Актуальный основной процесс определяется N/FL20_ZL_CONTINUOUS_CONTROLLER.json
и реальными PID/starttime. Число параметров читается из активных полос компонента:
сейчас{parameter_count}. Этот snapshot не доказывает работу процесса после остановки среды.
Отдельный watch_ZL_useful_complete_backups.py сохраняет полезные улучшения
полными комплектами после реального рендера, разбора и проверки ZIP.
Оригинал используется только для анализа/A-B, никогда не подмешивается в синтез.
'''
   (PUBLIC/f'ZL{code}_CONTINUATION_RU.md').write_text(guide,encoding='utf-8');(research/'README_RU.md').write_text(guide,encoding='utf-8')
   p=PUBLIC/'README_RU.md';p.write_text(f'[Актуальный полный ZL{code}: ZIP, A/B, FL20](ZL{code}_CONTINUATION_RU.md).\n\n'+p.read_text(),encoding='utf-8')
   header=f'''BEGIN_LATEST_COMPLETE_ZL{code}_VARIABLEPARAM
LATEST COMPLETE KIT ZL{code}. Read local-fl-studio/cloud-after-1625/2026-10-22/ZL{code}_CONTINUATION_RU.md and ZL-WIP{code}/FL_STUDIO_RU.md. Acceptedcohort{choice['source_accepted_cohort']} mean{choice['loss']:.9f}; actualfullexport6mean{report['mean_original_objective']:.9f}; NEW ZIP replay6mean{proof['six_fresh_whole_chain_mean']:.9f}. All12native state bytes exact, actualZLcomponent FLP/FST/VSTpreset verified, wholezero-depth maxerror{proof['whole_native_plus_ZL_zero_depth_max_abs_error']}/bitexact{proof['whole_native_plus_ZL_zero_depth_audio_bit_exact']}. OrdinarywetChorusvaries. No complete-reference-match/human-audition/newFLGUIexport/ASIOlatency/freshmachineclaim. Onlythreeincomingheldnotes41->37->36 perphrase twice/internalARP unchanged. Diva_source_SHA256={choice["native_base"]["source_manifest"]["source_preset_SHA256"]}; source_tone_changed_since_ZL16={bool(choice.get("source_tone_changed_since_ZL16"))}. Nativebase={choice.get("native_base_export_directory","legacybase17")}; native_settings_rebased={bool(choice.get("native_parameters_changed"))}. Original onlyanalysis/AB, noMistaTowa. Free officialZL1.4.1 Windowsx64 VST3 downloaded separately, MinimumPhase/lookahead0/PDC0/impulse0.

CURRENT REAL MATCHER D/continue_ZL_matching.py, N/FL20_ZL_CONTINUOUS_CONTROLLER.json, D/ZL-continuous65/BEST_CANDIDATE.json. ActualactiveAllPass derivedfromcomponentXML; now12staticPeak+{count}AllPass+{dynamic_count}dynamicPeak+OutputGain ->{parameter_count}params. The directory ZL-continuous65 retains its historical name. Check actualPID/starttime/hosts; snapshots are not permanent evidence. FourrealVST3workers/train+2heldout+paired6, robust>max(.0005,3SEM), all12validationWAVs losslessarchived+SHAverified, componentbytesexact and2NEWcoldinstances rtol8eps/atol1e-12/actualerrorrecorded, hotcold diagnosticonly. Root64MiB/tmp112MiB observedreserves, finite-cohortstop N/zl-continuation.stop. Ownednumericpauseexternal-ZL-continuous65-refinement. Prior idle native stock143848, watcher144989 and spectralFinish Gitpublisher14628 are RETIRED, not just paused. N/fl20-corrected-search.stop intentionally keeps legacy stockcontrollers retired; don't restart them against this externalbranch. N/zl-continuation.stop is only temporary for legitimatefinitehandoffs and currently should be absent. New watch_ZL_useful_complete_backups.py handles usefulcompletebackups via its own instance lock plus shared Gitlock and ownedGitpause. User requests continuous work/fullGitbackups, no per-trialquestions, internetFL20plugins allowed.

STORAGE prior authorizedcleanup preserved allGit versions/history/treeOIDs and currentinputs.1024checkoutoldZIP/audio+247tmp+844oldprivate copies omitted onlyafterblobexact origin verification. Restore individualskippedcheckout with git restore --ignore-skip-worktree-bits -- exactpath; restoreprivate via recordedgitshowpath. Retained~1GiB232oldarchives rebalanced /tmp->/workspace/offline-storage withSHAverifieddirectorysymlink. Don't blindly restoreallcopies. Preserve aggregateSHA256SUMS for omitted ZL04ZIP viaGitblob. Full latestkit06+ stays onGitHub. Everynewexport must derivephysicalarraysfromREALcomponentXML+610readbacks; old inherited metadata maybestale. Unsupported x95guard retained; use extendedZLexporter, preserveall2+4+8WS curves andsource. Onboardingdraft is saved/unpublished fromolderturn, not a current Publishclaim or blocker.
END_LATEST_COMPLETE_ZL{code}_VARIABLEPARAM

'''
   p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,BASE/'start_skill_current.md')
   aggregate();git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
   assert all(x.startswith('diva-lead/research/native-low-latency-effects/')for x in git('diff','--cached','--name-only').splitlines())
   git('commit','-m',f'Back up verified ZL{code} full FL20 kit and continued causal phase refinement');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+x)==oid for x,oid in old.items())
   push_and_confirm(commit)
   checks=[]
   for rel in [f'ZL-WIP{code}/{label}_complete_WIP.zip',f'ZL-WIP{code}/AB_REFERENCE_ZL{code}_WIP.mp3',f'ZL-WIP{code}/FL_STUDIO_RU.md',f'ZL{code}_CONTINUATION_RU.md']:
    p=PUBLIC/rel
    b=read_public_bytes('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())
    assert b==p.read_bytes();checks.append(dict(path=rel,bytes=len(b),HTTP_byte_exact=True))
   receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP'+code,all_old_complete_kit_and_numbered_tree_OIDs_preserved=True,HTTP_checks=checks,complete_ZIP_SHA256=hashlib.sha256((B/(label+'_complete_WIP.zip')).read_bytes()).hexdigest(),original_objective_export_mean=report['mean_original_objective'],ZIP_replay_mean=proof['six_fresh_whole_chain_mean'],reference_match_reached=False)
   (N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');record('verified_complete_kit_pushed',publication=receipt);print('ZL_FULL_KIT_PUSHED',json.dumps(receipt),flush=True)
 finally:
  if created and pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
def watch():
 startup_deadline=time.monotonic()+45
 while not STOP.exists():
  main=read(N/'FL20_ZL_CONTINUOUS_CONTROLLER.json');running=alive(main['owner']['PID']);latest=read(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json');code=latest['full_kit'][-2:];public_mean=read(PUBLIC/f'ZL-WIP{code}/verification/ZL_FULL_VERIFICATION.json')['mean_original_objective'];best=read(D/'ZL-continuous65/BEST_CANDIDATE.json')
  pending=initializing_main_after(main['owner']['PID'])if not running else None
  if pending and time.monotonic()<startup_deadline:
   record('waiting_for_new_actual_matcher_controller_initialization',actual_new_main_PID=pending,prior_controller_PID=main['owner']['PID']);time.sleep(.25);continue
  record('monitoring_actual_matching_for_next_useful_complete_kit',main_PID=main['owner']['PID'],actual_main_alive=running,main_phase=main['phase'],private_best_mean=best['loss'],latest_public_kit='ZL'+code,latest_public_mean=public_mean)
  useful=best['loss']<public_mean-(.006 if running else .001)
  if useful:
   reserves={p:shutil.disk_usage(p).free/2**20 for p in ['/workspace','/tmp']}
   if reserves['/workspace']<192 or reserves['/tmp']<180:record('stopped_before_full_kit_at_observed_storage_reserve',reserves=reserves);return
   number=max(int(p.name[-2:])for p in PUBLIC.glob('ZL-WIP[0-9][0-9]'))+1;new=f'{number:02}'
   if(D/f'ZL-auto-export-input-{new}').exists()or(B/f'FL20_ZL_{new}_WIP').exists():raise RuntimeError('Partial prior export exists; preserve and diagnose instead of overwriting')
   build(new);publish(new)
  elif not running:
   record('ended_after_actual_numeric_matcher_stopped',main_phase=main['phase'],latest_public_kit='ZL'+code,private_best_mean=best['loss']);return
  time.sleep(10)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--publish-existing');a.add_argument('--watch',action='store_true');args=a.parse_args()
 with(N/'zl-useful-backup-instance.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   if args.publish_existing:publish(args.publish_existing)
   if args.watch:watch()
  except BaseException:record('failed_preserve_reviewable_files_and_diagnose',error=traceback.format_exc());raise
