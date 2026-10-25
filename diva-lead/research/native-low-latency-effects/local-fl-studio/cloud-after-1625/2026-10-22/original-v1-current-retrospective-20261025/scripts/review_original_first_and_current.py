"""Re-score historical stages and current actual WAV against one original.

Analysis only. Fixed existing alignment/edit, common stereo RMS level,
unchanged ranking scales/weights. No subjective-audition or similarity-% claim.
"""
from pathlib import Path
import hashlib,json,os,subprocess
import numpy as np,soundfile as sf
H=Path(__file__).resolve().parent;OUT=H/'original-first-current-review';OUT.mkdir(exist_ok=False);(OUT/'scores').mkdir();(OUT/'audio').mkdir()
os.environ['DIVALEAD_NATIVE_OBJECTIVE_ROOT']=str(OUT/'objective')
from fl20_objective import a,SCALES,TONE
a.WORK=OUT
P=Path('/workspace/divalead');PUBLIC=P/'diva-lead/research/native-low-latency-effects/local-fl-studio/cloud-after-1625/2026-10-22'
reference,rate=sf.read(P/'diva-lead/v83-wip/Diva_original_lead_reference.wav',always_2d=True);assert rate==48000;np.testing.assert_array_equal(reference,a.REF)
N=len(reference);ref_rms=float(np.sqrt(np.mean(reference**2)));inventory=json.loads(Path('/workspace/divalead-work/all-repository-selection/candidate_inventory.json').read_text())
def from_alias(rel):
 c=next(c for c in inventory['candidates']if any(alias['path']==rel for alias in c['aliases']));p=Path(c['canonical_path'])
 if p.is_file():return sf.read(p,always_2d=True)[0],dict(source=rel,canonical_source=str(p),canonicalization=[r for r in c['aliases']if r['path']==rel])
 p=P/rel
 if not p.exists():
  dest=OUT/'audio'/('source-'+p.name);dest.write_bytes(subprocess.check_output(['git','-C',str(P),'show','HEAD:'+rel]));p=dest
 x,sr=sf.read(p,always_2d=True);assert sr==48000
 # Only missing canonical selected here is a saved already-aligned edit.
 assert len(x)==N
 return x,dict(source=rel,canonical_source=str(p),already_reference_edit=True)
def edit_saved(rel):
 p=P/rel
 if not p.exists():
  dest=OUT/'audio'/('source-'+p.parent.name+'-'+p.name);dest.write_bytes(subprocess.check_output(['git','-C',str(P),'show','HEAD:'+rel]));p=dest
 x,sr=sf.read(p,always_2d=True);assert sr==48000 and len(x)==N;return x,dict(source=rel,already_reference_edit=True)
cases=[]
v1=P/'diva-lead/research/repository-selection/V1_FRESH_CONTROLLED_REFERENCE_EDIT.wav';v1data,sr=sf.read(v1,always_2d=True);assert sr==48000 and len(v1data)==N
cases.append(('v1_controlled',v1data,dict(source=str(v1.relative_to(P)),meaning='earliest preset, previously rendered through actual Diva on common controlled performance; not a historical v1 delivery WAV')))
for label,rel in [('v2_stereo','diva-lead/v2/Diva_v2_STEREO.wav'),('v8','diva-lead/v8/Diva_v8_FINAL_ALIGNED.wav'),('v20','diva-lead/v20-wip/Diva_v20_VIDEO_REFERENCE_EDIT.wav'),('v24','diva-lead/v24-wip/Diva_v24_VIDEO_REFERENCE_EDIT.wav'),('v53','diva-lead/v53-wip/Diva_v53_VIDEO_REFERENCE_EDIT.wav')]:
 x,meta=from_alias(rel);cases.append((label,x,meta))
for label,rel in [('v57','diva-lead/v57-wip/Diva_Lead_v57_REFERENCE_EDIT.wav'),('v58_three_held','diva-lead/v58-wip/THREE_HELD_RESEARCH/Diva_THREE_HELD_REFERENCE_EDIT.wav'),('v83_old_finish','diva-lead/v83-wip/Diva_Lead_v83_REFERENCE_EDIT.wav'),('ZL01',str((PUBLIC/'ZL-WIP01/NATIVE_REFERENCE_EDIT_WIP.wav').relative_to(P))),('ZL25',str((PUBLIC/'ZL-WIP25/ZL25_STEREO_REFERENCE_EDIT_WIP.wav').relative_to(P)))]:
 x,meta=edit_saved(rel);cases.append((label,x,meta))
