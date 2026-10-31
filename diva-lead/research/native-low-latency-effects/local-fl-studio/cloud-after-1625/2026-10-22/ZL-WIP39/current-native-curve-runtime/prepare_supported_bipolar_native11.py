"""Migrate validated native even8 point with explicit geometry/fingerprint support."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,struct
import numpy as np,soundfile as sf
from native_chain import NativeChain
from apply_native_candidate import apply as apply_raw
from fl20_curve import apply_candidate,curve_metadata,native_dsp_settings_SHA256,unipolar_parent_geometry_SHA256,bipolar_even_curve_bytes,BIPOLAR_FORMAT
from native_fst import parse,event,container
U=Path(__file__).resolve().parent;R=U/'BIPOLAR_FINALIST1_AIR_MARGIN_REPAIR';N=U.parent/'native-low-latency-effects';oldroot=N/'validated-bases/FL20_NATIVE_ZL_REBASED_10';root=N/'validated-bases/FL20_NATIVE_ZL_REBASED_11';best=json.loads((U.parent/'pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json').read_text());assert best['source_accepted_cohort']==556;parent=best['native_base'];summary=json.loads((R/'completion.json').read_text());assert summary['robust_improvement']and summary['winner']['delta']!=[0.,0.,0.];assert(R/'CANDIDATE_PRIMARY.bin').read_bytes()!=(R/'PRIMARY.bin').read_bytes();assert native_dsp_settings_SHA256(parent['x'],parent)==parent['native_saved_state_bundle']['settings_SHA256']=='dfedaf40815781d04d06abb16b20a866524a5b77681baab6557e2b4bb2868dae';assert not root.exists();shutil.copytree(oldroot,root,ignore=shutil.ignore_patterns('*.wav','*.mp3','*.flac','SHA256SUMS.txt'))
for name in ['Diva_original_lead_reference.wav','Diva_SOURCE_FROZEN_48k.wav']:shutil.copyfile(oldroot/name,root/name)
oldbundle=parent['native_saved_state_bundle'];oldWS=(oldroot/'verification/SOURCE_WaveShaper.bin').read_bytes();newWS=(R/'CANDIDATE_WS_NATIVE_CANONICAL.bin').read_bytes();assert oldWS!=newWS;changes={}
for source in[*root.rglob('*.flp'),*root.rglob('*.fst')]:
 data=parse(source.read_bytes());count=0;items=[]
 for ident,value in data['events']:
  if ident==213 and value==oldWS:value=newWS;count+=1
  items.append((ident,value))
 if count:source.write_bytes(container(data['format'],b''.join(event(i,v)for i,v in items),data['channels']));changes[source.relative_to(root).as_posix()]=count
(root/'verification/SOURCE_WaveShaper.bin').write_bytes(newWS);assert changes.get('presets/SOURCE_WaveShaper.fst')==1;manifest=[]
for row in oldbundle['manifest']:
 path=root/row['state'];assert next(v for i,v in parse((root/row['preset']).read_bytes())['events']if i==213)==path.read_bytes()
 if row['node']!=0:assert path.read_bytes()==(oldroot/row['state']).read_bytes()
 manifest.append(dict(row,state_bytes=path.stat().st_size,state_SHA256=hashlib.sha256(path.read_bytes()).hexdigest()))
base=root/'verification/WS_BIPOLAR_GUI_CONVERTED_BASE.bin';shutil.copyfile(R/'GUI_CONVERTED_BIPOLAR_BASE.bin',base);research=json.loads((R/'BIPOLAR_RESEARCH_METADATA_NOT_STANDARD.json').read_text());seed={k:v for k,v in parent.items()if k.startswith('waveshaper_')or k in['x','source_manifest','chorus_overrides','host_context','common_phase_pair','objective_version']};seed.update(waveshaper_bipolar_format=BIPOLAR_FORMAT,waveshaper_bipolar_even_adjustment=research['even_vector'],waveshaper_bipolar_base_state=str(base),waveshaper_bipolar_base_SHA256=hashlib.sha256(base.read_bytes()).hexdigest(),waveshaper_bipolar_parent_geometry_SHA256=unipolar_parent_geometry_SHA256(parent['x'],parent),model_family='native95_WS_bipolar_even8_canonical_saved_states',only_three_held_notes=True,actual_FL_validation_pending=True,original_reference_match_reached=False)
bundle=dict(oldbundle,directory=str(root),manifest=manifest,settings_SHA256=native_dsp_settings_SHA256(seed['x'],seed));seed['native_saved_state_bundle']=bundle;(root/'verification/candidate.json').write_text(json.dumps(seed,indent=2)+'\n');(U/'SUPPORTED_NATIVE11_CANDIDATE.json').write_text(json.dumps(seed,indent=2)+'\n');assert 'waveshaper_bipolar_even_adjustment'in curve_metadata(seed)
before=parse((oldroot/'Diva_NATIVE_17_WIP.flp').read_bytes());after=parse((root/'Diva_NATIVE_17_WIP.flp').read_bytes());assert[v for i,v in before['events']if i in[224,235]]==[v for i,v in after['events']if i in[224,235]];bs=[v for i,v in before['events']if i==213];aa=[v for i,v in after['events']if i==213];assert len(bs)==len(aa)and sum(a!=b for a,b in zip(bs,aa))==1
source=parent['source_manifest']['native_input'];clients=[];tag='Native11Migration-'+str(os.getpid())
def bare(name):
 c=NativeChain(source,tag+'-'+name,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');clients.append(c);return c
def manual(c,candidate):
 apply_raw(c,np.array(parent['x']))
 for row in oldbundle['manifest']:c.load_state(row['node'],root/row['state']if candidate else oldroot/row['state'])
 for k,v in parent['chorus_overrides'].items():c.set(3,int(k),int(v))
 c.set(3,1,0)
errors={};resaves=[]
try:
 c=bare('manual-legacy');manual(c,False);legacy,_=c.render();c.close();clients.remove(c);c=bare('supported-legacy');apply_candidate(c,np.array(parent['x']),parent)
 for k,v in parent['chorus_overrides'].items():c.set(3,int(k),int(v))
 for row in oldbundle['manifest']:
  p=U/('legacy-runtime-resave-'+str(row['node'])+'.bin');c.save_state(row['node'],p);assert p.read_bytes()==(oldroot/row['state']).read_bytes();resaves.append(row['node'])
 c.set(3,1,0);got,_=c.render();np.testing.assert_array_equal(got,legacy);errors['legacy_manual_vs_new_runtime']=float(abs(got-legacy).max());c.close();clients.remove(c)
 c=bare('manual-new');manual(c,True);expected,_=c.render();sf.write(root/'verification/ZERO_DEPTH_EXPECTED_NATIVE11.wav',expected,48000,subtype='FLOAT');c.close();clients.remove(c)
 for k in range(2):
  c=bare('supported-new-'+str(k));apply_candidate(c,np.array(seed['x']),seed)
  for key,value in seed['chorus_overrides'].items():c.set(3,int(key),int(value))
  for row in manifest:
   p=U/('new-runtime-'+str(k)+'-resave-'+str(row['node'])+'.bin');c.save_state(row['node'],p);assert p.read_bytes()==(root/row['state']).read_bytes()
  c.set(3,1,0);got,_=c.render();np.testing.assert_array_equal(got,expected);errors['new_supported_cold_'+str(k)]=float(abs(got-expected).max());c.close();clients.remove(c)
 # The saved-state bundle must not hide an incorrect new curve generator.
 c=bare('new-without-bundle');without=dict(seed,native_saved_state_bundle=None);apply_candidate(c,np.array(seed['x']),without);p=U/'NEW_BIPOLAR_GENERATOR_NATIVE_WS.bin';c.save_state(0,p);assert p.read_bytes()==newWS;c.close();clients.remove(c)
finally:
 for c in clients:c.close()
raw,sr=sf.read(R/'NATIVE_CANDIDATE_00.wav',dtype='float32',always_2d=True);assert sr==48000;sf.write(root/'NATIVE_FULL_180BPM_WIP.wav',raw[:288000],sr,subtype='FLOAT');sf.write(root/'verification/NATIVE_WITH_TAIL_WIP.wav',raw,sr,subtype='FLOAT');os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(U/'native11-assessment');from fl20_objective import a
sf.write(root/'NATIVE_REFERENCE_EDIT_WIP.wav',a.h.edit_aligned(a.h.align_with_pdc(raw,dict(alignment_frames=819),latency=0)),sr,subtype='FLOAT');history=root/'verification/history-base10';history.mkdir()
for name in['NATIVE_PRESET_VERIFICATION.json','NATIVE_LATENCY_AND_BLOCKS.json','FLP_VERIFICATION.json','FST_INDEPENDENT_PARSE.json']:
 p=root/'verification'/name
 if p.exists():p.rename(history/name)
proof=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),native_base='11',actual_native_DLL_audio=True,native_plugin_manifest=manifest,native_saved_state_bundle=bundle,source_manifest=seed['source_manifest'],chorus_overrides=seed['chorus_overrides'],only_three_held_notes=True,source_Diva_MIDI_ARP_ADSR_and_other11_native_states_unchanged=True,only_source_WS_state_replaced=True,changed_FLP_FST_payloads=changes,legacy_settings_fingerprint_unchanged=oldbundle['settings_SHA256'],all12_legacy_resaves_byte_exact=resaves,generator_without_bundle_WS_state_byte_exact=True,manual_vs_supported_zeroDepth_errors=errors,actual_FL_validation_pending=True,FL_GUI_tested=False,subjective_audition_claimed=False,match_reached=False,all_reference_comparisons_use_original_WAV=True)
(root/'verification/NATIVE_PRESET_VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n');(U/'NATIVE11_SUPPORTED_RUNTIME_PROOF.json').write_text(json.dumps(proof,indent=2)+'\n');(root/'README_RU.md').write_text('Nativebase11: штатный WaveShaper в двустороннем режиме с8чётными поправками. Только SOURCE WS изменён, другие11native/Diva/MIDI/ARP/ADSR прежние. Это вспомогательная nativeбаза до2ZL; полный пользовательский комплект публикуется отдельно. Metadata/generator/fingerprint/all-state resave и два coldzeroDepth0/0 проверены. GUIFL/ASIO не проверены, полного совпадения нет.\n');(root/'FL_STUDIO_RU.md').write_text((root/'README_RU.md').read_text());(root/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n'for p in sorted(root.rglob('*'))if p.is_file()and p.name!='SHA256SUMS.txt'));print(json.dumps(dict(native_base_root=str(root),legacy_fingerprint_unchanged=True,new_fingerprint=bundle['settings_SHA256'],legacy_and_new_actual_errors=errors,generator_without_bundle_byte_exact=True,source_held3_unchanged=True)),flush=True)
