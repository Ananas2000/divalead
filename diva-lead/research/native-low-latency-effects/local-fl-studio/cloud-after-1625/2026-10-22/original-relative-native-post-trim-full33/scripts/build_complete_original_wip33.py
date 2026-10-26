"""Build complete FL20 WIP33 with actual native trim after the two ZLs."""
from pathlib import Path
import csv,gzip,hashlib,io,json,os,shutil,struct,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from native_post_trim import NativePostTrim
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;Q=H/'RELATIVE_AIR_NATIVE_POST_TRIM';PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');SOURCE=PUBLIC/'ZL-WIP32';ROOT=H/'full33-build/FL20_ZL33_STEREO_WIP';V=ROOT/'verification';s=json.loads((Q/'completion.json').read_text());assert s['robust_improvement'];assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT)
for p in ROOT.glob('*.zip'):p.unlink()
old_primary=(SOURCE/'verification/ZL32_PRIMARY_COMPONENT.bin').read_bytes();primary=(Q/'PRIMARY.bin').read_bytes();post=(Q/'CONTROL_POST.bin').read_bytes();trim=(Q/'CANDIDATE_TRIM.bin').read_bytes();assert primary!=old_primary and post==(SOURCE/'verification/ZL32_POST_COMPONENT.bin').read_bytes()
template=parse((SOURCE/'presets/SUM_Stereo.fst').read_bytes());native_shell=next(v for i,v in template['events']if i==212)
sum_events=parse((SOURCE/'presets/04_SUM.fst').read_bytes())['events'];native_color=next(v for i,v in sum_events if i==155);native_flags=next(v for i,v in sum_events if i==128)
def native_events(track,slot):
 shell=bytearray(native_shell);struct.pack_into('<II',shell,0,track,slot)
 return[(201,('Fruity Stereo Shaper\0').encode('utf-16-le')),(212,bytes(shell)),(203,('ZL33 POST STEREO TRIM WIP\0').encode('utf-16-le')),(155,native_color),(128,native_flags),(213,trim)]
def transform(data,is_project=False,add_trim=False):
 p=parse(data)
 if any(i==213 and old_primary in v for i,v in p['events']):data=replace_primary(data,old_primary,primary);p=parse(data)
 armed=not is_project;inserted=False;out=[];control_changes=[]
 for ident,value in p['events']:
  if is_project and ident==204 and value.decode('utf-16-le').rstrip('\0')=='04_SUM':armed=True
  if add_trim and armed and not inserted and ident==98 and value==struct.pack('<H',3):out.extend(native_events(4 if is_project else 1,3));inserted=True
  if add_trim and ident==225:
   b=bytearray(value)
   for off in range(0,len(b),12):
    unused,param,kind,track,old=struct.unpack_from('<IBBHi',b,off)
    if kind==31 and(track&63)==3 and((track>>6)&127)==(4 if is_project else 1)and param in[0,1]:
     new=1 if param==0 else 12800
     if old!=new:control_changes.append(dict(param=param,track=track,before=old,after=new))
     struct.pack_into('<i',b,off+8,new)
   value=bytes(b)
  if ident==203:value=value.replace('ZL32'.encode('utf-16-le'),'ZL33'.encode('utf-16-le'))
  out.append((ident,value))
 if add_trim:assert inserted and any(r['param']==0 for r in control_changes)
 return container(p['format'],b''.join(event(i,v)for i,v in out),p['channels']),control_changes
project,project_changes=transform((SOURCE/'Diva_ZL32_STEREO_WIP.flp').read_bytes(),True,True);(ROOT/'Diva_ZL32_STEREO_WIP.flp').unlink();(ROOT/'Diva_ZL33_STEREO_WIP.flp').write_bytes(project)
fst_changes={}
for src in(SOURCE/'presets').glob('*.fst'):
 data,changes=transform(src.read_bytes(),False,src.name=='04_SUM.fst');dst=ROOT/'presets'/src.name.replace('ZL32','ZL33');old=ROOT/'presets'/src.name
 if old!=dst:old.unlink()
 dst.write_bytes(data);fst_changes[dst.name]=changes
standalone=container(template['format'],event(199,b'20.8.4.2576\0')+b''.join(event(i,v)for i,v in native_events(0,0)),template['channels']);(ROOT/'presets/SUM_ZL33_STEREO_TRIM.fst').write_bytes(standalone)
assert next(v for i,v in parse(standalone)['events']if i==213)==trim
for stem,state in[('PRIMARY',primary),('STEREO_FIX',post)]:
 (ROOT/f'presets/ZL32_{stem}.vstpreset').unlink();dst=ROOT/f'presets/ZL33_{stem}.vstpreset';dst.write_bytes(vstpreset(state));assert read_vstpreset(dst.read_bytes())==state
