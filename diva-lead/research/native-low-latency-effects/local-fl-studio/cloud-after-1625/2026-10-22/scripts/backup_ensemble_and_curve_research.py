"""Back up real research code/proofs; completed playable WIP trees stay immutable."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
base=P/'diva-lead/research/native-low-latency-effects';D=base/'local-fl-studio/cloud-after-1625/2026-10-22'
OWNER='phase-ensemble-and-local-WS-research-backup';pause=R/'auto-backup.pause'
def read(p):return json.loads(p.read_text())
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():
 return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
with pause.open('x')as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
 deadline=time.monotonic()+90
 while read(R/'auto-backup-state.json')['phase']!='paused_for_manual_Git_work':assert time.monotonic()<deadline;time.sleep(1)
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
  subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');old=protected()
  keep=[p.relative_to(P).as_posix()for p in D.glob('WIP[0-9][0-9]')if p.is_dir()]+['diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22','diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP','diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']
  trees={p:git('rev-parse','HEAD:'+p)for p in keep}
  scripts=['fit_fl20_EQ76_ensemble.py','run_ensemble_finite.py','probe_fl20_local4_WS.py','run_local4_WS_finite.py','backup_ensemble_and_curve_research.py',
      'fl20_curve.py','search_fl20_controls.py','fit_fl20_EQ76_scaled.py','verify_local4_curve_integration.py',
      'compare_supported_native_candidates24.py','probe_fl20_postLR_EQ.py','run_postLR_EQ_finite.py',
      'run_local4_integration_and_LR_repair.py','publish_fl20_WIP.py','make_direct_reference_AB.py',
      'probe_fl20_postLR_EQ_phase20.py','run_postLR_EQ_phase20_finite.py','compare_research_postLR_to_current.py',
      'run_postLR_current_comparison.py','backup_best_after_postLR_research.py','probe_fl20_extraMS_EQ.py','run_extraMS_EQ_finite.py']
  for name in scripts:
   s=B/name;compile(s.read_text(),str(s),'exec');shutil.copyfile(s,D/'scripts'/name);shutil.copyfile(s,N/'FL20-corrected/runtime-scripts'/name)
  shutil.copyfile(B/'tools/fl_native_fl20_postLR_host.c',D/'scripts/fl_native_fl20_postLR_host.c')
  shutil.copyfile(B/'tools/fl_native_fl20_extraMS_host.c',D/'scripts/fl_native_fl20_extraMS_host.c')
  listening=D/'listening-Native13';listening.mkdir(exist_ok=True)
  for src in (B/'listening-Native13-01').iterdir():
   target=listening/src.name
   if target.exists():assert target.read_bytes()==src.read_bytes()
   else:shutil.copyfile(src,target)
  now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=D/'proofs'/('ensemble-and-local-curve-'+now);dest.mkdir(exist_ok=False)
  states={}
  for name in ['FL20_CORRECTED_SEARCH_CONTROLLER.json','FL20_ENSEMBLE_EQ_FINITE.json','FL20_LOCAL4_WS_FINITE_PROFILE.json','FL20_POST_LR_EQ_FINITE.json','FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json','FL20_POST_LR_EQ_PHASE20_FINITE.json','FL20_POST_LR_CURRENT_COMPARISON_FINITE.json','FL20_POST_RESEARCH_BEST_BACKUP.json','FL20_EXTRA_MS_EQ_FINITE.json']:
   if(N/name).exists():states[name]=read(N/name);shutil.copyfile(N/name,dest/name)
  for name in ['LOCAL4_WS_BASELINE_GUARD.json','POST_LR_HOST_BUILD.json','EXTRA_MS_HOST_BUILD.json','WIP12_STEREO_BAND_DIAGNOSTIC.json']:
   if(B/name).exists():shutil.copyfile(B/name,dest/name)
  for name in ['FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP.json','FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP_BATCH2.json','WIP13_DIRECT_AB_ZIP_GUIDE_HTTP.json']:
   if(N/name).exists():shutil.copyfile(N/name,dest/name)
  shutil.copyfile(N/'FL20-corrected/BEST_CANDIDATE.json',dest/'LATEST_FULLY_VALIDATED_SUPPORTED_CANDIDATE.json')
  for rootname in ['fl20-EQ76-ensemble3-01','fl20-EQ76-ensemble3-independent-01','fl20-WS-local4-curve-01','local4-WS-integration-audit-01','local4-current-EQ-independent24-01','fl20-post-LR-structural-repair-02','fl20-post-LR-EQ-02','fl20-post-LR-EQ-phase20-01','post-LR16-20-vs-current-independent24-01','fl20-20261022T230716Z-0001','fl20-extra-MID-SIDE-EQ16-01']:
   root=B/rootname
   if(root/'completion.json').exists()or(root/'PROOF.json').exists():
    folder=dest/rootname;folder.mkdir()
    for p in root.glob('*.json'):
     data=p.read_bytes()
     if len(data)>200000:
      packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(folder/(p.name+'.gz')).write_bytes(packed)
     else:shutil.copyfile(p,folder/p.name)
  guide='''# Продолжение подбора после Native WIP12

Последний полный воспроизводимый комплект: [Native WIP13](WIP13_CONTINUATION_RU.md).
Полное совпадение с оригиналом ещё не достигнуто. Поисковые настройки
принимаются только после независимой проверки и не объявляются final.

Проверяются два направления:

- EQ76 подбирается по среднему ошибки трёх настоящих WS/Chorus-рендеров.
  Ещё два рендера не участвуют в обучении; после подбора заново рендерится
  полная цепь, по12 проходов нового и исходного вариантов. При выигрыше
  проводится ещё отдельный выбор и12+12 контрольных проходов.
- Четыре плавные локальные поправки WaveShaper теперь поддерживаются общим
  кодом fitting/export/restore. Все12 native состояний и zero-depth аудио
  побитно совпали с фактически сохранённой DLL-кривой. На текущем улучшенном
  EQ новая кривая прошла выбор12 captures, затем независимые24+24 captures:
  1.575384 против1.578485, SEM0.000317. Принята в полный Native WIP13.
- Измерение WIP12 показало сильный перевес левого верха:5–10kHz около+10dB
  L/R против−0.41dB у оригинала. Исследуется отдельная post-L/R EQ-ветка из
  настоящих Stereo Shaper и EQ2. Первый тест обнаружил перепутанные матричные
  регуляторы; он не был принят. После исправления bypass контроль побитно
  совпал с исходной цепью. Активный flat EQ не предполагается тождественным:
  у настоящей DLL измерено изменение фазы. Сравнение идёт с исходным графом,
  а не только с новой flat-EQ основой. Новая ветка ещё не интегрирована в FLP.

Общий источник: настоящий Diva OscMix6.3/PW KeyFollow+1/VCA ModDepth−58,
только три длинные входящие ноты на фразу, внутренний ARP. Референс используется
лишь для анализа и A/B. Длинная задержка прежнего Finish не возвращается.

Конечные задания получают свою паузу только на границе завершённого цикла
основного поиска и освобождают её вfinally. Обычный подбор затем продолжается.
Для текущего состояния проверяйте живые PID/starttime/cmdline и актуальные
FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json, а затем
FL20_CORRECTED_SEARCH_CONTROLLER.json. Датированные JSON ниже являются снимками.
Это native-DLL проверки в подготовленной среде; новый контрольный экспорт
в GUI FL Studio остаётся отдельной незавершённой проверкой.

'''
  guide+='Последний снимок: '+now+'.\n\n'
  for name,d in states.items():guide+='- '+name+': `'+d['phase']+'`.\n'
  guide+='\n[Снимки и проверяемые результаты](proofs/'+dest.name+'/).\n'
  guide+='''

ПослеWIP13 обычный EQ76 в прежней цепи прошёл полную проверку приmean1.572109
против1.575753 у своей основы. Отдельная post-L/R EQ16 ветка дала1.570970
против старого WIP13-контроля1.576133; добавление4 SS delay/phase controls
дало1.570474 против старого1.575896. Это ещё не подтверждало выигрыш над
обновлённым EQ76. Поэтому отдельно проверены четыре новых/перенесённых
ветки, выбор12 captures, затем24+24:лучший1.570928 против текущего1.571932,
SEM0.000376. Порог3SEM не пройден; новая post-L/R схема НЕ принята.

FL20_POST_RESEARCH_BEST_BACKUP.json отвечает за полный бекап поддерживаемого
улучшенного EQ; его актуальное состояние проверяйте отдельно. Следующий
конечный тест FL20_EXTRA_MS_EQ_FINITE.json проверяет два дополнительных EQ2
в существующих MID/SIDE ветках, без новых маршрутов микшера. Новая схема
исследовательская и не принимается до фактического сравнения и интеграции.
Для места освобождены ещё92 завершённых перезаписываемых host-буфера225MiB,
все meaningful captures, исходники и старые полные комплекты сохранены.
'''
  (D/'ENSEMBLE_AND_CURVE_RESEARCH_RU.md').write_text(guide,encoding='utf-8')
  continuation='''# Native WIP13: полный промежуточный комплект

[Короткое A/B: оригинал → Native WIP13](listening-Native13/AB_REFERENCE_NATIVE13_WIP.mp3).
Native13 начинается с4.168с. [Полный ZIP: FLP/WAV/Diva/MIDI/16FST/проверки](WIP13/Diva_NATIVE_13_WIP_complete_WIP.zip).
[Как открыть в FL Studio20](WIP13/FL_STUDIO_RU.md).

Доработана форма искажения WaveShaper и сохранены улучшенные EQ/Chorus
настройки фонового поиска. Дополнительная кривая поддерживается fitting,
FST/FLP export, контролем задержки и восстановлением. Её saved native state
совпал с общим кодом по всем12 состояниям; zero-depth WAV побитно точен.
Независимая проверка24+24:1.575384 против1.578485, SEM0.000317.
Отдельный полный экспорт6 captures:mean1.575600/std0.001157; WIP12 mean1.580435.
Это значения ошибки, не проценты сходства. Выбран медианный WAV, а не лучший.

Источник прежний: OscMix6.3, PW KeyFollow+1, VCA ModDepth−58, три длинные
входящие ноты на фразу, две фразы; внутренний ARP сохранён. Цепь прежняя:
SOURCE → MID/SIDE → SUM. Длинная задержка Finish не возвращается.
Полного совпадения с оригиналом пока нет; новый экспорт в GUI FL ещё предстоит.

[Продолжение: независимые рендеры и частотный перекос L/R](ENSEMBLE_AND_CURVE_RESEARCH_RU.md).
После полного сохраненияWIP13 подбор продолжается. Тестовая отдельная L/R EQ
ветка ещё не является частьюWIP13. Сохранены все старые номерные версии и
полные native комплекты. Для места удалены только170 старых перезаписываемых
буферов native host в/tmp, освобождено416MiB; все meaningful captures,
исходники, пресеты, референсы и полные результаты опытов сохранены.
'''
  (D/'WIP13_CONTINUATION_RU.md').write_text(continuation,encoding='utf-8')
  r=D/'README_RU.md';link='[Текущий подбор по нескольким рендерам и уточнение WaveShaper](ENSEMBLE_AND_CURVE_RESEARCH_RU.md).\n\n';s=r.read_text();r.write_text(s if link in s else link+s,encoding='utf-8')
  header='BEGIN_PHASE_ENSEMBLE_CONTINUATION\nLATEST FULL WIP13 AND SUPPORTED LOCAL4 CURVE. Supersedes earlier descriptions that local4 WS metadata is unsupported. Read WIP13_CONTINUATION_RU.md and ENSEMBLE_AND_CURVE_RESEARCH_RU.md. Native WIP13 has complete FLP/WAV/Diva/MIDI/16FST/A-B/FL20 instructions. WaveShaper keeps two original coefficients plus waveshaper_local_bump_format=smooth_local_bumps4_v1 and four waveshaper_local_bump_adjustment values[0,0,.025,0]. Current fl20_curve helper, controls, EQ fits, export, latency and restoration support these fields; all12 actual native state bytes and zero-depth audio were independently exact against the research DLL-saved curve. Old research flag true remains rejected until explicit migration. Independent12 selection then24+24 current-incumbent holdout1.575384 vs1.578485 SEM.000317; full export6 mean1.575600/std.001157. Three-phase EQ ensemble itself was NOT accepted. Only3 held external MIDI notes per phrase, internal ARP, physical OscMix6.3/KeyFollow+1/VCA-58 source unchanged.\n\nCURRENT RESEARCH: verify actual N/FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json identities and then corrected controller. The old standalone local4 and first post-LR coordinator snapshots are completed/history. First post-LR trial failed because Stereo Shaper extraction controls were in the wrong order; original production graph was untouched. Correct isolation is L raw[0,12800,0,0,0,0], R[0,0,12800,0,0,0]. Repaired bypass zero-depth control is bit-exact; active flat extra EQ has actual phase change and is NOT assumed transparent. New research host fl_native_fl20_postLR_host.exe leaves original host unchanged, repurposes unused EQ nodes1/2 after SUM, appends SS isolation nodes15/16, and keeps corrected Chorus warmup. This extra graph remains RESEARCH ONLY and cannot be exported as an ordinary x95 candidate; not_compatible_with_standard_x95_exporter=true guards it. Actual post-LR fitting compares with the original graph on three training/two heldout prefixes and fresh12+12 full renders. Integrate actual FL mixer routing and real state replay/latency before any adoption. Native13 stays the complete usable kit meanwhile.\n\nOwned finite jobs finally release only their own N pause and normal matching resumes. All current complete kits/releases are immutable protected Git trees. Deleted only170 old terminated-host overwritten output buffers (416MiB) outside completed experiment roots, with hashes/completion/current-path guards; all recorded captures, sources and releases kept. Actual FL GUI export and full reference match remain pending. Do not claim perceptual listening, percentages, a fresh machine or user-PC control. Continue actual matching until full match or observed limits; no per-trial user questions.\nEND_PHASE_ENSEMBLE_CONTINUATION\n\n'
  private=R/'start_skill_current.md';text=private.read_text();text=re.sub(r'BEGIN_PHASE_ENSEMBLE_CONTINUATION\n.*?END_PHASE_ENSEMBLE_CONTINUATION\n\n','',text,flags=re.S);private.write_text(header+text);shutil.copyfile(private,base/'start_skill_current.md')
  files=sorted(p for p in D.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(D).as_posix()+'\n'for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
  assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Back up multi-realization native EQ fitting and guarded local WaveShaper research')
  commit=git('rev-parse','HEAD');assert protected()==old and all(git('rev-parse','HEAD:'+p)==v for p,v in trees.items())
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  path=D/'ENSEMBLE_AND_CURVE_RESEARCH_RU.md'
  with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+path.relative_to(P).as_posix(),timeout=30)as response:assert response.read()==path.read_bytes()
  receipt=dict(commit=commit,previous_HEAD=before,UTC=now,all_old_complete_kits_and_releases_preserved=True,documentation_HTTP_byte_exact=True,reference_match_reached=False)
  (N/'ENSEMBLE_AND_CURVE_RESEARCH_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
