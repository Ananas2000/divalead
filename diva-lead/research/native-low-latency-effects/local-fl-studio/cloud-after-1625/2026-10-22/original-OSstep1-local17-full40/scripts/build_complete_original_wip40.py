"""Package supported native12 and exact recovered two-ZL point; cold replay ZIP."""
from pathlib import Path
import copy,csv,datetime,gzip,hashlib,io,json,os,shutil,struct,subprocess,xml.etree.ElementTree as ET,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from native_post_trim import NativePostTrim
from win_vst3 import WinVST3
from fl20_curve import native_dsp_settings_SHA256
U=Path(__file__).resolve().parent;Q=Path('/tmp/divalead-recovered-OS17-point-new12-20261104');N=U.parent/'native-low-latency-effects';BASE=N/'validated-bases/FL20_NATIVE_ZL_REBASED_12'
PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');SOURCE=PUBLIC/'ZL-WIP39';ROOT=Path('/tmp/divalead-full40-build/FL20_ZL40_STEREO_WIP');V=ROOT/'verification'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=read(Q/'completion.json');proof=read(U/'NATIVE12_SUPPORTED_RUNTIME_PROOF.json');prior=read(Q/'PRIOR_COMBINED_CANDIDATE.json');latest=read(U.parent/'pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json');assert latest['source_accepted_cohort']==prior['source_accepted_cohort']==565
assert s['robust_improvement'] and s['all12_stereo_and_pairedlowmid'] and proof['new_curve_generator_without_saved_bundle_byte_exact'];assert all(v==0 for v in proof['legacy_and_new_actual_zeroDepth_errors'].values())
assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT,ignore=shutil.ignore_patterns('*.zip','*.wav','*.mp3','*.flac','SHA256SUMS.txt'))
for name in ['Diva_original_lead_reference.wav','Diva_SOURCE_FROZEN_48k.wav']:shutil.copyfile(SOURCE/name,ROOT/name)
old_primary=(SOURCE/'verification/ZL39_PRIMARY_COMPONENT.bin').read_bytes();primary=(Q/'CANDIDATE_PRIMARY.bin').read_bytes();old_post=(SOURCE/'verification/ZL39_POST_COMPONENT.bin').read_bytes();post=(Q/'CANDIDATE_POST.bin').read_bytes();old_trim=(SOURCE/'verification/POST_NATIVE_STEREO_TRIM.bin').read_bytes();trim=(Q/'CANDIDATE_NATIVE_TRIM.bin').read_bytes();old_ws=(SOURCE/'verification/SOURCE_WaveShaper.bin').read_bytes();ws=(Q/'CANDIDATE_WS.bin').read_bytes()
assert all(a!=b for a,b in [(primary,old_primary),(post,old_post),(trim,old_trim),(ws,old_ws)])
changes={}
for source in [SOURCE/'Diva_ZL39_STEREO_WIP.flp',*(SOURCE/'presets').glob('*.fst')]:
 data=source.read_bytes();parsed=parse(data);pc=any(i==213 and old_primary in v for i,v in parsed['events']);zc=any(i==213 and old_post in v for i,v in parsed['events'])
 if pc:data=replace_primary(data,old_primary,primary)
 if zc:data=replace_primary(data,old_post,post)
 parsed=parse(data);wc=tc=0;events=[]
 for ident,value in parsed['events']:
  if ident==213 and value==old_ws:value=ws;wc+=1
  if ident==213 and value==old_trim:value=trim;tc+=1
  if ident==203:value=value.replace('ZL39'.encode('utf-16-le'),'ZL40'.encode('utf-16-le'))
  events.append((ident,value))
 rel=source.relative_to(SOURCE);dst=ROOT/str(rel).replace('ZL39','ZL40');old=ROOT/rel
 if old!=dst:old.unlink()
 dst.write_bytes(container(parsed['format'],b''.join(event(i,v)for i,v in events),parsed['channels']));changes[dst.relative_to(ROOT).as_posix()]=dict(PRIMARY_replaced=pc,POST_replaced=zc,source_WS_replaced=wc,final_trim_replaced=tc)
