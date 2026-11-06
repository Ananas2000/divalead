from pathlib import Path
V=Path(__file__).resolve().parent;s=(V/'common109_native_gain11_support.py').read_text().replace('/tmp/divalead-native12-common109-native-globalgain11-20261104','/tmp/divalead-native12-common109-native-stereo18-bank16-20261104').replace('ORIGINAL_NATIVE12_COMMON109_NATIVE_GLOBALGAIN11_STUDY.json','ORIGINAL_NATIVE12_COMMON109_NATIVE_STEREO18_BANK16_STUDY.json');(V/'common109_native_stereo18_support.py').write_text(s)
s=(V/'study_common109_native_gain11.py').read_text().replace('import common109_native_gain11_support as q','import common109_native_stereo18_support as q').replace('Common109NativeGain11','Common109Stereo18')
s=s.replace("t.configure(12764+int(delta[0]),12800+int(delta[0]))","t.configure(12764+int(delta[0]),12800+int(delta[1]))")
s=s.replace("models=[(0,)]+[(d,)for d in[-12,-8,-4,-2,-1,1,2,4,8,12]]","models=[(0,0)]+[(l,r)for l in[-16,-8,0,8]for r in[0,8,16,24]if(l,r)!=(0,0)]+[(-4,4),(0,4)]")
needle=" aircap=min(np.mean([d['Air']for d in controls[:3]]),np.mean([d['Air']for d in anchors[:3]]))-.006"
block=''' bank=[];bank_members=[];bankarc=Path('/tmp/divalead-native-stereo18-bank-'+str(os.getpid())+'.tar.gz');(R/'STEREO_CALIBRATION_BANK32_WAVs.tar.gz').symlink_to(bankarc)
 with tarfile.open(bankarc,'w:gz',compresslevel=3)as bt:
  for k in range(16):
   raw,_=n.render();out=cascade(raw,'candidate',[0,0]);edit=q.a.h.edit_aligned(q.a.h.align_with_pdc(out,dict(alignment_frames=819),latency=0));lr=q.lr(edit)[1:];bank.append(lr.tolist())
   for name,y in [('native',raw),('parent',out)]:
    buf=io.BytesIO();sf.write(buf,y,48000,format='WAV',subtype='FLOAT');blob=buf.getvalue();name=name+'-'+str(k)+'.wav';entry=tarfile.TarInfo(name);entry.size=len(blob);bt.addfile(entry,io.BytesIO(blob));bank_members.append(dict(name=name,bytes=len(blob),SHA256=hashlib.sha256(blob).hexdigest()))
   record('actual_stereo_calibration16_native_draws',completed_bank_draws=k+1,bank_max_abs_LR=float(np.max(abs(np.array(bank)))))
 model([0,0]);t.save(R/'PARENT_ZERO_DELTA_NATIVE_TRIM.bin');assert(R/'PARENT_ZERO_DELTA_NATIVE_TRIM.bin').read_bytes()==(R/'TRIM.bin').read_bytes()
 with tarfile.open(bankarc)as bt:
  for row in bank_members:assert hashlib.sha256(bt.extractfile(row['name']).read()).hexdigest()==row['SHA256']
 (R/'STEREO_BANK16_MEASUREMENTS.json').write_text(json.dumps(dict(LR_high_bands=bank,members=bank_members,prediction_is_constant_native_linear_LR_gain_difference_only=True,additional_training_max_abs_LR_limit=1.595),indent=2)+'\\n')
'''+needle
assert needle in s;s=s.replace(needle,block)
needle="feasible=bool(np.mean([d['Air']for d in ds])<=aircap and all(d['stereo_preservation_passed']and d['lowmid_error']<=controls[j]['lowmid_error']+.005 for j,d in enumerate(ds)));row="
replacement="shift=np.zeros(3)if k==0 else np.mean([np.array(d['LR_dB'])[1:]-np.array(base['LR_dB'])[1:]for d,base in zip(ds,rows[0]['captures'])],axis=0);bank_max=float(np.max(abs(np.asarray(bank)+shift)));feasible=bool(bank_max<=1.595 and np.mean([d['Air']for d in ds])<=aircap and all(d['stereo_preservation_passed']and d['lowmid_error']<=controls[j]['lowmid_error']+.005 for j,d in enumerate(ds)));row="
assert needle in s;s=s.replace(needle,replacement)
s=s.replace("row=dict(delta=list(delta),loss=","row=dict(delta=list(delta),predicted_bank_max_abs_LR=bank_max,loss=")
s=s.replace('source_MIDI3_ARP_ADSR_native12_trim_unchanged=True','source_MIDI3_ARP_ADSR_pre_ZL_native12_unchanged=True,final_native_trim_LR_gain_changed=True')
s=s.replace('new_native_both_channels_raw_gain_deltas=[-12,-8,-4,-2,-1,0,1,2,4,8,12]','new_native_L_raw_offsets=[-16,-8,0,8],new_native_R_raw_offsets=[0,8,16,24],additional_near_offsets=[[-4,4],[0,4]],calibration16_common_parent_native_draws=True,training_bank_max_abs_LR1595=True')
s=s.replace('all11_training_models_same3_actual_native_inputs=True','all18_training_models_same3_actual_native_inputs=True').replace('PARTIAL_11_RESULTS','PARTIAL_18_RESULTS').replace('native_global_gain11','native_stereo18_bank16').replace('common109-nativeGain11-new12','common109-nativeStereo18-new12')
s=s.replace('Calibrate finer native output gain; only actual changed presets eligible, all original gates fixed.','Calibrate actual native LR gains with16-draw stereo headroom; all original final gates fixed.')
(V/'study_common109_native_stereo18.py').write_text(s)
print('Prepared18 true native LR settings plus16-draw stereo calibration; final12 unchanged and independent')
