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
  scripts=['fit_fl20_EQ76_ensemble.py','run_ensemble_finite.py','probe_fl20_local4_WS.py','run_local4_WS_finite.py','backup_ensemble_and_curve_research.py']
  for name in scripts:
   s=B/name;compile(s.read_text(),str(s),'exec');shutil.copyfile(s,D/'scripts'/name);shutil.copyfile(s,N/'FL20-corrected/runtime-scripts'/name)
  now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=D/'proofs'/('ensemble-and-local-curve-'+now);dest.mkdir(exist_ok=False)
  states={}
  for name in ['FL20_CORRECTED_SEARCH_CONTROLLER.json','FL20_ENSEMBLE_EQ_FINITE.json','FL20_LOCAL4_WS_FINITE_PROFILE.json']:
   if(N/name).exists():states[name]=read(N/name);shutil.copyfile(N/name,dest/name)
  for name in ['LOCAL4_WS_BASELINE_GUARD.json']:
   if(B/name).exists():shutil.copyfile(B/name,dest/name)
  for rootname in ['fl20-EQ76-ensemble3-01','fl20-EQ76-ensemble3-independent-01','fl20-WS-local4-curve-01']:
   root=B/rootname
   if(root/'completion.json').exists():
    folder=dest/rootname;folder.mkdir()
    for p in root.glob('*.json'):
     data=p.read_bytes()
     if len(data)>200000:
      packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(folder/(p.name+'.gz')).write_bytes(packed)
     else:shutil.copyfile(p,folder/p.name)
  guide='''# Продолжение подбора после Native WIP12

Последний полный воспроизводимый комплект: [Native WIP12](WIP12_CONTINUATION_RU.md).
Полное совпадение с оригиналом ещё не достигнуто. Новые поисковые настройки
не заменяют готовый WIP12 автоматически и не объявляются final.

Проверяются два направления:

- EQ76 подбирается по среднему ошибки трёх настоящих WS/Chorus-рендеров.
  Ещё два рендера не участвуют в обучении; после подбора заново рендерится
  полная цепь, по12 проходов нового и исходного вариантов. При выигрыше
  проводится ещё отдельный выбор и12+12 контрольных проходов.
- К существующей native-кривой WaveShaper добавляются четыре плавные локальные
  поправки. Каждая проверяется настоящей DLL. При нулевых поправках состояние
  кривой побитно совпадает с поддерживаемым исходным. Новые ненулевые поправки
  пока исследовательские: стандартный экспорт намеренно отказывает им,
  пока их формат не интегрирован и не проверен сохранением/загрузкой.

Общий источник: настоящий Diva OscMix6.3/PW KeyFollow+1/VCA ModDepth−58,
только три длинные входящие ноты на фразу, внутренний ARP. Референс используется
лишь для анализа и A/B. Длинная задержка прежнего Finish не возвращается.

Конечные задания получают свою паузу только на границе завершённого цикла
основного поиска и освобождают её вfinally. Обычный подбор затем продолжается.
Для текущего состояния проверяйте живые PID/starttime/cmdline и актуальные
FL20_ENSEMBLE_EQ_FINITE.json / FL20_LOCAL4_WS_FINITE_PROFILE.json, а затем
FL20_CORRECTED_SEARCH_CONTROLLER.json. Датированные JSON ниже являются снимками.
Это native-DLL проверки в подготовленной среде; новый контрольный экспорт
в GUI FL Studio остаётся отдельной незавершённой проверкой.

'''
  guide+='Последний снимок: '+now+'.\n\n'
  for name,d in states.items():guide+='- '+name+': `'+d['phase']+'`.\n'
  guide+='\n[Снимки и проверяемые результаты](proofs/'+dest.name+'/).\n'
  (D/'ENSEMBLE_AND_CURVE_RESEARCH_RU.md').write_text(guide,encoding='utf-8')
  r=D/'README_RU.md';link='[Текущий подбор по нескольким рендерам и уточнение WaveShaper](ENSEMBLE_AND_CURVE_RESEARCH_RU.md).\n\n';s=r.read_text();r.write_text(s if link in s else link+s,encoding='utf-8')
  header='BEGIN_PHASE_ENSEMBLE_CONTINUATION\nLatest research after full Native WIP12: read ENSEMBLE_AND_CURVE_RESEARCH_RU.md and actual N/FL20_ENSEMBLE_EQ_FINITE.json / FL20_LOCAL4_WS_FINITE_PROFILE.json. The three-phase EQ76 mean fit holds out2 more actual Chorus prefixes and requires fresh12+12 full-chain captures; an adopted improvement also passes separate selection/12+12 holdout. A queued research-only four-local-bump WS screen retains the existing two supported coefficients; zero extra bumps are byte-exact to current curve, but nonzero local bump metadata MUST NOT enter standard export until explicit integration plus actual native-state replay. No source/MIDI change: only3 held notes per phrase and original internal ARP. Existing corrected controller waits at owned finite boundaries; the finite jobs finally release only their own pause, and matching resumes. Verify current actual identities, do not treat historical snapshots as live work. Native WIP12 remains the latest complete playable backup until a separately verified full successor is published. Match and actual FL GUI validation remain pending.\nEND_PHASE_ENSEMBLE_CONTINUATION\n\n'
  private=R/'start_skill_current.md';text=private.read_text();text=re.sub(r'^BEGIN_PHASE_ENSEMBLE_CONTINUATION\n.*?END_PHASE_ENSEMBLE_CONTINUATION\n\n','',text,flags=re.S);private.write_text(header+text);shutil.copyfile(private,base/'start_skill_current.md')
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
