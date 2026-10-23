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
  for name in ['backup_latest_native_continuation.py','backup_best_after_postLR_research.py','fl20_curve.py','search_fl20_controls.py','fit_fl20_EQ76_scaled.py','probe_fl20_extraMS_EQ.py','run_extraMS_EQ_finite.py','probe_fl20_postLR_EQ_phase20.py','run_postLR_EQ_phase20_finite.py','compare_research_postLR_to_current.py','run_postLR_current_comparison.py','probe_fl20_source_prepost_EQ.py','run_source_prepost_EQ_finite.py','create_Diva_pan_fixture.py','audit_Diva_pan_source.py','run_Diva_pan_source_profiles.py','create_Diva_plate_fixture.py','audit_Diva_plate_source.py','run_Diva_plate_source_profiles.py','compare_supported_native_candidates24_archived.py','diagnose_Diva_Plate_note_residue.py','archive_rejected_native_WAVs.py','archive_rejected_native_WAVs_batch2.py','native_note_residue.py','diagnose_native_signed_spectral_errors.py','probe_fl20_detail8_WS.py','run_detail8_WS_finite.py','fl20_curve_detail8_supported_proposal.py','verify_detail8_curve_integration.py','compare_detail8_supported_proposals24_archived.py','maintain_native_scratch_space.py','continue_corrected_fl20.py','archive_historical_AB_cache.py','run_detail8_integration_and_backup.py','publish_fl20_WIP.py','export_fl20_checkpoint.py','restore_corrected_workspace.py','watch_useful_full_native_backups.py']:
   p=B/name;compile(p.read_text(),str(p),'exec');shutil.copyfile(p,D/'scripts'/name);shutil.copyfile(p,N/'FL20-corrected/runtime-scripts'/name)
  for name in ['fl_native_fl20_postLR_host.c','fl_native_fl20_extraMS_host.c','fl_native_fl20_source_prepost_host.c']:shutil.copyfile(B/'tools'/name,D/'scripts'/name)
  statefiles=['FL20_CORRECTED_SEARCH_CONTROLLER.json','FL20_POST_RESEARCH_BEST_BACKUP.json','FL20_EXTRA_MS_EQ_FINITE.json','FL20_POST_LR_EQ_PHASE20_FINITE.json','FL20_POST_LR_CURRENT_COMPARISON_FINITE.json','FL20_LOCAL4_INTEGRATION_AND_LR_REPAIR.json','FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP.json','FL20_OLD_OVERWRITTEN_HOST_BUFFERS_CLEANUP_BATCH2.json','HISTORICAL_AB_CACHE_LOSSLESS_ARCHIVING.json','FL20_SOURCE_PRE_POST_EQ_FINITE.json','FL20_DIVA_PAN_SOURCE_PROFILES.json','FL20_DIVA_PLATE_SOURCE_PROFILES.json','COMPLETED_RESTORE_ANALYSIS_FIXTURE_DEDUPLICATION.json','REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING.json','REJECTED_NATIVE_WAV_LOSSLESS_ARCHIVING_BATCH2.json','OLD_ASSESSMENT_WORKER_SCRATCH_CLEANUP.json','OLD_UNREFERENCED_NATIVE_HOST_OUTPUT_CLEANUP_BATCH3.json','DIVA_PLATE_FULL_NATIVE_NOTE_RESIDUE_DIAGNOSTIC.json','FL20_DETAIL8_WS_FINITE_PROFILE.json','HISTORICAL_AB_ARCHIVE_STAGING_DUPLICATES_CLEANUP.json','FL20_DETAIL8_INTEGRATION_AND_BACKUP.json','FL20_NATIVE_MAINTENANCE_CONTROLLER_HANDOFF.json','ORIGINAL_REFERENCE_ATTACHMENT_BYTE_IDENTITY.json','NATIVE15_EXPORTED_CAPTURE_POINTER_CORRECTION.json','FL20_USEFUL_FULL_BACKUP_WATCHER.json']
  for name in statefiles:
   if(N/name).exists():shutil.copyfile(N/name,proof/name)
  for name in ['EXTRA_MS_HOST_BUILD.json','POST_LR_HOST_BUILD.json','SOURCE_PREPOST_HOST_BUILD.json','DRY_DIVA_PLATE_RAW_NOTE_LEAKAGE_DIAGNOSTIC.json','NATIVE14_OLD_NOTE_LEAKAGE_STAGE_DIAGNOSTIC.json','ORIGINAL_NATIVE14_SUBHARMONIC_DIAGNOSTIC.json','DETAIL8_PROPOSED_HELPER_LEGACY_CURVE_BYTE_COMPATIBILITY.json','NATIVE14_SIGNED_SPECTRAL_ERRORS.json','NATIVE15_SIGNED_SPECTRAL_ERRORS.json']:
   if(B/name).exists():shutil.copyfile(B/name,proof/name)
  for p in N.glob('NATIVE_HOST_SCRATCH_MAINTENANCE_*.json'):shutil.copyfile(p,proof/p.name)
  extra_restore=B/'corrected-restoration-WIP15-capture-path-check'
  if(extra_restore/'RESTORATION_PROOF.json').exists():copy_jsons(extra_restore,proof/extra_restore.name)
  shutil.copyfile(N/'FL20-corrected/BEST_CANDIDATE.json',proof/'LATEST_FULLY_VALIDATED_SUPPORTED_CANDIDATE.json')
  for rootname in ['fl20-20261022T230716Z-0001','fl20-post-LR-EQ-02','fl20-post-LR-EQ-phase20-01','post-LR16-20-vs-current-independent24-01','fl20-extra-MID-SIDE-EQ16-01','fl20-source-pre-post-WS-EQ16-01','paired-two-physical-Pan-profiles-independent24-01','fresh-FL05_Pan_minus20_profile14-source-audit','fresh-FL05_Pan_zero_profile14-source-audit','fresh-FL05_PlateWet_zero_profile14-source-audit','fresh-FL05_PlateWet_0p1_profile14-source-audit','paired-physical-PlateWet-zero-and-0p1-direct-independent24-01','fl20-Diva-PlateWet-zero-EQ76-profile14-01','fl20-Diva-PlateWet-zero-controls-profile14-01','fl20-Diva-PlateWet-0p1-EQ76-profile14-01','fl20-Diva-PlateWet-0p1-controls-profile14-01','paired-physical-PlateWet-zero-and-0p1-refitted-independent24-01','fl20-WS-detail8-curve-01','detail8-WS-integration-audit-01','paired-supported-detail8-vs-current-independent24-01']:
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
  phase_descriptions=[]
  for name in ['FL20_DIVA_PLATE_SOURCE_PROFILES.json','FL20_DETAIL8_WS_FINITE_PROFILE.json','FL20_DETAIL8_INTEGRATION_AND_BACKUP.json']:
   if(N/name).exists():
    state=read(N/name);result=state.get('independent_result',state.get('completion',{}))
    phase_descriptions.append(name+': '+state['phase']+'. '+json.dumps(result,ensure_ascii=False))
  work_snapshot='\n\n'.join(phase_descriptions)
  kit_choice=read(kit/'verification/candidate.json')
  detail_curve=kit_choice.get('waveshaper_detail_bump_adjustment')
  detail_text=('Дополнительно приняты8 узких поправок smooth_detail_bumps8_v1: '+json.dumps(detail_curve)+'. Все2+4+8 коэффициентов входят в native состояние и общий helper для fitting/export/replay; отдельно проверены реальные12 states и zero-depth audio, затем независимые24+24.\n')if detail_curve is not None else'Детальная кривая8 остаётся исследовательской до успешной интеграции и независимой проверки.\n'

  guide=f'''# Native WIP{code}: полный промежуточный комплект

[Короткое A/B: оригинал → Native WIP{code}](listening-Native{code}/AB_REFERENCE_NATIVE{code}_WIP.mp3).
Наш вариант начинается с4.168с. [Полный ZIP: FLP/WAV/Diva/MIDI/16FST/проверки](WIP{code}/{label}_complete_WIP.zip).
[Как открыть в FL Studio20](WIP{code}/FL_STUDIO_RU.md).

Уточнён гармонический баланс в прежней цепи SOURCE → MID/SIDE → SUM. Источник: настоящий Diva
OscMix6.3, PW KeyFollow+1, VCA ModDepth−58. Три удерживаемые ноты на фразу,
две фразы, внутренний ARP. Поддерживаемая кривая WaveShaper сохранена в
состоянии native плагина:2 исходных коэффициента и4 локальные поправки
smooth_local_bumps4_v1; текущая поправка[0,0,0.025,0].

{detail_text}

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
не принят по этому прямому тесту. Его отдельные EQ76/controls refit и новая
независимая проверка описаны в FL20_DIVA_PLATE_SOURCE_PROFILES.json.
Проверка8 узких поправок WaveShaper поверх2+4 прежних завершена;
итог интеграции показан выше и в FL20_DETAIL8_INTEGRATION_AND_BACKUP.json.
Её новая поддерживаемая metadata принимается только после реального
state/audio round-trip и независимого сравнения.
Общий старый критерий не менялся; residue измеряется отдельно. Смотрите также
FL20_DETAIL8_WS_FINITE_PROFILE.json,
затем corrected controller с проверкой PID/starttime/cmdline.
Снимки ниже — история, не текущий статус. Никакого полного совпадения нет.

Статус на момент резервной копии:

{work_snapshot}

[Снимок состояния и проверки](proofs/{proof.name}/).
Сохранены все номерные версии, старые полные комплекты и полезные captures.
Для места удалены только проверенные перезаписываемые рабочие буферы.
Исторические A/B cache и captures завершённых отвергнутых cohorts сжаты
без потерь; SHA каждого WAV проверен до освобождения несжатой копии.
Исходники и релизы сохранены; пооперационные квитанции включены в proofs.
'''
  (D/('WIP'+code+'_CONTINUATION_RU.md')).write_text(guide,encoding='utf-8')
  link=f'[Актуальный полный Native WIP{code}, короткое A/B и продолжающийся подбор](WIP{code}_CONTINUATION_RU.md).\n\n';r=D/'README_RU.md';s=r.read_text();r.write_text(s if link in s else link+s,encoding='utf-8')
  live_main=read(N/'FL20_CORRECTED_SEARCH_CONTROLLER.json');private_best=read(N/'FL20-corrected/BEST_CANDIDATE.json')
  header=f'''BEGIN_LATEST_NATIVE_FULL_CONTINUATION
LATEST COMPLETE SUPPORTED NATIVE WIP{code}. Read WIP{code}_CONTINUATION_RU.md first. This block supersedes older latest-kit, source, curve and startup statements below. Full ZIP has FLP/WAV/Diva/MIDI/16FST/FL20 guide, short original->Native{code} A/B starts4.168sec. Full actual DLL export6 mean{report['mean_original_objective']:.9f}, std{report['std_original_objective']:.9f}, prior full WIP{number-1:02} mean{previous:.9f}. ZIP restored into NEW directory: all12 actual native states, real Diva program in FLP and zero-depth routing audio bit-exact;6 ordinary free-running-Chorus replays mean{restore['six_actual_full_capture_mean']:.9f}, std{restore['six_actual_full_capture_std']:.9f}. No exact wet-WAV, subjective audition, perceptual percentage, fresh-machine or FL GUI claim. Original-reference WAV SHA7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f matches the user's attachment byte-for-byte. Never use MistaTowa or reference samples as synthesis input. Only3 held incoming notes per phrase, two phrases, original internal ARP/ADSR/MIDI preserved.

SUPPORTED SOURCE/CURVES: latest complete-kit source_manifest and actual effGetChunk are authoritative. Source remains OscMix6.3/PWKeyFollow+1/VCA ModDepth-58/Pan-39.33/Plate2 Wet1.12 unless a NEW audited manifest explicitly changes it. Shared fl20_curve must preserve every present coefficient group and Chorus overrides; apply(x95) alone is wrong. Parent2 and local4 smooth_local_bumps4_v1 remain supported. Detail status: {detail_text}

COMPLETED RESEARCH, DO NOT RESTART: old corrected-context ensemble3 EQ, repaired post-LR EQ16/phase20 vs NEW incumbent, ExtraMS EQ16 and source preEQ->WS->postEQ16 were not adopted. Pan-20 andPan0 each got own actual-source EQ76 and controls; final independent24+24 was1.628857 vs1.572446, rejected. Diva PlateWet0/0.1 raw h2p/native chunk/281params/12MIDI verified; ONLY parameter235 changed. Dry Wet0 reduced old-note half-carrier residue24-27dB through full old graph, but direct old-EQ result was worse; own EQ76+controls refits/four-candidate selection/independent24+24 finished1.608987 vs1.571871, rejected. These source studies used the earlier2+4 curve and are history, not current jobs. Detail8 research finished398 cases and independent24+24:1.557243 vs1.572324. Prospective supported helper matched actual saved12 states and zero-depth audio exactly; separate comparison vs current gave1.557453 vs1.571896, robust. Inspect integration result before declaring installed or starting any follow-up. All research-only unintegrated graphs retain not_compatible_with_standard_x95_exporter=true; never use ordinary x95 export for unsupported topology.

CURRENT WORK IS NUMERIC MATCHING, NOT AN OLD FINITE JOB. Inspect N/FL20_CORRECTED_SEARCH_CONTROLLER.json and verify actual PID/starttime/cmdline plus actual current native child/hosts. Snapshot at this backup: controller{live_main['controller']['PID']}, phase{live_main['phase']}, private validated mean{private_best['loss']:.9f}. This is a snapshot, not proof that those PIDs are still running. Current matcher alternates actual EQ76 coordinate/scaled fits and full controls; all metadata is preserved. Corrected host excludes ONLY Chorus from128 silent warm blocks. Old native-search.stop stays; never restart high-latency Finish/obsolete continue_native_chorus.py. Current objective local_full_original_criteria_FL20_context_v1 is unchanged; note residue is a separate diagnostic. Private best can improve beyond latest complete public kit. Do not call WIP complete reference match. No new user-PC/FL GUI control is exposed here.

USEFUL FULL BACKUP WATCHER: inspect N/FL20_USEFUL_FULL_BACKUP_WATCHER.json and actual PID/starttime/cmdline. It follows genuine matcher; useful robust private improvements >=.004 below best complete public mean get an owned pause AFTER a completed current cohort, complete native export/FST parsing/latency/real-FLP program/ZIP checks, normal Git push, actual new-directory ZIP replay12 states/Diva program/zero-depth control/6 fresh captures, short AB and updated handoff, then matching resumes. Never start a duplicate watcher. It does not install an unverified new source/graph. useful-full-backup-watcher.stop or main stop ends it; dead genuine matcher is diagnosed, not silently revived. Existing Git pause/flock protocol remains mandatory. Preserve all numbered releases/root ZIPs and ALL already complete kit tree OIDs.

STORAGE AND CAPTURE PATHS: bounded maintenance in current controller deletes only verified duplicate archive staging and unreferenced inactive overwritten host scratch, with SHA receipts. Source/recorded validation captures/model/releases retained; historical rejected WAVs are losslessly archived and verified. Third-party .vscode JSONC is not task audio metadata. A metadata pointer in existing WIP15 candidate referred to its earlier independent capture while loss described exported median; actual full WAV/FLP/FST/ZIP bytes were correct and remain immutable. Separate correction receipt reassessed exact exported WAV loss1.557143503153 and verified local/public/ZIP bytes. Future export and restoration now point recorded_audio to actual checkpoint full WAV; restored path exists and its bytes match. Do not mutate complete WIP15 to fix metadata. Use latest exporter/restorer and correction sidecar for analysis.

FINITE SNAPSHOTS AT BACKUP (HISTORY): {work_snapshot}
Continue real source/native matching until complete reference match or observed limits; no per-trial user questions. Saved onboarding drafts are not publication or proof of fresh-machine/PC GUI execution.
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
