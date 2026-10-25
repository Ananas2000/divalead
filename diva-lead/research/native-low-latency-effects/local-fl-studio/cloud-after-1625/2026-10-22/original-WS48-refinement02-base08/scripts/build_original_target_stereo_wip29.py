"""Export WS48+new PRIMARY as complete WIP27; actual cold saved-state replay."""
from pathlib import Path
import csv,gzip,hashlib,io,json,os,shutil,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from win_vst3 import WinVST3
from native_chain import NativeChain
from fl20_curve import apply_candidate
H=Path(__file__).resolve().parent
J=Path('/tmp/divalead-original-native-WS48-20261025-02')
SOURCE=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22/ZL-WIP28')
BASE=Path('/tmp/divalead-local-1625/FL20_NATIVE_ZL_REBASED_08')
ROOT=Path('/tmp/divalead-full29-20261025/FL20_ZL29_STEREO_WIP')
assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT)
for p in ROOT.glob('*.zip'):p.unlink()
V=ROOT/'verification';summary=json.loads((J/'completion.json').read_text());assert summary['robust_improvement']
choice=json.loads(BASE.with_name(BASE.name+'-COMBINED_CANDIDATE_READY.json').read_text())
old_native=json.loads((SOURCE/'verification/NATIVE_BASE_PRESET_VERIFICATION.json').read_text())
new_native=json.loads((BASE/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())
assert new_native['preset_state_bytes_exact'] and new_native['zero_depth_routing_audio_exact']
old_ws=(SOURCE/'verification/SOURCE_WaveShaper.bin').read_bytes();new_ws=(BASE/'verification/SOURCE_WaveShaper.bin').read_bytes();assert old_ws!=new_ws
old_primary=(SOURCE/'verification/ZL28_PRIMARY_COMPONENT.bin').read_bytes();primary=(J/'PRIMARY.bin').read_bytes();post=(J/'POST.bin').read_bytes()
assert old_primary!=primary and post==(SOURCE/'verification/ZL28_POST_COMPONENT.bin').read_bytes()
changed=[]
for old,new in zip(old_native['native_plugin_manifest'],new_native['native_plugin_manifest']):
 assert old['node']==new['node'];b=(BASE/new['state']).read_bytes()
 assert hashlib.sha256(b).hexdigest()==new['state_SHA256']
 if b!=(SOURCE/old['state']).read_bytes():changed.append(new['node'])
 (ROOT/new['state']).write_bytes(b)
assert changed==[0]
def transform(data):
 p=parse(data);out=[];nws=0;np_=0
 for ident,value in p['events']:
  if ident==213 and value==old_ws:value=new_ws;nws+=1
  elif ident==213 and old_primary in value:
   # Wrapper-aware replacement, never a blind binary length edit.
   payload=container(p['format'],event(213,value),p['channels'])
   value=next(v for i,v in parse(replace_primary(payload,old_primary,primary))['events']if i==213);np_+=1
  if ident==203 and isinstance(value,bytes):
   value=value.replace('ZL28'.encode('utf-16-le'),'ZL29'.encode('utf-16-le'))
  out.append((ident,value))
 return container(p['format'],b''.join(event(i,v)for i,v in out),p['channels']),nws,np_
proj_old=SOURCE/'Diva_ZL28_STEREO_WIP.flp';data,nws,np_=transform(proj_old.read_bytes());assert (nws,np_)==(1,1)
(ROOT/proj_old.name).unlink();project=ROOT/'Diva_ZL29_STEREO_WIP.flp';project.write_bytes(data)
fst_changes={}
for src in sorted((SOURCE/'presets').glob('*.fst')):
 data,nws,np_=transform(src.read_bytes());dst=ROOT/'presets'/src.name.replace('ZL28','ZL29')
 old=ROOT/'presets'/src.name
 if old!=dst:old.unlink()
 dst.write_bytes(data);fst_changes[dst.name]=dict(WS=nws,primary=np_)
for stem,state in [('PRIMARY',primary),('STEREO_FIX',post)]:
 (ROOT/f'presets/ZL28_{stem}.vstpreset').unlink();dst=ROOT/f'presets/ZL29_{stem}.vstpreset';dst.write_bytes(vstpreset(state));assert read_vstpreset(dst.read_bytes())==state
for p in V.glob('ZL28*'):p.unlink()
(V/'ZL29_PRIMARY_COMPONENT.bin').write_bytes(primary);(V/'ZL29_POST_COMPONENT.bin').write_bytes(post)
for name in ['completion.json','FROZEN_BEFORE_FRESH_VALIDATION.json','PRIOR_COMBINED_CANDIDATE.json','PREDECLARED_PROTOCOL.json']:shutil.copyfile(J/name,V/('WS48_REFINEMENT02_'+name))
for name in ['CASCADE_BUILD_PROOF.json','ZIP_ACTUAL_REPLAY_PROOF.json','AB_LEVELS.json']:
 p=V/name
 if p.exists():p.rename(V/('historical_ZL28_'+name))
(V/'NATIVE_BASE_PRESET_VERIFICATION.json').write_text(json.dumps(new_native,indent=2)+'\n')
shutil.copyfile(BASE/'verification/NATIVE_LATENCY_AND_BLOCKS.json',V/'NATIVE_LATENCY_AND_BLOCKS.json')
shutil.copyfile(BASE/'verification/candidate.json',V/'native-base-candidate.json')
before=parse(proj_old.read_bytes());after=parse(project.read_bytes());bs=[v for i,v in before['events']if i==213];as_=[v for i,v in after['events']if i==213]
assert len(bs)==len(as_);native_changed=[k for k,(b,a)in enumerate(zip(bs[:-2],as_[:-2]))if b!=a];assert len(native_changed)==1
assert [v for i,v in before['events']if i in [224,235]]==[v for i,v in after['events']if i in [224,235]]
assert [(i,v)for i,v in before['events']if i not in [203,213]]==[(i,v)for i,v in after['events']if i not in [203,213]]
assert component_from_wrapper(as_[-2],8)==primary and component_from_wrapper(as_[-1],8)==post
for row in new_native['native_plugin_manifest']:
 assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==(ROOT/row['state']).read_bytes()
layout=dict(project=project.name,primary_component='verification/ZL29_PRIMARY_COMPONENT.bin',post_component='verification/ZL29_POST_COMPONENT.bin',primary_preset='presets/SUM_ZL29_PRIMARY.fst',post_preset='presets/SUM_ZL29_STEREO_FIX.fst',sum_insert='presets/04_SUM.fst',primary_vstpreset='presets/ZL29_PRIMARY.vstpreset',post_vstpreset='presets/ZL29_STEREO_FIX.vstpreset')
(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
choice.update(native_ZL_component_state=str(V/'ZL29_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL29_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL29_POST_COMPONENT.bin'),source_accepted_cohort='original-WS48-refinement02-with-primary258',full_public_kit_directory='ZL-WIP29',accepted_full_public_kit='ZL29',not_adopted_until_publication=True,native_parameters_changed_from_previous_public_kit=True,source_Diva_unchanged=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,requires_two_ZL_instances=True,topology='native12/base08 WS48refinement02 -> PRIMARY258 -> unchanged WIP28 POST 3SideAP + 1StereoAP + LeftPeak1013Hz',ZL_parameter_metadata_source='PRIMARY_610_PARAMETERS.tsv and POST_610_PARAMETERS.tsv',reference_match_reached=False)
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
for p in ROOT.iterdir():
 if p.is_file()and(p.suffix in ['.mp3','.flac']or(p.suffix=='.wav'and p.name!='Diva_original_lead_reference.wav'and not p.name.startswith('Diva_SOURCE_'))):p.unlink()
raw,sr=sf.read(J/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);audio,sr=sf.read(J/'CANDIDATE_00.wav',dtype='float32',always_2d=True);control,sr=sf.read(J/'CONTROL_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(ROOT/'ZL29_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment')
from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0))
ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);assert hashlib.sha256((ROOT/'Diva_original_lead_reference.wav').read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF)
old=edit(control);new=edit(audio);rms=lambda y:float(np.sqrt(np.mean(y*y)));gains=[1.,rms(ref)/rms(old),rms(ref)/rms(new)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old*gains[1],gap,new*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'ZL29_STEREO_REFERENCE_EDIT_WIP.wav',new,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_258_ZL29_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_258_ZL29_WIP.mp3')],check=True);tmp.unlink()
(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','previous_accepted_numeric258','WS48_refinement02_ZL29'],starts_seconds=[0,4.168,8.336],RMS_gains=gains,common_peak_safety_gain=safety,only_AB_level_normalized=True,independent_native_Chorus_realizations_for_control_and_candidate=True),indent=2)+'\n')
guide='# ZL29 WIP: следующий подтверждённый шаг к исходному оригиналу\n\nПолного совпадения ещё нет. Цель — загруженный Diva_original_lead_reference.wav; старыйv83/Finish не цель и неэффект. Nativebase08: ещё одна поправка48поддерживаемых координат кривой штатного WaveShaper. Остальные11native состояний, все281параметровDiva, ARP/ADSR, маршруты и входящие три длинные ноты41→37→36 дважды сохранены. PRIMARY — ранее подтверждённый numeric258; POST тот же28, включая LeftPeak1013.3Hz. Относительно258 меняется толькоWS; относительно полного28 — WS и PRIMARY.\n\n1. Распаковать ZIP в новую папку и открыть Diva_ZL29_STEREO_WIP.flp в FL Studio20/26. Pattern,180BPM. Нужны прежние Diva и штатные Fruity, плюс бесплатный ZL Equalizer2 v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi\n2. На SOURCE новая кривая WaveShaper; SUM: StereoShaper → ZL29 PRIMARY → ZL29 STEREO FIX. Mix обоих100%, MinimumPhase/Lookahead0/AutoGainOFF, всего ДВАZL. Второй ZL сохраняет3SideAllPass10000Hz/Q2,2200Hz/Q4,895.8Hz/Q13.84, StereoAllPass783.2Hz/Q19.422 и LeftPeak1013.3Hz/Q4.786/−1.04dB. Сохранить порядок.\n3. В прежнем GUIпроекте обязательно обновить SOURCE WaveShaper через presets/SOURCE_WaveShaper.fst и первый SUM ZL через presets/SUM_ZL29_PRIMARY.fst. Если уже стоит numeric258, PRIMARY прежний, а WS обязательно заменить. POST через presets/SUM_ZL29_STEREO_FIX.fst тот же28. Загрузка только новыхZL безWS не воспроизводит29. Альтернатива — Mixer track states presets/01_SOURCE.fst и presets/04_SUM.fst; проверить SOURCE→MID/SIDE, MID/SIDE→SUM, SUM→Master. Использовать отдельную копию проекта.\n4. Если Diva не восстановилась, загрузить Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI — Diva_THREE_HELD_180BPM.mid, шесть note-on на две фразы. Высокие скачки создаёт внутреннийARP.\n\nA/B: AB_ORIGINAL_258_ZL29_WIP.mp3 или losslessFLAC: оригинал0с → прежнийnumeric258 с4.168с → ZL29 с8.336с. Только A/B выровнен общей stereoRMS, рабочие WAV без нормировки. Контроль/кандидат — разные реализации свободного nativeChorus; поэтому решение принято по12новым парам, а не одному WAV.\n\n161настоящий nativeDLL/VST3вариант всех48поддерживаемых WSкоординат. Кандидат заморожен до12новыхпар. Заранее требовалось пройти ОБА порога: первые6 и первые10 улучшения>max(.0005,3SEM), обе холодныепары положительны и все12 со прежней стереозащитой. First6gain .006999041660,SEM.001135144400,порог.003405433199. First10gain .007092516686,SEM.000767313164,порог.002301939492. Cold2+.006436968520/+.006033872861. Другие11native statebytesexact. Latest PRIMARY/POST после gracefulостановки основного поиска побитово совпали с замороженными, устаревший контекст не применён.\n\nПо первым10 H24ошибка1.663271→1.640222дБ, ERB1.199396→1.191644дБ, whole.087155→.086999, envelope.149904→.149796. Relativephase слегка хуже1.184308→1.185765, upperoff3.913383→3.924890, stereoBalance4.097620→4.128236: смешанные изменения раскрыты. Общая исходная оценка лучше, но это не процентсходства и не полное совпадение.\n\nFLP/FST/VSTpreset, все12native состояния, Diva/MIDI/маршруты проверены. Два новых холодных каскада из независимой распаковки ZIP воспроизводят сохранённый WAV строго8float32eps/1e-12; компонентыпересохраняются побитово. NativeDLL/FST roundtrip и zeroDepthChorusконтроль≤2e-7; активныйChorus свободный, независимые рендеры не обещаются побитовоодинаковыми. ZL declaredPDC0 и добавочный импульсный сдвиг0, неASIO/wholeDAW. Nativeпервая реакция2samples; небольшие blocksizeразличия показаны в verification/NATIVE_LATENCY_AND_BLOCKS.json, абсолютная blockinvariance не заявляется.\n\nНовыйFLP ещё неоткрывалсявWindowsGUI. Реальные Linux/Winepluginrenders, без заявления о новомGUIэкспорте или субъективном прослушивании ассистентом. Оригинал только дляанализа/A-B, в синтез не подмешивается. MistaTowa не используется. Все старыеfullkits и последнийPCGUIпроект сохранены.\n'
for name in ['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
for stem,state in [('PRIMARY',V/'ZL29_PRIMARY_COMPONENT.bin'),('POST',V/'ZL29_POST_COMPONENT.bin')]:
 c=WinVST3('kit27-dump-'+stem)
 try:
  c.load(state);p=V/(stem+'_610_PARAMETERS.tsv');c.dump(p);b=p.read_bytes();t=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in t.splitlines())+'\n';assert list(csv.reader(io.StringIO(t),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(p.name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));p.write_text(normal)
 finally:c.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(native_changed_nodes=changed,all12_native_FST_state_bytes_exact=True,all281_Diva_parameters_and_chunk_unchanged=True,MIDI_and_routes_preserved=True,POST_unchanged=True,primary_SHA256=hashlib.sha256(primary).hexdigest(),post_SHA256=hashlib.sha256(post).hexdigest(),FST_changes=fst_changes,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL29_STEREO_WIP_complete.zip'
def pack():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack();restore=ROOT.parent/'independent-ZIP-restore';restore.mkdir();
with zipfile.ZipFile(archive)as z:assert z.testzip()is None;z.extractall(restore)
restored=restore/ROOT.name
for line in(restored/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((restored/name).read_bytes()).hexdigest()==digest
errors=[];delays=[]
for k in range(2):
 p=WinVST3('kit27-cold-primary-'+str(k));z=WinVST3('kit27-cold-post-'+str(k))
 try:
  for c,path in [(p,restored/layout['primary_component']),(z,restored/layout['post_component'])]:
   c.load(path);saved=ROOT.parent/('cold-resave-'+str(k)+'-'+path.name);c.save(saved);assert saved.read_bytes()==path.read_bytes()
  mid,_=p.render(raw);out,_=z.render(mid);np.testing.assert_allclose(out,audio,rtol=8*np.finfo(np.float32).eps,atol=1e-12);errors.append(float(abs(out-audio).max()));assert p.latency()==z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);assert not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0;delays.append(delay)
 finally:p.close();z.close()
seed=choice['native_base'];native_errors=[];all_resaved=[]
for mode in ['state-binary','ZIP-standalone-FST']:
 c=NativeChain(seed['source_manifest']['native_input'],'kit27-native-'+mode,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe')
 try:
  apply_candidate(c,np.array(seed['x']),seed)
  for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
  for row in new_native['native_plugin_manifest']:
   b=(restored/row['state']).read_bytes()
   if mode=='ZIP-standalone-FST':
    fst=next(v for i,v in parse((restored/row['preset']).read_bytes())['events']if i==213);assert fst==b
   path=ROOT.parent/('native-load-'+str(row['node'])+'.bin');path.write_bytes(b);c.load_state(row['node'],path);saved=ROOT.parent/('native-resave-'+str(row['node'])+'.bin');c.save_state(row['node'],saved);assert saved.read_bytes()==b
  c.set(3,1,0);out,status=c.render()
  if mode=='state-binary':native_control=out.copy()
  else:native_errors.append(float(abs(out-native_control).max()));assert native_errors[-1]<=2e-7
  all_resaved.append(True)
 finally:c.close()
proof=dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_ZL_cascades_max_abs_errors=errors,all_ZL_component_roundtrips_exact=True,combined_declared_ZL_PDC_frames=0,combined_ZL_impulse_added_delay_frames=delays,actual_native12_DLL_saved_state_roundtrips=all_resaved,ZIP_native_FST_zero_depth_max_abs_errors=native_errors,source_Diva_native11_MIDI_ARP_ADSR_POST_unchanged=True,changed_native_node0_WS_and_PRIMARY_only=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for p in ROOT.rglob('*'):
  if p.is_file():assert z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix())==p.read_bytes()
result=dict(root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),original_objective_export_mean=choice['loss'],ZIP_actual_two_cold_cascade_max_abs_errors=errors,ZIP_native_FST_zero_depth_max_abs_errors=native_errors,native_base='08',source_Diva_native11_MIDI_ARP_ADSR_POST_unchanged=True,changed_native_node0_WS_and_PRIMARY_only=True,requires_two_ZL_instances=True,post_Side_AllPasses=choice['post_Side_AllPasses'],post_Stereo_AllPasses=choice['post_Stereo_AllPasses'],original_is_the_only_target=True,v83_Finish_not_used=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(H/'ZL29_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
