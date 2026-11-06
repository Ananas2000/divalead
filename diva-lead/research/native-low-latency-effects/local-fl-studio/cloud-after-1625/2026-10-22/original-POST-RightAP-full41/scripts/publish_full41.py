"""Publish full41 only after strict NEW12, complete backup and independent cold ZIP."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,runpy,shutil,time
from bounded_git_audio_backup import verify_and_offload
J=Path(__file__).resolve().parent;A=J.parent/'pc-stereo-20261024';N=J.parent/'native-low-latency-effects';Q=Path('/tmp/divalead-native12-POST-single-AP97-current620-20261107')
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=read(J/'ZL41_BUILD_COMPLETION.json');assert build['two_cold_ZIP_full_working_WAV_errors']==[0.,0.]and build['native_no_cache_vs_cached_zeroDepth_error']==0 and build['ZL_PDC_frames']==build['postprocessing_impulse_added_delay_frames']==[0,0]
proof_path=J/'original-native12-POST-RightAP12800-Q25-current620-NEW12-passed-20261107_COMPLETE_PUBLICATION.json';proof=read(proof_path);assert proof['all_original_members_remote_verified']and len(proof['all_parts'])==6
kit=Path(build['root']);archive=Path(build['ZIP']);assert sha(archive)==build['ZIP_SHA256'];s=read(Q/'completion.json');assert s['robust_improvement'];assert read(N/'zl-stereo-continuation.stop')['owner']=='full41-POST-RightAP-supported-export-20261107';assert not(N/'zl-stereo-numerical.pause').exists()
h=runpy.run_path('/tmp/divalead-local-1625/internet-plugins-20261023/watch_ZL_useful_complete_backups.py',run_name='publish_full41_after_exact_NEW12');P,C,PUBLIC=[h[k]for k in['P','R','PUBLIC']];git=h['git'];pause=C/'auto-backup.pause';deadline=time.monotonic()+240
while True:
    try:
        with pause.open('x')as f:json.dump(dict(owner='authorized-local-backed-copy-cleanup-20261023',PID=os.getpid(),reason='publish complete full41 after exact NEW12, six-part all-WAV backup and actual coldZIP replay'),f)
        break
    except FileExistsError:
        if time.monotonic()>deadline:raise TimeoutError('Existing Git publisher still active')
        time.sleep(.5)
try:
    with(C/'auto-backup-Git.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc)
        latest=read(A/'stereo-continuous87/BEST_CANDIDATE.json');assert latest['source_accepted_cohort']==620;assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes();assert Path(latest['post_native_trim_state']).read_bytes()==(Q/'TRIM.bin').read_bytes()
        state=read(N/'FL20_ZL_STEREO_CONTINUOUS_CONTROLLER.json');pid=state['owner']['PID'];proc=Path('/proc')/str(pid)/'stat';assert not proc.exists()or proc.read_text().split()[2]=='Z','Old-POST matcher must finish before handover'
        dest=PUBLIC/'ZL-WIP41';shutil.copytree(kit,dest);shutil.copyfile(archive,dest/archive.name);research=PUBLIC/'original-POST-RightAP-full41';research.mkdir();scripts=research/'scripts';scripts.mkdir()
        for name in ['ZL41_BUILD_COMPLETION.json','ACTUAL_DIVA_SOURCE_RECHECK.json','CURRENT620_READINESS_PROOF.json','RUNTIME_READINESS.log','EXACT_PART02_REFETCHED_PACK_RELEASE.json','ONBOARDING_DRAFT_READBACK.json',proof_path.name]:shutil.copyfile(J/name,research/name)
        for source in J.glob('*.py'):shutil.copyfile(source,scripts/source.name)
        runtime=research/'current-runtime';runtime.mkdir()
        for name in ['continue_stereo_ZL_matching.py','stereo_cascade_runtime.py','stereo_artifact_helpers.py','backup_stereo_numeric_checkpoint.py','native_post_trim.py']:shutil.copyfile(A/name,runtime/name)
        doc='''# WIP41: следующий подтверждённый шаг к оригиналу

- [Полный ZIP для FL Studio20](ZL-WIP41/Diva_ZL41_STEREO_WIP_complete.zip).
- [A/B оригинал →620→41](ZL-WIP41/AB_ORIGINAL_620_ZL41_WIP.mp3), [FLAC](ZL-WIP41/AB_ORIGINAL_620_ZL41_WIP.flac).
- [Как открыть и перенести обработку](ZL-WIP41/FL_STUDIO_RU.md).

WIP41 начинается с8.336с. Оба наших фрагмента получены из одного реального native-входа; WAV41 в комплекте воспроизведён из ZIP двумя холодными каскадами точно0/0. Полного совпадения с оригиналом нет; частотный перекос L/R остаётся. Это небольшой устойчивый шаг по тембру и избытку воздуха.

Изменён только второй ZL: Right AllPass7,12800Hz,Q25,12dB/oct. Первый ZL620,13 Fruity, Diva, три длинные ноты/ARP/ADSR, маршруты и последний StereoShaper прежние. Нового плагина нет, старого Finish/свёртки нет.

12 новых пар: first6 gain.001164563393/SEM.000161265562; first10.001151706076/SEM.000099057976; обе холодные пары положительны. Air снизился против620 и полного40, Tone улучшился, все12 стерео/pairedlowmid гейтов пройдены. All12 native-state resaves точные; генератор без cachedbundle в zeroDepth-диагностике0. Новый рабочий WAV cold-vs-validation-warm отличается максимум5.9604645e-8 при прежнем native2e-7. ZL PDC0 и измеренный добавочный onset0; это не измерение ASIO. Новый FLP в WindowsGUI не открыт. Веса/пороги/допуски сохранены, проценты сходства не заявляются.
'''
        (PUBLIC/'ZL41_CONTINUATION_RU.md').write_text(doc);(research/'README_RU.md').write_text(doc.replace('](ZL-WIP41/','](../ZL-WIP41/'))
        (PUBLIC/'LATEST_THREE_NOTE_RU.md').write_text('# Текущий полный трёхнотный комплект WIP41\n\n[ZIP для FL Studio20](ZL-WIP41/Diva_ZL41_STEREO_WIP_complete.zip), [инструкция](ZL-WIP41/FL_STUDIO_RU.md), [A/B оригинал →620→41](ZL-WIP41/AB_ORIGINAL_620_ZL41_WIP.mp3). WIP41 начинается с8.336с. Полного совпадения пока нет. При переносе из620 заменяется только второй ZL; предпочтителен полный FLP. [Проверки и ограничения](ZL41_CONTINUATION_RU.md). Все прежние комплекты сохранены.\n')
        p=PUBLIC/'README_RU.md';p.write_text('[WIP41: полный FL20 комплект, A/B с оригиналом и инструкция](ZL41_CONTINUATION_RU.md). Полного совпадения пока нет.\n\n'+p.read_text());(research/'FILE_SHA256.json').write_text(json.dumps({p.relative_to(research).as_posix():sha(p)for p in research.rglob('*')if p.is_file()and p.name!='FILE_SHA256.json'},indent=2)+'\n')
        h['aggregate']();git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Publish complete WIP41: Right AP phase refinement, strict original NEW12 and exact cold FL20 ZIP');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit)
        checks=[]
        for file in [dest/archive.name,dest/'AB_ORIGINAL_620_ZL41_WIP.mp3',dest/'FL_STUDIO_RU.md',dest/'verification/COLD_ZIP_PROOF.json']:
            assert h['read_public_bytes']('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+file.relative_to(P).as_posix())==file.read_bytes();checks.append(file.relative_to(PUBLIC).as_posix())
        # Release only the verified ZIP cache duplicate, retaining all live states/audio.
        row=dict(name=archive.name,path=(dest/archive.name).relative_to(P).as_posix(),OID=git('rev-parse','HEAD:'+(dest/archive.name).relative_to(P).as_posix()),SHA256=build['ZIP_SHA256'],bytes=build['ZIP_bytes'])
        verify_and_offload(P,git,commit,[row],J/'verified-full41-ZIP-structural-cache');git('update-index','--skip-worktree','--',row['path']);assert sha(dest/archive.name)==row['SHA256'];(dest/archive.name).unlink()
        receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,full_kit='ZL-WIP41',complete_ZIP_SHA256=build['ZIP_SHA256'],complete_ZIP_bytes=build['ZIP_bytes'],all_retained_study_members_and_all48_NEW12_WAVs_remote_verified=True,study_backup_parts=proof['all_parts'],latest_comparator620_rechecked_after_graceful_main_stop=True,two_cold_ZIP_full_errors=build['two_cold_ZIP_full_working_WAV_errors'],source_Diva_MIDI3_ARP_ADSR_all13_native_PRIMARY_unchanged=True,only_POST_Right_AP7_added=True,HTTP_byte_exact_paths=checks,verified_public_ZIP_duplicate_cache_evicted=True,all_old_kits_and_PC_GUI_preserved=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
        (J/'ZL41_FULL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');(N/'LATEST_EXTERNAL_ZL_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');assert not git('status','--porcelain');print(json.dumps({k:v for k,v in receipt.items()if k!='study_backup_parts'}),flush=True)
finally:
    if pause.exists()and read(pause).get('PID')==os.getpid():pause.unlink()
