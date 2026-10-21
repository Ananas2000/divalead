"""Publish a proved native WIP, preserving all numbered releases and user DLLs."""
from pathlib import Path
import datetime,fcntl,hashlib,json,re,shutil,subprocess,sys,time,urllib.request,zipfile
P=Path('/workspace/divalead');R=Path('/workspace/divalead-work/three-held-continuation')
W=Path('/tmp/divalead-native-effects');N=Path('/workspace/divalead-work/native-low-latency-effects')
kit=Path(sys.argv[1]);owner=sys.argv[2] if len(sys.argv)>2 else 'native-auto-'+str(time.time_ns())
base=P/'diva-lead/research/native-low-latency-effects';d=base/'after-DSP-arrival'
proof=json.loads((kit/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
assert proof['actual_native_DLL_audio'] and proof['only_three_held_notes'] and not proof['match_reached']
chorus=proof.get('modulated_audio_sample_exact_expected') is False
if chorus:
 assert proof['preset_state_bytes_exact'] and proof['zero_depth_routing_audio_exact']
 assert len(proof['modulated_captures'])>=6 and proof['selected_capture_is_median_not_best']
 assert all(x['state_bytes_exact'] and x['zero_depth_routing_control_max_abs_error']<=2e-7 for x in proof['preset_round_trip'].values())
else:assert all(x['max_abs_error']<=2e-7 for x in proof['preset_round_trip'].values())
assert (kit/'verification/FST_INDEPENDENT_PARSE.json').is_file()
assert (kit/'verification/ORIGINAL_REFERENCE_COMPARISON.json').is_file()
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],text=True).strip()
def protected():
 return sorted([x for x in git('ls-tree','HEAD:diva-lead').splitlines() if re.search(r'\tv\d+-wip$',x)]+[x for x in git('ls-tree','HEAD').splitlines() if re.search(r'\tDiva_lead_v\d+_WIP_checkpoint.zip$',x)])
pause=R/'auto-backup.pause'
if pause.exists():assert json.loads(pause.read_text())['owner']==owner,'Another Git writer owns the pause'
else:
 with pause.open('x') as f:json.dump(dict(owner=owner,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()),f)
