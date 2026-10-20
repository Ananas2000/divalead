"""Back up physical source research/startup and freeze Git for exact config save."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');ROOT=P/'diva-lead/research/three-held-continuation';O=ROOT/'after-v76-runtime';PAUSE=R/'auto-backup.pause';OWNER='publish-post74-source-runtime'
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0',*a],cwd=P,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def immutable_copy(a,b):
 b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
 try:os.link(a,b)
 except OSError:shutil.copyfile(a,b)
 assert sha(a)==sha(b);return str(b)
scripts=['auto_backup_three.py','start_three_services.py','continue_post74joint_main.py','continue_post74joint_phase.py','continue_post74joint_balance.py','handoff_to_post74_source.py','probe_source_post74.py','run_source_post74_probe.py','probe_source_post74joint.py','run_source_post74joint_probe.py','prepare_post74_joint_source.py','run_source_post74proof.py','fit_post74_source_finish.py','run_source_post74fit.py','prove_post74_source_transplant.py','prove_post74_source_transplant02.py','verify_post74_source_registration.py','archive_post74_physical_screens.py','share_retired_root_wavs.py','discover_workspace_projects.py','publish_post74_runtime.py','build_three_v75.py','write_v75_docs.py','finalize_v75.py','verify_zip_windows_v75.py','run_full_v75_build.py','publish_full_v75.py','prepare_next_full_v75.py','refresh_post74_startup_guide.py','summarize_current_three_variants.py','build_three_v76.py','write_v76_docs.py','finalize_v76.py','verify_zip_windows_v76.py','run_full_v76_build.py','publish_full_v76.py','prepare_next_full_v76.py','probe_and_prove_post74_blend.py','run_source_post74blend.py','switch_to_post74_at_checkpoint.py']
diags=['post73-storage-sharing-summary.json','post73-fixed-fir-kernel-sharing.json','post73-completed-three-source-dedup.json','post73-retired-root-WAV-sharing.json','v74-publication-recovery.json','public-v74-verification.json','public-v75-verification.json','post74-source-registration-checks.json','post74-publisher-restart.json','v75-FL-instruction-file-checks.json','post74-source-handoff-state.json','source-post74fit-state.json','service-start-last.json','post74-checkout-discovery.json','active-three-source-family.json','current-three-note-variant-registry.json','v76-preparation-controller-state.json','v76-publisher-input-checks.json','first-post74-idle-handoff-state.json','post74-checkpoint-handoff-state.json','source-post74blend-state.json','new-source-cohort-readiness.json','public-v76-verification.json','v76-FL-instruction-file-checks.json']
for name in scripts+diags:assert (R/name).is_file(),name
assert json.loads((R/'post74-source-handoff-state.json').read_text())['phase'] in ['new_selected_source_cohort_started_budget2_1_1','old_source_remains_best_resume_current_cohort']
assert json.loads((R/'source-post74fit-state.json').read_text())['slot_released']
archives=Path('/tmp/divalead-post74-physical-archives');manifest=json.loads((archives/'manifest.json').read_text())
for row in manifest['archives']:assert sha(archives/row['file'])==row['SHA256']
while True:
 try:fd=os.open(PAUSE,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 except FileExistsError:time.sleep(2);continue
 with os.fdopen(fd,'w') as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
 break
for _ in range(90):
 state=json.loads((R/'auto-backup-state.json').read_text())
 if state['phase']=='paused_for_manual_Git_work':break
 time.sleep(1)
else:raise RuntimeError(state)
with (R/'auto-backup-Git.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
 O.mkdir(exist_ok=False);(O/'scripts').mkdir();(O/'diagnostics').mkdir()
 for name in scripts:shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
 for name in diags:shutil.copyfile(R/name,O/'diagnostics'/name)
 shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md')
 for p in sorted(archives.iterdir()):
  if p.is_file():immutable_copy(p,O/'physical-screen-archives'/p.name)
 for tag in ['post74','post74joint','post74proof','post74fit']:
  shutil.copyfile(R/('source-'+tag+'-state.json'),O/'diagnostics'/('source-'+tag+'-state.json'))
 shutil.copytree(R/'source-post74-blend',O/'coefficient-blend-research')
 shutil.copytree(R/'retired-PW-numeric-checkpoints',O/'unaccepted-retired-PW-checkpoints')
 for tag in ['source-post74-transplant','source-post74-transplant02']:
  shutil.copytree(R/tag,O/'combination-research'/tag,ignore=lambda d,ns:[n for n in ns if n.endswith(('.wav','.so','.dll','.exe','.tmp'))])
 # Reuse the same strict checker/exporter; do not duplicate already public proofs.
 p=R/'auto_backup_three.py';ns={'__file__':str(p),'__name__':'runtime_snapshot'};exec(compile(p.read_text().split("\nif '--check-only' in sys.argv:",1)[0],str(p),'exec'),ns)
 published={}
 for f in ROOT.rglob('validation.json'):
  if not (f.parent/'arbitrary-input-verification.json').is_file():continue
  try:published[Path(json.loads(f.read_text())['core_model']).parent.parent.name]=str(f.relative_to(P))
  except KeyError:pass
 preserved=[]
 for f in [R/'source-post74joint-basis/validation.json']+list(R.glob('post74joint-verified-*/validation.json')):
  d,family,base=ns['checked'](f)
  if f.parent.name in published:preserved.append(dict(private_model=f.parent.name,already_public=published[f.parent.name]));continue
  dest=O/'new-completed-proofs'/f.parent.name;ns['snapshot'](f.parent,dest);ns['export_numeric'](f,O/'new-numeric-runs'/f.parent.name)
  sourcebase=O/'matching-physical-source'
  if not sourcebase.exists():
   sourcebase.mkdir()
   for n in ['Diva_THREE_HELD_BASELINE.h2p','Diva_source.wav','Diva_before_spectral.wav','NEW-independent-base-pdc.wav','Diva_all281.tsv']:immutable_copy(base/n,sourcebase/n)
  write(dest/'portable-source.json',dict(source_family=family,source_base_relative=os.path.relpath(sourcebase,dest),is_selected_best=False,match_reached=False))
  preserved.append(dict(private_model=f.parent.name,new_public=str(dest.relative_to(P)),tone_score=d['tone_score']))
 write(O/'completed-proof-preservation.json',preserved)
 (O/'README_RU.md').write_text('''# Продолжение трёхнотного подбора после полного v76

[Полный v76](../../../v76-wip/README.md), [инструкция FL Studio](../../../v76-wip/FL_STUDIO_RU.md), [оригинал → v76](../../../v76-wip/AB_REFERENCE_V76_WIP.wav). v76 начинается с4,168с. Все прежние номерные версии сохранены. Точное совпадение ещё не достигнуто.

Проверены46 настоящих рендеров Diva:21 отдельных и25 совместных изменений. В physical-screen-archives/ сохранены исходные WAV, пресеты, все281 параметр, логи и метрики каждого случая; все распакованные члены сверены поSHA256. Непрошедшие ограничения пробы не объявлялись принятыми. Новая четырёхпараметрическая настройка имеет собственные заново построенные NEW и before-fixture; смешивание источников запрещено и проверено отрицательными контролями.

Комбинация новой Diva с последней подтверждённой обработкой прошла свежую Diva/Windows/native/ownNEW/fixture и все12 причинных случаев. Полный комплект76 дополнительно прошёл API/FXP/состояние/PDC/блоки/точную пересборку/фактическую DLL из чистогоZIP; HTTP-байты проверены. Сохранена и отдельная менее удачная попытка HF100. Первый проход учитывал все завершившиеся старые раунды. Затем шесть промежуточных наборов прежних коэффициентов дали новый подтверждённый результат; после него незавершённые новые попытки старого источника сохранены побайтовыми численными снимками в unaccepted-retired-PW-checkpoints/ и явно не считаются завершёнными проверенными звуками. Подбор переведён на новый лучший источник с тем же бюджетом2+1+1. Реальное состояние передачи — diagnostics/post74-source-handoff-state.json, текущее направление — active preference/JSON и startup guide. Старые PID в снимках не являются командами запуска.

Дополнительное объединение точных копий освободило2190036992 фактически измеренных байта на основном диске, сохранив пути и содержимое. Ничего уникального не удалено; историяGit не переписывалась. При последующем редактировании общей неизменяемой копии сначала требуется отдельныйinode. Не восстанавливать намеренно удалённые ненужные старые промежуточные кэши.

GUI FL Studio и субъективное прослушивание ассистентом не выполнялись. Лицензионная Diva не включена. MistaTowa не используется. Сохранение конфигурации среды не означает публикацию снимка или проверенное восстановление в новой задаче.
''')
 target=str(O.relative_to(P));git('add','--',target);assert all(x.startswith(target+'/') for x in git('diff','--cached','--name-only').splitlines());git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log');git('commit','-m','Preserve all physical three-note Diva trials and continuation on the best verified source')
 assert all(x.startswith(target+'/') for x in git('diff',before,'HEAD','--name-only').splitlines())
 head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
 for name in ['README_RU.md','start_skill_current.md','scripts/handoff_to_post74_source.py']:
  data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/'+name,timeout=60).read();assert data==(O/name).read_bytes()
 # Bounded archive contents were verified before the copy and Git object creation.
 first=manifest['archives'][0];remote=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+head+'/'+target+'/physical-screen-archives/'+first['file'],timeout=60).read();assert hashlib.sha256(remote).hexdigest()==first['SHA256']
 assert not git('status','--porcelain');write(R/'post74-runtime-public-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=head,remote_exact=True,HTTP_bytes_exact=True,all_numbered_releases_unchanged=True,all46_screens_archived=True,match_reached=False))
 write(R/'post74-runtime-ready-for-config.json',dict(commit=head,lock_held=True,owner=OWNER));print('POST74_RUNTIME_PUSHED_READY_FOR_CONFIG',head,flush=True)
 until=time.monotonic()+180
 while time.monotonic()<until and not (R/'post74-runtime-config-readback-complete.json').exists():time.sleep(2)
 assert json.loads(PAUSE.read_text())['owner']==OWNER;PAUSE.unlink();print('POST74_RUNTIME_GIT_LOCK_AND_PAUSE_RELEASED',flush=True)
