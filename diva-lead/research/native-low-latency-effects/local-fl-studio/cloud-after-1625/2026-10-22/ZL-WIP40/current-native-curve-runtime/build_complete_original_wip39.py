"""Export supported native11 even8 + MID20/SIDE22 point, then cold ZIP replay."""
from pathlib import Path
import csv,datetime,gzip,hashlib,io,json,os,shutil,struct,subprocess,zipfile
import numpy as np,soundfile as sf
from native_fst import parse,event,container
from fl20_vst3_state import component_from_wrapper,vstpreset,read_vstpreset
from stereo_artifact_helpers import replace_primary
from native_post_trim import NativePostTrim
from win_vst3 import WinVST3
from fl20_curve import native_dsp_settings_SHA256
U=Path(__file__).resolve().parent;Q=U/'BIPOLAR_FINALIST1_AIR_MARGIN_REPAIR';N=U.parent/'native-low-latency-effects';BASE=N/'validated-bases/FL20_NATIVE_ZL_REBASED_11'
PUBLIC=Path('/workspace/divalead/diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22');SOURCE=PUBLIC/'ZL-WIP38';ROOT=Path('/tmp/divalead-full39-build/FL20_ZL39_STEREO_WIP');V=ROOT/'verification'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=read(Q/'completion.json');proof=read(U/'NATIVE11_SUPPORTED_RUNTIME_PROOF.json');prior=read(Q/'PRIOR_COMBINED_CANDIDATE.json');latest=read(U.parent/'pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json');assert latest['source_accepted_cohort']==prior['source_accepted_cohort']==556
assert s['robust_improvement'] and s['all12_original_stereo_lowmid_guards'] and proof['generator_without_bundle_WS_state_byte_exact'];assert all(x==0 for x in proof['manual_vs_supported_zeroDepth_errors'].values())
assert Path(latest['native_ZL_component_state']).read_bytes()==(Q/'PRIMARY.bin').read_bytes();assert Path(latest['post_ZL_component_state']).read_bytes()==(Q/'POST.bin').read_bytes()
assert not ROOT.exists();ROOT.parent.mkdir(exist_ok=True);shutil.copytree(SOURCE,ROOT,ignore=shutil.ignore_patterns('*.zip','*.wav','*.mp3','*.flac','SHA256SUMS.txt'))
for name in ['Diva_original_lead_reference.wav','Diva_SOURCE_FROZEN_48k.wav']:shutil.copyfile(SOURCE/name,ROOT/name)
old_primary=(SOURCE/'verification/ZL38_PRIMARY_COMPONENT.bin').read_bytes();primary=(Q/'CANDIDATE_PRIMARY.bin').read_bytes();old_post=(SOURCE/'verification/ZL38_POST_COMPONENT.bin').read_bytes();post=(Q/'CANDIDATE_POST.bin').read_bytes();trim=(SOURCE/'verification/POST_NATIVE_STEREO_TRIM.bin').read_bytes();old_ws=(SOURCE/'verification/SOURCE_WaveShaper.bin').read_bytes();ws=(Q/'CANDIDATE_WS_NATIVE_CANONICAL.bin').read_bytes()
assert post==old_post and primary!=old_primary and ws!=old_ws and sha(SOURCE/'verification/POST_NATIVE_STEREO_TRIM.bin')==prior['post_native_trim_state_SHA256']
changes={}
for source in [SOURCE/'Diva_ZL38_STEREO_WIP.flp',*(SOURCE/'presets').glob('*.fst')]:
 data=source.read_bytes();parsed=parse(data);pc=any(i==213 and old_primary in v for i,v in parsed['events'])
 if pc:data=replace_primary(data,old_primary,primary);parsed=parse(data)
 wc=0;events=[]
 for ident,value in parsed['events']:
  if ident==213 and value==old_ws:value=ws;wc+=1
  if ident==203:value=value.replace('ZL38'.encode('utf-16-le'),'ZL39'.encode('utf-16-le'))
  events.append((ident,value))
 rel=source.relative_to(SOURCE);dst=ROOT/str(rel).replace('ZL38','ZL39');old=ROOT/rel
 if old!=dst:old.unlink()
 dst.write_bytes(container(parsed['format'],b''.join(event(i,v)for i,v in events),parsed['channels']));changes[dst.relative_to(ROOT).as_posix()]=dict(primary_replaced=pc,source_WS_replaced=wc,POST_unchanged=True,trim_unchanged=True)
