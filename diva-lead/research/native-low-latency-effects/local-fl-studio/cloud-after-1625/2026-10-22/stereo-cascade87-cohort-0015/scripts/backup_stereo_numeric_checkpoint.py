"""Back up each accepted TWO-ZL cohort, all24 validation WAVs, FLP/FST/ZIP."""
from pathlib import Path
import argparse,datetime,fcntl,gzip,hashlib,json,os,runpy,shutil,subprocess,time,zipfile,zlib
from stereo_artifact_helpers import replace_primary
from fl20_vst3_state import vstpreset
A=Path(__file__).resolve().parent;D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
parser=argparse.ArgumentParser();parser.add_argument('--cohort',required=True);args=parser.parse_args();work=Path(args.cohort).resolve();summary=json.loads((work/'completion.json').read_text());assert summary['robust_improvement']and len(summary['captures'])==8
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='stereo_numeric_checkpoint');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause';full=PUBLIC/'ZL-WIP24';old=(full/'verification/ZL24_PRIMARY_COMPONENT.bin').read_bytes();primary=(work/'candidate-component.bin').read_bytes();post=(work/'fixed-post-component.bin').read_bytes();assert post==(full/'verification/ZL24_POST_COMPONENT.bin').read_bytes()
def claim_pause():
 deadline=time.monotonic()+240
 while True:
  try:return pause.open('x')
  except FileExistsError:
   if time.monotonic()>deadline:raise TimeoutError('Existing publisher pause still owned; preserve current private cohort')
   time.sleep(.25)
