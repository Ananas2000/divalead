"""Publish a verified v70 kit without duplicating superseded numeric payloads."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parent;P=Path('/workspace/divalead');ROOT=P/'diva-lead/research/three-held-continuation'
T=Path('/tmp/divalead-v70-build');D=T/'v70-wip';O=ROOT/'after-v70';PAUSE=R/'auto-backup.pause'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def git(*a):return subprocess.check_output(['git','-c','gc.auto=0',*a],cwd=P,text=True).strip()
def immutable_copy(a,b):
 b=Path(b);b.parent.mkdir(parents=True,exist_ok=True)
 try:os.link(a,b)
 except OSError:shutil.copyfile(a,b)
 assert sha(a)==sha(b);return str(b)
def same_wave(a,b):
 x,xr=sf.read(a);y,yr=sf.read(b);return xr==yr and np.array_equal(x,y)
proof=json.loads((D/'verification/selected_validation.json').read_text());zipproof=json.loads((T/'ZIP-proof.json').read_text())
assert proof['all_chosen_three_guards_passed'] and proof['original_three_held_MIDI_events_unchanged']
assert proof['source_family']=='PulseWidth51.90' and proof['changed_source_fields']=={'OSC:PW':51.9}
assert proof['tone_score']<json.loads((P/'diva-lead/v69-wip/verification/selected_validation.json').read_text())['tone_score']-1e-6
assert zipproof['all_extracted_files_byte_equal'] and zipproof['clean_extraction_release_replay_passed'] and zipproof['byte_exact_DLL_rebuild']
assert json.loads((T/'clean-ZIP-Windows-proof.json').read_text())['full_WAV_sample_exact']
assert sha(T/'Diva_lead_v70_WIP_checkpoint.zip')==zipproof['ZIP_SHA256']
assert not PAUSE.exists();write(PAUSE,dict(owner='publish-full-v70',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat()))
for _ in range(60):
 status=json.loads((R/'auto-backup-state.json').read_text())
 if status['phase']=='paused_for_manual_Git_work':break
 time.sleep(1)
else:raise RuntimeError(status)
with (R/'auto-backup-Git.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);assert not git('status','--porcelain')
 parent=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
 # Protect every numbered historical kit, rather than just recent releases.
 immutable={str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in (P/'diva-lead').glob('v*') if p.is_dir()}
 immutable.update({str(p.relative_to(P)):git('rev-parse','HEAD:'+str(p.relative_to(P))) for p in P.glob('Diva_lead*.zip')})
 assert not O.exists() and not (P/'diva-lead/v70-wip').exists()
 shutil.copytree(D,P/'diva-lead/v70-wip',copy_function=immutable_copy);immutable_copy(T/'Diva_lead_v70_WIP_checkpoint.zip',P/'Diva_lead_v70_WIP_checkpoint.zip')
 O.mkdir();(O/'scripts').mkdir()
 for name in ['ZIP-proof.json','clean-ZIP-Windows-proof.json','clean-extraction-proof.json','fresh-source-proof.json','release-proof.json','spectral-proof.json','selected-basis.json']:
  shutil.copyfile(T/name,O/name)
 for name in ['build_three_v70.py','write_v70_docs.py','finalize_v70.py','verify_zip_windows_v70.py','run_full_v70_build.py','publish_full_v70.py','prepare_next_full_v70.py','probe_cleaner_offharmonic_hf.py','auto_backup_three.py','start_three_services.py']:
  shutil.copyfile(R/name,O/'scripts'/name);assert not (R/name).samefile(O/'scripts'/name)
 (O/'diagnostics').mkdir()
 for name in ['selective-temp-copy-cleanup.json','selective-cleanup-public-verification.json','selective-cleanup-config-save-readback.json','after-cleanup-residual-band-diagnostic.json','cleaner-offharmonic-hf-grid-result.json','selective-cleanup-checkout-discovery.json','service-start-last.json']:
  shutil.copyfile(R/name,O/'diagnostics'/name)
 shutil.copyfile(R/'start_skill_current.md',O/'start_skill_current.md')
 selected=O/'selected-full-proof';selected.mkdir()
 shutil.copyfile(D/'verification/selected_validation.json',selected/'validation.json');shutil.copyfile(D/'verification/arbitrary_input_verification.json',selected/'arbitrary-input-verification.json')
 current=json.loads((P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json').read_text())
 current={k:(v.replace('v69','v70').replace('V69','V70') if isinstance(v,str) else v) for k,v in current.items()}
 current.update(ZIP_SHA256=zipproof['ZIP_SHA256'],DLL_SHA256=sha(D/'Diva_Lead_Finish_v70_WIP_x64.dll'),research_model=str(O.relative_to(P)),score=proof['score'],tone_score=proof['tone_score'],AB_previous_current='diva-lead/v70-wip/AB_REFERENCE_V69_V70_WIP.wav',AB_MP3='diva-lead/v70-wip/AB_REFERENCE_V69_V70_WIP.mp3')
 write(P/'diva-lead/CURRENT_FL_STUDIO_RELEASE.json',current)
 pointer=json.loads((ROOT/'CURRENT_THREE_NOTE_MODEL.json').read_text())
 if proof['tone_score']<pointer['tone_score']-1e-12:
  pointer.update(research_validation='after-v70/selected-full-proof/validation.json',tone_score=proof['tone_score'],score=proof['score'],research_source_family=proof['source_family'],research_source_changes=proof['changed_source_fields'],research_source_is_user_selected_preset=False)
 research=json.loads((ROOT/pointer['research_validation']).read_text());manifest=json.loads((D/'source_manifest.json').read_text())
 covered=bool(json.loads(Path(research['core_model']).read_text())==json.loads((D/'analysis/spectral_model.json').read_text()) and sha(research['source_preset'])==sha(D/manifest['source_preset']) and same_wave(research['new_source_raw'],D/manifest['source_WAV']) and same_wave(research['new_source_before_fixture'],D/manifest['before_spectral_WAV']) and same_wave(research['NEW_independent_prebase'],D/manifest['NEW_independent_base']))
 pointer.update(selected_complete_release='diva-lead/v70-wip',selected_complete_release_tone_score=proof['tone_score'],selected_complete_release_score=proof['score'],selected_complete_release_source_family=proof['source_family'],selected_complete_release_source_changes=proof['changed_source_fields'],research_model_already_in_selected_complete_release=covered,latest_research_is_not_a_new_complete_DLL_release=not covered)
 write(ROOT/'CURRENT_THREE_NOTE_MODEL.json',pointer)
 (O/'README.md').write_text(f'''# Полный v70 WIP: три удерживаемые ноты

[Комплект](../../../v70-wip/README.md), [FL Studio](../../../v70-wip/FL_STUDIO_RU.md), [ZIP](../../../../Diva_lead_v70_WIP_checkpoint.zip), [оригинал → v69 → v70](../../../v70-wip/AB_REFERENCE_V69_V70_WIP.mp3).

После выборочной очистки подбор возобновлён от v69. Все номерные версии сохранены; удалены только повторные промежуточные данные. Уточнены существующие коэффициенты Finish, все 281 параметр Diva и трёхнотный MIDI прежние. Ошибка тембра {proof['tone_score']:.10f}; общая {proof['score']:.10f}. Это ошибки измерений, не проценты сходства. Расхождения приведены в COMPARISON_RU.md. Совпадение ещё не достигнуто.

Проверены свежая настоящая Diva, все параметры/сырой WAV/12 MIDI-событий, Windows/native, собственная независимая NEW-база, отдельный fixture, 12 причинных случаев четырёх частот, API/FXP/состояние/PDC/размеры блоков, точная пересборка и фактическая DLL из чистого ZIP. GUI FL Studio и прослушивание ассистентом не выполнялись. Лицензионная Diva не включена. MistaTowa не используется.

Бэкапы остальных новых проверенных попыток публикуются автоматическим контроллером. Эта публикация не останавливает подбор.
''')
 readme=P/'README.md';text=readme.read_text();archive=text[text.index('**Архивный исследовательский этап:**'):]
 readme.write_text(f'''# Diva: реконструкция лида для FL Studio

**[Полный v70 WIP](diva-lead/v70-wip/README.md)** — [ZIP](Diva_lead_v70_WIP_checkpoint.zip), [FL Studio](diva-lead/v70-wip/FL_STUDIO_RU.md), [оригинал → v69 → v70](diva-lead/v70-wip/AB_REFERENCE_V69_V70_WIP.mp3). Наш новый вариант начинается с 8,336 с; [прямое A/B](diva-lead/v70-wip/AB_REFERENCE_V70_WIP.wav), наш с 4,168 с.

Три удерживаемые ноты MIDI 41 → 37 → 36; внутренний ARP Diva. Источник, все 281 параметр и MIDI прежние от v69. Обновлены коэффициенты Finish. Ошибка тембра {proof['tone_score']:.10f}, общая {proof['score']:.10f}; точное совпадение не достигнуто. [Измерения и регрессии](diva-lead/v70-wip/COMPARISON_RU.md), [проверки](diva-lead/research/three-held-continuation/after-v70/README.md), [новые WAV](diva-lead/research/three-held-continuation/after-v64/auto-checkpoints/README.md).

[Выборочная очистка](diva-lead/research/three-held-continuation/selective-cleanup-20261020/README_RU.md) сохранила все номерные комплекты, включая v69. Прослушивание ассистентом и GUI FL Studio не выполнялись.

'''+archive)
 p=ROOT/'README.md';text=p.read_text();start=text.index('Полный проверенный промежуточный комплект:');end=text.index('\n\n## Что выполнено',start)
 p.write_text(text[:start]+'Полный проверенный промежуточный комплект: [v70](../../v70-wip/README.md), [FL Studio](../../v70-wip/FL_STUDIO_RU.md), [оригинал → v69 → v70](../../v70-wip/AB_REFERENCE_V69_V70_WIP.mp3). [Проверки](after-v70/README.md), [новые WAV](after-v64/auto-checkpoints/README.md), [текущая основа](CURRENT_THREE_NOTE_MODEL.json). Совпадение не достигнуто.'+text[end:])
 targets=['README.md','Diva_lead_v70_WIP_checkpoint.zip','diva-lead/v70-wip','diva-lead/CURRENT_FL_STUDIO_RELEASE.json',str(O.relative_to(P)),str((ROOT/'README.md').relative_to(P)),str((ROOT/'CURRENT_THREE_NOTE_MODEL.json').relative_to(P))]
 git('add','--',*targets);assert all(any(n==p or n.startswith(p+'/') for p in targets) for n in git('diff','--cached','--name-only').splitlines())
 git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--','.',':!*.tsv',':!*.log')
 git('commit','-m','Back up verified three-held Diva v70 after selective cleanup and resumed matching')
 assert all(git('rev-parse','HEAD:'+p)==oid for p,oid in immutable.items())
 commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent;git('push','origin','HEAD:main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
 public=[]
 for name in ['Diva_lead_v70_WIP_checkpoint.zip','diva-lead/v70-wip/FL_STUDIO_RU.md','diva-lead/v70-wip/Diva_Lead_Finish_v70_WIP_x64.dll','diva-lead/v70-wip/AB_REFERENCE_V69_V70_WIP.mp3','diva-lead/CURRENT_FL_STUDIO_RELEASE.json']:
  data=urllib.request.urlopen('https://raw.githubusercontent.com/Ananas2000/divalead/'+commit+'/'+name,timeout=60).read();assert data==(P/name).read_bytes();public.append(dict(path=name,SHA256=sha(P/name),byte_exact=True))
 assert not git('status','--porcelain');write(R/'public-v70-verification.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),commit=commit,remote_exact=True,all_older_numbered_releases_unchanged=True,HTTP_files=public,tone_score=proof['tone_score'],match_reached=False))
 assert json.loads(PAUSE.read_text())['owner']=='publish-full-v70';PAUSE.unlink();print('FULL_V70_PUSHED_AND_HTTP_BYTE_VERIFIED',commit,proof['tone_score'],flush=True)
