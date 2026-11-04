"""Migrate the exact NEW12-validated state into supported native12 metadata/export."""
from pathlib import Path
import copy,datetime,hashlib,json,os,shutil
import numpy as np,soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply as apply_raw
from fl20_curve import (apply_candidate,native_dsp_settings_SHA256,curve_metadata,
    os_local17_parent_geometry_SHA256,os_local17_curve_bytes,OS_LOCAL17_FORMAT)
from native_fst import parse,event,container
V=Path(__file__).resolve().parent;R=Path('/tmp/divalead-recovered-OS17-point-new12-20261104');N=V.parent/'native-low-latency-effects';oldroot=N/'validated-bases/FL20_NATIVE_ZL_REBASED_11';root=N/'validated-bases/FL20_NATIVE_ZL_REBASED_12'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=read(R/'PRIOR_COMBINED_CANDIDATE.json');parent=prior['native_base'];s=read(R/'completion.json');assert s['robust_improvement'] and s['frozen_comparator']==565;assert not root.exists()
assert native_dsp_settings_SHA256(parent['x'],parent)==parent['native_saved_state_bundle']['settings_SHA256']=='df61a952e95b48a0f23ac16a91fd270f2c28bb09918235428d9626ca74565b90'
shutil.copytree(oldroot,root,ignore=shutil.ignore_patterns('*.wav','*.mp3','*.flac','SHA256SUMS.txt'))
for name in ['Diva_original_lead_reference.wav','Diva_SOURCE_FROZEN_48k.wav']:shutil.copyfile(oldroot/name,root/name)
oldWS=(oldroot/'verification/SOURCE_WaveShaper.bin').read_bytes();newWS=(R/'CANDIDATE_WS.bin').read_bytes();assert oldWS!=newWS;changes={}
for source in [*root.rglob('*.flp'),*root.rglob('*.fst')]:
 data=parse(source.read_bytes());count=0;items=[]
 for ident,value in data['events']:
  if ident==213 and value==oldWS:value=newWS;count+=1
  items.append((ident,value))
 if count:source.write_bytes(container(data['format'],b''.join(event(i,v)for i,v in items),data['channels']));changes[source.relative_to(root).as_posix()]=count
(root/'verification/SOURCE_WaveShaper.bin').write_bytes(newWS);assert changes['presets/SOURCE_WaveShaper.fst']==1
manifest=[]
for row in parent['native_saved_state_bundle']['manifest']:
 p=root/row['state'];assert next(v for i,v in parse((root/row['preset']).read_bytes())['events']if i==213)==p.read_bytes()
 if row['node']!=0:assert p.read_bytes()==(oldroot/row['state']).read_bytes()
 manifest.append(dict(row,state_bytes=p.stat().st_size,state_SHA256=sha(p)))
base=root/'verification/WS_OSSTEP1_NATIVE11_PARENT.bin';shutil.copyfile(R/'GUI_OS_PARENT_NATIVE11.bin',base);recipe=read(R/'CANONICAL_POINT_AND_FLOAT32_RECIPE.json');assert sha(base)==recipe['parent_GUI_state_SHA256']
seed={k:v for k,v in parent.items()if k.startswith('waveshaper_')or k in['x','source_manifest','chorus_overrides','host_context','common_phase_pair','objective_version']}
seed.update(waveshaper_bipolar_base_state=str(root/'verification/WS_BIPOLAR_GUI_CONVERTED_BASE.bin'),waveshaper_os_local17_format=OS_LOCAL17_FORMAT,waveshaper_os_local17_adjustment=recipe['vector17'],waveshaper_os_local17_parent_state=str(base),waveshaper_os_local17_parent_SHA256=sha(base),waveshaper_os_local17_parent_geometry_SHA256=os_local17_parent_geometry_SHA256(parent['x'],parent),waveshaper_os_local17_factor_step=1,waveshaper_os_local17_quantization='native_float32_y_v1',model_family=OS_LOCAL17_FORMAT,only_three_held_notes=True,actual_FL_validation_pending=True,reference_match_reached=False)
assert os_local17_curve_bytes(seed['x'],seed)==newWS
bundle=dict(parent['native_saved_state_bundle'],directory=str(root),manifest=manifest,settings_SHA256=native_dsp_settings_SHA256(seed['x'],seed));seed['native_saved_state_bundle']=bundle
(root/'verification/candidate.json').write_text(json.dumps(seed,indent=2)+'\n');(V/'SUPPORTED_NATIVE12_CANDIDATE.json').write_text(json.dumps(seed,indent=2)+'\n')
# Mutation checks ensure saved bundles never hide a stale parent or ignored new controls.
for field in ['waveshaper_os_local17_adjustment','waveshaper_os_local17_factor_step','waveshaper_os_local17_quantization']:
 changed=copy.deepcopy(seed)
 if field.endswith('adjustment'):changed[field][0]+=.0001;assert native_dsp_settings_SHA256(changed['x'],changed)!=bundle['settings_SHA256']
 else:
  changed[field]=2 if field.endswith('step') else 'unknown'
  try:curve_metadata(changed)
  except AssertionError:pass
  else:raise AssertionError('Unsupported native semantics accepted')