with claim_pause()as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='back up accepted two-ZL source/control/candidate pairs and complete playable WIP'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main'),'New remote PC work requires review before further cloud publication'
  before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/('stereo-cascade87-'+work.name);dest.mkdir(exist_ok=False)
  for p in work.iterdir():
   if not p.is_file()or p.suffix in ['.f32','.log']:continue
   if p.name.endswith('WAVs.tar.gz'):os.link(p,dest/p.name)
   else:shutil.copyfile(p,dest/p.name)
  playable=dest/'FL20_STEREO_WIP';playable.mkdir();presets=playable/'presets';shutil.copytree(full/'presets',presets)
  (playable/'Diva_STEREO_CONTINUED_WIP.flp').write_bytes(replace_primary((full/'Diva_ZL24_STEREO_WIP.flp').read_bytes(),old,primary))
  for name in ['SUM_ZL24_PRIMARY.fst','04_SUM.fst']:(presets/name).write_bytes(replace_primary((full/'presets'/name).read_bytes(),old,primary))
  (presets/'ZL24_PRIMARY.vstpreset').write_bytes(vstpreset(primary))
  for name in ['Diva_NATIVE_WIP_THREE_HELD.h2p','Diva_THREE_HELD_180BPM.mid']:shutil.copyfile(full/name,playable/name)
  shutil.copyfile(work/'SELECTED_CANDIDATE_WIP.wav',playable/'STEREO_CONTINUED_FULL_WIP.wav')
  guide=f'''# Продолжение ZL24 на трёх нотах: {work.name}

Это промежуточный полный FL20/26 проект с теми же12native эффектами и ДВУМЯ ZL.
Новый primary принят только после fresh6+2cold nativeпар, exact savedstate/cold
replay и дополнительной защиты исправленного стереобаланса. PostSideAllPass
10000Гц/Q2+2200Гц/Q4 неизменен. Источник Diva281/ARP/ADSR/три длинные ноты
41→37→36 дважды/native06/fine32/маршруты сохранены. Полного совпадения нет.

Распаковать ZIP в новую папку, открыть Diva_STEREO_CONTINUED_WIP.flp,
Pattern180BPM. SUM: StereoShaper → ZL PRIMARY → ZL STEREO FIX, Mix100%.
Для текущего проекта перетащить presets/SUM_ZL24_PRIMARY.fst на первый ZL
и presets/SUM_ZL24_STEREO_FIX.fst на следующий ZL. Бесплатный ZL1.4.1 тот же,
новых плагинов нет. При проблеме Diva загрузить h2p из этой папки.

Fresh6mean улучшение{summary['first6_mean_improvement']:.12f},
SEM{summary['paired_difference_SEM']:.12f}; cold2{summary['cold_input_improvements']}.
Числа control/candidate в completion включают8пар; правило принятия использовало только first6
и два положительных cold, не усреднение для обхода отказа. All24native-input/
control/candidate WAV сохранены отдельно lossless. Original objective/tolerances
прежние; stereo gate RMS<=1.5dB и |LR|<=1.6dB по2–5/5–10/10–14кГц.
Новый GUIэкспорт/открытие проекта на ПК не заявляется; сохранённый проект
проверен по неизменности всех MIDI/нативных состояний/postи заменённого primary.
Последний отдельно проверенный полный базовый ZIP и A/B: ../ZL24_CONTINUATION_RU.md.
Вся работа продолжается. Полное совпадение с оригиналом не достигнуто.
'''
  (playable/'FL_STUDIO_RU.md').write_text(guide);(dest/'README_RU.md').write_text(guide)
  (playable/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(playable).as_posix()+'\n'for p in sorted(playable.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
  archive=dest/(work.name+'_complete_FL20_STEREO_WIP.zip')
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
   for p in sorted(playable.rglob('*')):
    if p.is_file():z.write(p,playable.name+'/'+p.relative_to(playable).as_posix())
  with zipfile.ZipFile(archive)as z:
   assert z.testzip()is None
   for p in playable.rglob('*'):
    if p.is_file():assert z.read(playable.name+'/'+p.relative_to(playable).as_posix())==p.read_bytes()
  scripts=dest/'scripts';scripts.mkdir()
  for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py']:shutil.copyfile(A/name,scripts/name)
  (dest/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in dest.rglob('*')if p.is_file()},indent=2)+'\n')
  p=PUBLIC/'README_RU.md';p.write_text(f'[Дальнейший проверенный stereoWIP {work.name}, полный ZIP и все пары]({dest.name}/README_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_TWO_ZL_NUMERIC_{work.name}
Latest complete base remains ZL24 with TWO ZL. New accepted numerical continuation {dest.name}: originalpaired control{summary['current_control_mean']}, candidate{summary['candidate_mean']}, SEM{summary['paired_difference_SEM']}, separatecold2{summary['cold_input_improvements']}, stereo guard passes all8. Full smallplayable FLP/FST/WAV/h2p/MIDI ZIP and all24native-source/control/candidateWAV backed there. SourceDiva281/native06/3longincomingnotes/ARP/postSide10000Q2+2200Q4 unchanged. New GUIexport/opening NOTclaimed. Follow actual N/FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json and actualPID/4realVST3hosts (2workers*2instances). Oldsingle65matcher/watcher mustremainretired. Fixedoriginalscore and allpreviousstrictcold tolerances kept; stereo preservation is extrauser-requested gate. FullsoundmatchFALSE. Publiclargeproof blobcache may be evicted after currentstructuralpromisormark, allaudio staysremoteGit; neverbulkrestoreallcache or use two-treegitdiff/ls-tree--long.
END_TWO_ZL_NUMERIC_{work.name}

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve '+work.name+' two-ZL stereo continuation, complete FL20 WIP and fresh6/cold2 audio');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+(dest/'README_RU.md').relative_to(P).as_posix())==(dest/'README_RU.md').read_bytes()
  # Keep references and structural objects locally; large public archives use
  # the already-tested standard on-demand promisor cache, never private data.
  large=dest/'independent8-native-control-candidate-WAVs.tar.gz';rel=large.relative_to(P).as_posix();oid=git('rev-parse','HEAD:'+rel);blob=large.read_bytes();assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==oid
  git('update-index','--skip-worktree','--',rel);large.unlink();private=work/large.name;assert private.read_bytes()==blob;private.unlink()
  temp=A/'current-stereo-public-metadata-cache';temp.mkdir(exist_ok=True);out=temp/'structural.pack';ids=[x.split()[0]for x in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
  with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
  packhash=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();packdest=P/'.git/objects/pack'/('pack-'+packhash);Path(str(packdest)+'.promisor').touch()
  for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(packdest)+suffix);out.with_suffix(suffix).unlink()
  loose=P/'.git/objects'/oid[:2]/oid[2:]
  if loose.exists():assert zlib.decompress(loose.read_bytes())==b'blob '+str(len(blob)).encode()+b'\0'+blob;loose.unlink()
  subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL)
  assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),complete_playable_ZIP=archive.relative_to(P).as_posix(),all24_validation_WAVs_remote_byte_verified=True,old_kits_and_PC_GUI_preserved=True,public_large_validation_cache_offloaded=True,reference_match_reached=False)
  (work/'REMOTE_BACKUP.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_STEREO_NUMERIC_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
