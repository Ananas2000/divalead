"""Publish full tested WIP26 and all30 phase-study WAVs against original only."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,subprocess,zlib
H=Path(__file__).resolve().parent;ROOT=Path('/tmp/divalead-original-target-stereo-AllPass-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='original_target_full26_publication')
P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];build=read(H/'ZL26_BUILD_COMPLETION.json');kit=Path(build['root']);archive=Path(build['ZIP']);assert build['ZIP_actual_two_cold_cascade_max_abs_errors']==[0.,0.]and hashlib.sha256(archive.read_bytes()).hexdigest()==build['ZIP_SHA256']
owner='authorized-local-backed-copy-cleanup-20261023';pause=R/'auto-backup.pause'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='publish full original-target WIP26 plus all30phaseWAVs after exactZIPcoldreplay'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');before=git('rev-parse','HEAD');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
  dest=PUBLIC/'ZL-WIP26';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name)
  research=PUBLIC/'original-target-stereo-phase-study01';h['copy_evidence'](ROOT,research,True);scripts=research/'scripts';scripts.mkdir()
  for name in ['study_original_target_stereo_AllPass.py','verify_original_target_stereo_AP_cold_and_latency.py','build_original_target_stereo_wip26.py','publish_original_target_full26_and_phase_proofs.py']:shutil.copyfile(H/name,scripts/name)
  shutil.copyfile(H/'ZL26_BUILD_COMPLETION.json',research/'ZL26_BUILD_COMPLETION.json');s=read(ROOT/'completion.json')
  doc='''# ZL26 WIP — следующая поправка непосредственно к оригиналу

- [Полный ZIP FL20/26:FLP/WAV/h2p/MIDI/FST/VSTpreset](ZL-WIP26/Diva_ZL26_STEREO_WIP_complete.zip).
- [A/B:оригинал0с → принятый155 с4.168с → ZL26 с8.336с](ZL-WIP26/AB_ORIGINAL_BEST155_ZL26_WIP.mp3).
- [Тот же A/B без потерь](ZL-WIP26/AB_ORIGINAL_BEST155_ZL26_WIP.flac).
- [Как загрузить в FLStudio](ZL-WIP26/FL_STUDIO_RU.md).

Цель — загруженный оригинальный WAV на обычной обработке с малой задержкой.
v83/старый Finish не используются как цель подбора или эффект. Это небольшое
устойчивое улучшение фазовой формы сигнала; полного совпадения нет.
Три входящие длинные ноты41→37→36 дважды,внутреннийARP/ADSR/Diva281/native06/
fine32/маршруты сохранены. PRIMARY — принятый155. В POST к прежним трём SideAP
добавлен StereoAllPass783.2Гц/Q19.422. Всего два экземпляра того же ZL1.4.1.

133настоящих VST3пробы,3новыхnativeinput,2heldout,затем frozenstate и новые
fresh6+2coldnativeпары. Mean gain.001321763822,SEM.000017126913, прежний порог
.0005. Cold2+.001319150380/+.001294888173. Все8улучшили полный originalobjective
и сохранили дополнительные стереоguards. Веса/819alignment/tolerances прежние.
Ошибка фазового профиля1.21164→1.18280. H24почтипрежняя1.68402→1.68455дБ,
ERB1.19308→1.19344дБ: эти малые регрессии не скрыты, оценка общая улучшилась.
Не заявляются большой слышимыйскачок или процентсовпадения.

Настоящие два холодных каскада воспроизвели сохранённый WAV точно0/0,
оба компонента resavebytesexact. НовыйFLP/FST/VSTpreset разобран, native12/
Diva/MIDI/routes неизменны. ПолныйZIPCRC/SHA и отдельные два холодных реальных
каскада из распакованногоZIP дали0/0. CombinedZLPDC0/impulse0, не ASIO/wholeDAW.
Новый проект не открывался вWindowsGUI. Это cloudLinux/Wine render, не GUIэкспорт.

[Все30training/validationWAV и исследования](original-target-stereo-phase-study01/README_RU.md).
Отдельно [21настоящий вариантDiva, все42source/processedWAV](original-target-actual-Diva-tone-study01/README_RU.md)
не улучшили полный originalcriterion и не применены. Оригинал только дляанализа/
A-B, не подмешиваетсявсинтез; MistaTowa не используется. Старые комплекты и
последний PCGUIпроект сохранены. Далее искать к оригиналу, сохраняя три ноты
и normalnative/twoZLобработку. СтарыйsingleZLкод потеряет второйэффект.
'''
  (PUBLIC/'ZL26_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP26/','](../ZL-WIP26/').replace('](original-target-stereo-','](../original-target-stereo-').replace('](original-target-actual-','](../original-target-actual-'))
  (research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in research.rglob('*')if p.is_file()},indent=2)+'\n');p=PUBLIC/'README_RU.md';p.write_text('[ZL26: полный трёхнотный WIP, непосредственно к оригиналу, A/B и инструкция](ZL26_CONTINUATION_RU.md).\n\n'+p.read_text())
  header='''BEGIN_ORIGINAL_TARGET_ZL26_20261025
Latestfullkit ZL-WIP26/Diva_ZL26_STEREO_WIP_complete.zip, SHAee8817b94ce8cf7fd46b167a512c800075d9c187e0e4d835600e866254657aae; readZL26_CONTINUATION_RU.md. ORIGINALuploadedWAVonlytarget, neverv83/Finishproxy/effect. SourceDiva281/native06/fine32/3longincomingnotes41-37-36twice/ARP/ADSR/routesunchanged. TWOactualZL: primaryaccepted155 -> POSTthreeSideAP10000Q2+2200Q4+895.8Q13.84 PLUS StereoAP783.2Hz/Q19.422; fourbandsinsideSECONDinstance, notfourinstances. NewPOSTSHA195e46104902cd1d5140104e8d951c859ee9ec8b1e2bb9890ce68e0597538688.13x? Actual133phasevariants,3trainingnativeinput,2heldouts, frozenbeforefresh6+2cold. First6gain.001321763822 SEM.000017126913 floor.0005; cold2+.001319150380/+.001294888173, all8positiveandstereoguarded. Originalobjective/weights/819alignment/tolerancesunchanged. Relativephaseerror1.21164to1.18280, H24tinyregression1.68402to1.68455/ERB1.19308to1.19344 disclosed, smallWIPnotbigsoundjump. Realcold2cascades exact0/0, componentsbyteexact, combinedZLPDC0/impulse0; independentcompleteZIPCRC/SHA/2actualcoldreplay0/0. Source/native/MIDI/routes preserved inFLP/FST. NoGUIopening/newGUIexport/ASIO/subjectiveauditionclaim. Phaseall30WAVpubliclossless inoriginal-target-stereo-phase-study01. Other21actualDiva/42WAVstudyrejected, currentpresetchangedONLYeffects. MainmustfreezeNEWPOSTfromadoptedBEST andnormal2ZLpublisherpreservesall4bands; currentSTOPowneroriginal-reference-tone-finite-20261025 removeonlyafteradoption/runtimecheck. RetiredlegacysingleZLstopsremain. FullsoundmatchFALSE, useraskscontinuetooriginallimits/noquestions/Mista. Gitcacheoldholesexpected, preserveprivateoriginalsource48/allrefs/fullkits/PCGUI. APIquota%unknown, completedusefulstagesbackedprogressively.
END_ORIGINAL_TARGET_ZL26_20261025

'''.replace('13x? ','')
  p=R/'start_skill_current.md';p.write_text(header+p.read_text());shutil.copyfile(p,h['BASE']/'start_skill_current.md');h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)),str((h['BASE']/'start_skill_current.md').relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete original-target ZL26 low-latency three-note WIP and all phase validation WAVs');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
  checks=[]
  for p in [dest/archive.name,dest/'AB_ORIGINAL_BEST155_ZL26_WIP.mp3',dest/'FL_STUDIO_RU.md']:
   assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+p.relative_to(P).as_posix())==p.read_bytes();checks.append(dict(path=p.relative_to(PUBLIC).as_posix(),HTTP_byte_exact=True))
  archives=[]
  for p in research.glob('*WAVs.tar.gz'):
   rel=p.relative_to(P).as_posix();b=p.read_bytes();oid=git('rev-parse','HEAD:'+rel);assert subprocess.check_output(['git','-C',str(P),'show',commit+':'+rel])==b;archives.append(dict(path=rel,OID=oid,SHA256=hashlib.sha256(b).hexdigest()));git('update-index','--skip-worktree','--',rel);p.unlink();private=ROOT/p.name;assert private.read_bytes()==b;private.unlink()
  temp=H/'full26-public-structural-cache';temp.mkdir();out=temp/'structural.pack';ids=[line.split()[0]for line in subprocess.check_output(['git','--no-lazy-fetch','-C',str(P),'rev-list','--objects','--filter=blob:none','--missing=allow-promisor','origin/main'],text=True).splitlines()]
  with out.open('wb')as f:subprocess.run(['git','-C',str(P),'pack-objects','--stdout','--no-reuse-delta','--no-reuse-object'],input=('\n'.join(ids)+'\n').encode(),stdout=f,check=True)
  ph=subprocess.check_output(['git','index-pack',str(out)],text=True).strip();dst=P/'.git/objects/pack'/('pack-'+ph);Path(str(dst)+'.promisor').touch()
  for suffix in ['.pack','.idx']:shutil.copyfile(out.with_suffix(suffix),str(dst)+suffix);out.with_suffix(suffix).unlink()
  for row in archives:
   oid=row['OID'];loose=P/'.git/objects'/oid[:2]/oid[2:]
   if loose.exists():raw=zlib.decompress(loose.read_bytes());assert hashlib.sha1(raw).hexdigest()==oid and hashlib.sha256(raw.split(b'\0',1)[1]).hexdigest()==row['SHA256'];loose.unlink()
  subprocess.run(['git','--no-lazy-fetch','-C',str(P),'fsck','--connectivity-only','--no-dangling'],check=True,stdout=subprocess.DEVNULL);assert not git('status','--porcelain')
  receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,previous_HEAD=before,full_kit='ZL-WIP26',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],native_base='06',requires_two_ZL_instances=True,post_Side_AllPasses=build['post_Side_AllPasses'],post_Stereo_AllPasses=build['post_Stereo_AllPasses'],original_is_the_only_target=True,v83_Finish_not_used=True,original_objective_export_mean=build['original_objective_export_mean'],ZIP_replay_fixed_native_input_max_abs_errors=[0.,0.],all30_phase_WAVs_Git_verified=True,proof_archives=archives,HTTP_checks=checks,all_old_kits_and_PC_GUI_preserved=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
  (H/'ZL26_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
