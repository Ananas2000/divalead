"""Build a complete two-ZL WIP25 with only the verified third Side AllPass added."""
from pathlib import Path
import csv,gzip,hashlib,io,json,os,shutil,struct,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from win_vst3 import WinVST3
A=Path(__file__).resolve().parent;R=Path('/tmp/divalead-lowmid-side-phase-20261025-01');SOURCE=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP24');ROOT=Path('/tmp/divalead-full25-20261025/FL20_ZL25_STEREO_WIP')
assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT)
summary=json.loads((R/'completion.json').read_text());assert summary['robust_improvement'];audit=json.loads((R/'ACTUAL_COLD_REPLAY_AND_LATENCY_PROOF.json').read_text());assert max(audit['two_fresh_cold_actual_two_ZL_instances_replay_max_abs_errors'])==0
old_primary=(SOURCE/'verification/ZL24_PRIMARY_COMPONENT.bin').read_bytes();old_post=(SOURCE/'verification/ZL24_POST_COMPONENT.bin').read_bytes();primary=(R/'PRIMARY.bin').read_bytes();post=(R/'CANDIDATE_POST.bin').read_bytes()
def rename_display(data):
 p=parse(data);out=list(p['events']);label=None
 for k,(ident,value)in enumerate(out):
  if ident==203:label=k
  if ident==213 and label is not None:
   if primary in value:out[label]=(203,('ZL25 PRIMARY WIP\0').encode('utf-16-le'))
   elif post in value:out[label]=(203,('ZL25 STEREO FIX WIP\0').encode('utf-16-le'))
 return container(p['format'],b''.join(event(i,b)for i,b in out),p['channels'])
def both(data):return rename_display(replace_primary(replace_primary(data,old_primary,primary),old_post,post))
project=both((SOURCE/'Diva_ZL24_STEREO_WIP.flp').read_bytes());(ROOT/'Diva_ZL24_STEREO_WIP.flp').unlink();(ROOT/'Diva_ZL25_STEREO_WIP.flp').write_bytes(project)
(ROOT/'presets/04_SUM.fst').write_bytes(both((SOURCE/'presets/04_SUM.fst').read_bytes()))
for stem,old,new in [('PRIMARY',old_primary,primary),('STEREO_FIX',old_post,post)]:
 p=ROOT/f'presets/SUM_ZL24_{stem}.fst';data=rename_display(replace_primary(p.read_bytes(),old,new));p.unlink();(ROOT/f'presets/SUM_ZL25_{stem}.fst').write_bytes(data)
 p=ROOT/f'presets/ZL24_{stem}.vstpreset';p.unlink();new_path=ROOT/f'presets/ZL25_{stem}.vstpreset';new_path.write_bytes(vstpreset(new));assert read_vstpreset(new_path.read_bytes())==new
for p in ROOT.iterdir():
 if p.is_file()and(p.suffix in ['.mp3','.flac']or(p.suffix=='.wav'and p.name!='Diva_original_lead_reference.wav'and not p.name.startswith('Diva_SOURCE_'))):p.unlink()
V=ROOT/'verification'
for p in V.glob('*ZL24*'):p.unlink()
(V/'ZL25_PRIMARY_COMPONENT.bin').write_bytes(primary);(V/'ZL25_POST_COMPONENT.bin').write_bytes(post)
for name in ['completion.json','FROZEN_BEFORE_FRESH_VALIDATION.json','ACTUAL_COLD_REPLAY_AND_LATENCY_PROOF.json']:shutil.copyfile(R/name,V/('LOWMID_'+name))
for name in ['completion.json','FROZEN_BEFORE_VALIDATION.json','ARCHIVAL_GUI_SUMMARY.json','NEW_NATIVE_SUMMARY.json','ZIP_ACTUAL_REPLAY_PROOF.json','TSV_EMPTY_FINAL_FIELD_FORMAT_PROOF.json']:
 p=V/name
 if p.exists():p.rename(V/('historical_ZL24_'+name))