before=parse((SOURCE/'Diva_ZL38_STEREO_WIP.flp').read_bytes());after=parse((ROOT/'Diva_ZL39_STEREO_WIP.flp').read_bytes());bs=[v for i,v in before['events']if i==213];aa=[v for i,v in after['events']if i==213]
assert len(bs)==len(aa)and sum(a!=b for a,b in zip(bs,aa))==2;assert aa[-1]==trim and component_from_wrapper(aa[-3],8)==primary and component_from_wrapper(aa[-2],8)==post;assert [v for i,v in before['events']if i in[224,235]]==[v for i,v in after['events']if i in[224,235]]
for stem,state in [('PRIMARY',primary),('STEREO_FIX',post)]:
 (ROOT/f'presets/ZL38_{stem}.vstpreset').unlink();dst=ROOT/f'presets/ZL39_{stem}.vstpreset';dst.write_bytes(vstpreset(state));assert read_vstpreset(dst.read_bytes())==state
# Preserve earlier proofs explicitly as history, never as current positive metadata.
history=V/'history38';history.mkdir()
for p in list(V.iterdir()):
 if p.is_file() and (p.suffix in ['.json','.tsv'] or p.name.startswith(('ZL38','COLD_','PRIMARY_610','POST_610'))):p.rename(history/p.name)
for stem,state in [('PRIMARY',primary),('POST',post)]:(V/f'ZL39_{stem}_COMPONENT.bin').write_bytes(state)
(V/'SOURCE_WaveShaper.bin').write_bytes(ws);(V/'POST_NATIVE_STEREO_TRIM.bin').write_bytes(trim)
shutil.copyfile(BASE/'verification/WS_BIPOLAR_GUI_CONVERTED_BASE.bin',V/'WS_BIPOLAR_GUI_CONVERTED_BASE.bin')
shutil.copyfile(U/'NATIVE11_SUPPORTED_RUNTIME_PROOF.json',V/'NATIVE_BASE_PRESET_VERIFICATION.json')
for name in ['completion.json','PREDECLARED_PROTOCOL.json','FROZEN_BEFORE_NEW_VALIDATION.json','ACTUAL_NATIVE_STATE_PROOF.json']:shutil.copyfile(Q/name,V/('BIPOLAR39_'+name))
runtime=ROOT/'current-native-curve-runtime';runtime.mkdir();shutil.copyfile(U/'bipolar-runtime/fl20_curve.py',runtime/'fl20_curve.py');shutil.copyfile(U/'prepare_supported_bipolar_native11.py',runtime/'prepare_supported_bipolar_native11.py');shutil.copyfile(Path(__file__),runtime/Path(__file__).name)
manifest=proof['native_plugin_manifest']
for row in manifest:
 assert(ROOT/row['state']).read_bytes()==(BASE/row['state']).read_bytes();assert next(v for i,v in parse((ROOT/row['preset']).read_bytes())['events']if i==213)==(ROOT/row['state']).read_bytes()
