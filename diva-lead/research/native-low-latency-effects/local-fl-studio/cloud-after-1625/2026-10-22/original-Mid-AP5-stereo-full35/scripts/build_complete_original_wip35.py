"""Full FL20 export of the independently validated94-primary/channel-trim point."""
from pathlib import Path
import csv,gzip,hashlib,io,json,os,shutil,struct,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from native_post_trim import NativePostTrim
from win_vst3 import WinVST3
H=Path(__file__).resolve().parent;Q=H/'MID_AP5_STEREO_ORIGINAL';PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');SOURCE=PUBLIC/'ZL-WIP34';ROOT=H/'full35-build/FL20_ZL35_STEREO_WIP';V=ROOT/'verification';s=json.loads((Q/'completion.json').read_text());assert s['robust_improvement']and json.loads((H/'FULL35_INPUT_AND_COLD_PROOF.json').read_text())['two_actual_cold_ZL_ZL_nativeTrim_replay_errors']==[0.,0.];assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT)
for p in ROOT.glob('*.zip'):p.unlink()
old_primary=(SOURCE/'verification/ZL34_PRIMARY_COMPONENT.bin').read_bytes();primary=(Q/'PRIMARY.bin').read_bytes();old_post=(SOURCE/'verification/ZL34_POST_COMPONENT.bin').read_bytes();post=Path(s['winner']['component']).read_bytes();old_trim=(SOURCE/'verification/POST_NATIVE_STEREO_TRIM.bin').read_bytes();trim=old_trim;assert primary==old_primary and trim==old_trim and post!=old_post
def transform(data):
 parsed=parse(data);changed_primary=primary!=old_primary and any(i==213 and old_primary in v for i,v in parsed['events'])
 if changed_primary:data=replace_primary(data,old_primary,primary);parsed=parse(data)
 post_changed=any(i==213 and old_post in v for i,v in parsed['events'])
 if post_changed:data=replace_primary(data,old_post,post);parsed=parse(data)
 events=[];trim_changes=0
 for ident,value in parsed['events']:
  if ident==213 and value==old_trim and trim!=old_trim:value=trim;trim_changes+=1
  if ident==203:value=value.replace('ZL34'.encode('utf-16-le'),'ZL35'.encode('utf-16-le'))
  events.append((ident,value))
 assert trim_changes<=1
 return container(parsed['format'],b''.join(event(i,v)for i,v in events),parsed['channels']),dict(primary_replaced=changed_primary,POST_replaced=post_changed,native_trim_replaced=trim_changes)
changes={}
for source in [SOURCE/'Diva_ZL34_STEREO_WIP.flp',*(SOURCE/'presets').glob('*.fst')]:
 rel=source.relative_to(SOURCE);target=ROOT/str(rel).replace('ZL34','ZL35');data,proof=transform(source.read_bytes());old=ROOT/rel
 if old!=target:old.unlink()
 target.write_bytes(data);changes[target.relative_to(ROOT).as_posix()]=proof
before=parse((SOURCE/'Diva_ZL34_STEREO_WIP.flp').read_bytes());after=parse((ROOT/'Diva_ZL35_STEREO_WIP.flp').read_bytes());bs=[v for i,v in before['events']if i==213];aa=[v for i,v in after['events']if i==213];assert len(bs)==len(aa)and bs[:-3]==aa[:-3]and aa[-1]==trim;assert component_from_wrapper(aa[-3],8)==primary and component_from_wrapper(aa[-2],8)==post;assert[v for i,v in before['events']if i in[224,235]]==[v for i,v in after['events']if i in[224,235]]
for stem,state in [('PRIMARY',primary),('STEREO_FIX',post)]:
 (ROOT/f'presets/ZL34_{stem}.vstpreset').unlink();dst=ROOT/f'presets/ZL35_{stem}.vstpreset';dst.write_bytes(vstpreset(state));assert read_vstpreset(dst.read_bytes())==state
