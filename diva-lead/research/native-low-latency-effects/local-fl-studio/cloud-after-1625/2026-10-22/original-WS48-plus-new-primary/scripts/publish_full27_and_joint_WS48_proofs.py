"""Publish complete supported WIP27 and all48 fresh actual validation WAVs."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil
from bounded_git_audio_backup import stage_archive,finish_manifest,verify_and_offload
H=Path(__file__).resolve().parent;J=Path('/tmp/divalead-original-WS48-primary-joint-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023')
h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='publish_original_WS48_joint_full27')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL27_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);summary=read(J/'completion.json')
assert summary['robust_improvement'] and build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.] and build['ZIP_native_FST_zero_depth_max_abs_errors']==[0.]
assert hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256']
pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='full WIP27 after strict actualZIPreplay and all48validationWAVs'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP27';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name)
  research=PUBLIC/'original-WS48-plus-new-primary';research.mkdir();parts=[];archives=[]
  for p in J.iterdir():
   if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,research/p.name)
  for p in J.glob('*.tar.gz'):
   manifest=stage_archive(P,git,p,research);parts+=manifest['parts'];archives.append(dict(local=str(p),manifest=manifest))
  scripts=research/'scripts';scripts.mkdir()
  for name in ['study_WS48_and_normal_primary_joint_original.py','normal_real_ZL_refit.py','build_original_target_stereo_wip27.py','publish_full27_and_joint_WS48_proofs.py','bounded_git_audio_backup.py']:shutil.copyfile(H/name,scripts/name)
  shutil.copyfile(H/'ZL27_BUILD_COMPLETION.json',research/'ZL27_BUILD_COMPLETION.json')
  doc='''# ZL27 WIP — к оригиналу на штатной кривой WaveShaper и обычном EQ

- [Полный ZIP: FLP, WAV, h2p, MIDI, FST и VSTpreset](ZL-WIP27/Diva_ZL27_STEREO_WIP_complete.zip).
- [A/B: оригинал0с → ZL26 с4.168с → ZL27 с8.336с](ZL-WIP27/AB_ORIGINAL_ZL26_ZL27_WIP.mp3).
- [Lossless A/B](ZL-WIP27/AB_ORIGINAL_ZL26_ZL27_WIP.flac).
- [Инструкция FL Studio20/26](ZL-WIP27/FL_STUDIO_RU.md).

Полного совпадения нет. Цель — исходный оригинальный WAV, не v83/Finish.
Меняются штатная кривая SOURCE FruityWaveShaper и обычный первый ZL; остальные
11native состояний, все281 параметровDiva, ARP/ADSR, входящие три длинные ноты
41→37→36 дважды, маршруты и второйZL прежние. Nativebase теперь07. Эффектов ZL
всего два, оба MinimumPhase/Lookahead0/AutoGainOFF, старыйFinish не нужен.

Предыдущая попытка применить только кривую без новогоEQ не прошла независимое
подтверждение и не принята. Здесь новый DSPвариант:48поддерживаемых координат
кривой плюс новая согласованная настройка87параметров PRIMARY.1189настоящих
VST3предложений,3новыхtrainingnativeinput,2heldout. До12новыхпар зафиксированы
кандидат и двойное правило: первые6 и первые10 должны улучшить оценку более
max(.0005,3SEM), обе холодныепары положительны и все сохраняют стереоguards.

First6gain .003943129777,SEM.001250715383,порог.003752146150. First10gain
.003934344670,SEM.000967415846,порог.002902247537. Cold2+.002827654530/
+.008038104221. Все12прошли стерео. Средняя полная originalobjective первых10
1.313698163934; это не процентперцептивногосовпадения. Веса,819alignment,
правилаприёма,допускисохранены. Все48native/processed контрольныхикандидатных
WAV сохранены losslessвобычномGit, каждыйSHAпроверен; большиеархивы parts48MiB
сmanifestточнойсборки. Ниотдельнаяпробанитолько выбранныйWAV не основаниеприёма.

Полный ZIP прошёлCRC/SHA, двахолодных настоящих каскадаZL изZIP дали0/0
отличияотвыбранного WAV при прежнемstrict8float32eps/1e-12. Компонентыпересохранены
побитово. Actualnative12DLL state/FST загрузка/пересохранение, zero-depthконтроль
изZIP дал0 при допуске2e-7. В FLP/FST/VSTpreset изменилисьименноWSиPRIMARY;
источник/входящийMIDI/маршруты/POST прежние. DeclaredZLPDC0/impulse0, это неASIO.
НовыйFLP пока неоткрывалсявWindowsGUI; реальные рендеры Linux/Wine, новогоGUI
экспортаилисубъективногопрослушиванияассистентом не заявлено.

В прежнем GUIпроекте обязательно заменить и SOURCE WaveShaper, и SUM PRIMARY.
Только заменаZL не воспроизведёт27. Полныепошаговыеинструкции вкомплекте.
Оригинал не подмешиваетсявсинтез, MistaTowa неиспользуется. Все старыеfullkits,
история и последнийPCGUIпроект сохранены. Следующий подбор продолжать прямо
к оригиналу на трёхнотном источнике с этим nativebase07 и двумяZL.
'''
  (PUBLIC/'ZL27_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP27/','](../ZL-WIP27/'))
  p=PUBLIC/'README_RU.md';p.write_text('[ZL27: новый штатный WaveShaper и PRIMARY, полный FL20 WIP, A/B](ZL27_CONTINUATION_RU.md).\n\n'+p.read_text())
  header=f'''BEGIN_ORIGINAL_WS48_PRIMARY_ZL27_20261025
Latest supported full kit ZL-WIP27/Diva_ZL27_STEREO_WIP_complete.zip SHA {build['ZIP_SHA256']}; readZL27_CONTINUATION_RU.md and FL_STUDIO_RU.md. Target ONLY uploaded originalWAV, never v83/Finish proxy/effect. Nativebase07: only nativeWS curve changed with48 supported controls(2+2+4+8+32), other11native/Diva281/incoming3longnotes41-37-36twice/ARP/ADSR/routes unchanged. New refitted87primary; POSTsame26:3SideAP+1StereoAP, TWOactualZLs zeroLookahead.1189actualZLproposals,3traininginputs,2heldouts, frozenbefore12newpairs. Predeclared BOTHfirst6 andfirst10>max(.0005,3SEM), bothcoldpositive, all12stereoguards. Gains .003943129777(first6) .003934344670(first10), SEM .001250715383/.000967415846, cold+.002827654530/+.008038104221. No exactmatch orperceptualpercentageclaim. CurveALONE earlierfailedindependent12 andwasnotadopted, don'tpoolit. Twoactualcoldcascades fromZIPexact0/0, componentsbyteexact, native12DLLstate/FST zeroDepthreplay0 at2e-7, ZLPDC0/impulse0 notASIO. NewFLPnotWindowsGUItested, noGUIexport/listeningclaim. IMPORTANT existingGUIuser mustupdateSOURCEWSFST andPRIMARYZLFST, notjustZL; POSTunchanged. All48freshvalidationWAVspreservedlosslessGit parts48MiBwithmanifest. Keepcurrentbase07/supportednativebundle fingerprint andtwoZLruntime, doNOTrestartretiredsingleZLloops. Oldfullkits/PCGUI/history/privateoriginalsource48/refsretained. APIquota%unavailable, do notinvent5percent. Userwantsactiveworkuntilmatch/actualresourcebarrier, neverendturnclaimingbackgroundcontinues.
END_ORIGINAL_WS48_PRIMARY_ZL27_20261025

'''
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');finish_manifest(h,research,parts)
  git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL27 WS48 plus new primary WIP and all48 actual validation WAVs');commit=git('rev-parse','HEAD')
  assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_ZL26_ZL27_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  verify_and_offload(P,git,commit,parts,H/'full27-public-structural-cache')
  for row in archives:Path(row['local']).unlink()
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP27',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='07',all48_actual_validation_WAVs_remote_Git_verified=True,ZIP_replay_max_abs_errors=[0.,0.],native_ZIP_FST_zero_depth_error=0.,HTTP_checks=checks,all_old_kits_and_PC_GUI_preserved=True,original_is_the_only_target=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (H/'ZL27_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