try:
 deadline=time.monotonic()+90
 while json.loads((R/'auto-backup-state.json').read_text())['phase']!='paused_for_manual_Git_work':
  assert json.loads(pause.read_text())['owner']==owner
  assert time.monotonic()<deadline,'Publisher did not acknowledge pause';time.sleep(1)
 with (R/'auto-backup-Git.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
  before=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==before
  current=d/'checkpoint-WIP/verification/candidate.json'
  if current.exists() and json.loads((kit/'verification/candidate.json').read_text())['loss']>=json.loads(current.read_text())['loss']:
   print('SKIPPED_PUBLICATION_CURRENT_NATIVE_CHECKPOINT_IS_BETTER',flush=True);raise SystemExit(0)
  old=protected();d.mkdir(exist_ok=True);scripts=d/'scripts';scripts.mkdir(exist_ok=True);diag=d/'diagnostics';diag.mkdir(exist_ok=True)
  names=['fl_native_chain_host.c','fl_native_probe.c','native_chain.py','native_features.py','native_harmonic_features.py','fit_native_joint.py','fit_native_harmonic.py','search_native_coordinates.py','search_native_original.py','native_original_objective.py','apply_native_candidate.py','native_fst.py','export_native_checkpoint.py','complete_native_checkpoint.py','verify_fst_with_pyflp.py','verify_native_latency_blocks.py','assess_native_reference.py','compare_to_v83.py','extract_dsp_archive.py','prepare_native_runtime.py','publish_native_progress.py','continue_native_search.py']
  for name in names:shutil.copyfile(W/name,scripts/name)
  for name in ['native_cpu_slots.py','probe_native_common_filters.py','probe_native_source_cleanliness.py','probe_native_lowwet_chorus.py','refit_native_chorus_EQ.py','export_native_chorus_checkpoint.py','search_native_chorus.py','search_native_chorus_controls.py','continue_native_chorus.py','start_native_chorus.py','pack_audio_git_objects.py','verify_chorus_runtime_after_prepare.py']:
   if (W/name).is_file():shutil.copyfile(W/name,scripts/name)
  for name in ['SIGNED_NATIVE_ORIGINAL_BAND_ERRORS.json']:
   if (W/name).is_file():shutil.copyfile(W/name,diag/name)
  for name in ['NATIVE_CHORUS_RUNTIME_REPEATED_PREPARE_CHECK.json','LOSSLESS_GIT_OBJECT_PACKING.json','LOSSLESS_AUDIO_GIT_PACKING.json','LEGACY_NATIVE_EQ_CONTROLLER_RETIRED.json']:
   if (N/name).is_file():shutil.copyfile(N/name,diag/name)
  for name in ['native-source-cleanliness','common-native-filter-grid-02','native-modulated-chorus-grid','native-lowwet-chorus-grid','native-chorus-EQ-refit']:
   src=W/name
   if src.is_dir():
    dest=diag/name;dest.mkdir(exist_ok=True)
    for path in src.glob('*.json'):
     if path.stat().st_size<2*1024**2:shutil.copyfile(path,dest/path.name)
  for name in ['staged-plugin-manifest.json','Fruity_WaveShaper_x64-default-state.bin']:shutil.copyfile(W/name,scripts/name)
  for name in ['DSP_ARCHIVE_EXTRACTION.json','FRESH_DIVA_THREE_SOURCE.json','DIRECT_EQ2_GAIN_PROOF.json','CORRECTED_CHORUS_REPEAT.json','RUNTIME_PREPARE_FIRST.log','RUNTIME_PREPARE_SECOND.log']:
   shutil.copyfile(W/name,diag/name)
  target=d/'checkpoint-WIP'
  if target.exists():
   assert json.loads((target/'verification/CHECKPOINT_KIND.json').read_text())['native_port_checkpoint'];shutil.rmtree(target)
  shutil.copytree(kit,target)
  assert not any(p.suffix.lower() in ['.dll','.exe','.rar'] for p in d.rglob('*') if p.is_file())
  state=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='native-low-latency-effects',current_blocker=None,missing_runtime_uploads=[],DSP_received_and_extracted=True,native_FL_audio_render_started=True,native_FST_round_trip_verified=True,declared_effect_PDC_frames=0,old_Finish_PDC_frames=12416,strict_transfer_target='v83 FULL_180BPM',v83_transfer_complete=False,only_three_held_notes=True,finished_native_presets=False,usable_technical_WIP_presets=True,FL_GUI_tested=False,reference_match_reached=False,main_complete_release_still='v83-wip',checkpoint='after-DSP-arrival/checkpoint-WIP',background_native_search_state='/workspace/divalead-work/native-low-latency-effects/NATIVE_SEARCH_CONTROLLER.json')
  for path in [base/'CURRENT_NATIVE_EFFECTS_STATE.json',N/'CURRENT_NATIVE_EFFECTS_STATE.json',W/'CURRENT_NATIVE_EFFECTS_STATE.json']:path.write_text(json.dumps(state,indent=2)+'\n')
  (base/'README_RU.md').write_text('''# Перенос на штатные эффекты FL Studio — продолжается

`dsp_ippv2_x64.rar` получен и успешно распакован. Настоящие родные DLL
запущены; созданы и проверены FST, полный WAV и A/B. Цепочка заявляет
0 сэмплов PDC против 12416 у старого Finish при 48 kHz.

**100% переноса v83 пока нет. По сравнению с оригиналом новая цепочка пока
хуже v83; основная законченная комплектация остаётся v83.**
Это технический промежуточный бекап для продолжения подбора.

- [Пресеты, WAV и инструкция](after-DSP-arrival/checkpoint-WIP/FL_STUDIO_RU.md)
- [Скачать весь технический WIP](after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip)
- [A/B: оригинал → v83 → штатные эффекты](after-DSP-arrival/checkpoint-WIP/AB_ORIGINAL_V83_NATIVE_WIP.mp3)
- [Проверки настоящих DLL и состояния](after-DSP-arrival/README_RU.md)

Присланные проприетарные DLL не включены в Git. Дополнительный файл сейчас
не запрашивается. Подбор сохраняет только три длинные входящие ноты.
''')
  (d/'README_RU.md').write_text('''# DSP получен: настоящий нативный рендер и FST

Архив 7369307 байт распакован через libarchive с успешной проверкой чтения.
DLL 40509224 байта, SHA256
`9ba8a03bf803b2ffd1165cafd55ccf4c51dddef52704a297112f47ef7df8bfbb`.
Никакие аудиофункции или проверки лицензии не подменялись.

Используются настоящие Fruity WaveShaper, Parametric EQ 2 и Stereo Shaper.
FST сохранены через Native SaveRestoreState; на свежих DLL их повторный
рендер совпал с исходной нативной цепочкой по всем отсчётам. Контейнеры FST
также прочитаны независимым PyFLP с явно описанной совместимостью Python 3.12.
FL Studio GUI здесь не запускался.

Для EQ2 и Maximus потребовалась GUI-палитра Artwork/Spectrum.bmp.
Создана только палитра, исходные DLL и их DSP не изменялись. Maximus
не входит в кандидат: этот исследовательский хост не реализует проверку
его лицензии. Chorus пока исключён из повторяемого кандидата: его LFO
даёт немного разные рендеры при новом запуске.

Гипотеза об ошибке EQ2 при обработке в одном буфере была **отозвана**:
прежний тест менял только Mid, поэтому закономерно смешивал L/R. Прямой
контроль до M/S подтверждает обычную шкалу Main dB×100 и отсутствие такого
смешивания. В хосте оставлены раздельные буферы входа/выхода.

Новая цепочка пока хуже v83 относительно оригинала. Проверки миграции
отдельно показывают ненулевую разность с v83. Последовательные приближения
оцениваются по оригиналу и по замороженному v83, а не объявляются готовыми
по уменьшению одного вспомогательного спектрального числа.

[Инструкция FL Studio](checkpoint-WIP/FL_STUDIO_RU.md).
[Полный промежуточный комплект](Diva_native_effects_WIP_checkpoint.zip).
Проверки в `checkpoint-WIP/verification`, код в `scripts`.

Подготовка runtime дважды выполнена в текущей среде. Это не независимая
проверка восстановления новой облачной машины. Присланные DSP/FL DLL остаются
приватными; `prepare_native_runtime.py` использует их существующие пути.
Xvfb :90 и Wine должны быть готовы до запуска рендеров. Нельзя пересобирать
исполняемые файлы хоста, пока подбор использует их.
''')
  if chorus:
   path=d/'README_RU.md';text=path.read_text()
   text=text.replace('Fruity WaveShaper, Parametric EQ 2 и Stereo Shaper.','Fruity WaveShaper, Chorus, Parametric EQ 2 и Stereo Shaper.')
   text=text.replace('FST сохранены через Native SaveRestoreState; на свежих DLL их повторный\nрендер совпал с исходной нативной цепочкой по всем отсчётам.','FST сохранены через Native SaveRestoreState. Байты всех десяти состояний\nсовпали после загрузки; аудиоконтроль с нулевой глубиной Chorus совпал\nпо отсчётам. Рабочая модуляция имеет свободную фазу LFO: её рендеры\nслегка различаются. Оценены шесть повторов, в комплекте средний по оценке.')
   text=text.replace('Chorus пока исключён из повторяемого кандидата: его LFO\nдаёт немного разные рендеры при новом запуске.','Chorus теперь включён со слабым подмешиванием 8% ручкой Mix слота\nмикшера. Ранние опыты с сильным подмешиванием были хуже; новый вариант\nпроверен с несколькими фазами LFO и оказался устойчиво лучше прежнего\nтехнического переноса. Для индивидуального FST выставь Mix слота вручную.')
   path.write_text(text.replace('8%',f"{proof['native_Chorus_mixer_slot_mix_percent']:.6g}%"))
  shutil.copyfile(R/'native-effects-priority.json',base/'diagnostics/native-effects-priority.json')
  shutil.copyfile(R/'start_skill_current.md',base/'start_skill_current.md')
  for folder in [target]:
   files=sorted(p for p in folder.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
   (folder/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(folder).as_posix()+'\n' for p in files))
  archive=d/'Diva_native_effects_WIP_checkpoint.zip'
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p in sorted(target.rglob('*')):
    if p.is_file():
     info=zipfile.ZipInfo('Diva_native_effects_WIP/'+p.relative_to(target).as_posix(),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
  files=sorted(p for p in d.rglob('*') if p.is_file() and p!=d/'SHA256SUMS.txt')
  (d/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(d).as_posix()+'\n' for p in files))
  git('add','--','diva-lead/research/native-low-latency-effects');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
  assert all(p.startswith('diva-lead/research/native-low-latency-effects/') for p in git('diff','--cached','--name-only').splitlines())
  git('commit','-m','Back up actual three-note FL native WIP with FST and low-latency verification')
  commit=git('rev-parse','HEAD');assert old==protected()
  subprocess.run(['git','-C',str(P),'push','origin','HEAD:main'],check=True)
  assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
  checked=[]
  for relative in ['CURRENT_NATIVE_EFFECTS_STATE.json','after-DSP-arrival/checkpoint-WIP/FL_STUDIO_RU.md','after-DSP-arrival/Diva_native_effects_WIP_checkpoint.zip']:
   local=base/relative;url=f'https://raw.githubusercontent.com/Ananas2000/divalead/{commit}/diva-lead/research/native-low-latency-effects/'+relative
   data=None
   for attempt in range(6):
    try:
     with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
     if data==local.read_bytes():break
    except Exception:
     if attempt==5:raise
    time.sleep(3)
   assert data==local.read_bytes();checked.append(dict(path=relative,SHA256=hashlib.sha256(data).hexdigest(),HTTP_byte_exact=True))
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,main_remote_matches=True,all_numbered_release_trees_and_root_ZIPs_unchanged=True,clean_worktree=True,HTTP_files=checked,native_to_v83_transfer_complete=False,original_reference_match_reached=False)
  (N/'native-latest-publication.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists() and json.loads(pause.read_text()).get('owner')==owner:pause.unlink()
