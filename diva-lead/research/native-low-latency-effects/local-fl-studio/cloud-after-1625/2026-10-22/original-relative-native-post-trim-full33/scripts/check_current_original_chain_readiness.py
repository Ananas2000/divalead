"""Exercise current saved native12 -> two actual ZLs without changing BEST."""
from pathlib import Path
import datetime,hashlib,json,os
import numpy as np,soundfile as sf
from native_chain import NativeChain
from fl20_curve import apply_candidate,native_dsp_settings_SHA256
from win_vst3 import WinVST3
from native_post_trim import NativePostTrim
H=Path(__file__).resolve().parent;A=Path('/workspace/divalead-work/pc-stereo-20261024');P=Path('/workspace/divalead');bestpath=A/'stereo-continuous87/BEST_CANDIDATE.json';before=bestpath.read_bytes();best=json.loads(before);seed=best['native_base'];bundle=seed['native_saved_state_bundle'];assert bundle['settings_SHA256']==native_dsp_settings_SHA256(seed['x'],seed)
ref=P/'diva-lead/v83-wip/Diva_original_lead_reference.wav';assert hashlib.sha256(ref.read_bytes()).hexdigest()=='7617928f743f5ceed1c3d7cf557423e2a5ff0a5e0b2b7c87f00c118a63aff14f'
R=H/'readiness-checks'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');R.mkdir(parents=True);os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(R/'assessment')
from fl20_objective import FeaturesOriginal
tag='CurrentReady-'+str(os.getpid());native=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');zs=[]
try:
 apply_candidate(native,np.array(seed['x']),seed)
 for key,value in seed['chorus_overrides'].items():native.set(3,int(key),int(value))
 manifest=[]
 for row in bundle['manifest']:
  original=Path(bundle['directory'])/row['state'];assert hashlib.sha256(original.read_bytes()).hexdigest()==row['state_SHA256'];dst=R/('native-'+str(row['node'])+'.bin');native.save_state(row['node'],dst);assert dst.read_bytes()==original.read_bytes();manifest.append(dict(node=row['node'],state_resave_byte_exact=True))
 raw,_=native.render();sf.write(R/'ACTUAL_NATIVE_INPUT.wav',raw,48000,subtype='FLOAT');native.close();native=None;results=[]
 for k in range(2):
  p=WinVST3(tag+'-primary-'+str(k));z=WinVST3(tag+'-post-'+str(k));zs=[p,z];trim=None
  for c,path in [(p,Path(best['native_ZL_component_state'])),(z,Path(best['post_ZL_component_state']))]:
   c.load(path);dst=R/(str(k)+'-'+path.name);c.save(dst);assert dst.read_bytes()==path.read_bytes()
  mid,_=p.render(raw);out,_=z.render(mid);assert p.latency()+z.latency()==0
  if best.get('requires_post_native_trim'):
   state=Path(best['post_native_trim_state']);assert hashlib.sha256(state.read_bytes()).hexdigest()==best['post_native_trim_state_SHA256'];trim=NativePostTrim(R,tag+'-native-trim-'+str(k),cleanup_on_close=True);trim.load(state);dst=R/('trim-resaved-'+str(k)+'.bin');trim.save(dst);assert dst.read_bytes()==state.read_bytes();out=trim.render(out)
  if k==0:want=out.copy();sf.write(R/'ACTUAL_CURRENT_FULL_WIP.wav',out,48000,subtype='FLOAT')
  else:np.testing.assert_allclose(out,want,rtol=8*np.finfo(np.float32).eps,atol=1e-12)
  results.append(float(abs(out-want).max()));p.close();z.close();zs=[]
  if trim:trim.close()
 f=FeaturesOriginal();r=f.residual(want[:288000]);score=float(r@r)+float(np.sum(np.array(seed['x'])[:28]**2))*.00000025;assert np.isfinite(score)and 0<abs(want).max()<1.0
 assert bestpath.read_bytes()==before
 result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),current_full_kit=best['full_public_kit_directory'],current_source_cohort=best['source_accepted_cohort'],all12_actual_native_saved_state_resaves_byte_exact=manifest,two_fresh_actual_two_ZL_replays_errors=results,post_native_trim_included=bool(best.get('requires_post_native_trim')),combined_ZL_PDC_frames=0,original_WAV_objective=score,original_WAV_is_only_target=True,all_BEST_and_public_artifacts_unchanged=True,source_h2p_SHA256=seed['source_manifest']['source_preset_SHA256'],native_settings_SHA256=bundle['settings_SHA256'],root=str(R),actual_FL_GUI_validation_pending=True,reference_match_reached=False);(H/'CURRENT_CHAIN_READINESS.json').write_text(json.dumps(result,indent=2)+'\n');(R/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
finally:
 if native is not None:native.close()
 for z in zs:z.close()