layout={k:v.replace('ZL38','ZL39')for k,v in read(SOURCE/'artifact_layout.json').items()};(ROOT/'artifact_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
seed=read(U/'SUPPORTED_NATIVE11_CANDIDATE.json');seed['native_saved_state_bundle']['directory']=str(ROOT);seed['waveshaper_bipolar_base_state']=str(V/'WS_BIPOLAR_GUI_CONVERTED_BASE.bin');assert native_dsp_settings_SHA256(seed['x'],seed)==seed['native_saved_state_bundle']['settings_SHA256']
loss=float(np.mean([r['candidate']['loss']for r in s['captures'][:10]]));choice=dict(native_base=seed,native_base_ID='11',validated_native_base_ID='native11-bipolar-even8',native_base_export_directory=str(BASE),native_ZL_component_state=str(V/'ZL39_PRIMARY_COMPONENT.bin'),primary_ZL_component_state=str(V/'ZL39_PRIMARY_COMPONENT.bin'),post_ZL_component_state=str(V/'ZL39_POST_COMPONENT.bin'),post_native_trim_state=str(V/'POST_NATIVE_STEREO_TRIM.bin'),post_native_trim=prior['post_native_trim'],post_native_trim_state_SHA256=hashlib.sha256(trim).hexdigest(),requires_two_ZL_instances=True,not_compatible_with_single_ZL_pipeline=True,requires_post_native_trim=True,post_native_trim_added_delay_frames=0,declared_added_PDC_frames=0,native_effect_count=13,pre_ZL_native_effect_count=12,additional_dynamic_filter_indices=[20,21,22],primary_relative_dynamic_bands=[21,22],source_accepted_cohort='bipolar-even8-Mid20-Side22-margin39',full_public_kit_directory='ZL-WIP39',accepted_full_public_kit='ZL39',recorded_audio=str(ROOT/'ZL39_STEREO_FULL_WIP.wav'),loss=loss,loss_definition='new first10 paired real original-reference comparisons against accepted556; first6/first10/cold2 and nonincreasing Air vs556 and full38',not_adopted_until_publication=True,not_adopted_until_supported_export=False,source_Diva_unchanged=True,only_three_held_notes=True,original_is_the_only_target=True,v83_Finish_not_used_as_target_or_effect=True,source_and_other11_pre_ZL_native_states_unchanged=True,native_parameters_changed_from_previous_public_kit=True,source_WS_bipolar_even8_changed=True,POST_and_nativeTrim_unchanged_from38=True,topology='native12/base11 bipolar even8 WaveShaper -> PRIMARY556 with linked MID20/SIDE22 Gain+TargetGain -0.08dB -> POST38 -> native StereoShaper trim34',actual_FL_GUI_validation_pending=True,reference_match_reached=False,required_native_curve_runtime_family='native_bipolar_compact_even8_v1',upper_stereo_error_limit_dB=1.48,lowmid_error_limit_dB=3.25,positive_excess_air_preservation_required=True,paired_air_increase_limit_dB=.02,nonincreasing_Air_fresh10_and_bothcold_confirmed=True,nonincreasing_Air_proof_scope='this exact frozen39 point vs556/full38 only; future numeric cohorts require their own gates')
(V/'candidate.json').write_text(json.dumps(choice,indent=2)+'\n')
raw,sr=sf.read(Q/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);old,_=sf.read(Q/'CONTROL556_00.wav',dtype='float32',always_2d=True);audio,_=sf.read(Q/'CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000
sf.write(V/'NATIVE12_BEFORE_ZL_WIP.wav',raw,sr,subtype='FLOAT');sf.write(V/'CONTROL556_FULL_UNNORMALIZED.wav',old,sr,subtype='FLOAT');sf.write(ROOT/'ZL39_STEREO_FULL_WIP.wav',audio[:288000],sr,subtype='FLOAT');sf.write(V/'NATIVE_WITH_TAIL_WIP.wav',audio,sr,subtype='FLOAT')
# First real cold chain creates the before-trim working WAV and verifies the full validation output.
p=WinVST3('ZL39-beforeTrim-P');z=WinVST3('ZL39-beforeTrim-Z');c=NativePostTrim(ROOT.parent/'buffers','ZL39-beforeTrim-T',cleanup_on_close=True)
try:
 p.load(V/'ZL39_PRIMARY_COMPONENT.bin');z.load(V/'ZL39_POST_COMPONENT.bin');c.load(V/'POST_NATIVE_STEREO_TRIM.bin');mid,_=p.render(raw);pre,_=z.render(mid);got=c.render(pre);np.testing.assert_allclose(got,audio,rtol=8*np.finfo(np.float32).eps,atol=1e-12);sf.write(V/'BEFORE_NATIVE_TRIM_WIP.wav',pre,sr,subtype='FLOAT')
finally:p.close();z.close();c.close()
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT.parent/'assessment');from fl20_objective import a
edit=lambda y:a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));ref,sr=sf.read(ROOT/'Diva_original_lead_reference.wav',always_2d=True);assert sha(ROOT/'Diva_original_lead_reference.wav')=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f';np.testing.assert_array_equal(ref,a.REF)
rms=lambda y:float(np.sqrt(np.mean(y*y)));old_edit,new_edit=edit(old),edit(audio);gains=[1.,rms(ref)/rms(old_edit),rms(ref)/rms(new_edit)];gap=np.zeros((24000,2));ab=np.concatenate([ref,gap,old_edit*gains[1],gap,new_edit*gains[2]]);safety=min(1.,.95/float(abs(ab).max()));ab*=safety
sf.write(ROOT/'ZL39_STEREO_REFERENCE_EDIT_WIP.wav',new_edit,sr,subtype='FLOAT');sf.write(ROOT/'AB_ORIGINAL_556_ZL39_WIP.flac',ab,sr,subtype='PCM_24');tmp=ROOT.parent/'AB-working.wav';sf.write(tmp,ab,sr,subtype='FLOAT');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-codec:a','libmp3lame','-b:a','320k',str(ROOT/'AB_ORIGINAL_556_ZL39_WIP.mp3')],check=True);tmp.unlink()
(V/'AB_LEVELS.json').write_text(json.dumps(dict(order=['original','accepted556','new39'],starts_seconds=[0,4.168,8.336],global_stereo_RMS_gains=gains,common_peak_safety_gain=safety,only_AB_normalized=True,no_independent_channel_normalization=True,control_and_candidate_are_separate_actual_native_Chorus_realizations=True,source_Diva_same=True),indent=2)+'\n')
guide=f'''# WIP39: три длинные ноты, Diva и обычная обработка

Полного совпадения с оригиналом пока нет. WIP39 прошёл новое сравнение с принятой556: изменена двухсторонняя кривая Fruity WaveShaper на SOURCE и немного уменьшены связанные Gain/TargetGain MID20 и SIDE22 в PRIMARY. Остальные11 native-состояний, POST38, последний StereoShaper, Diva, MIDI, ARP и ADSR сохранены. Цель — исходный оригинал, не предыдущая версия.

1. Распакуйте полный ZIP в новую папку. Нужны Diva, штатные Fruity FL Studio20 и бесплатный ZL Equalizer2v1.4.1 Windows x64: https://github.com/ZL-Audio/ZLEqualizer/releases/download/1.4.1/ZL.Equalizer.2-1.4.1-Windows-x86-64.msi . После установки при необходимости Plugin Manager → Find installed plugins.
2. Откройте Diva_ZL39_STEREO_WIP.flp, 180BPM/48000Hz/Pattern. При запросе Diva загрузите Diva_NATIVE_WIP_THREE_HELD.h2p. MIDI Diva_THREE_HELD_180BPM.mid:41→37→36 дважды, шесть note-on/12событий. Верхние скачки создаёт внутренний ARP.
3. Для переноса в свою копию556/38: на SOURCE Fruity WaveShaper загрузите presets/SOURCE_WaveShaper.fst; на SUM замените первый ZL через presets/ZL39_PRIMARY.vstpreset. Без нового WaveShaper переноса нет. Полный presets/01_SOURCE.fst и presets/04_SUM.fst можно загрузить как Mixer track state; при переносе проверяйте SOURCE→MID/SIDE→SUM маршруты. Для остальных версий предпочтителен полный FLP. POST38 и финальный StereoShaper те же.
4. На SUM: прежний StereoShaper → ZL39 PRIMARY → ZL39 STEREO FIX → Fruity StereoShaper POST TRIM → Master. Всего13native и2ZL. Финальный raw[0,12782,12800,0,0,0], Left−.020dB/Right0dB, без задержки/crossfeed. Сохранённый MixChorus на SOURCE не меняйте. Оба ZL minimum phase/lookahead0/AutoGainOff; Finish/свёртки нет.

A/B: AB_ORIGINAL_556_ZL39_WIP.mp3/FLAC, оригинал0с →556с4.168с →39с8.336с. Только A/B выровнен общей stereoRMS; L/R отдельно не нормировались. Рабочие WAV без нормировки. Контроль и кандидат содержат отдельные реальные реализации Chorus, поэтому решение основано на12 новых парах, а не одном рендере.

First6gain{s['first6_mean_improvement']:.12f}/SEM{s['first6_SEM']:.12f}; first10gain{s['first10_mean_improvement']:.12f}/SEM{s['first10_SEM']:.12f}; оба>max(.0005,3SEM). Cold2{s['cold2_improvements']}. Все12 stereo/pairedlowmid гейтов пройдены. Airfirst10−.09261dB относительно556 и−.08304dB относительно38; оба cold также снизились. Это значения критерия, не процент сходства на слух. Гарантия нерастущего Air относится к этой точке39, не к будущим промежуточным.

Проверены настоящий DLL/VST3-рендер, байты FLP/FST/пресетов, независимая распаковка ZIP и два холодных каскада. Новый nativeгенератор без cachedbundle сохраняет точное WS-состояние; повторный zeroDepthрендер0/0, старый формат сохранён. Оба ZL PDC0; это не измерение ASIO/всей задержки DAW. Открытие нового FLP в WindowsGUI ещё не проверено. Прослушивание ассистентом не заявляется. Исходный референс не подмешан в синтез; MistaTowa не используется.
'''
for name in ['README_RU.md','FL_STUDIO_RU.md']:(ROOT/name).write_text(guide)
for stem,state in [('PRIMARY',V/'ZL39_PRIMARY_COMPONENT.bin'),('POST',V/'ZL39_POST_COMPONENT.bin')]:
 host=WinVST3('ZL39-dump-'+stem)
 try:
  host.load(state);dst=V/(stem+'_610_PARAMETERS.tsv');host.dump(dst);b=dst.read_bytes();t=b.decode();normal='\n'.join(line+'""'if line.endswith('\t')else line for line in t.splitlines())+'\n';assert list(csv.reader(io.StringIO(t),delimiter='\t'))==list(csv.reader(io.StringIO(normal),delimiter='\t'));(V/(dst.name+'.raw.gz')).write_bytes(gzip.compress(b,mtime=0));dst.write_text(normal)
 finally:host.close()
