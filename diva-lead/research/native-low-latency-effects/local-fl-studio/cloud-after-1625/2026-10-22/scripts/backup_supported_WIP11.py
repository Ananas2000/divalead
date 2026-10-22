from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
base=P/'diva-lead/research/native-low-latency-effects';D=base/'local-fl-studio/cloud-after-1625/2026-10-22';pause=R/'auto-backup.pause';owner='supported-curve11-continuation-backup'
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def read(p):return json.loads(p.read_text())
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
 deadline=time.monotonic()+90
 while read(R/'auto-backup-state.json')['phase']!='paused_for_manual_Git_work':assert time.monotonic()<deadline;time.sleep(1)
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');old=protected();paths=[p.relative_to(P).as_posix()for p in D.glob('WIP[0-9][0-9]')if p.is_dir()]+['diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22','diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP','diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip'];retained={p:git('rev-parse','HEAD:'+p)for p in paths}
  for name in ['fl20_curve.py','continue_corrected_fl20.py','start_corrected_fl20.py','search_fl20_controls.py','fit_fl20_EQ76_with_shapes.py','fit_fl20_EQ76_scaled.py','fit_fl20_EQ76_coordinates.py','verify_corrected_restoration.py','restore_corrected_workspace.py','verify_extended_curve_integration.py','export_fl20_checkpoint.py','verify_fl20_latency.py','publish_fl20_WIP.py','backup_supported_WIP11.py']:
   shutil.copyfile(B/name,D/'scripts'/name);shutil.copyfile(B/name,N/'FL20-corrected/runtime-scripts'/name)
  proof=D/'proofs/WIP11-restoration';proof.mkdir(exist_ok=True)
  for src,dest in [(B/'corrected-restoration-WIP11-curve-check/RESTORATION_PROOF.json','RESTORATION_PROOF.json'),(B/'corrected-restoration-WIP11-curve-check/actual-DLL-restoration-check/PROOF.json','ACTUAL_NATIVE_REPLAY.json')]:shutil.copyfile(src,proof/dest)
  for name in ['FL20_SUPPORTED_CURVE_HANDOFF.json','PLANNED_WS_INTEGRATION_HANDOFF.json']:shutil.copyfile(N/name,D/'proofs'/name)
  live=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');assert live['phase']=='corrected_pipeline_step_running'and live['numeric_workers_observed']==4
  assert live['waveshaper_curve_metadata']['waveshaper_curve_adjustment']==[0.2995963583619089,-0.4069654303527342]
  for ident in [live['controller'],live['child'],*live['actual_native_hosts']]:
   proc=Path('/proc')/str(ident['PID']);stat=(proc/'stat').read_text().split();assert stat[21]==ident['starttime']and stat[2]!='Z';assert(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()==ident['cmdline']
  (D/'proofs/WIP11_ACTUAL_CONTINUOUS_CURVE_FIT_SNAPSHOT.json').write_text(json.dumps(live,indent=2)+'\n')
  guide='''# Поддерживаемая кривая и полный WIP11

[Полный ZIP, FLP, WAV, Diva, MIDI и16 FST](WIP11/Diva_NATIVE_11_WIP_complete_WIP.zip).
[Инструкция для FL20](WIP11/FL_STUDIO_RU.md).
[A/B: оригинал → v83 → реальный FL05 → WIP11](WIP11/AB_ORIGINAL_V83_ACTUAL_FL05_Diva_NATIVE_11_WIP.mp3).
WIP11 начинается с12.504с. Три длинные ноты на фразу и ARP сохранены.
Полного совпадения с референсом или переносаv83 пока нет; новый GUI FL export
ещё предстоит. Это WAV настоящих native DLL и подготовленный FLP.

Ошибка независимого6+6 сравнения:1.586350→1.583332, SEM0.000655.
Отдельный экспорт6 рендеров: mean1.583736/std0.001179; WIP10 mean1.588693.
Эти числа — ошибки, не проценты сходства. В новом каталоге восстановлен
опубликованный ZIP:6 новых DLL captures mean1.582952/std0.000522. Все12 native
состояний и program Diva совпали с FLP/ZIP, контрольный zero-depth WAV побитно
точен. Это проверка подготовленной машины, не нового компьютера или GUI FL.

Состояние WaveShaper теперь включает дополнительные2 коэффициента. Они
поддерживаются fl20_curve.py во всех актуальных playback/fit/controls/export/
latency/restore scripts. Новый shared helper дал ровно те же12 native states
и zero-depth audio, что настоящий сохранённый native preset. Сам FLP/FST
содержит готовую кривую; пользователю не требуется вводить её формулу.

Для продолжения подбора x95 недостаточно: сохраняйте source_manifest,
chorus_overrides, waveshaper_curve_format=native_monotone_bump_v1 и
waveshaper_curve_adjustment=[0.2995963583619089,-0.4069654303527342].
Применяйте apply_candidate(c,x,candidate) из fl20_curve.py, затем Chorus
settings. Голый apply(x) потеряет кривую. Кандидат из раннего исследования
с флагом not_compatible_with_standard_x95_exporter=true по-прежнему не
принимается: используйте полностью проверенный WIP11 с поддерживаемым форматом.

Предыдущий старый curve fit03 намеренно закрыт через SIGINT/finally ради
проверенного улучшения; его training не принят. Новый controller установлен
только на наблюдаемой idle границе. Интеграционный pause снят после фактической
проверки восстановления. Сейчас идёт следующий реальный четырёхпроцессный fit
с кривой WIP11. Контролируется FL20_CORRECTED_SEARCH_CONTROLLER.json и реальные
PID/starttime/cmdline. Старые finite snapshots описывают завершённые задания.
Ротация: EQ coordinates → controls/SIDE/curve → scaled EQ → controls/SIDE/curve.
Все новые best требуют свежих полных6+6; полезные улучшения получают полный
комплект и Git backup. Прежние WIP, FL05, номерные версии и корневые ZIP сохранены.
'''
  (D/'WIP11_SUPPORTED_CURVE_CONTINUATION_RU.md').write_text(guide,encoding='utf-8');r=D/'README_RU.md';r.write_text('[Актуальное продолжение с поддерживаемой кривой WIP11](WIP11_SUPPORTED_CURVE_CONTINUATION_RU.md).\n\n'+r.read_text(),encoding='utf-8')
  header='''LATEST SUPPORTED WIP11 CURVE (2026-10-22). Supersedes earlier research-only WaveShaper guidance below. Read WIP11_SUPPORTED_CURVE_CONTINUATION_RU.md first. Complete WIP11 is public with real native WAV/FLP/MIDI/Diva/16 FST/A-B/FL20 guide. Original/v83 match=false; new actual FL GUI export still pending. Source remains audited OscMix6.3, PW KeyFollow+1, VCA ModDepth-58, THREE held notes per phrase repeated twice. Native curve is now fully supported by fl20_curve.py: preserve waveshaper_curve_format=native_monotone_bump_v1 and waveshaper_curve_adjustment=[0.2995963583619089,-0.4069654303527342] in addition to x95, source_manifest and chorus_overrides. Use apply_candidate(c,x,candidate), not bare apply(x), then restore/read back Chorus overrides. A real native saved-curve replay and this shared helper had all12 states byte-exact and zero-depth audio bit-exact. Independent6+6 error1.586350->1.583332, SEM0.000655; complete export mean1.583736/std0.001179. Public ZIP restored into a new folder passed all12 states, actual Diva program, zero-depth exact and6 full captures mean1.582952/std0.000522. Prepared-machine restore only; don't claim a new machine or actual FL GUI.

CURRENT WORK: new corrected controller is actually running the next four-worker EQ fit with supported WIP11 metadata. Verify FL20_CORRECTED_SEARCH_CONTROLLER.json and actual PID/starttime/cmdline; old scaled/source/extended-curve finite jobs are completed. Earlier old-curve fit03 was gracefully SIGINT-closed deliberately to validate the better curve, and its partial training was NOT adopted. Its old failure receipt is history, not a current service failure. Integration pause was removed only after actual restoration check. Rotation: EQ coordinates, native controls including SIDE and both curve coordinates, scaled EQ, native controls. Each acceptance needs full independent fresh6+6; full useful kits are pushed normally with protected Git pause/flock protocol. Old native-search.stop stays. Unsupported early research curve candidates still require explicit format migration; use the complete WIP11 candidate. If /tmp is gone, restore latest complete WIP into a NEW directory with current restore_corrected_workspace.py; it copies fl20_curve.py too, preserves real program/curve metadata, and rebuilds the padded source from audited raw. Existing native Wine/DLL runtime is separately required. No worktrees, no16-note MIDI transcription, no MistaTowa, no original-derived playback. User authorized continuing real work and useful full Git backups; don't ask per-trial questions.

'''
  private=R/'start_skill_current.md';private.write_text(header+private.read_text(),encoding='utf-8');shutil.copyfile(private,base/'start_skill_current.md')
  files=sorted(p for p in D.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(D).as_posix()+'\n'for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines());git('commit','-m','Verify supported WIP11 curve restoration and resume real native matching with complete curve metadata');commit=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+p)==v for p,v in retained.items());subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  checks=[]
  for rel in ['WIP11_SUPPORTED_CURVE_CONTINUATION_RU.md','scripts/fl20_curve.py','proofs/WIP11-restoration/ACTUAL_NATIVE_REPLAY.json']:
   path=D/rel
   with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path.relative_to(P).as_posix(),timeout=30)as response:data=response.read()
   assert data==path.read_bytes();checks.append(dict(path=rel,HTTP_byte_exact=True))
  receipt=dict(commit=commit,previous_HEAD=before,all_complete_kits_and_numbered_releases_preserved=True,HTTP_checks=checks,actual_supported_curve_fit_four_workers_observed=True,match_reached=False);(N/'WIP11_SUPPORTED_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
