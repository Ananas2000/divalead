"""Keep all80 actual validation WAVs and the negative independent verdict."""
from pathlib import Path
import datetime,fcntl,json,os,runpy,shutil,time
from bounded_git_audio_backup import stage_archive,finish_manifest,verify_and_offload
H=Path(__file__).resolve().parent;R0=Path('/tmp/divalead-original-native-WS48-20261025-01');R1=Path('/tmp/divalead-WS48-independent12-20261025-01');D=Path('/tmp/divalead-local-1625/internet-plugins-20261023');h=runpy.run_path(str(D/'watch_ZL_useful_complete_backups.py'),run_name='WS48_independent_confirmation_backup');P,N,R,PUBLIC=[h[k]for k in ['P','N','R','PUBLIC']];git,read=h['git'],h['read'];assert read(R0/'completion.json')['robust_improvement']and not read(R1/'completion.json')['robust_independent_confirmation'];pause=R/'auto-backup.pause';owner='authorized-local-backed-copy-cleanup-20261023'
with pause.open('x')as f:json.dump(dict(owner=owner,PID=os.getpid(),reason='save initial WS48 andindependent12verdict withall80actualvalidationWAVs; no adoption'),f)
try:
 with(R/'auto-backup-Git.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain');h['fetch_main']();assert git('rev-parse','HEAD')==git('rev-parse','origin/main');protected=h['protected']();pc='diva-lead/research/native-low-latency-effects/local-fl-studio/2026-10-24';pc_oid=git('rev-parse','HEAD:'+pc);dest=PUBLIC/'original-WS48-independent12-not-adopted';dest.mkdir();parts=[];archives=[]
  for root,prefix in [(R0,'INITIAL_WS48'),(R1,'INDEPENDENT12')]:
   for p in root.iterdir():
    if p.is_file()and p.suffix in ['.json','.gz','.bin']and not p.name.endswith('.tar.gz'):shutil.copyfile(p,dest/(prefix+'_'+p.name))
   for p in root.glob('*.tar.gz'):manifest=stage_archive(P,git,p,dest);archives.append(dict(local=str(p),manifest=manifest));parts+=manifest['parts']
  shutil.copytree(R0/'saved-native-bundle',dest/'RESEARCH_ONLY_native_bundle');scripts=dest/'scripts';scripts.mkdir()
  for name in ['study_native_WaveShaper48_original.py','confirm_WS48_independent12_latest_original.py','backup_WS48_initial_and_independent_confirmation.py','bounded_git_audio_backup.py']:shutil.copyfile(H/name,scripts/name)
  doc='''# WS48: независимая проверка не подтвердила принятие

Проверены120реальных вариантов всех48поддерживаемых координат кривой штатного
FruityWaveShaper(2основные+2parent+4local+8detail+32fine). Старыйcanonicalstate
сохранён какоснова, меняются толькоYточки; другие11native/Diva281/ARP/ADSR/
3длинныевходящиеноты/маршруты иобаZL фиксированы. Дифференциальныепробы и
совместныепредложения сделаны настоящимиDLL/VST3. Физическиеfeaturevector
нормы сверены с прежнимиH24/ERB/phase/upper/lowметриками; линейныепрогнозы
использованы толькодляпредложений, не дляпринятия. Цель — оригинальныйWAV.

Первыеfresh6+2cold: gain.002695300169,SEM.000897509200,порог.002692527601,
cold2+.000560870330/+.002590562270. Формально прошёл, нозапас оченьмал.
Поэтому доэкспорта заранее зафиксирована одна дополнительная независимая
серия:10новыхпар+2новыхcoldпары наlatestfrozenprimary/POST. Mean gain.001498593195,
SEM.000539299266,порог.001617897797, cold2+.002460003896/+.003189578352.
Эта серия НЕ прошла. Кандидат НЕ принят иНЕ названновойверсией. Нельзяпулить
обе серии послетакогоисхода,чтобы обойти заранее выбраннуюпроверку, или повторять
тежеусловиядопобеды. Полныйoriginalobjective/веса/порог/стереоguards прежние.

Все80native-control/native-candidate/processed-control/processed-candidateWAV
сохранены lossless:32впервомархиве,48внезависимом. КаждыйmemberSHAпроверен.
Архивы разбиты на48MiBparts сmanifestразмера/SHA дляточнойсборки; ordinaryGit,
безизмененияаудиобайтов. ResearchONLYnativebundle и48вектор сохранены дляновых
гипотез, неподменяютcurrentnativebase06 иWIP26. Другие11native statesbyteexact,
независимыйzero-depthnative replay0 припрежнемдопуске2e-7. Source/MIDIне менялись.

Следующаягипотеза — совместная поправка этойкривой иобычногоEQ, после чего
снова нужнаполнаяпроверкак原игиналу. Старыйv83/Finish не цельинеэффект.
GUI/ASIO/полноесовпадение/субъективноепрослушивание не заявляются.
Все прежниеполныекомплекты/PCGUI/privateoriginalsource48/refsсохранены.
Большиеproofblobcache могут быть fetch-on-demand; архивныеданныеполностьюGit.
'''.replace('к原игиналу','к оригиналу')
  (dest/'README_RU.md').write_text(doc);finish_manifest(h,dest,parts);git('add','--',str(PUBLIC.relative_to(P)));git('-c','core.whitespace=cr-at-eol','diff','--cached','--check');git('commit','-m','Preserve all80 WS48 validation WAVs and failed independent confirmation without adoption');commit=git('rev-parse','HEAD');assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in protected.items());assert git('rev-parse','HEAD:'+pc)==pc_oid;h['push_and_confirm'](commit);verify_and_offload(P,git,commit,parts,H/'WS48-confirmation-public-metadata-cache')
  for row in archives:Path(row['local']).unlink()
  assert not git('status','--porcelain');receipt=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,public_path=dest.relative_to(P).as_posix(),all80_actual_validation_WAVs_remote_Git_verified=True,initial8_passed=True,independent12_failed=True,accepted=False,original_is_the_only_target=True,reference_match_reached=False);(H/'WS48_INDEPENDENT12_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
finally:
 if pause.exists()and read(pause).get('owner')==owner:pause.unlink()