stale=copy.deepcopy(seed);stale['waveshaper_bipolar_even_adjustment'][0]+=.0001
try:os_local17_curve_bytes(stale['x'],stale)
except AssertionError:pass
else:raise AssertionError('Stale OS parent geometry accepted')
legacy10=read(V.parent/'continuation-20261031/BEST_BEFORE_FULL39.json')['native_base'];assert native_dsp_settings_SHA256(legacy10['x'],legacy10)==legacy10['native_saved_state_bundle']['settings_SHA256']=='dfedaf40815781d04d06abb16b20a866524a5b77681baab6557e2b4bb2868dae'
clients=[];errors={};tag='Native12Migration-'+str(os.getpid())
def bare(name):
 c=NativeChain(parent['source_manifest']['native_input'],tag+'-'+name,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');clients.append(c);return c
def finish(c,metadata):
 for key,value in metadata['chorus_overrides'].items():c.set(3,int(key),int(value))
 c.set(3,1,0);return c.render()[0]
def close(c):c.close();clients.remove(c)
try:
 for label,metadata in [('legacy10',legacy10),('legacy11',parent)]:
  c=bare(label+'-manual');apply_raw(c,np.array(metadata['x']))
  for row in metadata['native_saved_state_bundle']['manifest']:c.load_state(row['node'],Path(metadata['native_saved_state_bundle']['directory'])/row['state'])
  expected=finish(c,metadata);close(c);c=bare(label+'-supported');apply_candidate(c,np.array(metadata['x']),metadata)
  for row in metadata['native_saved_state_bundle']['manifest']:
   p=V/(label+'-resave-'+str(row['node'])+'.bin');c.save_state(row['node'],p);assert p.read_bytes()==(Path(metadata['native_saved_state_bundle']['directory'])/row['state']).read_bytes()
  got=finish(c,metadata);np.testing.assert_array_equal(got,expected);errors[label+'_manual_vs_supported']=float(abs(got-expected).max());close(c)
 c=bare('manual12');apply_raw(c,np.array(seed['x']))
 for row in manifest:c.load_state(row['node'],root/row['state'])
 expected=finish(c,seed);close(c);sf.write(root/'verification/ZERO_DEPTH_EXPECTED_NATIVE12.wav',expected,48000,subtype='FLOAT')
 for k in range(2):
  c=bare('supported12-'+str(k));apply_candidate(c,np.array(seed['x']),seed)
  for row in manifest:
   p=V/('native12-cold-'+str(k)+'-resave-'+str(row['node'])+'.bin');c.save_state(row['node'],p);assert p.read_bytes()==(root/row['state']).read_bytes()
  got=finish(c,seed);np.testing.assert_array_equal(got,expected);errors['supported12_cold_'+str(k)]=float(abs(got-expected).max());close(c)
 c=bare('generator-without-bundle');apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None));p=V/'NATIVE12_GENERATOR_NO_BUNDLE_WS.bin';c.save_state(0,p);assert p.read_bytes()==newWS;close(c)
finally:
 for c in clients:c.close()
# Native-only helper is labelled as such; full chain includes the refitted two ZLs and final trim.
raw,sr=sf.read(R/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000;sf.write(root/'NATIVE_FULL_180BPM_WIP.wav',raw[:288000],sr,subtype='FLOAT');sf.write(root/'verification/NATIVE_WITH_TAIL_WIP.wav',raw,sr,subtype='FLOAT')
for name in ['NATIVE_PRESET_VERIFICATION.json','NATIVE_LATENCY_AND_BLOCKS.json','FLP_VERIFICATION.json','FST_INDEPENDENT_PARSE.json']:
 p=root/'verification'/name
 if p.exists():dest=root/'verification/history-base11';dest.mkdir(exist_ok=True);p.rename(dest/name)
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_base='12',native_plugin_manifest=manifest,native_saved_state_bundle=bundle,source_Diva_MIDI_ARP_ADSR_other11_native_unchanged=True,changed_FLP_FST_payloads=changes,new_curve_generator_without_saved_bundle_byte_exact=True,legacy10_and_11_fingerprints_unchanged=True,legacy_and_new_actual_zeroDepth_errors=errors,all12_native_resaves_exact=True,OS_step1_actual_GUI_parent_pinned=True,new_local17_fields_fingerprinted_and_validated=True,stale_parent_geometry_rejected=True,supported_export=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False)
(root/'verification/NATIVE_PRESET_VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');(V/'NATIVE12_SUPPORTED_RUNTIME_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n')
for name in ['README_RU.md','FL_STUDIO_RU.md']:(root/name).write_text('Native12 — вспомогательная база до двух ZL. SOURCE WaveShaper: native bipolar, oversampling step1, canonical float32 local even8+odd9. Только WS изменён; другие11native/Diva/MIDI/ARP/ADSR сохранены. Полный звук в WIP40, где также перенастроены оба ZL и финальный trim. Совпадение с оригиналом не достигнуто. FL GUI/ASIO не проверены.\n')
(root/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(root).as_posix()+'\n'for p in sorted(root.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'))
print(json.dumps(dict(root=str(root),settings_SHA256=bundle['settings_SHA256'],actual_zeroDepth_errors=errors,generator_byte_exact=True)),flush=True)
