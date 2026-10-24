"""Frozen stereo candidate: archival GUI robustness plus NEW actual native6/cold2.

Native fresh renders use the preserved actual Diva source. New GUI exports,
fresh Diva synth instances and whole-DAW latency are not claimed.
"""
from pathlib import Path
import datetime,hashlib,io,json,os,shutil,tarfile
import numpy as np,soundfile as sf
from win_vst3 import WinVST3
from native_chain import NativeChain
from fl20_curve import apply_candidate
A=Path(__file__).resolve().parent;ROOT=A/'frozen-stereo-validation01';ROOT.mkdir(exist_ok=False)
C=A/'local-fl-matching/sessions/2026-10-24';B=Path('/tmp/divalead-local-1625/FL20_NATIVE_ZL_REBASED_06')
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(ROOT/'assessment')
from fl20_objective import FeaturesOriginal,a
features=FeaturesOriginal()
for name,path in [('CONTROL_PRIMARY.bin',C/'ZL23_CONFIRMED_INPUT.bin'),('PRIMARY_COMPONENT.bin',A/'cloud476-GUI-recheck/PRIMARY_COMPONENT.bin'),('POST_COMPONENT.bin',A/'second-side-midrange-screen/POST_SIDE_PAIR_2200_4.bin')]:shutil.copyfile(path,ROOT/name)
frozen=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rationale='Cloud-confirmed cohort476 improves tone; TWO post Side-only AllPass filters 10000Hz/Q2 and2200Hz/Q4 reduce the reported band-dependent left dominance while preserving mono. Chosen from old GUI input00 before reading any archival8 outcomes.',components={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('*.bin')},source_native_all281_MIDI_unchanged=True,new_GUI_exports_not_claimed=True,not_adopted=True)
(ROOT/'FROZEN_BEFORE_VALIDATION.json').write_text(json.dumps(frozen,indent=2)+'\n')
ref,sr=sf.read('/workspace/divalead/diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);ff=np.fft.rfftfreq(len(ref),1/48000);masks=[(ff>=lo)&(ff<hi)for lo,hi in [(2000,5000),(5000,10000),(10000,14000)]]
def balance(edit):
 power=abs(np.fft.rfft(edit,axis=0))**2
 return np.array([10*np.log10(power[m,0].sum()/power[m,1].sum())for m in masks])
target=balance(ref)
def assess(y):
 r=features.residual(y);edit=a.h.edit_aligned(a.h.align_with_pdc(y,dict(alignment_frames=819),latency=0));lr=balance(edit)
 return dict(loss=float(r@r),assessment=features.local.last,high_LR_dB=lr.tolist(),stereo_high_band_error=float(np.sqrt(np.mean((lr-target)**2))))
def state(phase,**extra):
 (ROOT/'STATE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),PID=os.getpid(),phase=phase,only_three_held_notes=True,actual_FL_GUI_validation_pending=True,reference_match_reached=False,**extra),indent=2)+'\n')
def wav_bytes(y):
 s=io.BytesIO();sf.write(s,y,48000,format='WAV',subtype='FLOAT');return s.getvalue()
def archive_add(tar,name,y,members):
 b=wav_bytes(y);info=tarfile.TarInfo(name);info.size=len(b);tar.addfile(info,io.BytesIO(b));members.append(dict(name=name,bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()))
def pair(raw):
 control=WinVST3('PC-stereo-validation-control');primary=WinVST3('PC-stereo-validation-primary');post=WinVST3('PC-stereo-validation-post')
 try:
  for c,name in [(control,'CONTROL_PRIMARY.bin'),(primary,'PRIMARY_COMPONENT.bin'),(post,'POST_COMPONENT.bin')]:c.load(ROOT/name)
  old,_=control.render(raw);main,_=primary.render(raw);out,_=post.render(main)
  assert control.latency()==primary.latency()==post.latency()==0
  return old,out,assess(old),assess(out),float(abs(main.sum(axis=1)-out.sum(axis=1)).max())
 finally:control.close();primary.close();post.close()
def validate_set(label,inputs,new_native):
 rows=[];members=[];archive=ROOT/(label+'_ALL_RAW_CONTROL_CANDIDATE_WAVs.tar.gz')
 with tarfile.open(archive,'w:gz',compresslevel=3)as tar:
  for i,raw in enumerate(inputs):
   state('actual_frozen_'+label+'_validation',rep=i)
   old,out,c0,c1,mono_error=pair(raw);rows.append(dict(rep=i,control=c0,candidate=c1,improvement=c0['loss']-c1['loss'],post_mono_max_abs_error=mono_error))
   if new_native:archive_add(tar,f'native-input-{i}.wav',raw,members)
   archive_add(tar,f'control-{i}.wav',old,members);archive_add(tar,f'candidate-{i}.wav',out,members)
   if i==0:
    for name,y in [('CONTROL',old),('CANDIDATE',out),('NATIVE_INPUT',raw)]:sf.write(ROOT/f'{label}_{name}_00.wav',y,48000,subtype='FLOAT')
   (ROOT/(label+'_RUNNING_PAIRS.json')).write_text(json.dumps(rows,indent=2)+'\n')
 with tarfile.open(archive)as tar:
  for m in members:assert hashlib.sha256(tar.extractfile(m['name']).read()).hexdigest()==m['SHA256']
 delta=np.array([r['improvement']for r in rows[:6]]);sem=float(np.std(delta,ddof=1)/np.sqrt(6));cold=[r['improvement']for r in rows[6:8]]
 result=dict(pairs=rows,first6_mean_improvement=float(np.mean(delta)),first6_SEM=sem,required_improvement=max(.0005,3*sem),last2_cold_input_improvements=cold,original_criterion_passed=bool(np.mean(delta)>max(.0005,3*sem)and min(cold)>0),all_stereo_band_errors_improve=all(r['candidate']['stereo_high_band_error']<r['control']['stereo_high_band_error']for r in rows),archive_members=members,archive_SHA256=hashlib.sha256(archive.read_bytes()).hexdigest(),archival_GUI_inputs_previously_used_for_other_candidate=not new_native,new_GUI_exports_not_claimed=True,new_native_on_preserved_Diva_source=new_native)
 (ROOT/(label+'_SUMMARY.json')).write_text(json.dumps(result,indent=2)+'\n');return result
def archival_inputs():
 for i in range(8):
  y,sr=sf.read(A/f'archival-GUI-validation/FRESH_{i:02}.wav',dtype='float32',always_2d=True);assert sr==48000;yield y
gui=validate_set('ARCHIVAL_GUI',archival_inputs(),False)
seed=json.loads((A/'cloud476-GUI-recheck/CLOUD476_PRIOR_VALIDATION.json').read_text())['native_base'];manifest=json.loads((B/'verification/NATIVE_PRESET_VERIFICATION.json').read_text())['native_plugin_manifest'];assert len(manifest)==12
def native(tag):
 c=NativeChain(seed['source_manifest']['native_input'],tag,fl_graph=True,phase_pair=True,engine_override='fl_native_fl20_host.exe');apply_candidate(c,np.array(seed['x']),dict(seed,native_saved_state_bundle=None))
 for row in manifest:
  path=B/row['state'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['state_SHA256'];c.load_state(row['node'],path)
 return c
def new_native_inputs():
 c=native('PC-stereo-validation-native')
 try:
  for i in range(6):yield c.render()[0]
 finally:c.close()
 for i in range(2):
  c=native('PC-stereo-validation-cold-native')
  try:yield c.render()[0]
  finally:c.close()
fresh=validate_set('NEW_NATIVE',new_native_inputs(),True)
state('actual_saved_component_and_cold_replay_checks')
raw=sf.read(ROOT/'ARCHIVAL_GUI_NATIVE_INPUT_00.wav',dtype='float32',always_2d=True)[0];expected=None;replay=[]
for i in range(2):
 p=WinVST3('PC-stereo-validation-cold-primary');z=WinVST3('PC-stereo-validation-cold-post')
 try:
  p.load(ROOT/'PRIMARY_COMPONENT.bin');z.load(ROOT/'POST_COMPONENT.bin');main,_=p.render(raw);out,_=z.render(main)
  for c,name in [(p,'PRIMARY_COMPONENT.bin'),(z,'POST_COMPONENT.bin')]:
   dst=ROOT/(str(i)+'_RESAVED_'+name);c.save(dst);assert dst.read_bytes()==(ROOT/name).read_bytes()
  if expected is None:expected=out
  else:np.testing.assert_allclose(out,expected,rtol=8*np.finfo(np.float32).eps,atol=1e-12);replay.append(float(abs(out-expected).max()))
  impulse=np.zeros((32768,2),np.float32);impulse[4096]=[.1,.073];primary_out,_=p.render(impulse);response,_=z.render(primary_out);first=int(np.flatnonzero(abs(response).max(axis=1)>1e-9)[0])-4096;assert first==0 and not np.any(response[:4096]);assert p.latency()==z.latency()==0
 finally:p.close();z.close()
result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),archival_GUI_original_criterion_passed=gui['original_criterion_passed'],new_native6_and_cold2_original_criterion_passed=fresh['original_criterion_passed'],all_archival_GUI_stereo_errors_improve=gui['all_stereo_band_errors_improve'],all_new_native_stereo_errors_improve=fresh['all_stereo_band_errors_improve'],actual_component_roundtrip_byte_exact=True,two_fresh_cold_complete_ZL_chain_replay_max_abs_error=max(replay),declared_combined_ZL_PDC_frames=0,impulse_added_delay_frames=first,post_only_Side_processing_mono_max_abs_error=max(r['post_mono_max_abs_error']for r in gui['pairs']+fresh['pairs']),source_native_281_MIDI_unchanged=True,native_base='06',only_three_held_notes=True,actual_FL_GUI_validation_pending=True,no_new_GUI_exports_or_new_Diva_instances_claimed=True,reference_match_reached=False,not_adopted=True)
(ROOT/'completion.json').write_text(json.dumps(result,indent=2)+'\n');state('frozen_stereo_validation_complete_not_adopted',summary=result);print(json.dumps(result),flush=True)
