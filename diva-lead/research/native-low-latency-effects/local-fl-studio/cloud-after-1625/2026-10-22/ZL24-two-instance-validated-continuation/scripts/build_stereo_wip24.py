"""Build a portable FL20/26 TWO-ZL kit and actually replay extracted presets."""
from pathlib import Path
import csv,hashlib,json,os,shutil,struct,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import decode_records,encode_records,component_from_wrapper,vstpreset,read_vstpreset
from win_vst3 import WinVST3
A=Path(__file__).resolve().parent;C=A/'local-fl-matching/sessions/2026-10-24';V=A/'frozen-stereo-validation01'
ROOT=A/'FL20_ZL24_STEREO_WIP';ROOT.mkdir(exist_ok=False)
source=C/'ZL23_upstream/FL20_ZL_23_WIP'
for p in source.iterdir():
 if p.is_dir():shutil.copytree(p,ROOT/p.name)
 else:shutil.copyfile(p,ROOT/p.name)
report=json.loads((V/'completion.json').read_text());assert report['new_native6_and_cold2_original_criterion_passed']and report['archival_GUI_original_criterion_passed']
primary=(V/'PRIMARY_COMPONENT.bin').read_bytes();post=(V/'POST_COMPONENT.bin').read_bytes();old=(C/'ZL23_CONFIRMED_INPUT.bin').read_bytes();old_public=(source/'verification/ZL_component.bin').read_bytes()
def patch_wrapper(state,old,new):
 marker=struct.unpack_from('<I',state)[0];records=decode_records(state,marker);out=[];changes=0
 for ident,data in records:
  if ident==53:
   inner=decode_records(data,1);assert sum(i==3 and b==old for i,b in inner)==1
   data=encode_records([(i,new if i==3 else b)for i,b in inner],1);changes+=1
  out.append((ident,data))
 assert changes==1;result=encode_records(out,marker);assert component_from_wrapper(result,marker)==new;return result
def replace(data,before,after,label=None):
 p=parse(data);events=[];count=0
 for ident,b in p['events']:
  if ident==213 and before in b:b=patch_wrapper(b,before,after);count+=1
  if label is not None and ident==203:b=(label+'\0').encode('utf-16-le')
  events.append((ident,b))
 assert count==1
 return container(p['format'],b''.join(event(i,b)for i,b in events),p['channels'])
template=parse((C/'SUM_ZL23_CONFIRMED_LOCAL.fst').read_bytes())
standalone_primary=replace((C/'SUM_ZL23_CONFIRMED_LOCAL.fst').read_bytes(),old,primary,'ZL24 PRIMARY WIP')
standalone_post=replace((C/'SUM_ZL23_CONFIRMED_LOCAL.fst').read_bytes(),old,post,'ZL24 STEREO FIX WIP')
post_state10=next(b for i,b in parse(standalone_post)['events']if i==213);post_state8=encode_records(decode_records(post_state10,10),8)
template_shell=next(b for i,b in template['events']if i==212)
def plugin_events(track,slot,is_project):
 b=bytearray(template_shell);struct.pack_into('<II',b,0,track,slot)
 return [(201,('Fruity Wrapper\0').encode('utf-16-le')),(212,bytes(b)),(203,('ZL24 STEREO FIX WIP\0').encode('utf-16-le')),(155,bytes(4)),(128,b'HQV\0'),(213,post_state8 if is_project else post_state10)]
def add_post(data,is_project):
 p=parse(data);events=p['events'];out=[];armed=not is_project;inserted=False;changed=[]
 start=max(k for k,(i,b)in enumerate(events)if i==204 and b.decode('utf-16-le').rstrip('\0')=='04_SUM')if is_project else -1
 for k,(i,b)in enumerate(events):
  if k==start:armed=True
  if armed and not inserted and i==98 and b==struct.pack('<H',2):out.extend(plugin_events(4 if is_project else 1,2,is_project));inserted=True
  if i==225:
   b=bytearray(b)
   for offset in range(0,len(b),12):
    _,param,kind,track,value=struct.unpack_from('<IBBHi',b,offset)
    if kind==31 and(track&63)==2 and((track>>6)&127)==(4 if is_project else 1)and param in [0,1]:
     new=1 if param==0 else 12800
     if new!=value:changed.append(dict(param=param,track=track,before=value,after=new))
     struct.pack_into('<i',b,offset+8,new)
   b=bytes(b)
  out.append((i,b))
 assert inserted and any(x['param']==0 for x in changed)
 result=container(p['format'],b''.join(event(i,b)for i,b in out),p['channels']);q=parse(result)
 assert[b for i,b in events if i in [224,235]]==[b for i,b in q['events']if i in [224,235]]
 old_states=[b for i,b in events if i==213];new_states=[b for i,b in q['events']if i==213]
 assert new_states[:-1]==old_states and component_from_wrapper(new_states[-1],8 if is_project else 10)==post
 return result,changed