for p in V.glob('*610_PARAMETERS*'):p.unlink()
source_manifest=json.loads((SOURCE/'verification/NATIVE_BASE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']
for row in source_manifest:
 b=(ROOT/row['state']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['state_SHA256'];assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==b
before=parse((SOURCE/'Diva_ZL24_STEREO_WIP.flp').read_bytes());after=parse(project);bs=[v for i,v in before['events']if i==213];as_=[v for i,v in after['events']if i==213];assert bs[:-2]==as_[:-2]
assert [v for i,v in before['events']if i in [224,235]]==[v for i,v in after['events']if i in [224,235]]
assert component_from_wrapper(as_[-2],8)==primary and component_from_wrapper(as_[-1],8)==post
layout=dict(project='Diva_ZL25_STEREO_WIP.flp',primary_component='verification/ZL25_PRIMARY_COMPONENT.bin',post_component='verification/ZL25_POST_COMPONENT.bin',primary_preset='presets/SUM_ZL25_PRIMARY.fst',post_preset='presets/SUM_ZL25_STEREO_FIX.fst',sum_insert='presets/04_SUM.fst',primary_vstpreset='presets/ZL25_PRIMARY.vstpreset',post_vstpreset='presets/ZL25_STEREO_FIX.vstpreset')
(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
prior=json.loads((R/'PRIOR_CONFIRMED.json').read_text());loss=float(np.mean([c['candidate']['loss']for c in summary['captures'][:6]]));candidate=dict(prior,native_ZL_component_state=str(V/'ZL25_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL25_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL25_POST_COMPONENT.bin'),loss=loss,source_accepted_cohort='lowmid-Side-phase-after-cohort15',requires_two_ZL_instances=True,post_Side_AllPasses=[dict(frequency=10000,Q=2),dict(frequency=2200,Q=4),dict(frequency=895.8,Q=13.84)],full_public_kit_directory='ZL-WIP25',accepted_full_public_kit='ZL25',not_adopted_until_publication=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(V/'candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
raw,sr=sf.read(R/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);control,sr=sf.read(R/'CONTROL_00.wav',dtype='float32',always_2d=True);audio,sr=sf.read(R/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(ROOT/'ZL25_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment')
from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);old=edit(control);new=edit(audio);rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[1.,rms(ref)/rms(old),rms(ref)/rms(new)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old*gains[1],gap,new*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'ZL25_STEREO_REFERENCE_EDIT_WIP.wav',new,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_BEST15_ZL25_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB25-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_BEST15_ZL25_WIP.mp3')],check=True);tmp.unlink()
(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','previous_accepted_stereo_cohort15','ZL25_Side_lowmid_WIP'],starts_seconds=[0,4.168,8.336],RMS_gains=gains,common_peak_safety_gain=safety,only_AB_level_normalized=True,same_native_input_for_control_and_candidate=True),indent=2)+'\n')
guide='''# ZL25 STEREO WIP — следующий трёхнотный вариант

Полного совпадения с оригиналом ещё нет. Улучшение по исходному критерию
прошло6новых nativeпар и2холодных nativeвхода; новыйGUIэкспорт наПК не сделан.
Главный ZL — ранее принятый cohort15, дополнительный — новая Side-onlyфаза.
Три длинные ноты41→37→36 на фразу, дважды; движение делает внутренний ARP.
Все281 параметр Diva,ADSR/ARP/native06/fine32 и маршруты сохранены.

1. Распакуйте ZIP в новую папку и откройте Diva_ZL25_STEREO_WIP.flp в FL20/26.
   Pattern,180BPM. Нужны те же Diva/штатные Fruityэффекты и ZL Equalizer2v1.4.1.
   Если ZL не установлен: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SUM: StereoShaper → ZL25 PRIMARY → ZL25 STEREO FIX, оба ZL Mix100%.
   Во втором ZL три Side AllPass:10000Гц/Q2,2200Гц/Q4,895.8Гц/Q13.84.
   Gain0,остальные полосы OFF. MinimumPhase/Lookahead0/AutoGainOFF в обоих.
3. Для вашего уже работающего GUIпроекта: на первый ZL вSUM перетащите
   presets/SUM_ZL25_PRIMARY.fst; на следующий ZL — presets/SUM_ZL25_STEREO_FIX.fst.
   Второй экземпляр ZL нужно добавить, если его ещё нет. Можно загрузить
   presets/04_SUM.fst какMixer trackstate, затем проверитьSUM→Master ON.
   Сначала делать отдельную копию проекта. Новых скачиваемых эффектов нет.
4. Если Diva не восстановилась, загрузите h2p из комплекта. Имя пресета Diva
   может остаться прежним: изменены эффекты, все её звуковые параметры сохранены.

A/B: AB_ORIGINAL_BEST15_ZL25_WIP.mp3 — оригинал0с → предыдущий подтверждённый
cohort15 с4,168с → новый с8,336с. Оба варианта получили один и тот же native
input; отличие не вызвано новым случайным дублем Chorus. Есть losslessFLAC.
Нормирование громкости только в A/B, рабочийWAV не нормализован.

В300–800Гц перекос уменьшился примерно4.8→4.2дБ; оригинал тем же методом
около1дБ, так что это улучшение, а не готовое совпадение. Исправленный верх
сохранён, бас не выровнен искусственно в центр. Дополнительная Side-only
поправка сохраняет моно с остатком до1.2e-7. Оба ZL PDC0, первый импульсный
отклик без добавочного сдвига; это не измерение ASIO/всей DAW.

Кандидат зафиксирован до новых8проверок. Fresh6mean improvement.001388351833,
SEM.000015055695; прежний порог.0005 пройден. Cold2+.001292979650/+.001385139518.
Все8 дали улучшение. Рендеры настоящими nativeDLL иофициальными ZLVST3 на
сохранённом реальном Divaисточнике; новыеDivaVST/GUIэкспорты не заявляются.
Проверены12nativeFST/statebytes,оба реальных компонента вFLP/FST/VSTpreset,
неизменныеMIDI/routes и два холодных actualZLreplay после распаковкиZIP.
Все30training/validationWAV сохранены отдельно в Git. Оригинал толькоанализ/A/B,
не подмешивается в синтез. MistaTowa не используется. Поиск продолжается.
'''
for name in ['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
primary_host=WinVST3('ST25-kit25-primary');post_host=WinVST3('ST25-kit25-post')
try:
 for c,name,state in [(primary_host,'PRIMARY_610_PARAMETERS.tsv',V/'ZL25_PRIMARY_COMPONENT.bin'),(post_host,'POST_610_PARAMETERS.tsv',V/'ZL25_POST_COMPONENT.bin')]:
  c.load(state);p=V/name;c.dump(p);b=p.read_bytes();text=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in text.splitlines())+'\n';assert list(csv.reader(io.StringIO(text),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));p.write_text(normal)
finally:primary_host.close();post_host.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(all_native12_FST_state_bytes_exact=True,all_Diva_and_native_plugin_states_unchanged=True,MIDI_and_routes_preserved=True,only_two_ZL_payloads_and_display_labels_changed=True,primary_SHA256=hashlib.sha256(primary).hexdigest(),post_SHA256=hashlib.sha256(post).hexdigest(),actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL25_STEREO_WIP_complete.zip'
def pack():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack();restore=ROOT.parent/'independent-ZIP-restore';restore.mkdir(exist_ok=False)
with zipfile.ZipFile(archive)as z:assert z.testzip()is None;z.extractall(restore)
restored=restore/ROOT.name
for line in(restored/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==digest
errors=[]
for k in range(2):
 p=WinVST3('ST25-kit25-cold-primary');z=WinVST3('ST25-kit25-cold-post')
 try:
  p.load(restored/layout['primary_component']);z.load(restored/layout['post_component']);first,_=p.render(raw);out,_=z.render(first);np.testing.assert_allclose(out,audio,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-audio).max()));assert p.latency()==z.latency()==0
 finally:p.close();z.close()
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_ZL_cascades_max_abs_errors=errors,not_two_new_full_native_GUI_exports=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in ROOT.rglob('*'):
  if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
result=dict(root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),original_objective_export_mean=loss,ZIP_actual_two_cold_cascade_max_abs_errors=errors,source_Diva_native_MIDI_unchanged=True,requires_two_ZL_instances=True,post_Side_AllPasses=candidate['post_Side_AllPasses'],actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(A/'ZL25_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