for p in V.glob('ZL32*'):p.unlink()
(V/'ZL33_PRIMARY_COMPONENT.bin').write_bytes(primary);(V/'ZL33_POST_COMPONENT.bin').write_bytes(post);(V/'POST_NATIVE_STEREO_TRIM.bin').write_bytes(trim)
for name in['CASCADE_BUILD_PROOF.json','ZIP_ACTUAL_REPLAY_PROOF.json','AB_LEVELS.json']:
 p=V/name
 if p.exists():p.rename(V/('historical_ZL32_'+name))
for name in['completion.json','PREDECLARED_PROTOCOL.json','FROZEN_BEFORE_FRESH_VALIDATION.json','HELDOUT.json','ACTUAL_NATIVE_TRIM_IDENTITY_GAIN_COLD_IMPULSE_PROOF.json']:shutil.copyfile(Q/name,V/('NATIVE_POST_TRIM_'+name))
before=parse((SOURCE/'Diva_ZL32_STEREO_WIP.flp').read_bytes());after=parse(project);bs=[v for i,v in before['events']if i==213];as_=[v for i,v in after['events']if i==213];assert len(as_)==len(bs)+1 and as_[-1]==trim;assert bs[:-2]==as_[:-3];assert component_from_wrapper(as_[-3],8)==primary and component_from_wrapper(as_[-2],8)==post
assert[v for i,v in before['events']if i in[224,235]]==[v for i,v in after['events']if i in[224,235]]
native_manifest=json.loads((SOURCE/'verification/NATIVE_BASE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']
for row in native_manifest:
 assert(ROOT/row['state']).read_bytes()==(SOURCE/row['state']).read_bytes();assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==(ROOT/row['state']).read_bytes()
layout=dict(project='Diva_ZL33_STEREO_WIP.flp',primary_component='verification/ZL33_PRIMARY_COMPONENT.bin',post_component='verification/ZL33_POST_COMPONENT.bin',primary_preset='presets/SUM_ZL33_PRIMARY.fst',post_preset='presets/SUM_ZL33_STEREO_FIX.fst',sum_insert='presets/04_SUM.fst',primary_vstpreset='presets/ZL33_PRIMARY.vstpreset',post_vstpreset='presets/ZL33_STEREO_FIX.vstpreset',post_native_trim_state='verification/POST_NATIVE_STEREO_TRIM.bin',post_native_trim_preset='presets/SUM_ZL33_STEREO_TRIM.fst');(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
prior=json.loads((Q/'PRIOR_CONFIRMED.json').read_text());settings=s['winner']['settings'];loss=float(np.mean([r['candidate']['loss']for r in s['captures'][:10]]));choice=dict(prior,native_ZL_component_state=str(V/'ZL33_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL33_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL33_POST_COMPONENT.bin'),post_native_trim_state=str(V/'POST_NATIVE_STEREO_TRIM.bin'),requires_post_native_trim=True,post_native_trim=settings,post_native_trim_added_delay_frames=0,post_native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),native_effect_added_after_ZLs=True,native_effect_count=13,pre_ZL_native_effect_count=12,requires_two_ZL_instances=True,primary_relative_dynamic_bands=[21],upper_stereo_error_limit_dB=1.48,lowmid_error_limit_dB=3.25,positive_excess_air_preservation_required=True,paired_air_increase_limit_dB=.02,full_public_kit_directory='ZL-WIP33',accepted_full_public_kit='ZL33',source_accepted_cohort='relative-primary-plus-actual-native-post-trim',loss=loss,native_parameters_changed_from_previous_public_kit=False,source_Diva_unchanged=True,recorded_audio=str(ROOT/'ZL33_STEREO_FULL_WIP.wav'),not_adopted_until_publication=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,topology='native12/base10 WS52 -> relative PRIMARY -> unchanged POST32 -> native Stereo Shaper channel trim',actual_FL_GUI_validation_pending=True,reference_match_reached=False)
for key in['ZL_peaking_MidSide_x','ZL_allpass_bands','ZL_dynamic_bands','ZL_output_gain_dB']:choice.pop(key,None)
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
for p in ROOT.iterdir():
 if p.is_file()and(p.suffix in['.mp3','.flac']or(p.suffix=='.wav'and p.name!='Diva_original_lead_reference.wav'and not p.name.startswith('Diva_SOURCE_'))):p.unlink()
raw,sr=sf.read(Q/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);old,_=sf.read(Q/'CONTROL_00.wav',dtype='float32',always_2d=True);pre,_=sf.read(Q/'BEFORE_TRIM_00.wav',dtype='float32',always_2d=True);audio,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(ROOT/'ZL33_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT');sf.write(V/'BEFORE_NATIVE_TRIM_WIP.wav',pre,sr,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment');from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);assert hashlib.sha256((ROOT/'Diva_original_lead_reference.wav').read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF);rms=lambda y:float(np.sqrt(np.mean(y*y)));old_edit,new_edit=edit(old),edit(audio);gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old_edit*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'ZL33_STEREO_REFERENCE_EDIT_WIP.wav',new_edit,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_ZL32_ZL33_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_ZL32_ZL33_WIP.mp3')],check=True);tmp.unlink();(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','accepted32_same_native_input','new33_same_native_input'],starts_seconds=[0,4.168,8.336],global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_normalized=True,no_independent_channel_normalization=True),indent=2)+'\n')
metrics={key:{label:float(np.mean([r[label]['assessment']['metrics'][key]for r in s['captures'][:10]]))for label in['control','candidate']}for key in s['captures'][0]['control']['assessment']['metrics']};(V/'PAIRED_FIRST10_METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
guide=f'''# ZL33 WIP: относительная динамика и штатная коррекция каналов после EQ

Полного совпадения с оригиналом ещё нет. Это прошедшее новую проверку промежуточное улучшение относительно32. Цель — исходный Diva_original_lead_reference.wav, не v83/Finish.

1. Распаковать ZIP в новую папку и открыть Diva_ZL33_STEREO_WIP.flp в FL Studio20/26. Pattern180BPM. Нужны прежние Diva, штатные Fruity и бесплатный ZL Equalizer2v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. SUM: прежний Stereo Shaper → ZL33 PRIMARY → ZL33 STEREO FIX → НОВЫЙ Fruity Stereo Shaper POST TRIM. Последний эффект стоит именно ПОСЛЕ второгоZL, Mix100%, задержки0, перекрёстные каналы0. Его штатные rawпараметры: [0,{settings['left_raw']},{settings['right_raw']},0,0,0]; запрошенное ослабление левого канала−0.035dB, правый прежний. Это очень небольшая поправка, полного устранения слышимого перекоса не заявляется.
3. Для переноса из32 загрузить presets/SUM_ZL33_PRIMARY.fst в первыйZL; второйZL имеет прежние настройки32. Добавить presets/SUM_ZL33_STEREO_TRIM.fst в следующий слот SUM. Альтернатива — загрузить весь presets/04_SUM.fst какMixertrackstate и проверить SUM→Master. SOURCE/MID/SIDE прежние32. Всего13nativeэффектов и ДВАZL; новыйnative — только последний Stereo Shaper. При переносе из30и старше дополнительно обновить SOURCE WaveShaper изкомплекта; нужентотжеWS52как31/32.
4. Если Diva не восстановилась — загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid: 41→37→36 дважды, шестьnote-on. Верхние скачки создаёт внутреннийARP. Все281параметров Diva, ARP/ADSR, прежние12nativeсостояний/криваяWS52/маршруты сохранены.

A/B AB_ORIGINAL_ZL32_ZL33_WIP.mp3 илиFLAC: оригинал0с →32с4.168с →33с8.336с. Контроль/кандидат получили один и тот же настоящий nativeinput. Только A/B выровнен общейstereoRMS; рабочийWAV безнормировки, независимая нормировкаL/R не применялась.

Изменённый PRIMARY сохраняет Relative ON в существующей Sideдинамическойполосе21 и согласованные параметры EQ. POST тот же32:3SideAP10207.6Hz/Q2.198,2149.8/Q4.702,930/Q11.336; StereoAP782.9/Q20.561; LeftPeak994/Q5.871/−1.70dB. Последний Stereo Shaper меняет только уровни каналов. СтарыйFinish/длиннаясвёртка не используются.

Отдельныйrelativeвариант был отклонён за увеличившийся воздух; новыйPRIMARY после793реальныхпроб улучшил тон/чистоту, ноодна из12пар не прошла прежнююstereoguard. Эти варианты не принимались. НовыйDSPпункт33 добавляет реальнуюnativeкоррекцию каналов:27реальныхпроб,3новыхtraininginput/2heldout, фиксациядо12НОВЫХпар. First6gain{s['first6_mean_improvement']:.12f},SEM{s['first6_SEM']:.12f}; first10gain{s['first10_mean_improvement']:.12f},SEM{s['first10_SEM']:.12f}; оба>max(.0005,3SEM). Cold2{s['cold2_improvements']}. UpperLRRMSerror всех12≤1.48dB, строже прежних1.5; maxabsupperLR≤1.6; lowmid≤3.25 и≤контроль+.02. Среднее увеличение положительного offharmonicизбытка3.5–6.5k{s['first10_air_increase']:.12f}dB; обаcold≤+.02. Это физические метрики, не субъективное прослушивание или процентсходства.

First10исходныйobjective{loss:.12f}. Полная таблица плюсов и оставшихся/ухудшившихся метрик в verification/PAIRED_FIRST10_METRICS.json. Остаточные различия тембра, стерео и шума сохраняются; точное совпадение не объявляется.

ActualFruityStereoShaper: unitymaxerror5.96e-8, калибровка6усилений≤2e-7, раздельныеимпульсы безперекрёстныхканалов и добавленнойзадержки, холодныйnativeState0/resaveexact. ZIPпроверяется независимойраспаковкой; два холодных настоящих каскадаZL+nativeTrim воспроизводят WAV. ZL PDC0, nativeTrim impulse0; это не оценкаASIO/всегоDAW. Предыдущаяnative12база не менялась, её малые blocksizeразличия/начальнаяреакция2samples раскрыты встаром nativeproof.

НовыйFLP здесь не открывался вWindowsGUI. Проверены его данные, пресеты и настоящиеDLL/VST3рендеры вLinux/Wine. Субъективное прослушивание ассистентом не заявляется. Оригинал используется только для анализа/A-B, в синтез не подмешивается. MistaTowa не используется. Старые комплекты/история/PCGUIпроект сохранены.
'''
for name in['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
for stem,state in[('PRIMARY',V/'ZL33_PRIMARY_COMPONENT.bin'),('POST',V/'ZL33_POST_COMPONENT.bin')]:
 c=WinVST3('ZL33-dump-'+stem)
 try:
  c.load(state);dst=V/(stem+'_610_PARAMETERS.tsv');c.dump(dst);b=dst.read_bytes();t=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in t.splitlines())+'\n';assert list(csv.reader(io.StringIO(t),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(dst.name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));dst.write_text(normal)
 finally:c.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(all_original_native12_states_and_Diva_MIDI_routes_unchanged=True,new_native13th_effect_after_ZLs=True,native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),native_trim_slot=3,project_effect_enable_mix_changes=project_changes,FST_effect_enable_mix_changes=fst_changes,post_ZL_unchanged_from32=True,reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL33_STEREO_WIP_complete.zip'
def pack():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack();restore=ROOT.parent/'independent-ZIP-restore';restore.mkdir()
with zipfile.ZipFile(archive)as z:assert z.testzip()is None;z.extractall(restore)
restored=restore/ROOT.name
for line in(restored/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==digest
errors=[];ZL_errors=[];delays=[]
for k in range(2):
 p=WinVST3('ZL33-ZIP-cold-primary-'+str(k));z=WinVST3('ZL33-ZIP-cold-post-'+str(k));c=NativePostTrim(ROOT.parent/'cold-native-inputs','ZL33-ZIP-cold-trim-'+str(k))
 try:
  for host,path in[(p,restored/layout['primary_component']),(z,restored/layout['post_component'])]:
   host.load(path);dst=ROOT.parent/('cold-'+str(k)+'-'+path.name);host.save(dst);assert dst.read_bytes()==path.read_bytes()
  fst_state=next(v for i,v in parse((restored/layout['post_native_trim_preset']).read_bytes())['events']if i==213);assert fst_state==(restored/layout['post_native_trim_state']).read_bytes();c.load(restored/layout['post_native_trim_state']);dst=ROOT.parent/f'cold-native-{k}.bin';c.save(dst);assert dst.read_bytes()==trim
  mid,_=p.render(raw);got,_=z.render(mid);np.testing.assert_allclose(got,pre,rtol=8*np.finfo(np.float32).eps,atol=1e-12);ZL_errors.append(float(abs(got-pre).max()));out=c.render(got);error=float(abs(out-audio).max());assert error<=2e-7,error;errors.append(error);assert p.latency()+z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);out=c.render(out);assert not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0;delays.append(delay)
 finally:p.close();z.close();c.close()
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_two_ZL_before_native_trim_errors=ZL_errors,two_fresh_actual_full_chain_with_native_trim_errors=errors,strict_ZL_rtol_float32eps=8,strict_ZL_atol=1e-12,strict_native_trim_absolute_tolerance=2e-7,all_component_and_native_state_resaves_byte_exact=True,combined_ZL_PDC_frames=0,full_ZL_plus_nativeTrim_impulse_added_delay_samples=delays,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in ROOT.rglob('*'):
  if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
result=dict(root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),first10_original_objective=loss,actual_two_cold_ZL_replay_errors=ZL_errors,actual_two_cold_full_native_trim_chain_errors=errors,native_base='10',native_effects_before_ZL=12,native_effects_after_ZL=1,post_trim=settings,post_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),post_ZL_unchanged32=True,source_Diva_MIDI_ARP_ADSR_unchanged=True,actual_FL_GUI_validation_pending=True,original_is_the_only_target=True,reference_match_reached=False);(H/'ZL33_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