project=replace((C/'Diva_ZL23_CONFIRMED_LOCAL.flp').read_bytes(),old,primary)
project,controls=add_post(project,True)
for p in ROOT.glob('*.flp'):p.unlink()
(ROOT/'Diva_ZL24_STEREO_WIP.flp').write_bytes(project)
insert=replace((source/'presets/04_SUM.fst').read_bytes(),old_public,primary)
insert,sum_controls=add_post(insert,False);(ROOT/'presets/04_SUM.fst').write_bytes(insert)
for p in(ROOT/'presets').glob('*ZL*'):p.unlink()
(ROOT/'presets/SUM_ZL24_PRIMARY.fst').write_bytes(standalone_primary);(ROOT/'presets/SUM_ZL24_STEREO_FIX.fst').write_bytes(standalone_post)
for name,component in [('ZL24_PRIMARY',primary),('ZL24_STEREO_FIX',post)]:
 p=ROOT/'presets'/(name+'.vstpreset');p.write_bytes(vstpreset(component));assert read_vstpreset(p.read_bytes())==component
verification=ROOT/'verification'
for p in verification.glob('ZL*'):p.unlink()
for name,component in [('ZL24_PRIMARY_COMPONENT.bin',primary),('ZL24_POST_COMPONENT.bin',post)]: (verification/name).write_bytes(component)
for name in ['completion.json','FROZEN_BEFORE_VALIDATION.json','ARCHIVAL_GUI_SUMMARY.json','NEW_NATIVE_SUMMARY.json']:shutil.copyfile(V/name,verification/name)
native=json.loads((source/'verification/NATIVE_BASE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest'];native_checks=[]
for row in native:
 state=(ROOT/row['state']).read_bytes();assert hashlib.sha256(state).hexdigest()==row['state_SHA256'];fst=parse((ROOT/row['preset']).read_bytes());assert next(b for i,b in fst['events']if i==213)==state;native_checks.append(row)
assert len(native_checks)==12
for p in ROOT.glob('*.mp3'):p.unlink()
for p in ROOT.glob('NATIVE*.wav'):p.unlink()
audio,sr=sf.read(V/'NEW_NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);control,_=sf.read(V/'NEW_NATIVE_CONTROL_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(ROOT/'ZL24_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(A/'kit24-assessment')
from fl20_objective import a
edit=a.h.edit_aligned(a.h.align_with_pdc(audio,dict(alignment_frames=819),latency=0));old_edit=a.h.edit_aligned(a.h.align_with_pdc(control,dict(alignment_frames=819),latency=0));sf.write(ROOT/'ZL24_STEREO_REFERENCE_EDIT_WIP.wav',edit,sr,subtype='FLOAT')
ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(edit)];clips=[ref,old_edit*gains[1],edit*gains[2]];gap=np.zeros((24000,2));ab=np.concatenate([clips[0],gap,clips[1],gap,clips[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'AB_ORIGINAL_ZL23_ZL24_STEREO_WIP.flac',ab,sr,subtype='PCM_24');working=A/'AB24-working.wav';sf.write(working,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(working),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_ZL23_ZL24_STEREO_WIP.mp3')],check=True);working.unlink()
(verification/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','confirmed_ZL23_same_native_input','ZL24_stereo_WIP_same_native_input'],starts_seconds=[0,4.168,8.336],RMS_gains=gains,common_peak_safety_gain=safety,only_AB_normalized=True),indent=2)+'\n')
guide='''# ZL24 STEREO WIP — три длинные ноты, исправление перекоса влево

Это промежуточный вариант. Полного совпадения с оригиналом ещё нет. Реальный
GUI FL26 использован для контрольных входов; новый проект ещё не открывался
и не экспортировался в GUI на вашем ПК. Файл собран в формате FL20.8.4.

1. Уже установленные Diva и штатные Fruity эффекты остаются. Нужен тот же
   бесплатный ZL Equalizer2 v1.4.1 Windows x64 VST3. Если его нет:
   https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. Распакуйте ZIP в новую папку и откройте Diva_ZL24_STEREO_WIP.flp.
   Pattern,180BPM. Три длинные ноты41→37→36 на фразу, фраза дважды.
   Взлёты создаёт внутренний ARP Diva; MIDI не заменён множеством коротких нот.
3. На SUM порядок: Stereo Shaper → ZL24 PRIMARY → ZL24 STEREO FIX.
   Это ДВА экземпляра того же ZL, оба слота Mix100%. Не менять их местами.
   Второй содержит только Side AllPass10000Гц/Q2 и2200Гц/Q4; Gain0.
   Он исправляет стереофазу, без подъёма/среза спектра моносигнала.
4. Для существующего лучшего проекта FL26 можно загрузить изменения вручную:
   на существующий ZL в SUM перетащите presets/SUM_ZL24_PRIMARY.fst;
   добавьте ЕЩЁ ZL сразу следующим слотом и перетащите
   presets/SUM_ZL24_STEREO_FIX.fst. Mix обоих100%. Остальные дорожки не меняйте.
   Альтернатива — presets/04_SUM.fst как Mixer track state SUM; проверьте
   включённый выход SUM в Master. Стандартные VSTpreset оставлены как резерв.
5. В обоих ZL Minimum Phase,Lookahead0,AutoGainOFF. Оба дают declaredPDC0
   и первый импульсный отклик0. Это не замер задержки ASIO/всей DAW.
6. При проблеме загрузки Diva загрузите сохранённый h2p из этого комплекта.
   У источника OscMix6.5,Noise0,Drift24.8,Pan−39.33; ARP/ADSR сохранены.

Послушать AB_ORIGINAL_ZL23_ZL24_STEREO_WIP.mp3: оригинал0с, прежний ZL23 с4,168с,
новый вариант с8,336с. Контроль и кандидат обработали ОДИН native input,
поэтому различие не вызвано другим случайным дублем Chorus. Только A/B
выровнен по RMS; рабочий WAV не нормализован. Есть lossless FLAC.

На8архивных реальных входах FL и6новых native рендерах+2холодных загрузках
исходный общий критерий и stereoошибка улучшились. Архивные GUIвходы раньше
использовались для другого кандидата: это не новый нетронутый GUIholdout.
Новые native рендеры использовали сохранённый реальный Divaисточник.
Новое исполнение Diva VST/GUI FL в этом этапе не заявляется. Два холодных
каскада VST3 дали точный0остаток. Все12native состояния и ноты сохранены.

В5–10кГц прежний GUI давал около5,4дБ слева. Новый trainingвариант дал около
0,9дБ, а2–5кГц около0,3дБ. Это исправление частотного перекоса, не раздельная
RMSнормализация каналов. Бас оригинала сам асимметричен. Стерео и тембр ещё
имеют остаточные различия; готовое совпадение не объявляется. Не сводите два
ZL к одному без проверки: порядок обработки M/S влияет на результат.
'''
(ROOT/'FL_STUDIO_RU.md').write_text(guide);(ROOT/'README_RU.md').write_text(guide)
(verification/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(native12_states_and_plugin_FST_payloads_byte_exact=True,all_original_routes_and_MIDI_224_235_byte_preserved=True,only_new_enabled_slot=2,changed_mixer_controls=controls,SUM_FST_controls=sum_controls,primary_component_SHA256=hashlib.sha256(primary).hexdigest(),post_component_SHA256=hashlib.sha256(post).hexdigest(),actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n')
zip_path=A/'Diva_ZL24_STEREO_WIP_complete.zip'
def checksums():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
def pack():
 checksums()
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack();restore=A/'ZL24-independent-ZIP-restore';restore.mkdir(exist_ok=False)
with zipfile.ZipFile(zip_path)as z:assert z.testzip()is None;z.extractall(restore)
extracted=restore/ROOT.name
for line in(extracted/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((extracted/name).read_bytes()).hexdigest()==digest
flp_states=[b for i,b in parse((extracted/'Diva_ZL24_STEREO_WIP.flp').read_bytes())['events']if i==213];primary2=component_from_wrapper(flp_states[-2],8);post2=component_from_wrapper(flp_states[-1],8);assert primary2==primary and post2==post
raw,sr=sf.read(V/'NEW_NATIVE_NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);expected=sf.read(V/'NEW_NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True)[0];errors=[]
for i in range(2):
 p=WinVST3('PC-kit24-replay-primary');z=WinVST3('PC-kit24-replay-post')
 try:
  for c,name in [(p,'ZL24_PRIMARY_COMPONENT.bin'),(z,'ZL24_POST_COMPONENT.bin')]:c.load(extracted/'verification'/name)
  first,_=p.render(raw);out,_=z.render(first);np.testing.assert_allclose(out,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-expected).max()))
  p.dump(verification/'PRIMARY_610_PARAMETERS.tsv');z.dump(verification/'POST_610_PARAMETERS.tsv');assert p.latency()==z.latency()==0
 finally:p.close();z.close()
proof=dict(independent_ZIP_CRC_and_all_SHA_verified=True,FLP_contains_both_exact_components=True,native12_states_and_FST_bytes_unchanged=True,MIDI_and_routes_preserved=True,two_fresh_cold_real_ZL_cascade_replays=True,whole_chain_fixed_native_input_replay_max_abs_errors=errors,not_six_new_full_native_exports_from_ZIP=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(verification/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');pack()
with zipfile.ZipFile(zip_path)as z:assert z.testzip()is None;assert z.read(ROOT.name+'/verification/ZIP_ACTUAL_REPLAY_PROOF.json')==(verification/'ZIP_ACTUAL_REPLAY_PROOF.json').read_bytes()
(A/'ZL24_BUILD_COMPLETION.json').write_text(json.dumps(dict(root=str(ROOT),ZIP=str(zip_path),ZIP_bytes=zip_path.stat().st_size,ZIP_SHA256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),proof=proof,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');print('STEREO_ZL24_KIT_AND_EXTRACTED_REAL_REPLAY_PASS',zip_path,zip_path.stat().st_size,flush=True)