best=json.loads(Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87/BEST_CANDIDATE.json').read_text());x,sr=sf.read(best['recorded_audio'],always_2d=True);assert sr==48000
x=a.h.edit_aligned(a.h.align_with_pdc(x,dict(alignment_frames=819),latency=0));cases.append(('current_cohort_'+str(best['source_accepted_cohort']),x,dict(source=best['recorded_audio'],public_backed_path=str((PUBLIC/f"stereo-cascade87-cohort-{best['source_accepted_cohort']:04d}/FL20_STEREO_WIP/STEREO_CONTINUED_FULL_WIP.wav").relative_to(P)),fixed_alignment_frames=819,current_best_loss_from_original_8_validation=best['loss'])))
freq=np.fft.rfftfreq(N,1/48000);bands=[(40,300),(300,800),(800,2000),(2000,5000),(5000,10000),(10000,14000)];masks=[(freq>=lo)&(freq<hi)for lo,hi in bands]
def balance(y):
 p=abs(np.fft.rfft(y,axis=0))**2;return [float(10*np.log10(p[m,0].sum()/p[m,1].sum()))for m in masks]
results=[];normalized={'reference':reference}
for label,x,meta in cases:
 assert len(x)==N and np.isfinite(x).all();gain=ref_rms/float(np.sqrt(np.mean(x**2)));y=x*gain;normalized[label]=y
 path=OUT/'audio'/(label+'_RMS_MATCHED.wav');sf.write(path,y,48000,subtype='FLOAT')
 row=a.score(dict(id=label,canonical_path=str(path),aliases=[]));metrics=row['metrics'];standard=sum(a.WEIGHTS[k]*metrics[k]/SCALES[k]for k in a.WEIGHTS);tone=sum(TONE[k]*metrics[k]/SCALES[k]for k in TONE);index=.65*tone+.35*standard
 power,car,bound=a.powers(y);err=10*np.log10(np.maximum(power,1e-15)/np.maximum(a.TP,1e-15))
 row.update(label=label,provenance=meta,comparison_index=index,tone_index=tone,standard_index=standard,global_RMS_gain=gain,source_peak=float(abs(x).max()),active_LR_correlation=row['diagnostics']['common_metrics']['active_lr_correlation'],whole_edit_LR_dB=float(10*np.log10(np.sum(y[:,0]**2)/np.sum(y[:,1]**2))),FFT_band_LR_dB=balance(y),upper_off_harmonic_signed_mean_dB=float(np.mean(err[:,4:,2:])),canonical_sample_SHA256=hashlib.sha256(x.astype('<f8').tobytes()).hexdigest(),current_match_claimed=False)
 results.append(row);print(label,json.dumps(dict(index=index,metrics=metrics,band_LR=row['FFT_band_LR_dB'])),flush=True)
# Original self-comparison is a numerical control and not a candidate.
sf.write(OUT/'audio/reference.wav',reference,48000,subtype='DOUBLE');selfcheck=a.score(dict(id='reference_selfcheck',canonical_path=str(OUT/'audio/reference.wav'),aliases=[]));assert max(abs(float(v))for v in selfcheck['metrics'].values())<1e-6
latest=json.loads(Path('/workspace/divalead-work/pc-stereo-20261024/stereo-continuous87/cohort-0155/completion.json').read_text());keys=results[-1]['metrics'].keys();eight={k:dict(mean=float(np.mean([r['assessment']['metrics'][k]for r in latest['captures']])),minimum=float(min(r['assessment']['metrics'][k]for r in latest['captures'])),maximum=float(max(r['assessment']['metrics'][k]for r in latest['captures'])))for k in keys}
report=dict(reference_file='diva-lead/v83-wip/Diva_original_lead_reference.wav',reference_decoded_SHA256=hashlib.sha256(reference.astype('<f8').tobytes()).hexdigest(),comparison='same original/176064-frame edit; common stereo RMS gain, no independent channel normalization; existing fixed historical alignment, original metrics/ranking scales',comparison_index='.65 existing tone index +.35 existing standard index; loudness/peak/regularization training penalties omitted for this level-matched retrospective, lower better; not a calibrated perceptual similarity percentage',weights=dict(tone=TONE,standard=a.WEIGHTS),scales=SCALES,reference_FFT_band_LR_dB=balance(reference),bands_Hz=bands,reference_active_LR_correlation=float(a.h.measure(reference)['active_lr_correlation']),rows=results,current_eight_independent_renders_metrics=eight,reference_selfcheck_metrics=selfcheck['metrics'],reference_match_reached=False,subjective_listening_performed_by_assistant=False,no_new_Diva_or_GUI_renders_claimed=True)
(OUT/'COMPARISON.json').write_text(json.dumps(report,indent=2)+'\n')
# Listen to original -> earliest controlled preset -> v8 -> current, at one
# common RMS level; use one shared headroom scale for all segments.
order=['reference','v1_controlled','v8','current_cohort_155'];gap=np.zeros((24000,2));joined=np.concatenate([part for label in order for part in [normalized[label],gap]][:-1]);safety=min(1.,.95/float(abs(joined).max()));joined*=safety
sf.write(OUT/'AB_ORIGINAL_V1_V8_CURRENT.wav',joined,48000,subtype='PCM_24');subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'AB_ORIGINAL_V1_V8_CURRENT.wav'),'-codec:a','libmp3lame','-b:a','256k',str(OUT/'AB_ORIGINAL_V1_V8_CURRENT.mp3')],check=True)
(OUT/'AB_METADATA.json').write_text(json.dumps(dict(order=order,starts_seconds=[k*(N+24000)/48000 for k in range(4)],only_AB_level_normalization=True,common_headroom_gain=safety,no_channel_rebalance=True),indent=2)+'\n')
print('REVIEW_COMPLETE',str(OUT/'COMPARISON.json'),flush=True)
