"""Back up the latest complete native kit's listening links, restoration and live research."""
from pathlib import Path
import datetime,fcntl,gzip,hashlib,json,re,shutil,subprocess,time,urllib.request
P=Path('/workspace/divalead');B=Path('/tmp/divalead-local-1625');N=Path('/workspace/divalead-work/native-low-latency-effects');R=Path('/workspace/divalead-work/three-held-continuation')
base=P/'diva-lead/research/native-low-latency-effects';D=base/'local-fl-studio/cloud-after-1625/2026-10-22'
OWNER='latest-complete-native-listening-restoration-and-research-backup';pause=R/'auto-backup.pause'
def read(p):return json.loads(Path(p).read_text())
def git(*args):return subprocess.check_output(['git','-C',str(P),*args],text=True).strip()
def protected():return sorted([s for s in git('ls-tree','HEAD:diva-lead').splitlines()if re.search(r'\tv\d+-wip$',s)]+[s for s in git('ls-tree','HEAD').splitlines()if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',s)])
def copy_jsons(src,dest):
 dest.mkdir(parents=True,exist_ok=True)
 for p in src.glob('*.json'):
  data=p.read_bytes()
  if len(data)>200000:
   packed=gzip.compress(data,mtime=0);assert gzip.decompress(packed)==data;(dest/(p.name+'.gz')).write_bytes(packed)
  else:shutil.copyfile(p,dest/p.name)
with pause.open('x')as f:json.dump(dict(owner=OWNER,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
 deadline=time.monotonic()+90
 while read(R/'auto-backup-state.json')['phase']!='paused_for_manual_Git_work':assert time.monotonic()<deadline;time.sleep(1)
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
  subprocess.run(['git','-C',str(P),'fetch','origin','main'],check=True);subprocess.run(['git','-C',str(P),'merge','--ff-only','origin/main'],check=True)
  before=git('rev-parse','HEAD');old=protected()
  wips=[p for p in D.glob('WIP[0-9][0-9]')if p.is_dir()];code=max(p.name[3:]for p in wips);number=int(code);kit=B/f'FL20_NATIVE_{code}_WIP';label=f'Diva_NATIVE_{code}_WIP'
  trees={p.relative_to(P).as_posix():git('rev-parse','HEAD:'+p.relative_to(P).as_posix())for p in wips}
  for rel in ['diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-22','diva-lead/research/native-low-latency-effects/after-DSP-arrival/checkpoint-WIP','diva-lead/research/native-low-latency-effects/after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']:trees[rel]=git('rev-parse','HEAD:'+rel)
  now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');proof=D/'proofs'/('WIP'+code+'-continued-'+now);proof.mkdir(exist_ok=False)
  listening=D/('listening-Native'+code);listening.mkdir(exist_ok=True)
  for src in (B/('listening-Native'+code+'-01')).iterdir():
   dest=listening/src.name
   if dest.exists():assert dest.read_bytes()==src.read_bytes()
   else:shutil.copyfile(src,dest)
  for name in ['backup_latest_native_continuation.py','backup_best_after_postLR_research.py','fl20_curve.py','search_fl20_controls.py','fit_fl20_EQ76_scaled.py','probe_fl20_extraMS_EQ.py','run_extraMS_EQ_finite.py','probe_fl20_postLR_EQ_phase20.py','run_postLR_EQ_phase20_finite.py','compare_research_postLR_to_current.py','run_postLR_current_comparison.py','probe_fl20_source_prepost_EQ.py','run_source_prepost_EQ_finite.py','create_Diva_pan_fixture.py','audit_Diva_pan_source.py','run_Diva_pan_source_profiles.py','create_Diva_plate_fixture.py','audit_Diva_plate_source.py','run_Diva_plate_source_profiles.py','compare_supported_native_candidates24_archived.py','diagnose_Diva_Plate_note_residue.py','archive_rejected_native_WAVs.py','archive_rejected_native_WAVs_batch2.py']:
   p=B/name;compile(p.read_text(),str(p),'exec');shutil.copyfile(p,D/'scripts'/name);shutil.copyfile(p,N/'FL20-corrected/runtime-scripts'/name)
  for name in ['fl_native_fl20_postLR_host.c','fl_native_fl20_extraMS_host.c','fl_native_fl20_source_prepost_host.c']:shutil.copyfile(B/'tools'/name,D/'scripts'/name)
  statefiles=['FL20_CORRECTED_SEARCH_CONTROLLER.json','FL20_POST_RESEARCH_BEST_BACKUP.json','FL20_EXTRA_MS_EQ_FINITE.json','FL20_POST_LR_EQ_PHASE20_FINITE.json','FL20_POST_LR_CURRENT_COMPARISON_FINITE.json','FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json','FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP.json','FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP_BATCH2.json','HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json','FL20_SOURCE_PRE_POST_EQ_FINITE.json','FL20_DIVA_PAN_SOURCE_PROFILES.json','FL20_DIVA_PLATE_SOURCE_PROFILES.json','COMPLETED_RESTORE_ANALYSIS_FIXTURE_DEDUPLICATION.json','REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING.json','REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING_BATCH2.json','OLD_ASSESSMENT_WORKER_SCRATCH_CLEANUP.json','OLD_UNREFERENCED_NATIVE_HOST_OUTPUT_CLEANUP_BATCH3.json','DIVA_PLATE_FULL_NATIVE_NOTE_RESIDUE_DIAGNOSTIC.json']
  for name in statefiles:
   if(N/name).exists():shutil.copyfile(N/name,proof/name)
  for name in ['EXTRA_MS_HOST_BUILD.json','POST_LR_HOST_BUILD.json','SOURCE_PREPOST_HOST_BUILD.json','DRY_DIVA_PLATE_RAW_NOTE_LEAKAGE_DIAGNOSTIC.json','NATIVE14_OLD_NOTE_LEAKAGE_STAGE_DIAGNOSTIC.json','ORIGINAL_NATIVE14_SUBHARMONIC_DIAGNOSTIC.json']:
   if(B/name).exists():shutil.copyfile(B/name,proof/name)
  shutil.copyfile(N/'FL20-corrected/BEST_CANDIDATE.json',proof/'LATEST_FULLY_VALIDATED_SUPPORTED_CANDIDATE.json')
  for rootname in ['fl20-20261022T230716Z-0001','fl20-post-LR-EQ-02','fl20-post-LR-EQ-phase20-01','post-LR16-20-vs-current-independent24-01','fl20-extra-MID-SIDE-EQ16-01','fl20-source-pre-post-WS-EQ16-01','paired-two-physical-Pan-profiles-independent24-01','fresh-FL05_Pan_minus20_profile14-source-audit','fresh-FL05_Pan_zero_profile14-source-audit','fresh-FL05_PlateWet_zero_profile14-source-audit','fresh-FL05_PlateWet_0p1_profile14-source-audit','paired-physical-PlateWet-zero-and-0p1-direct-independent24-01','fl20-Diva-PlateWet-zero-EQ76-profile14-01','fl20-Diva-PlateWet-zero-controls-profile14-01','fl20-Diva-PlateWet-0p1-EQ76-profile14-01','fl20-Diva-PlateWet-0p1-controls-profile14-01','paired-physical-PlateWet-zero-and-0p1-refitted-independent24-01']:
   root=B/rootname
   if(root/'completion.json').exists():copy_jsons(root,proof/rootname)
   elif(root/'PROOF.json').exists():copy_jsons(root,proof/rootname)
   elif(root/'STRUCTURAL_NATIVE_PROOF.json').exists():
    dest=proof/rootname;dest.mkdir();shutil.copyfile(root/'STRUCTURAL_NATIVE_PROOF.json',dest/'STRUCTURAL_NATIVE_PROOF.json')
  restoration=[]
  for name in ['corrected-restoration-WIP13-local4-check',f'corrected-restoration-WIP{code}-actual-check']:
   root=B/name
   if(root/'actual-DLL-restoration-check/PROOF.json').exists():
    dest=proof/name;dest.mkdir();shutil.copyfile(root/'RESTORATION_PROOF.json',dest/'RESTORATION_PROOF.json');shutil.copyfile(root/'actual-DLL-restoration-check/PROOF.json',dest/'ACTUAL_DLL_REPLAY.json');restoration.append(read(root/'actual-DLL-restoration-check/PROOF.json'))
  report=read(kit/'verification/NATIVE_PRESET_VERIFICATION.json');restore=next(r for r in restoration if r['source_checkpoint']=='WIP'+code)
  previous=read(D/f'WIP{number-1:02}/verification/NATIVE_PRESET_VERIFICATION.json')['mean_original_objective']
  guide=f'''# Native WIP{code}: полный промежуточный комплект

[Короткое A/B: оригинал → Native WIP{code}](listening-Native{code}/AB_REFERENCE_NATIVE{code}_WIP.mp3).
Наш вариант начинается с4.168с. [Полный ZIP: FLP/WAV/Diva/MIDI/16FST/проверки](WIP{code}/{label}_complete_WIP.zip).
[Как открыть в FL Studio20](WIP{code}/FL_STUDIO_RU.md).

Уточнены EQ в прежней цепи SOURCE → MID/SIDE → SUM. Источник: настоящий Diva
OscMix6.3, PW KeyFollow+1, VCA ModDepth−58. Три удерживаемые ноты на фразу,
две фразы, внутренний ARP. Поддерживаемая кривая WaveShaper сохранена в
состоянии native плагина:2 исходных коэффициента и4 локальные поправки
smooth_local_bumps4_v1; текущая поправка[0,0,0.025,0].

Отдельный полный экспорт6 captures:mean{report['mean_original_objective']:.9f},
std{report['std_original_objective']:.9f}; у WIP{number-1:02} mean{previous:.9f}.
Это критерий ошибки, не процент сходства. В ZIP медианный WAV, не лучший.
Только A/B выровнен по RMS; полный6с WAV48kHz stereoFLOAT32 не изменён.

ZIP восстановлен в новой папке этой подготовленной среды. Все12 native
состояний и реальный program chunk Diva совпали; zero-depth контроль
побитно точен. Шесть новых обычных рендеров:mean{restore['six_actual_full_capture_mean']:.9f},
std{restore['six_actual_full_capture_std']:.9f}. Работающий Chorus свободно
меняет повторные WAV. Это не тест новой машины или новый экспорт из GUI FL.
Полного совпадения с референсом пока нет; GUI экспорт ещё предстоит.

Проверены две отдельные post-L/R EQ/phase ветки. Их первоначальный выигрыш
относился к более старой основе. На обновлённом EQ, после выбора4 веток и
ещё24+24 независимых рендеров:1.570928 против1.571932, SEM0.000376;
порог3SEM не пройден. Эти новые маршруты не включены в комплект.

Дополнительные MID/SIDE EQ16 и цепь EQ→WaveShaper→EQ проверены на
настоящих DLL и не приняты. Физические Diva Pan−20 и Pan0 получили свои
EQ76 и controls fit: лучший независимый результат1.628857 против1.572446,
то есть хуже. Производственный источник и его Pan−39.33 сохранены.

Новое исследование: внутренний Plate2 Wet Diva1.12 оставляет предыдущую
ноту в октавных окнах заметно сильнее референса. Настоящая Diva с Wet0 и0.1
проверена по281 параметру,12 MIDI событиям и двум свежим загрузкам h2p/
реального native chunk; относительное изменение только index235. С Wet0
после полной прежней FX цепи half-carrier/carrier снизился на24–27dB.
Это спектральная диагностика остатка ноты, не процент сходства или шумомер.
Прямое сравнение с прежней обработкой пока хуже по полному критерию:
Wet0.1 mean1.635701 против1.571826, independent24+24. Поэтому сухой источник
не принят; сейчас получает собственные EQ76 и controls refit, затем новая
независимая проверка. Смотрите живые FL20_DIVA_PLATE_SOURCE_PROFILES.json,
затем corrected controller с проверкой PID/starttime/cmdline.
Снимки ниже — история, не текущий статус. Никакого полного совпадения нет.

[Снимок состояния и проверки](proofs/{proof.name}/).
Сохранены все номерные версии, старые полные комплекты и полезные captures.
Для места удалены только проверенные перезаписываемые рабочие буферы.
Исторические A/B cache и captures завершённых отвергнутых cohorts сжаты
без потерь; SHA каждого WAV проверен до освобождения несжатой копии.
Исходники и релизы сохранены; пооперационные квитанции включены в proofs.
'''
  (D/('WIP'+code+'_CONTINUATION_RU.md')).write_text(guide,encoding='utf-8')
  link=f'[Актуальный полный Native WIP{code}, короткое A/B и продолжающийся подбор](WIP{code}_CONTINUATION_RU.md).\n\n';r=D/'README_RU.md';s=r.read_text();r.write_text(s if link in s else link+s,encoding='utf-8')
  header=f'''BEGIN_LATEST_NATIVE_FULL_CONTINUATION
LATEST FULL SUPPORTED NATIVE WIP{code}. Read WIP{code}_CONTINUATION_RU.md first; it supersedes older latest-kit statements. Full ZIP includes FLP/WAV/Diva/MIDI/16FST/FL20 instructions. Short original->Native{code} A/B starts4.168sec. Actual export6 mean{report['mean_original_objective']:.9f}/std{report['std_original_objective']:.9f}, prior WIP{number-1:02} mean{previous:.9f}; latest ZIP restored into a NEW directory passed actual native12 states/real Diva program/bit-exact ZERO-DEPTH control,6 ordinary free-running-Chorus captures mean{restore['six_actual_full_capture_mean']:.9f}/std{restore['six_actual_full_capture_std']:.9f}. No exact wet-WAV, subjective listening, percentages, fresh-machine or FL GUI claim. Source OscMix6.3/PWKeyFollow+1/VCA-58 and only3 held external notes per phrase/two phrases/internal ARP unchanged. Current source manifest/VST chunk and all6 WS curve coefficients remain authoritative; fl20_curve supports2 parent plus4 smooth_local_bumps4_v1 values. All production fitting/export/restore must preserve them and Chorus overrides.

POST-LR RESEARCH FINISHED, NOT ADOPTED. Original incorrect isolation order was caught before adoption; repaired graph passed native zero-depth bypass bit-exact control. EQ16 and phase20 seemed better than oldNative13. Separate4-candidate selection then independent24+24 vs NEW supported EQ gave1.570928 vs1.571932 SEM.000376, below3SEM criterion; new6-insert post-LR topology not installed. Historical coordinator snapshots are completed. Current supported EQ76 had robust fresh1.572109 vs1.575753. Best full-backup coordinator completed; private supported best may continue improving past this full kit.

LATEST FINITE WORK: first inspect N/FL20_DIVA_PLATE_SOURCE_PROFILES.json and actual PID/starttime/cmdline, then FL20_CORRECTED_SEARCH_CONTROLLER.json. ExtraMS EQ16 and source preEQ->WS->postEQ16 finished negative; physical Diva Pan-20 andPan0 each got own EQ76+full controls and4-candidate selection/independent24+24:1.628857 vs1.572446, rejected. Do not restart these completed jobs. Original Pan-39.33 remains. New actual sources FL05_PlateWet_zero_profile14 and FL05_PlateWet_0p1_profile14 change ONLY Diva parameter235 relative to current6p3, all281/MIDI/ARP/ADSR/native chunk reload audited. PlateWet0 reduces upper-octave old-note half-carrier residue24-27dB through the full current native graph; this is a spectral diagnostic, not a hiss/perceptual score. Direct full native old-EQ comparison was worse(Wet0.1 independent1.635701 vscontrol1.571826); no adoption. Both sources now get OWN EQ76+full controls before fresh selection/independent24+24. Follow coordinator state; any new complete kit must be exported/state-round-tripped/FST-parsed/latency-checked/FLPprogram-checked/ZIP-verified/Git-pushed and restored in new directory before considered a supported WIP. Coordinator owns only its pause and releases after finite work; genuine supported4-host matching resumes. All research-only graph metadata stays guarded not_compatible_with_standard_x95_exporter=true. No unsupported graph in ordinary exporter. Preserve numbered releases/rootZIPs/all complete kit OIDs and Git pause/flock protocol. Only proven overwritten inactive scratch was deleted; rejected capture WAVs archived losslessly with per-file SHA verification, all source/model/public kits retained. Never revive completed jobs based on historical snapshots. Continue matching until full match or observed limits, no per-trial user questions.

END_LATEST_NATIVE_FULL_CONTINUATION

'''
  private=R/'start_skill_current.md';s=private.read_text();s=re.sub(r'BEGIN_LATEST_NATIVE_FULL_CONTINUATION\n.*?END_LATEST_NATIVE_FULL_CONTINUATION\n\n','',s,flags=re.S);private.write_text(header+s);shutil.copyfile(private,base/'start_skill_current.md')
  (base/'CLOUD_AFTER_LOCAL_1625_RU.md').write_text(f'[Актуальное продолжение: Native WIP{code}](local-fl-studio/cloud-after-1625/2026-10-22/WIP{code}_CONTINUATION_RU.md).\n\n'+(base/'CLOUD_AFTER_LOCAL_1625_RU.md').read_text(),encoding='utf-8')
  files=sorted(p for p in D.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt');(D/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(D).as_posix()+'\n'for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');assert all(p.startswith('diva-lead/research/native-low-latency-effects/')for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m',f'Back up WIP{code} direct A/B, actual ZIP replay and continued native timbre research');commit=git('rev-parse','HEAD')
  assert protected()==old and all(git('rev-parse','HEAD:'+p)==oid for p,oid in trees.items())
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  checks=[]
  for rel in [f'listening-Native{code}/AB_REFERENCE_NATIVE{code}_WIP.mp3',f'WIP{code}/{label}_complete_WIP.zip',f'WIP{code}/FL_STUDIO_RU.md',f'WIP{code}_CONTINUATION_RU.md']:
   p=D/rel
   with urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix(),timeout=30)as response:data=response.read()
   assert data==p.read_bytes();checks.append(dict(path=rel,bytes=len(data),HTTP_byte_exact=True))
  receipt=dict(commit=commit,previous_HEAD=before,checkpoint='WIP'+code,all_old_complete_kits_and_numbered_releases_preserved=True,HTTP_checks=checks,reference_match_reached=False)
  (N/'LATEST_NATIVE_FULL_CONTINUATION_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==OWNER:pause.unlink()