(V/'CASCADE_BUILD_PROOF.json').write_text(json.dumps(dict(source_Diva_MIDI_ARP_ADSR_routes_unchanged=True,only_source_WS_and_PRIMARY_changed_from_full38=True,all_other11_native_POST_and_trim_byte_exact=True,native_effect_count=13,pre_ZL_native_effect_count=12,number_of_ZL_instances=2,changed_artifact_payloads=changes,native_base='11',reference_match_reached=False),indent=2)+'\n')
archive=ROOT.parent/'Diva_ZL39_STEREO_WIP_complete.zip'
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
errors=[];zl_errors=[];delays=[]
for k in range(2):
 p=WinVST3('ZL39-ZIP-cold-primary-'+str(k));z=WinVST3('ZL39-ZIP-cold-post-'+str(k));c=NativePostTrim(ROOT.parent/'cold-native-inputs','ZL39-ZIP-cold-trim-'+str(k),cleanup_on_close=True)
 try:
  for host,path in [(p,restored/layout['primary_component']),(z,restored/layout['post_component'])]:
   host.load(path);dst=ROOT.parent/('cold-'+str(k)+'-'+path.name);host.save(dst);assert dst.read_bytes()==path.read_bytes()
  assert next(v for i,v in parse((restored/layout['post_native_trim_preset']).read_bytes())['events']if i==213)==trim;c.load(restored/layout['post_native_trim_state']);dst=ROOT.parent/f'cold-native-{k}.bin';c.save(dst);assert dst.read_bytes()==trim
  mid,_=p.render(raw);got,_=z.render(mid);np.testing.assert_allclose(got,pre,rtol=8*np.finfo(np.float32).eps,atol=1e-12);zl_errors.append(float(abs(got-pre).max()));out=c.render(got);err=float(abs(out-audio).max());assert err<=2e-7;errors.append(err);assert p.latency()+z.latency()==0
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];mid,_=p.render(impulse);out,_=z.render(mid);out=c.render(out);assert not np.any(out[:4096]);delay=int(np.flatnonzero(abs(out).max(axis=1)>1e-9)[0])-4096;assert delay==0;delays.append(delay)
 finally:p.close();z.close();c.close()