history=V/'history34';history.mkdir()
for p in list(V.iterdir()):
 if p.is_file()and(p.name.startswith('ZL34')or p.name.startswith('AIR22_TRIM_')or p.name.startswith('COLD_')or p.name in['candidate.json','CASCADE_BUILD_PROOF.json','ZIP_ACTUAL_REPLAY_PROOF.json','AB_LEVELS.json','PAIRED_FIRST10_METRICS.json','POST_NATIVE_STEREO_TRIM.bin']):p.rename(history/p.name)
(V/'ZL35_PRIMARY_COMPONENT.bin').write_bytes(primary);(V/'ZL35_POST_COMPONENT.bin').write_bytes(post);(V/'POST_NATIVE_STEREO_TRIM.bin').write_bytes(trim)
for name in ['completion.json','PREDECLARED_PROTOCOL.json','FROZEN_BEFORE_FRESH_VALIDATION.json','TRAINING_RESULTS.json.gz']:
 shutil.copyfile(Q/name,V/('MID_AP5_'+name))
for p in(H/'full35-inputs').glob('COLD_*.bin'):shutil.copyfile(p,V/p.name)
native_manifest=json.loads((SOURCE/'verification/NATIVE_BASE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest']
for row in native_manifest:
 assert(ROOT/row['state']).read_bytes()==(SOURCE/row['state']).read_bytes();assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==(ROOT/row['state']).read_bytes()
layout={k:v.replace('ZL34','ZL35')for k,v in json.loads((SOURCE/'artifact_layout.json').read_text()).items()};(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
prior=json.loads((Q/'PRIOR_CONFIRMED.json').read_text());settings=dict(prior['post_native_trim']);loss=float(np.mean([r['candidate']['loss']for r in s['captures'][:10]]));choice=dict(prior,native_ZL_component_state=str(V/'ZL35_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL35_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL35_POST_COMPONENT.bin'),post_native_trim_state=str(V/'POST_NATIVE_STEREO_TRIM.bin'),post_native_trim=settings,post_native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),additional_dynamic_filter_indices=[20,21,22],primary_relative_dynamic_bands=[21,22],source_accepted_cohort='POST-MidAP5-650Hz-Q9p6',full_public_kit_directory='ZL-WIP35',accepted_full_public_kit='ZL35',recorded_audio=str(ROOT/'ZL35_STEREO_FULL_WIP.wav'),loss=loss,loss_definition='new first10 pairs against complete34, not pooled with prior kit',not_adopted_until_publication=True,not_adopted_until_supported_export=False,source_Diva_unchanged=True,native_parameters_changed_from_previous_public_kit=False,native_post_trim_changed_from34=False,source_and_pre_ZL_native12_unchanged=True,post_Mid_AllPasses=[dict(frequency=650.,Q=9.6,slot=5)],topology='native12/base10 WS52 -> unchanged PRIMARY34/dynamic22 -> POST plus Mid AllPass5 -> unchanged native StereoShaper trim34',actual_FL_GUI_validation_pending=True,reference_match_reached=False)
for key in ['ZL_peaking_MidSide_x','ZL_allpass_bands','ZL_dynamic_bands','ZL_output_gain_dB','numeric_acceptance_warm_pairs','numeric_acceptance_cold_pairs']:choice.pop(key,None)
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
for p in ROOT.iterdir():
 if p.is_file()and(p.suffix in['.mp3','.flac']or(p.suffix=='.wav'and p.name!='Diva_original_lead_reference.wav'and not p.name.startswith('Diva_SOURCE_'))):p.unlink()
raw,sr=sf.read(Q/'NATIVE_INPUT_00.wav',dtype='float32',always_2d=True);old,_=sf.read(Q/'CONTROL_00.wav',dtype='float32',always_2d=True);pre,_=sf.read(H/'full35-inputs/BEFORE_TRIM_00.wav',dtype='float32',always_2d=True);audio,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000;sf.write(ROOT/'ZL35_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT');sf.write(V/'BEFORE_NATIVE_TRIM_WIP.wav',pre,sr,subtype='FLOAT')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment');from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);assert hashlib.sha256((ROOT/'Diva_original_lead_reference.wav').read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF);rms=lambda y:float(np.sqrt(np.mean(y*y)));old_edit,new_edit=edit(old),edit(audio);gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old_edit*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety;sf.write(ROOT/'ZL35_STEREO_REFERENCE_EDIT_WIP.wav',new_edit,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_ZL34_ZL35_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_ZL34_ZL35_WIP.mp3')],check=True);tmp.unlink();(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','accepted34_same_native_input','new35_same_native_input'],starts_seconds=[0,4.168,8.336],global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_normalized=True,no_independent_channel_normalization=True),indent=2)+'\n')
metrics={key:{label:float(np.mean([r[label]['assessment']['metrics'][key]for r in s['captures'][:10]]))for label in ['control','candidate']}for key in s['captures'][0]['control']['assessment']['metrics']};(V/'PAIRED_FIRST10_METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
guide=f'''# ZL35 WIP: фазовая коррекция стерео

Полного совпадения с оригиналом ещё нет. Это проверенное промежуточное улучшение относительно полного34; источник Diva/три длинные ноты/ARP/ADSR/native12/PRIMARY94/позднийStereoShaper прежние. Изменён только второй ZL: добавлен Mid AllPass650Hz/Q9.6, slot5.

1. Распакуйте ZIP в отдельную папку и откройте Diva_ZL35_STEREO_WIP.flp в FL Studio20/26,180BPM. Нужны прежние Diva, штатные Fruity и бесплатный ZL Equalizer2v1.4.1: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi
2. Для переноса из34 достаточно заменить ВТОРОЙ ZL на SUM через presets/SUM_ZL35_STEREO_FIX.fst или presets/ZL35_STEREO_FIX.vstpreset. Первый ZL, SOURCE/MID/SIDE и поздний nativeTrim не меняйте. Полный presets/04_SUM.fst тоже приложен; после загрузки Mixer track state проверьте SUM→Master. Из более старых версий используйте полный проект.
3. В SUM порядок: прежний Stereo Shaper → ZL35 PRIMARY → ZL35 STEREO FIX → Fruity Stereo Shaper POST TRIM. Оба ZL обязательны. Mix100% относится к цепочке SUM; сохранённую смесь Chorus на SOURCE не меняйте. Поздний Stereo Shaper без задержек/crossfeed, raw[0,12782,12800,0,0,0], левый−.020dB/правый0dB. Всего13native и2ZL, без Finish/свёртки.
4. Если Diva не восстановилась, загрузите Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI Diva_THREE_HELD_180BPM.mid:41→37→36 дважды, шестьnote-on/12events. Верхние скачки создаёт внутренний ARP, дополнительных коротких нот нет.

A/B AB_ORIGINAL_ZL34_ZL35_WIP.mp3/FLAC: оригинал0с →34с4.168с →35с8.336с. Контроль и кандидат получили один настоящий nativeinput. Только A/B выровнен общей stereoRMS; рабочий WAV без нормировки, L/R отдельно не нормировались.

48 Mid-AllPass моделей по трём одинаковым входам, выбор до12НОВЫХпар. First6gain{s['first6_mean_improvement']:.12f},SEM{s['first6_SEM']:.12f}; first10gain{s['first10_mean_improvement']:.12f},SEM{s['first10_SEM']:.12f}; оба>max(.0005,3SEM). Cold2{s['cold2_improvements']}. Ошибка баланса300–800Hz уменьшилась примерно с3.03 до1.38dB на каждой новой паре, с обязательным улучшением≥.25dB. Верхние LRграницы прежние1.48RMS/1.6abs; lowmid≤3.25. First10airchange{s['first10_air_increase']:.12f}dB и обаcold≤+.02. Небольшой прирост этого показателя раскрыт; полного устранения шума или перекоса не заявляется.

First10исходныйobjective{loss:.12f}. Таблица всех метрик в verification/PAIRED_FIRST10_METRICS.json; это физические критерии, не процент сходства и не слуховое одобрение. Две независимые настоящие2ZL+nativeTrim загрузки воспроизводят WAV точно; ZIP отдельно распакован/CRC/SHA и DSP проверены. AllPass меняет фазу при сохранённом амплитудном отклике полосы; весь звук всё равно сравнивается с оригиналом. PDC ZL0, импульс без добавленной задержки начала; это не оценка ASIO/всегоDAW.

Новый FLP здесь не открывался в WindowsGUI. Проверены данные проекта, MIDI, маршруты, пресеты и настоящие DLL/VST3-рендеры под Linux/Wine. Субъективное прослушивание ассистентом не заявляется. Оригинал только для анализа/A-B, в синтез не подмешивается. MistaTowa не используется. Старые комплекты и PCGUI-проект сохранены. History34 содержит исторические проверки прежнего комплекта.
'''

for name in ['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
for stem,state in [('PRIMARY',V/'ZL35_PRIMARY_COMPONENT.bin'),('POST',V/'ZL35_POST_COMPONENT.bin')]:
 c=WinVST3('ZL35-dump-'+stem)
 try:
  c.load(state);dst=V/(stem+'_610_PARAMETERS.tsv');c.dump(dst);b=dst.read_bytes();t=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in t.splitlines())+'\n';assert list(csv.reader(io.StringIO(t),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(dst.name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));dst.write_text(normal)
 finally:c.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(source_Diva_native12_MIDI_ARP_ADSR_routes_byte_exact=True,only_POST_added_Mid_AllPass5_changed=True,native_effect_count=13,pre_ZL_native_effect_count=12,number_of_ZL_instances=2,PRIMARY34_and_nativeTrim34_byte_exact=True,changed_artifact_payloads=changes,reference_match_reached=False),indent=2)+'\n');archive=ROOT.parent/'Diva_ZL35_STEREO_WIP_complete.zip'
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
 p=WinVST3('ZL35-ZIP-cold-primary-'+str(k));z=WinVST3('ZL35-ZIP-cold-post-'+str(k));c=NativePostTrim(ROOT.parent/'cold-native-inputs','ZL35-ZIP-cold-trim-'+str(k),cleanup_on_close=True)
 try:
  for host,path in [(p,restored/layout['primary_component']),(z,restored/layout['post_component'])]:
   host.load(path);dst=ROOT.parent/('cold-'+str(k)+'-'+path.name);host.save(dst);assert dst.read_bytes()==path.read_bytes()
  fst_state=next(v for i,v in parse((restored/layout['post_native_trim_preset']).read_bytes())['events']if i==213);assert fst_state==(restored/layout['post_native_trim_state']).read_bytes();c.load(restored/layout['post_native_trim_state']);dst=ROOT.parent/f'cold-native-{k}.bin';c.save(dst);assert dst.read_bytes()==trim;mid,_=p.render(raw);got,_=z.render(mid);np.testing.assert_allclose(got,pre,rtol=8*np.finfo(np.float32).eps,atol=1e-12);ZL_errors.append(float(abs(got-pre).max()));out=c.render(got);error=float(abs(out-audio).max());assert error<=2e-7,error;errors.append(error);assert p.latency()+z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);out=c.render(out);assert not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0;delays.append(delay)
 finally:p.close();z.close();c.close()
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_two_ZL_before_native_trim_errors=ZL_errors,two_fresh_actual_full_chain_with_native_trim_errors=errors,strict_ZL_rtol_float32eps=8,strict_ZL_atol=1e-12,strict_native_trim_absolute_tolerance=2e-7,all_component_and_native_state_resaves_byte_exact=True,combined_ZL_PDC_frames=0,full_ZL_plus_nativeTrim_impulse_added_delay_samples=delays,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for path in ROOT.rglob('*'):
  if path.is_file():assert z.read(ROOT.name+'/'+path.relative_to(ROOT).as_posix())==path.read_bytes()
result=dict(root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),first10_original_objective=loss,actual_two_cold_ZL_replay_errors=ZL_errors,actual_two_cold_full_native_trim_chain_errors=errors,native_base='10',native_effects_before_ZL=12,native_effects_after_ZL=1,post_trim=settings,post_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),post_ZL_added_only_Mid_AllPass5=True,source_Diva_MIDI_ARP_ADSR_unchanged=True,actual_FL_GUI_validation_pending=True,original_is_the_only_target=True,reference_match_reached=False);(H/'ZL35_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