before=parse((SOURCE/'Diva_ZL39_STEREO_WIP.flp').read_bytes());after=parse((ROOT/'Diva_ZL40_STEREO_WIP.flp').read_bytes());bs=[v for i,v in before['events']if i==213];aa=[v for i,v in after['events']if i==213]
assert len(bs)==len(aa)and sum(a!=b for a,b in zip(bs,aa))==4;assert aa[-1]==trim and component_from_wrapper(aa[-3],8)==primary and component_from_wrapper(aa[-2],8)==post;assert [v for i,v in before['events']if i in[224,235]]==[v for i,v in after['events']if i in[224,235]]
for stem,state in [('PRIMARY',primary),('STEREO_FIX',post)]:
 (ROOT/f'presets/ZL39_{stem}.vstpreset').unlink();dst=ROOT/f'presets/ZL40_{stem}.vstpreset';dst.write_bytes(vstpreset(state));assert read_vstpreset(dst.read_bytes())==state
# Keep prior verification explicitly historical, not as current positive claims.
history=V/'history39';history.mkdir()
for p in list(V.iterdir()):
 if p.is_file() and (p.suffix in ['.json','.tsv'] or p.name.startswith(('ZL39','COLD_','PRIMARY_610','POST_610'))):p.rename(history/p.name)