(V/'ZIP_ACTUAL_REPLAY_PROOF.json').write_text(json.dumps(dict(independent_ZIP_CRC_all_SHA_verified=True,two_fresh_actual_two_ZL_before_native_trim_errors=zl_errors,two_fresh_actual_full_chain_with_native_trim_errors=errors,strict_ZL_rtol_float32eps=8,strict_ZL_atol=1e-12,strict_native_trim_absolute_tolerance=2e-7,all_component_and_native_state_resaves_byte_exact=True,all12_native_FST_payloads_exact=True,combined_ZL_PDC_frames=0,ZL_plus_nativeTrim_impulse_added_delay_samples=delays,actual_FL_GUI_validation_pending=True,reference_match_reached=False),indent=2)+'\n');pack()
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for path in ROOT.rglob('*'):
  if path.is_file():assert z.read(ROOT.name+'/'+path.relative_to(ROOT).as_posix())==path.read_bytes()
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(ROOT),ZIP=str(archive),ZIP_bytes=archive.stat().st_size,ZIP_SHA256=sha(archive),first10_original_objective=loss,actual_two_cold_ZL_replay_errors=zl_errors,actual_two_cold_full_native_trim_chain_errors=errors,native_base='11',native_effects_before_ZL=12,native_effects_after_ZL=1,post_trim=prior['post_native_trim'],source_WS_bipolar_even8_and_primary_MID20_SIDE22_changed=True,source_Diva_MIDI_ARP_ADSR_other11native_POST_trim_unchanged=True,actual_FL_GUI_validation_pending=True,original_is_the_only_target=True,reference_match_reached=False)
(U/'ZL39_BUILD_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