for stem,state in [('PRIMARY',primary),('POST',post)]:(V/f'ZL40_{stem}_COMPONENT.bin').write_bytes(state)
(V/'SOURCE_WaveShaper.bin').write_bytes(ws);(V/'POST_NATIVE_STEREO_TRIM.bin').write_bytes(trim)
for name in ['WS_BIPOLAR_GUI_CONVERTED_BASE.bin','WS_OSSTEP1_NATIVE11_PARENT.bin']:shutil.copyfile(BASE/'verification'/name,V/name)
shutil.copyfile(U/'NATIVE12_SUPPORTED_RUNTIME_PROOF.json',V/'NATIVE_BASE_PRESET_VERIFICATION.json')
for name in ['completion.json','PREDECLARED_PROTOCOL.json','FROZEN_BEFORE_NEW12.json','NATIVE_CANONICAL_COLD_REPLAY_PROOF.json','CANONICAL_POINT_AND_FLOAT32_RECIPE.json']:shutil.copyfile(Q/name,V/('RECOVERED40_'+name))
runtime=ROOT/'current-native-curve-runtime';shutil.copyfile(U/'fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(U/'prepare_supported_OS_local17_native12.py',runtime/'prepare_supported_OS_local17_native12.py');shutil.copyfile(Path(__file__),runtime/Path(__file__).name)
manifest=proof['native_plugin_manifest']
for row in manifest:
 assert(ROOT/row['state']).read_bytes()==(BASE/row['state']).read_bytes();assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==(ROOT/row['state']).read_bytes()
layout={k:v.replace('ZL39','ZL40')for k,v in read(SOURCE/'artifact_layout.json').items()};(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
seed=read(U/'SUPPORTED_NATIVE12_CANDIDATE.json');seed['native_saved_state_bundle']['directory']=str(ROOT);seed['waveshaper_bipolar_base_state']=str(V/'WS_BIPOLAR_GUI_CONVERTED_BASE.bin');seed['waveshaper_os_local17_parent_state']=str(V/'WS_OSSTEP1_NATIVE11_PARENT.bin');assert native_dsp_settings_SHA256(seed['x'],seed)==seed['native_saved_state_bundle']['settings_SHA256']
loss=float(np.mean([r['candidate']['loss']for r in s['captures'][:10]]));raw_trim=list(struct.unpack_from('<6i',trim,4));assert raw_trim[0]==raw_trim[3]==raw_trim[4]==raw_trim[5]==0
choice=dict(native_base=seed,native_base_ID='12',validated_native_base_ID='native12-bipolar-OSstep1-local17',native_base_export_directory=str(BASE),native_ZL_component_state=str(V/'ZL40_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL40_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL40_POST_COMPONENT.bin'),post_native_trim_state=str(V/'POST_NATIVE_STEREO_TRIM.bin'),post_native_trim=dict(requested_Left_dB=-.04,requested_Right_dB=0,raw_controls=raw_trim),post_native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),requires_two_ZL_instances=True,not_compatible_with_single_ZL_pipeline=True,requires_post_native_trim=True,post_native_trim_added_delay_frames=0,declared_added_PDC_frames=0,native_effect_count=13,pre_ZL_native_effect_count=12,additional_dynamic_filter_indices=[20,21,22],primary_relative_dynamic_bands=[21,22],source_accepted_cohort='recovered-OSstep1-local17-joint109-trim004-full40',full_public_kit_directory='ZL-WIP40',accepted_full_public_kit='ZL40',recorded_audio=str(ROOT/'ZL40_STEREO_FULL_WIP.wav'),loss=loss,loss_definition='entirely new12 paired original-reference comparisons vs accepted565 and full39; first6/first10/cold2 and nonincreasing Air gates',not_adopted_until_publication=True,not_adopted_until_supported_export=False,source_Diva_unchanged=True,only_three_held_notes=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,source_and_other11_pre_ZL_native_states_unchanged=True,native_parameters_changed_from_previous_public_kit=True,source_WS_OS_step1_local17_changed=True,PRIMARY_and_POST_refitted=True,final_trim_Left_requested_dB=-.04,topology='native12/base12 bipolar OSstep1 canonical local even8+odd9 WaveShaper -> refitted PRIMARY -> refitted POST -> native StereoShaper trim Left-.040/Right0; unchanged number of effects and filters',actual_FL_GUI_validation_pending=True,reference_match_reached=False,required_native_curve_runtime_family='native_bipolar_OSstep1_local_even8_odd9_float32_v1',upper_stereo_error_limit_dB=1.48,lowmid_error_limit_dB=3.25,positive_excess_air_preservation_required=True,paired_air_increase_limit_dB=.02,nonincreasing_Air_fresh10_and_bothcold_confirmed=True,nonincreasing_Air_proof_scope='exact frozen40 point vs565/full39 only; future numeric cohorts require their own gates',interrupted897_training_search_recovered_not_claimed_completed=True)
# Summaries derived from the actual state; no stale inherited POST descriptions.
for label,state in [('primary',primary),('post',post)]:
 values={p.attrib['id']:float(p.attrib['value'])for p in ET.fromstring(state[8:8+struct.unpack_from('<I',state,4)[0]]).find('Para')}
 choice[label+'_active_filters']=[dict(slot=k,type=values['filter_type'+str(k)],lr_mode=values['lr_mode'+str(k)],frequency=values['freq'+str(k)],Q=values['q'+str(k)],gain_dB=values['gain'+str(k)])for k in range(24)if values['filter_status'+str(k)]==2]
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
raw,sr=sf.read(Q/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);old,_=sf.read(Q/'CONTROL_00.wav',dtype='float32',always_2d=True);audio,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(V/'NATIVE12_BEFORE_ZL_WIP.wav',raw,sr,subtype='FLOAT');sf.write(V/'CONTROL565_FULL_UNNORMALIZED.wav',old,sr,subtype='FLOAT');sf.write(ROOT/'ZL40_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT')
p=WinVST3('ZL40-beforeTrim-P');z=WinVST3('ZL40-beforeTrim-Z');c=NativePostTrim(ROOT.parent/'buffers','ZL40-beforeTrim-T',cleanup_on_close=True)
try:
 p.load(V/'ZL40_PRIMARY_COMPONENT.bin');z.load(V/'ZL40_POST_COMPONENT.bin');c.load(V/'POST_NATIVE_STEREO_TRIM.bin');mid,_=p.render(raw);pre,_=z.render(mid);got=c.render(pre);warm_replay_error=float(abs(got-audio).max());assert warm_replay_error<=2e-7;cold_canonical=got.copy();sf.write(V/'BEFORE_NATIVE_TRIM_WIP.wav',pre,sr,subtype='FLOAT');sf.write(V/'CANONICAL_COLD_FULL_WIP.wav',cold_canonical,sr,subtype='FLOAT')
finally:p.close();z.close();c.close()
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment');from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);assert sha(ROOT/'Diva_original_lead_reference.wav')=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF)
rms=lambda y:float(np.sqrt(np.mean(y*y)));old_edit,new_edit=edit(old),edit(audio);gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old_edit*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'ZL40_STEREO_REFERENCE_EDIT_WIP.wav',new_edit,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_565_ZL40_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_565_ZL40_WIP.mp3')],check=True);tmp.unlink()
(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','accepted565','new40'],starts_seconds=[0,4.168,8.336],global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_normalized=True,no_independent_channel_normalization=True,control_and_candidate_are_separate_actual_native_Chorus_realizations=True,source_Diva_same=True),indent=2)+'\n')
guide=f'''# WIP40: Diva, три длинные ноты и обычная обработка

Полное совпадение с исходным референсом пока не достигнуто. WIP40 — проверенное улучшение относительно565, а не окончательный звук. В SOURCE WaveShaper включена реальная native oversampling step1 и уточнена двусторонняя кривая. Оба ZL перенастроены совместно, финальный StereoShaper Left−.040dB/Right0. Diva, MIDI, ARP/ADSR, другие11native-состояний и количество эффектов сохранены.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 Windows x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . При необходимости Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL40_STEREO_WIP.flp. 180BPM, 48000Hz, режим Pattern. Если Diva попросит пресет — Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI Diva_THREE_HELD_180BPM.mid:41→37→36 дважды. Это три входящие длинные ноты на фразу, шесть note-on/12событий на два повтора. Верхние скачки создаёт внутренний ARP; дополнительных коротких нот нет.
3. Для переноса в свою копию565/39 нужны ЧЕТЫРЕ состояния: SOURCE presets/SOURCE_WaveShaper.fst; SUM первый ZL presets/ZL40_PRIMARY.vstpreset; второй ZL presets/ZL40_STEREO_FIX.vstpreset; последний StereoShaper presets/SUM_ZL40_STEREO_TRIM.fst. Предпочтителен полный FLP. При переносе Mixer track state presets/01_SOURCE.fst и presets/04_SUM.fst проверяйте маршруты SOURCE→MID/SIDE→SUM→Master.
4. SUM: прежний StereoShaper → ZL40 PRIMARY → ZL40 STEREO FIX → Fruity StereoShaper POST TRIM → Master. Всего13native и2ZL. Final raw{raw_trim}; задержка/crossfeed не добавлены. Mix/Depth Chorus на SOURCE сохранены. Оба ZL: minimum phase/lookahead0/AutoGainOff. Старого Finish/свёртки нет. Референс не подмешан в синтез, MistaTowa не используется.

A/B AB_ORIGINAL_565_ZL40_WIP.mp3/FLAC: оригинал0с →565с4.168с →40с8.336с. Только A/B выровнен общей stereoRMS и общим peak safety; L/R отдельно не нормировались. Рабочие WAV без нормировки. Контроль и кандидат — отдельные реальные реализации Chorus; вывод основан на12 новых парах.

First6 gain{s['first6_gain']:.12f}/SEM{s['first6_SEM']:.12f}; first10 gain{s['first10_gain']:.12f}/SEM{s['first10_SEM']:.12f}; оба>max(.0005,3SEM). Cold2{s['cold2_gains']}. Все12 стерео/pairedlowmid гейтов пройдены. Критерий избыточного Air first10{s['first10_Air_delta']:.6f}dB относительно565, оба cold снизились. Относительно полного39 Air также снизился. Это критерии сравнения, не процент сходства на слух. Гарантия Air относится к этой точке40, не к будущим numericcohort.

Сохранённая точка взята из прерванного поиска897 записанных испытаний; полный поиск не объявлен завершённым. Точка зафиксирована до проверки двух неиспользованных входов и до всех12 новых пар. Схема/generator/fingerprint обновлены явно: canonical Y float32 до загрузки DLL. Без cachedbundle новый генератор создаёт точный nativeWS; all12state resave и два независимых zeroDepth повтора0/0. Старые native10/11 форматы проверены, не изменены.

Проверены реальные DLL/VST3 под Wine, FLP/FST/MIDI/Diva байты, независимая распаковка ZIP и два холодных каскада. ZL PDC0 и impulse onset0 в проверенном каскаде; это не измерение ASIO/всей задержки DAW. Открытие нового FLP в WindowsGUI ещё не проверено. Прослушивание ассистентом не заявляется.
'''
for name in ['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
shutil.copyfile(U/'BUILD40_COLD_REPLAY_DIAGNOSIS.json',V/'BUILD40_COLD_REPLAY_DIAGNOSIS.json')
for stem,state in [('PRIMARY',V/'ZL40_PRIMARY_COMPONENT.bin'),('POST',V/'ZL40_POST_COMPONENT.bin')]:
 host=WinVST3('ZL40-dump-'+stem)
 try:
  host.load(state);dst=V/(stem+'_610_PARAMETERS.tsv');host.dump(dst);b=dst.read_bytes();text=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in text.splitlines())+'\n';assert list(csv.reader(io.StringIO(text),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(dst.name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));dst.write_text(normal)
 finally:host.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(source_Diva_MIDI_ARP_ADSR_routes_unchanged=True,exactly4_DSP_payloads_changed_from_full39=True,other11_native_byte_exact=True,native_effect_count=13,pre_ZL_native_effect_count=12,number_of_ZL_instances=2,changed_artifact_payloads=changes,native_base='12',reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL40_STEREO_WIP_complete.zip'
def pack():
 (ROOT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n'for p in sorted(ROOT.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(ROOT.rglob('*')):
   if p.is_file():z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
pack();restore=ROOT.parent/'independent-ZIP-restore';restore.mkdir()
with zipfile.ZipFile(archive)as z:assert z.testzip()is None;z.extractall(restore)
restored=restore/ROOT.name
for line in(restored/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(restored/name)==digest
for row in manifest:assert next(v for i,v in parse((restored/row['preset']).read_bytes())['events']if i==213)==(restored/row['state']).read_bytes()
errors=[];zl_errors=[];cold_errors=[];delays=[]
for k in range(2):
 p=WinVST3('ZL40-ZIP-cold-primary-'+str(k));z=WinVST3('ZL40-ZIP-cold-post-'+str(k));c=NativePostTrim(ROOT.parent/'cold-native-inputs','ZL40-ZIP-cold-trim-'+str(k),cleanup_on_close=True)
 try:
  for host,path in [(p,restored/layout['primary_component']),(z,restored/layout['post_component'])]:
   host.load(path);dst=ROOT.parent/('cold-'+str(k)+'-'+path.name);host.save(dst);assert dst.read_bytes()==path.read_bytes()
  assert next(v for i,v in parse((restored/layout['post_native_trim_preset']).read_bytes())['events']if i==213)==trim;c.load(restored/layout['post_native_trim_state']);dst=ROOT.parent/f'cold-native-{k}.bin';c.save(dst);assert dst.read_bytes()==trim
  mid,_=p.render(raw);got,_=z.render(mid);np.testing.assert_allclose(got,pre,rtol=8*np.finfo(np.float32).eps,atol=1e-12);zl_errors.append(float(abs(got-pre).max()));out=c.render(got);np.testing.assert_allclose(out,cold_canonical,rtol=8*np.finfo(np.float32).eps,atol=1e-12);cold_errors.append(float(abs(out-cold_canonical).max()));err=float(abs(out-audio).max());assert err<=2e-7;errors.append(err);assert p.latency()+z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);out=c.render(out);assert not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0;delays.append(delay)
 finally:p.close();z.close();c.close()
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_two_ZL_before_native_trim_errors=zl_errors,two_fresh_actual_full_chain_with_native_trim_errors=errors,strict_ZL_rtol_float32eps=8,strict_ZL_atol=1e-12,strict_native_trim_absolute_tolerance=2e-7,all_component_and_native_state_resaves_byte_exact=True,all12_native_FST_payloads_exact=True,cold_full_vs_initial_canonical_errors=cold_errors,warm_validation_vs_cold_absolute_error=warm_replay_error,hot_vs_cold_diagnostic_not_cold_reproducibility_gate=True,combined_ZL_PDC_frames=0,ZL_plus_nativeTrim_impulse_added_delay_samples=delays,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for path in ROOT.rglob('*'):
  if path.is_file():assert z.read(ROOT.name+'/'+path.relative_to(ROOT).as_posix())==path.read_bytes()
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),first10_original_objective=loss,actual_two_cold_ZL_replay_errors=zl_errors,actual_two_cold_full_native_trim_chain_errors=errors,actual_two_cold_vs_canonical_full_errors=cold_errors,native_base='12',native_effects_before_ZL=12,native_effects_after_ZL=1,post_trim=choice['post_native_trim'],exactly4_DSP_payloads_changed_from_full39=True,source_Diva_MIDI_ARP_ADSR_other11native_unchanged=True,actual_FL_GUI_validation_pending=True,original_is_the_only_target=True,reference_match_reached=False)
(U/'ZL40_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
